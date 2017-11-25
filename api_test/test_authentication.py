import json

from api.app import app
from api.common import db
import unittest


class TestAuth(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        db.setup(clean=True)
        # Create a known initial user and capture the secret
        cls.api = app.test_client()
        cls.api.testing = True
        cls.user = {
            'lts_id': '1234',
            'secret': ''}
        result = cls.api.post('/api/v1.0/enroll', query_string=cls.user)
        data = json.loads(result.data)
        cls.user['secret'] = data['keep_this']
        pass

    @classmethod
    def tearDownClass(cls):
        db.teardown()
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_auth_missing_secret(self):
        # Try to login as user that exists, empty secret
        query = {
            'lts_id': '1234',
            'secret': ''}
        result = self.api.post('/api/v1.0/enroll', query_string=query)
        self.assertEqual(result.status_code, 401)

    def test_auth_incorrect_secret(self):
        # Try to login as user that exists but incorrect secret
        query = {
            'lts_id': '1234',
            'secret': '999999123'}
        result = self.api.post('/api/v1.0/enroll', query_string=query)
        self.assertEqual(result.status_code, 401)
