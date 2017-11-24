import datetime

from peewee import CharField, DateTimeField, IntegerField, DoesNotExist

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


def start_scrap(course_id):
    """Begin the scraping process targeting the specified Piazza course id

    :param course_id: Piazza course ID
    :type course_id: str
    """
    try:
        login = Login.get(Login.can_access == course_id)
    except DoesNotExist:
        raise Exception("No login available for this class")

    scrape_record = Scrape(course_scanned=course_id)
    for post in iterate_piazza_posts(course_id, login.username, login.password):
        scrape_record.posts_scanned += 1

    scrape_record.end_time = datetime.datetime.now()
