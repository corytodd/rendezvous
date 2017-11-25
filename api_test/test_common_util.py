import datetime

from api.common import util
import unittest

from api.common.util import InvalidPiazzaLogin, PiazzaWrapper


class MockPiazzaWrapper(PiazzaWrapper):
    def __init__(self):
        super().__init__('', '', '')

    def login(self):
        return

    def get_post_iterator(self, limit=3):
        if not limit:
            limit = 3
        return ['data'] * limit


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
        it = util.iterate_piazza_posts(mock_piazza, limit=3)
        for i in it:
            print(i)

    def test_piazza_time_convert_good(self):
        s = '2017-09-18T14:47:57Z'
        actual = util.piazza_time_to_datetime(s)
        expected = datetime.datetime(2017, 9, 18, 14, 47, 57).timestamp()
        self.assertEqual(actual, expected)
