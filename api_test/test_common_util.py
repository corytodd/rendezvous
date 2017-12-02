import datetime

from api.common import util
import unittest

from api.common.util import InvalidPiazzaLogin
from api_test.common import MockPiazzaWrapper


class TestCommonUtils(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_validate_params_str(self):
        self.assertTrue(util.validate_params(str, 'hello', 'world'))

    def test_validate_params_int(self):
        self.assertTrue(util.validate_params(int, 1, 2, 3, 4, 5, 6))

    def test_validate_params_fail(self):
        self.assertFalse(util.validate_params(tuple, ['1', 1]))

    def test_validate_params_empty(self):
        self.assertFalse(util.validate_params(list))

    def test_bad_piazza_login(self):
        wrapper = util.PiazzaWrapper('19difen3fd3',
                                     'me@example.org',
                                     'p@$$word!')
        with self.assertRaises(InvalidPiazzaLogin):
            wrapper.login()

    def test_post_iterator(self):
        mock_piazza = MockPiazzaWrapper()
        it = util.iterate_piazza_posts(mock_piazza, limit=3, backoff_fn=lambda: 0)
        for i in it:
            print(i)

    def test_piazza_time_convert_good(self):
        s = '2017-09-18T14:47:57Z'
        actual = util.date_from_piazza_str(s)
        expected = datetime.datetime(2017, 9, 18, 14, 47, 57)
        self.assertEqual(actual, expected)

    def test_date_is_today(self):
        now = datetime.datetime.today()
        now_piazza = util.date_to_piazza_str(now)
        self.assertTrue(util.date_is_today(now_piazza))

        tomorrow = now + datetime.timedelta(days=1)
        tomorrow_piazza = util.date_to_piazza_str(tomorrow)
        self.assertFalse(util.date_is_today(tomorrow_piazza))

        yesterday = now - datetime.timedelta(days=1)
        yesterday_piazza = util.date_to_piazza_str(yesterday)
        self.assertFalse(util.date_is_today(yesterday_piazza))

    def test_date_get_day_0(self):
        now = datetime.datetime.today()
        start_of_week = now - datetime.timedelta(days=now.weekday())
        self.assertEqual(start_of_week.date(), util.date_get_day_0_of_week().date())

    def test_date_is_this_week(self):
        now = datetime.datetime.today()
        start_of_week = now - datetime.timedelta(days=now.weekday())

        # Previous week
        for i in range(1, 7):
            change = start_of_week - datetime.timedelta(days=i)
            change_str = util.date_to_piazza_str(change)
            self.assertFalse(util.date_is_this_week(change_str))

        # This week
        for i in range(0, 6):
            change = start_of_week + datetime.timedelta(days=i)
            change_str = util.date_to_piazza_str(change)
            self.assertTrue(util.date_is_this_week(change_str))

        # Next week
        for i in range(7, 20):
            change = start_of_week + datetime.timedelta(days=i)
            change_str = util.date_to_piazza_str(change)
            self.assertFalse(util.date_is_this_week(change_str))

    def test_date_is_prev_week(self):
        this_day_last_week = datetime.datetime.today() - datetime.timedelta(days=7)
        start_of_last_week = this_day_last_week - \
                             datetime.timedelta(days=this_day_last_week.weekday())

        # Previous-previous week
        for i in range(1, 7):
            change = start_of_last_week - datetime.timedelta(days=i)
            change_str = util.date_to_piazza_str(change)
            self.assertFalse(util.date_is_prev_week(change_str))

        # This week
        for i in range(0, 6):
            change = start_of_last_week + datetime.timedelta(days=i)
            change_str = util.date_to_piazza_str(change)
            self.assertTrue(util.date_is_prev_week(change_str))

        # Next week
        for i in range(7, 20):
            change = start_of_last_week + datetime.timedelta(days=i)
            change_str = util.date_to_piazza_str(change)
            self.assertFalse(util.date_is_prev_week(change_str))

    def test_get_weekday(self):
        # really silly test because Python is doing all the work
        start_of_week = util.date_get_day_0_of_week()
        self.assertEqual(0, start_of_week.weekday())