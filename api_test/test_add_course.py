import json

from api.app import app
from api.common import db
import unittest


class TestAddCourse(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        db.setup(clean=True)
        cls.api = app.test_client()
        cls.api.testing = True
        cls.user = {
            'lts_id': '1234',
            'secret': ''}
        result = cls.api.post('/api/v1.0/enroll', query_string=cls.user)
        data = json.loads(result.data)
        cls.user['secret'] = data['keep_this']

    @classmethod
    def tearDownClass(cls):
        db.teardown()
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_add_course_with_auth(self):
        query = {
            'lts_id': self.user['lts_id'],
            'secret': self.user['secret'],
            'course_id': '5678',
            'course_name': 'reeto'}
        result = self.api.post('/api/v1.0/addcourse', query_string=query)

        self.assertEqual(result.status_code, 200)

        # Make sure we got a secret key response
        data = json.loads(result.data)
        self.assertIsNotNone(data)
        self.assertEqual(data['course_id'], query['course_id'])
        self.assertEqual(data['course_name'], query['course_name'])

    def test_add_course_without_auth(self):
        course = {
            'course_id': '091234',
            'course_name': 'this_should_not_work'}
        result = self.api.post('/api/v1.0/addcourse', query_string=course)

        self.assertEqual(result.status_code, 401)
