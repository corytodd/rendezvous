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

            :param limit: Number of posts to iterate over. Set to None
                to retrieve all posts.
            :type limit: int
            :return Iterator that returns JSON
            :rtype iterator
        """
        return self.network.iter_all_posts(limit)


def iterate_piazza_posts(rpc_wrapper, limit=10):
    """Iterate over all piazza posts in specified network.
    This function will yield one post at a time until the iterator
    has been exhausted. This uses a random delay algorithm to wait
    between 3 and 7 seconds between each fetch. This is to prevent
    slamming the Piazza servers which are slow enough already.

    :param rpc_wrapper: Piazza RPC wrapper
    :param limit: Stop iterating after this many posts
    :type rpc_wrapper: PiazzaWrapper
    :type limit: int, None
    :return piazza post iterator
    :rtype iterator:
    """
    it = rpc_wrapper.get_post_iterator(limit=limit)
    for post in it:
        yield post
        time.sleep(2 + random.uniform(1.1, 5.1))


def piazza_time_to_datetime(datestr):
    """Convert a Piazza timestamp to a python datetime
        :param datestr: Input string
        :type datestr: str
        :return Python datetime
        :rtype datetime
    """
    datestr = str(datestr).replace(' ', '')
    astime = datetime.datetime.strptime(datestr, "%Y-%m-%dT%H:%M:%SZ")
    return astime.timestamp()
