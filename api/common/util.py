import calendar
import random
import time

import datetime

from collections import OrderedDict
from piazza_api.exceptions import AuthenticationError
from piazza_api.piazza import Piazza
from piazza_api.piazza import PiazzaRPC
from bs4 import BeautifulSoup

# https://stackoverflow.com/a/41496131
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module='bs4')



def validate_params(should_be, *args):
    """Returns true if each arg is of type 'should_be'
    """
    if not args:
        return False
    return all(type(a) is should_be for a in args)


class InvalidPiazzaLogin(Exception):
    """Wraps Piazza API auth failure
    """
    pass


class PiazzaWrapper(object):
    """Wraps Piazza API to control for authentication
    failure and to enable mocking the service
    """

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
        """
            Attempts to login to Piazza
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
            :param limit: Number of posts to iterate over. Set to -1 to retrieve all posts.
            :type limit: int
            :return Iterator that returns JSON
            :rtype iterator:
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
        :param backoff_fn: Function to produce a backoff time period, default produces a period between 3 and 7 seconds.
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


def date_is_today(timestamp):
    """Return true if timestamp is today in local time"""
    as_date = date_from_timestamp(timestamp)
    return as_date.date() == datetime.datetime.today().date()


def date_get_day_0_of_week():
    """Returns the date marking start of day zero for this current week
    To avoid ambiguity and make my life easier, we use Monday as 0.
    """
    now = datetime.datetime.today()
    day_offset = now.weekday()
    return now - datetime.timedelta(days=day_offset)


def date_is_this_week(timestamp):
    """Return true if date_str occurs within current week. For all dates, Sunday at midnight is considered epoch
        :example \
             Week 0 is Sunday 5th 12:00 AM through Sunday 12th 11:59 PM \
             Week 1 is Sunday 12th 12:00 AM ... etc.
        :
        :param timestamp: input date as Unix timestamp
        :type timestamp: float
        :return Python datetime object
        :rtype datetime
    """
    start_of_week = date_get_day_0_of_week()
    end_of_week = date_get_day_0_of_week() + datetime.timedelta(days=7)
    as_date = date_from_timestamp(timestamp)
    return start_of_week.date() <= as_date.date() < end_of_week.date()


def date_is_prev_week(timestamp):
    """Return true if date_str occurs before start of this week and after start of previous week
        Previous week would satisfy Week -1
        :example \
             Week -1 is Sunday 5th 12:00 AM through Sunday 12th 11:59 PM \
             Week 0 is Sunday 12th 12:00 AM ... etc.
        :
        :param timestamp: input date as Unix timestamp
        :type timestamp: float
        :return Python datetime object
        :rtype datetime
    """
    start_of_week = date_get_day_0_of_week()
    start_of_prev_week = start_of_week - datetime.timedelta(days=7)
    as_date = date_from_timestamp(timestamp)
    return start_of_prev_week.date() <= as_date.date() < start_of_week.date()


def date_get_weekday(timestamp):
    """Returns day of weeks as integer, Monday == 0"""
    as_date = date_from_timestamp(timestamp)
    return as_date.weekday()


def date_from_timestamp(timestamp):
    """Returns datetime from unix timestamp"""
    return datetime.datetime.fromtimestamp(timestamp)


def date_get_day_of_year(timestamp):
    """Returns integer day of year from timestamp"""
    return datetime.datetime.fromtimestamp(timestamp).timetuple().tm_yday


def date_from_year_day_number(year, day_number):
    """Return date from year and day number, e.g. 2017, 283 == Oct 10 2017"""
    return datetime.datetime(year, 1, 1) + datetime.timedelta(day_number - 1)


def day_from_number(day):
    """Return day of week name for day, 0-6 where 0 == Monday"""
    return calendar.day_name[day]


def extract_html_text(text):
    """Returns plain text from HTML blob
        :param text: input text
        :type text: str
        :return String with HTML removed
        :rtype: str
    """
    soup = BeautifulSoup(text, 'html.parser')
    return soup.get_text()


def make_sentiment_css(sentiment):
    """Convert sentiment map into a CSS gradient
        :param sentiment: dict with integer key and float values \
        key represents day of year, float is -1 to 1 sentiment polarity
        :type sentiment: dict
        :return css string
        :rtype str

    """

    def make_colors(vals=None, sat=100, lum=50):
        """Convert val to an HSL string clamped by -1 to 1, red to green
        respectively. For example, -0.45 will produce
            :param vals: List of float values to HSLify
            :param lum: lumenance
            :param sat: Saturation
            :type vals: list of float
            :type sat: int
            :type lum: int
            :return List of HSL color strings
            :rtype list(str)
        """
        result = []
        # Our range has two points, -1 to 1
        for val in vals:
            val = int(((val + 1) / 2) * 128)
            # HSL with full saturation and half luminance
            result.append("hsl({}, {}%, {}%)".format(val, sat, lum))
        return result

    def make_spread(vals=None):
        """Convert a list of ints to a list of floats distributed as
        percentages between the 100% scaled min and max values in the list.
        The list will not be rearranged. For examples, [3, 32, 12, 9, 24]
        produces [0.0, 100.0, 28.12, 18.75, 65.52]
            :param vals: list of values to spread
            :type vals: list of ints
            :return spread as a scaled list
            :rtype list of float
        """
        copy = list(vals)
        mn = min(copy)
        mx = max(copy)
        factor = 100.0 / float(mx - mn)
        copy = list(map(lambda x: x - mn, vals))
        copy = list(map(lambda x: int(x * factor), copy))
        return copy

    # Algorithm::
    #  The key is treated as the time series and the entire range
    #  of values is scaled such that the min and max become the respetive
    #  0% and 100 % values in the time range. The value is converted
    #  into a color by converting the clamped -1 to 1 range to an HSL
    # color space between 0 and 128 (red to green).
    css = '''background: -moz-linear-gradient(left, {0});
background: -webkit-linear-gradient(left, {0});
background: linear-gradient(to right, {0});'''

    # Put tuples in ascending key order
    in_order = list(OrderedDict(sorted(sentiment.items(), key=lambda t: t[0])).items())

    # This unpacks a list of tuples into n distinct lists, where n is tuple len
    k, v = zip(*in_order)
    spread = make_spread(k)
    colors = make_colors(v)
    recombined = zip(colors, spread)

    # Join list of tuples back into a string, a. la #FF0000 0%, # 7F8900 15%, ...
    gradient = ", ".join("%s %s%%" % t for t in recombined)
    return css.format(gradient)


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]
