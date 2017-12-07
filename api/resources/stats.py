import json

from peewee import IntegerField, BlobField, FloatField, DoesNotExist, CharField

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