import logging

from textblob import TextBlob

from api.common import util


def new_stats_dict():
    """Returns a new Stats object dict loaded with defaults"""
    return {
        'today_posts': 0,
        'prev_week_posts': 0,
        'this_week_posts': 0,
        'total_posts': 0,
        'sentiment': {},
        'subjectivity': {},
        'post_day_of_year' : set(),
        'total_words_posted': 0,
        'weekday_posts': {0:0,1:0,2:0,3:0,4:0,5:0,6:0},
        'days_apart_avg': 0,
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

    stats_dict[post.user_id]['course_id'] = post.course_id

    stats_dict[post.user_id]['total_posts'] += 1
    if util.date_is_today(post.timestamp):
        stats_dict[post.user_id]['today_posts'] += 1
    if util.date_is_prev_week(post.timestamp):
        stats_dict[post.user_id]['prev_week_posts'] += 1
    if util.date_is_this_week(post.timestamp):
        stats_dict[post.user_id]['this_week_posts'] += 1

    day_of_week = util.date_get_weekday(post.timestamp)
    stats_dict[post.user_id]['weekday_posts'][day_of_week] += 1

    day_of_year = util.date_get_day_of_year(post.timestamp)
    stats_dict[post.user_id]['post_day_of_year'].add(day_of_year)

    analysis = TextBlob(util.extract_html_text(post.content))
    if day_of_year not in stats_dict[post.user_id]['sentiment']:
        stats_dict[post.user_id]['sentiment'][day_of_year] = 0
    stats_dict[post.user_id]['sentiment'][day_of_year] += analysis.sentiment.polarity
    stats_dict[post.user_id]['sentiment'][day_of_year] /= stats_dict[post.user_id]['total_posts']
    if day_of_year not in stats_dict[post.user_id]['subjectivity']:
        stats_dict[post.user_id]['subjectivity'][day_of_year] = 0
    stats_dict[post.user_id]['subjectivity'][day_of_year] += analysis.sentiment.subjectivity
    stats_dict[post.user_id]['subjectivity'][day_of_year] /= stats_dict[post.user_id]['total_posts']
    stats_dict[post.user_id]['total_words_posted'] += len(analysis.words)

    # For average days bewteen, look at post_day_of_year dict, sort, sum the difference and average
    diff = 0
    days = sorted(stats_dict[post.user_id]['post_day_of_year'])
    if len(days) > 0:
        if len(days) % 2 != 0:
            days.pop(-1)
        for a,b in zip(days[::2], days[1::2]):
            diff += b-a
        stats_dict[post.user_id]['days_apart_avg'] = diff / len(stats_dict[post.user_id]['post_day_of_year'])