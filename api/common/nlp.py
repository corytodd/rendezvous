import logging

from bs4 import BeautifulSoup
from textblob import TextBlob

from api.common import util

def clean_text(text):
    """Returns plain text from HTML blob
        :param text: input text
        :type text: str
        :return String with HTML removed
        :rtype: str
    """
    soup = BeautifulSoup(text, 'html.parser')
    return soup.get_text()


def new_stats_dict():
    """Returns a new Stats object dict loaded with defaults"""
    return {
        'today_posts': 0,
        'prev_week_posts': 0,
        'this_week_posts': 0,
        'total_posts': 0,
        'sentiment': {},
        'total_words_posted': 0,
        'weekday_posts': [],
        'days_apart_sum': 0,
        'fractional_relevance_sum': 0,
        'lts_id': '',
        'course_id': ''
    }

def process_post(post, stats_dict=None):
    """Process PiazzaPost and extract attributes to associated
    with user stats

        :param post: Piazza Post to analyze
        :param stats_dict: Dictionary keyed by user_id containing stats dicts
        :type post: PiazzaPost
        :type stats_dict: dict
        :return None
    """
    logging.info("Processing post type: {}".format(type(post)))

    if len(post.content) <= 0:
        logging.info("Empty post from {} on {}, no processing", post.user_id, post.cid)
        return stats_dict


    if post.user_id not in stats_dict:
        stats_dict[post.user_id] = new_stats_dict()

    stats_dict[post.user_id]['total_posts'] += 1
    if util.date_is_today(post.timestamp):
        stats_dict[post.user_id]['today_posts'] += 1
    if util.date_is_prev_week(post.timestamp):
        stats_dict[post.user_id]['prev_week_posts'] += 1
    if util.date_is_this_week(post.timestamp):
        stats_dict[post.user_id]['this_week_posts'] += 1

    analysis = TextBlob(clean_text(post.content))
    day_of_year = util.date_get_day_of_year(post.timestamp)
    if day_of_year not in stats_dict[post.user_id]['sentiment']:
        stats_dict[post.user_id]['sentiment'][day_of_year] = 0
    stats_dict[post.user_id]['sentiment'][day_of_year] += analysis.sentiment.polarity

    stats_dict[post.user_id]['total_words_posted'] += len(analysis.words)

    return stats_dict
