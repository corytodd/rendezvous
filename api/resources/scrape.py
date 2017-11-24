import datetime

from peewee import CharField, DateTimeField, IntegerField, DoesNotExist

from api.common import util
from api.common.db import BaseModel
from api.common.util import iterate_piazza_posts


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
    start_time = DateTimeField(default=datetime.datetime.now)
    end_time = DateTimeField(null=True)
    course_scanned = CharField(null=False)
    posts_scanned = IntegerField(default=0)


class PiazzaPost(object):
    """Not stored in database, hold Piazza post. This only tracks the latest revision of
    a post, history is not considered"""

    def __init__(self, cid, user_id, timestamp, content, is_original_post):
        # Unique for a discussion, show in URL cid query param
        self.cid = cid
        # Piazza ID of the user who authored the post
        self.user_id = user_id
        # Datetime the most recent revision of the post was created
        self.timestamp = timestamp
        # The actual content
        self.content = content
        # The top level or topic post that all posts are in response to
        self.is_original_post = is_original_post


class NoLoginAvailable(Exception):
    """Raised when a course id does not have a known authentication
    record."""
    pass


def start_scrap(course_id):
    """Begin the scraping process targeting the specified Piazza course id

    :param course_id: Piazza course ID
    :type course_id: str
    :raises NoLoginAvailable: If no login credentials are available for specified course
    """
    try:
        login = Login.get(Login.can_access == course_id)
    except DoesNotExist:
        raise NoLoginAvailable("No login available for this class")

    scrape_record = Scrape(course_scanned=course_id)
    for obj in iterate_piazza_posts(course_id, login.username, login.password):
        scrape_record.posts_scanned += 1

        cid = obj['nr']

        # OP is the 1st item in the history list
        op = obj['history']
        if len(op) == 0:
            print("Zero length OP: {}".format(cid))
            continue
        post = op[0]

        if 'uid' not in post:
            print("Coward anon: {}".format(cid))
            uuid = 'anon'
        else:
            uuid = post['uid']

        timestamp = util.piazza_time_to_datetime(post['created'])

        top_post = PiazzaPost(cid, uuid, timestamp,
                              post['content'], True)

        def get_children(_obj):

            if 'children' not in _obj:
                print("Abandoned post: {}".format(cid))
                return

            for child in _obj['children']:
                if 'uid' not in child:
                    print("Coward anon child: {}".format(cid))
                    _uuid = 'anon'
                else:
                    _uuid = child['uid']

                if 'subject' not in child:
                    continue

                _timestamp = util.piazza_time_to_datetime(post['created'])
                child_post = PiazzaPost(cid, _uuid, _timestamp,
                                        post['subject'], False)

                get_children(child)

        get_children(obj)

    scrape_record.end_time = datetime.datetime.now()
