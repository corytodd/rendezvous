import random
import time
from piazza_api.piazza import Piazza
from piazza_api.piazza import PiazzaRPC

def validate_params(should_be, *args):
    """Returns true if each arg is of type 'should_be'"""
    return all(type(a) is should_be for a in args)


def iterate_piazza_posts(network_id, username, password):
    """Iterate over all piazza posts in specified network.
    This function will yield one post at a time until the iterator
    has been exhausted. This uses a random delay algorithm to wait
    between 3 and 7 seconds between each fetch. This is to prevent
    slamming the Piazza servers which are slow enough already.

    :param network_id: Piazza course id from url
    :param username: Piazza student email login
    :param password: Piazza student login password
    :type network_id: str
    :type username: str
    :type password: str
    :return piazza post iterator
    :rtype iterator:
    """
    rpc = PiazzaRPC(network_id)
    rpc.user_login(username, password)
    course = Piazza(rpc)
    network = course.network(network_id)
    it = network.iter_all_posts()

    for post in it:
        yield post
        time.sleep(2 + random.uniform(1.1, 5.1))