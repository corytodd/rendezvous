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
        'sentiment_trace' : {},
        'subjectivity': {},
        'subjectivity_trace' : {},
        'post_day_of_year' : {},
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
        stats = new_stats_dict()
    else:
        stats = stats_dict[post.user_id]

    stats['course_id'] = post.course_id

    # Dates
    stats['total_posts'] += 1
    if util.date_is_today(post.timestamp):
        stats['today_posts'] += 1
    if util.date_is_prev_week(post.timestamp):
        stats['prev_week_posts'] += 1
    if util.date_is_this_week(post.timestamp):
        stats['this_week_posts'] += 1

    day_of_week = util.date_get_weekday(post.timestamp)
    stats['weekday_posts'][day_of_week] += 1

    day_of_year = util.date_get_day_of_year(post.timestamp)
    if day_of_year not in stats['post_day_of_year']:
        stats['post_day_of_year'][day_of_year] = 0
    stats['post_day_of_year'][day_of_year] += 1



    # NLP - sentiment
    analysis = TextBlob(util.extract_html_text(post.content))
    if day_of_year not in stats['sentiment']:
        stats['sentiment'][day_of_year] = 0
    stats['sentiment'][day_of_year] += analysis.sentiment.polarity
    stats['sentiment'][day_of_year] /= stats['total_posts']

    # Calculate average sentiment for this date: score / total post for this day
    if day_of_year not in stats['sentiment_trace']:
        stats['sentiment_trace'][day_of_year] = 0.0
    date_sentiment = stats['sentiment_trace'][day_of_year] + analysis.sentiment.polarity
    stats['sentiment_trace'][day_of_year] = date_sentiment / stats['post_day_of_year'][day_of_year]



    # NLP - subjective vs. objective
    if day_of_year not in stats['subjectivity']:
        stats['subjectivity'][day_of_year] = 0
    stats['subjectivity'][day_of_year] += analysis.sentiment.subjectivity
    stats['subjectivity'][day_of_year] /= stats['total_posts']

    # Calculate average subjectivity for this date: score / total post for this day
    if day_of_year not in stats['subjectivity_trace']:
        stats['subjectivity_trace'][day_of_year] = 0.0
    date_subjectivity = stats['subjectivity_trace'][day_of_year] + analysis.sentiment.polarity
    stats['subjectivity_trace'][day_of_year] = date_subjectivity / stats['post_day_of_year'][day_of_year]

    stats['total_words_posted'] += len(analysis.words)

    # For average days between, look at post_day_of_year dict, sort, sum the difference and average
    diff = 0
    days = sorted(stats['post_day_of_year'].keys())
    if len(days) > 0:
        if len(days) % 2 != 0:
            days.pop(-1)
        for a,b in zip(days[::2], days[1::2]):
            diff += b-a
        stats['days_apart_avg'] = diff / len(stats['post_day_of_year'])

    stats_dict[post.user_id] = stats