import random
import time

import datetime

from piazza_api.exceptions import AuthenticationError
from piazza_api.piazza import Piazza
from piazza_api.piazza import PiazzaRPC


def validate_params(should_be, *args):
    """Returns true if each arg is of type 'should_be'"""
    if not args:
        return False
    return all(type(a) is should_be for a in args)


class InvalidPiazzaLogin(Exception):
    """Wraps Piazza API auth failure"""
    pass


class PiazzaWrapper(object):
    """Wraps Piazza API to control for authentication
    failure and to enable mocking the service"""

    def __init__(self, network_id, username, password):
        """Create a new wrapper

            :param network_id: Piazza network ID
            :param username: Piazza username
            :param password: Piazza login password
            :type network_id: str
            :type username: str
            :type password: str
        """
        self.network_id = network_id
        self.username = username
        self.password = password
        self.rpc = None
        self.course = None
        self.network = None

    def login(self):
        """Attempts to login to Piazza
            :raises InvalidPiazzaLogin
        """
        try:
            self.rpc = PiazzaRPC(self.network_id)
            self.course = Piazza(self.rpc)
            self.rpc.user_login(self.username, self.password)
            self.network = self.course.network(self.network_id)
        except AuthenticationError:
            raise InvalidPiazzaLogin("Failed to login to: {}".format(self.network_id))

    def get_post_iterator(self, limit=10):
        """Returns an interator for the specified number of posts

            :param limit: Number of posts to iterate over. Set to -1
                to retrieve all posts.
            :type limit: int
            :return Iterator that returns JSON
            :rtype iterator
        """
        if limit < 0:
            limit = None
        return self.network.iter_all_posts(limit)


def iterate_piazza_posts(rpc_wrapper, limit=10, backoff_fn=None):
    """Iterate over all piazza posts in specified network.
    This function will yield one post at a time until the iterator
    has been exhausted. This uses a random delay algorithm to wait
    between 3 and 7 seconds between each fetch. This is to prevent
    slamming the Piazza servers which are slow enough already.

    :param rpc_wrapper: Piazza RPC wrapper
    :param limit: Stop iterating after this many posts
    :param backoff_fn: Function to produce a backoff time period,
        default produces a period between 3 and 7 seconds.
    :type rpc_wrapper: PiazzaWrapper
    :type limit: int, None
    :type backoff_fn: function->int
    :yield piazza post iterator
    :rtype iterator:
    """
    it = rpc_wrapper.get_post_iterator(limit=limit)
    if not backoff_fn:
        def backoff_fn():
            return 2 + random.uniform(1.1, 5.1)
    for post in it:
        yield post
        time.sleep(backoff_fn())


def date_from_piazza_str(date_str):
    """Convert ugly date string into Python datetime
        :param date_str: Input string
        :type date_str: str
        :return Python datetime
        :rtype datetime:
    """
    clean = str(date_str).replace(' ', '')
    return datetime.datetime.strptime(clean, "%Y-%m-%dT%H:%M:%SZ")


def date_to_piazza_str(date_obj):
    """Returns date_obj as Piazza datetime string
        :param date_obj: Input datetime
        :type date_obj: datetime.datetime
        :rtype: str
        :return string format of datetime
    """
    return date_obj.strftime("%Y-%m-%dT%H:%M:%SZ")


def date_is_today(date_str):
    """Return true if date_str is today in local time"""
    as_date = date_from_piazza_str(date_str)
    return as_date.date() == datetime.datetime.today().date()


def date_get_day_0_of_week():
    """Returns the date marking start of day zero for this current week
    To avoid ambiguity and make my life easier, we use Monday as 0.
    """
    now = datetime.datetime.today()
    day_offset = now.weekday()
    return now - datetime.timedelta(days=day_offset)


def date_is_this_week(date_str):
    """Return true if date_str occurs within current week
    For all dates, Sunday at midnight is considered epoch
        :example
             Week 0 is Sunday 5th 12:00 AM through Sunday 12th 11:59 PM
             Week 1 is Sunday 12th 12:00 AM ... etc.
        :
        :param date_str: input date string in Pizza format, %Y-%m-%dT%H:%M:%SZ
        :type date_str: str
        :return Python datetime object
        :rtype datetime
    """
    start_of_week = date_get_day_0_of_week()
    end_of_week = date_get_day_0_of_week() + datetime.timedelta(days=7)
    as_date = date_from_piazza_str(date_str)
    return start_of_week.date() <= as_date.date() < end_of_week.date()


def date_is_prev_week(date_str):
    """Return true if date_str occurs before start of this week and after
    start of previous week
    Previous week would satisfy Week -1
        :example
             Week -1 is Sunday 5th 12:00 AM through Sunday 12th 11:59 PM
             Week 0 is Sunday 12th 12:00 AM ... etc.
        :
        :param date_str: input date string in Pizza format, %Y-%m-%dT%H:%M:%SZ
        :type date_str: str
        :return Python datetime object
        :rtype datetime
    """
    start_of_week = date_get_day_0_of_week()
    start_of_prev_week = start_of_week - datetime.timedelta(days=7)
    as_date = date_from_piazza_str(date_str)
    return start_of_prev_week.date() <= as_date.date() < start_of_week.date()


def date_get_weekday(date_str):
    """Returns day of weeks as integer, Monday == 0"""
    as_date = date_from_piazza_str(date_str)
    return as_date.weekday()
