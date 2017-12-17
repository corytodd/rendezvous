from api.common import db
from api.resources import scrape
import unittest

from api_test.common import MockPiazzaWrapper


class TestScrape(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        db.setup(clean=True)
        cls.course_id = 'yeigling'
        cls.login = scrape.Login(username='test',
                                 password='12345',
                                 can_access=cls.course_id)
        cls.login.save()

    @classmethod
    def tearDownClass(cls):
        db.teardown()
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_make_piazza_wrapper_invalid(self):
        course_id = "some course without login"
        result = scrape.make_piazza_wrapper(course_id)
        self.assertIsNone(result)

    def test_begin_valid_scrape(self):
        wrapper = MockPiazzaWrapper()
        scrape.start_scrape(wrapper, self.course_id)
