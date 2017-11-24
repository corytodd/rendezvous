import json

from api.app import app
from api.common import db
import unittest


class TestEnroll(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        db.setup(clean=True)
        pass

    @classmethod
    def tearDownClass(cls):
        db.teardown()
        pass

    def setUp(self):
        self.api = app.test_client()
        self.api.testing = True
        self.user = {
            'lts_id': '1234',
            'secret': ''}
        result = self.api.post('/api/v1.0/enroll', query_string=self.user)
        data = json.loads(result.data)
        self.user['secret'] = data['keep_this']

    def tearDown(self):
        pass

    def test_add_course(self):
        # Add a new course
        course = {
            'course_id': '5678',
            'course_name': 'reeto'}
        result = self.api.post('/api/v1.0/addcourse', query_string=course)

        # assert the status code of the response
        self.assertEqual(result.status_code, 200)

        # Make sure we got a secret key response
        data = json.loads(result.data)
        self.assertIsNotNone(data)
        self.assertEqual(data['course_id'], course['course_id'])
        self.assertEqual(data['course_name'], course['course_name'])
