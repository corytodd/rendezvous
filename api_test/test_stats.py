from api.common import db
from api.resources import stats
from api.resources import course
import unittest


class TestStats(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        db.setup(clean=True)
        # See with a known user
        course.create_if_not_exist('56565', 'english')
        d = stats.Stats.new_stats_dict()
        d['lts_id']='12345'
        d['course_id']='56565'
        d['weekday_posts_list'] = [1,2,3,4,5,6,7]
        d['post_day_of_year_dict'] = { 12:23, 34:1, 45:1}
        d['sentiment_dict'] = {12 : 0.23, 56:-0.4, 210:0.5}
        d['subjectivity_dict'] = {12 : 0.23, 56:-0.4, 210:0.5}
        d = stats.Stats.blobify({'12345': d})
        stats.Stats.create(**d[0])

    @classmethod
    def tearDownClass(cls):
        db.teardown()
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_known_stats(self):
        result = stats.get_stats('12345')
        self.assertTrue(len(result.keys()) == 1)

    def test_get_unknown_stats(self):
        result = stats.get_stats('9878')
        self.assertTrue(len(result.keys()) == 0)
