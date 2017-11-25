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
        cls.stats = stats.Stats(lts_id='12345', course_id='56565')
        cls.stats.save()

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
