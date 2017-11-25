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

    def tearDown(self):
        pass

    def test_enroll_new_user(self):
        user = {
            'lts_id': '1234',
            'secret': ''}
        result = self.api.post('/api/v1.0/enroll', query_string=user)

        # assert the status code of the response
        self.assertEqual(result.status_code, 200)

        # Make sure we got a secret key response
        data = json.loads(result.data)
        self.assertIsNotNone(data)

        # Make sure we can use the code we just received
        user['secret'] = data['keep_this']
        result = self.api.post('/api/v1.0/enroll', query_string=user)
        self.assertEqual(result.status_code, 200)
