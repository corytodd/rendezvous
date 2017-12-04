import json

from peewee import IntegerField, BlobField, FloatField, DoesNotExist, CharField

from api.common.db import BaseModel
from api.resources import course


class Stats(BaseModel):
    today_posts = IntegerField(default=0)
    prev_week_posts = IntegerField(default=0)
    this_week_posts = IntegerField(default=0)
    total_posts = IntegerField(default=0)
    sentiment = BlobField(json.dumps([]))
    total_words_posted = IntegerField(default=0)
    weekday_posts = BlobField(json.dumps([]))
    days_apart_sum = IntegerField(default=0)
    fractional_relevance_sum = FloatField(default=0)
    lts_id = CharField()
    course_id = CharField()


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
        result[name] = {}
    return result