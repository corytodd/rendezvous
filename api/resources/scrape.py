import datetime
import logging

from peewee import CharField, DateTimeField, IntegerField, DoesNotExist

from api.common import util, nlp, db
from api.common.db import BaseModel
from api.resources.stats import Stats


class Login(BaseModel):
    """Stores login credentials for each Piazza class
    TODO this can't really be made secure but we can
    obfuscate.
    """
    username = CharField()
    password = CharField()
    can_access = CharField()


class Scrape(BaseModel):
    """Record tracks a scrape event, useful for debugging"""
    start_time = DateTimeField(default=datetime.datetime.now, formats='%Y-%m-%d %H:%M:%S.%f')
    end_time = DateTimeField(null=True, formats='%Y-%m-%d %H:%M:%S.%f')
    course_scanned = CharField(null=False)
    posts_scanned = IntegerField(default=0)


class PiazzaPost(object):
    """Not stored in database, hold Piazza post. This only tracks the latest revision of
    a post, history is not considered"""

    def __init__(self, cid, user_id, course_id, timestamp, topic, content, is_original_post):
        # Unique for a discussion, show in URL cid query param
        self.cid = cid
        # Unique course id
        self.course_id = course_id
        # Piazza ID of the user who authored the post
        self.user_id = user_id
        # Datetime the most recent revision of the post was created
        self.timestamp = timestamp
        # Original post topic
        self.topic = topic
        # The actual content
        self.content = util.extract_html_text(content)
        # The top level or topic post that all posts are in response to
        self.is_original_post = is_original_post


def make_piazza_wrapper(course_id):
    """Creates a Piazza RPC wrapper using the specified login info

        :param course_id: Piazza course ID
        :type course_id: str
        :return PiazzaWrapper instance
        :rtype PiazzaWrapper
        :raises InvalidPiazzaLogin: If stored credentials are invalid
    """
    try:
        login = Login.get(Login.can_access == course_id)
        wrapper = util.PiazzaWrapper(course_id, str(login.username),
                                     str(login.password))
        wrapper.login()
        return wrapper
    except DoesNotExist:
        return None


def start_scrape(wrapper, course_id):
    """Begin the scraping process targeting the specified Piazza course id

    :param wrapper: Piazza wrapper
    :param course_id: Piazza course ID
    :type wrapper: PiazzaWrapper
    :type course_id: str
    """

    it = wrapper.get_post_iterator(limit=-1)

    # Keyed by user UID, value is Stats object in dict form
    user_stats_dict = {}

    scrape_record = Scrape(course_scanned=course_id)
    for obj in it:
        scrape_record.posts_scanned += 1

        cid = obj['nr']

        # OP is the 1st item in the history list
        op = obj['history']
        if len(op) == 0:
            logging.info("Zero length OP: {}".format(cid))
            continue
        post = op[0]

        if 'uid' not in post:
            logging.info("Coward anon: {}".format(cid))
            uuid = 'anon'
        else:
            uuid = post['uid']

        timestamp = util.date_from_piazza_str(post['created']).timestamp()

        top_post = PiazzaPost(cid, uuid, course_id, timestamp, post['subject'],
                              post['content'], True)
        nlp.process_post(top_post, user_stats_dict)

        def get_children(_obj, _user_stats_dict):

            if 'children' not in _obj:
                logging.info("Abandoned post: {}".format(cid))
                return

            for child in _obj['children']:
                _uuid = 'anon'
                if 'type' not in child:
                    # Malformed
                    continue
                if child['type'] in ['feedback', 'followup']:
                    if 'uid' in child:
                        _uuid = child['uid']
                elif child['type'] in ['s_answer', 'i_answer']:
                    if 'uid' in child:
                        _uuid = child['uid']
                    elif len(child['history']) > 0:
                        if 'uid' in child['history'][0]:
                            _uuid = child['history'][0]['uid']
                elif child['type'] == 'dupe':
                    logging.info("Skipping duplicate post")
                    continue
                else:
                    # Malformed
                    continue

                if 'subject' not in child:
                    continue

                _timestamp = util.date_from_piazza_str(post['created']).timestamp()
                child_post = PiazzaPost(cid, _uuid, course_id, _timestamp, post['subject'],
                                        post['content'], False)
                nlp.process_post(child_post, _user_stats_dict)
                get_children(child, _user_stats_dict)

        get_children(obj, user_stats_dict)

    scrape_record.end_time = datetime.datetime.now()
    scrape_record.save()

    print("Scrape took: {}".format(scrape_record.end_time - scrape_record.start_time))

    data_source = Stats.blobify(user_stats_dict)
    try:
        for m in util.chunks(data_source, 25):
            with db.db.atomic():
                Stats.insert_many(m).execute()

        print("Database store completed")
    except Exception as e:
        print("failed to db: {}".format(e))
