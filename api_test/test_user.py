import json

from api.common import db
from api.resources import user
import unittest


class TestUser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        db.setup(clean=True)
        # See with a known user
        cls.user = user.User(lts_id='12345', secret='sauce')
        cls.user.save()

    @classmethod
    def tearDownClass(cls):
        db.teardown()
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_non_existing_user(self):
        lts_id = 'terrence'
        new_user = user.create_if_not_exist(lts_id)
        self.assertIsNotNone(new_user)
        self.assertEqual(new_user.lts_id, lts_id)
        should_be_empty_list = json.loads(new_user.courses)
        self.assertTrue(type(should_be_empty_list) is list)
        self.assertTrue(len(should_be_empty_list) == 0)

        # new_user should now pass is_valid_user check
        self.assertTrue(user.is_valid_user(lts_id, new_user.secret))

    def test_create_existing_user(self):
        existing_user = user.create_if_not_exist(self.user.lts_id,
                                                 self.user.secret)
        self.assertIsNotNone(existing_user)
        courses = json.loads(existing_user.courses)
        self.assertTrue(type(courses) is list)

        # new_user should now pass is_valid_user check
        self.assertTrue(user.is_valid_user(self.user.lts_id,
                                           self.user.secret))

    def test_create_user_bad_args(self):
        actual = user.create_if_not_exist(1234, [90, '1234'])
        self.assertIsNone(actual)

    def test_is_valid_user_valid(self):
        self.assertTrue(user.is_valid_user(self.user.lts_id,
                                           self.user.secret))

    def test_is_valid_user_invalid(self):
        self.assertFalse(user.is_valid_user(self.user.lts_id,
                                            "wrong_word"))

    def test_add_course_to_known_user(self):
        self.assertTrue(user.add_course_to_user(self.user.lts_id, '12345'))

    def test_add_course_to_unknown_user(self):
        self.assertFalse(user.add_course_to_user('apple', '12345'))

