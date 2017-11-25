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
    pass

def iterate_piazza_posts(network_id, username, password, limit=10):
    """Iterate over all piazza posts in specified network.
    This function will yield one post at a time until the iterator
    has been exhausted. This uses a random delay algorithm to wait
    between 3 and 7 seconds between each fetch. This is to prevent
    slamming the Piazza servers which are slow enough already.

    :param network_id: Piazza course id from url
    :param username: Piazza student email login
    :param password: Piazza student login password
    :param limit: Stop iterating after this many posts
    :type network_id: str
    :type username: str
    :type password: str
    :type limit: int
    :return piazza post iterator
    :rtype iterator:
    """
    try:
        rpc = PiazzaRPC(network_id)
        rpc.user_login(username, password)
        course = Piazza(rpc)
        network = course.network(network_id)
        it = network.iter_all_posts(limit=limit)

        for post in it:
            yield post
            time.sleep(2 + random.uniform(1.1, 5.1))

    except AuthenticationError:
        raise InvalidPiazzaLogin("Failed to login to: {}".format(network_id))


def piazza_time_to_datetime(datestr):
    datestr = str(datestr).replace(' ', '')
    astime = datetime.datetime.strptime(datestr, "%Y-%m-%dT%H:%M:%SZ")
    return astime.timestamp()
