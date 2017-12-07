import datetime
import re

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
        self.assertTrue(util.date_is_today(now.timestamp()))

        tomorrow = now + datetime.timedelta(days=1)
        self.assertFalse(util.date_is_today(tomorrow.timestamp()))

        yesterday = now - datetime.timedelta(days=1)
        self.assertFalse(util.date_is_today(yesterday.timestamp()))

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
            self.assertFalse(util.date_is_this_week(change.timestamp()))

        # This week
        for i in range(0, 6):
            change = start_of_week + datetime.timedelta(days=i)
            self.assertTrue(util.date_is_this_week(change.timestamp()))

        # Next week
        for i in range(7, 20):
            change = start_of_week + datetime.timedelta(days=i)
            self.assertFalse(util.date_is_this_week(change.timestamp()))

    def test_date_is_prev_week(self):
        this_day_last_week = datetime.datetime.today() - datetime.timedelta(days=7)
        start_of_last_week = this_day_last_week - \
                             datetime.timedelta(days=this_day_last_week.weekday())

        # Previous-previous week
        for i in range(1, 7):
            change = start_of_last_week - datetime.timedelta(days=i)
            self.assertFalse(util.date_is_prev_week(change.timestamp()))

        # This week
        for i in range(0, 6):
            change = start_of_last_week + datetime.timedelta(days=i)
            self.assertTrue(util.date_is_prev_week(change.timestamp()))

        # Next week
        for i in range(7, 20):
            change = start_of_last_week + datetime.timedelta(days=i)
            self.assertFalse(util.date_is_prev_week(change.timestamp()))

    def test_get_weekday(self):
        # really silly test because Python is doing all the work
        start_of_week = util.date_get_day_0_of_week()
        self.assertEqual(0, start_of_week.weekday())

    def test_make_sentiment_css(self):
        data = {  123: -1.0, 85: -0.5, 213: 0.0, 180: 0.5, 275: 1.0, 179: 0.2 }
        expected = [32,0,76,96,64,128]
        css = util.make_sentiment_css(data)

        # css should be three lines, each with the same color codes just
        # different browser function calls. Split into three lines,
        # do the regex match on each line
        pattern = re.compile("(hsl\(\d{1,3})")
        for line in css.split('\n'):
            matches = re.findall(pattern, line)
            self.assertEqual(len(matches), len(expected))
            for (act, exp) in zip(re.findall(pattern, line), expected):
                num = int(act.split('(')[1])
                self.assertEqual(num, exp)
