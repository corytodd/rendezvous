import json

from peewee import IntegerField, BlobField, FloatField, DoesNotExist, CharField

from api.common import util
from api.common.db import BaseModel
from api.resources import course


class Stats(BaseModel):
    today_posts = IntegerField(default=0)
    prev_week_posts = IntegerField(default=0)
    this_week_posts = IntegerField(default=0)
    total_posts = IntegerField(default=0)
    total_words_posted = IntegerField(default=0)
    weekday_posts_list = BlobField(json.dumps([0, 0, 0, 0, 0, 0, 0]))
    post_day_of_year_dict = BlobField(json.dumps({}))
    days_apart_avg = IntegerField(default=0)
    sentiment_dict = BlobField(json.dumps({}))
    subjectivity_dict = BlobField(json.dumps({}))
    lts_id = CharField()
    course_id = CharField()

    @staticmethod
    def new_stats_dict():
        """Returns a new Stats object dict loaded with defaults"""
        return {
            'today_posts': 0,
            'prev_week_posts': 0,
            'this_week_posts': 0,
            'total_posts': 0,
            'total_words_posted': 0,
            'weekday_posts_list': [0, 0, 0, 0, 0, 0, 0],
            'post_day_of_year_dict': {},
            'days_apart_avg': 0,
            'sentiment_dict': {},
            'subjectivity_dict': {},
            'lts_id': '',
            'course_id': ''
        }

    @staticmethod
    def to_dict(stats, inject_css):
        """Convert Stats object to dict
            :param stats: Stats object to convert
            :type stats: Stats
            :param inject_css: True to convert sentiment_dict
                to sentiment gradient
            :type inject_css: bool
            :return stats in dict form
            :rtype dict
        """
        # If this field is in bytes form, stats must have been
        # queried from the db so all iterables must be cast
        if type(stats.weekday_posts_list) is bytes:
            result = {
                'today_posts': stats.today_posts,
                'prev_week_posts': stats.prev_week_posts,
                'this_week_posts': stats.this_week_posts,
                'total_posts': stats.total_posts,
                'total_words_posted': stats.total_words_posted,
                'weekday_posts_list': json.loads(stats.weekday_posts_list),
                'post_day_of_year_dict': json.loads(stats.post_day_of_year_dict),
                'days_apart_avg': stats.days_apart_avg,
                'sentiment_dict': json.loads(stats.sentiment_dict),
                'subjectivity_dict': json.loads(stats.subjectivity_dict),
                'lts_id': stats.lts_id,
                'course_id': stats.course_id
            }
            # Re-apply the data types we expect
            result['weekday_posts_list'] = [*map(int, result['weekday_posts_list'])]
            int_float_dicts = ['post_day_of_year_dict', 'sentiment_dict', 'subjectivity_dict']
            for m in int_float_dicts:
                result[m] = {int(k): float(v) for k, v in result[m].items()}
        else:
            result = {
                'today_posts': stats.today_posts,
                'prev_week_posts': stats.prev_week_posts,
                'this_week_posts': stats.this_week_posts,
                'total_posts': stats.total_posts,
                'total_words_posted': stats.total_words_posted,
                'weekday_posts_list': stats.weekday_posts_list,
                'post_day_of_year_dict': stats.post_day_of_year_dict,
                'days_apart_avg': stats.days_apart_avg,
                'sentiment_dict': stats.sentiment_dict,
                'subjectivity_dict': stats.subjectivity_dict,
                'lts_id': stats.lts_id,
                'course_id': stats.course_id
            }
        if inject_css:
            result['sentiment_css'] = util.make_sentiment_css(result['sentiment_dict'])

        lowest_sent = min(result['sentiment_dict'], key=result['sentiment_dict'].get)
        highest_sent = max(result['sentiment_dict'], key=result['sentiment_dict'].get)
        result['most_negative_date'] = util.date_from_year_day_number(2017, lowest_sent).strftime('%Y-%m-%d')
        result['most_positive_date'] = util.date_from_year_day_number(2017, highest_sent).strftime('%Y-%m-%d')
        return result


def get_stats(lts_id):
    """Returns the stats for the specified user or None if not found
    :param lts_id: Student id
    :type lts_id: str
    :return dictionary of stats keyed by course name
    :rtype dict:
    """
    result = {}
    for st in Stats.select().where(Stats.lts_id == lts_id):
        name = course.get_course_name(st.course_id)
        result[name] = Stats.to_dict(st, True)
    return result
