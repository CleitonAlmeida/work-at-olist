import unittest

from call_records import create_app, db
from call_records.model.call import Call
from call_records.model.user import User
from tests import set_logger
from flask import json

class TestApi(unittest.TestCase):

    """ Tests for API - Resource Call. """
    #Users for tests (normal 'username' and admin 'username_a')
    username = 'teste'
    password = 'teste123'

    username_a = 'teste_admin'
    password_a = 'teste123a'

    admin_access_token = None
    normal_access_token = None

    admin_refresh_token = None
    normal_refresh_token = None

    def login_request(self, username, password):
        with self.app.app_context():
            return self.client.post('/api/login', data=dict(
                username=username,
                password=password
            ))

    @classmethod
    def setUpClass(cls):
        cls.app = create_app(config_name="testing")
        cls.app.app_context().push()

        #Admin User
        user_a = User()
        user_a.is_admin = True
        user_a.username = cls.username_a
        user_a.gen_hash(password=cls.password_a)
        user_a.save()

        #Normal User
        user = User()
        user.username = cls.username
        user.gen_hash(password=cls.password)
        user.save()

        #Get tokens
        cls.client = cls.app.test_client()
        rv = cls.login_request(cls, cls.username_a, cls.password_a)

        data = json.loads(rv.data)
        cls.admin_access_token = data['access_token']
        cls.admin_refresh_token = data['refresh_token']

        cls.client = cls.app.test_client()
        rv = cls.login_request(cls, cls.username, cls.password)

        data = json.loads(rv.data)
        cls.normal_access_token = data['access_token']
        cls.normal_refresh_token = data['refresh_token']

        cls.call_id = 99999
        call = Call()
        call.call_id = cls.call_id
        call.initial_timestamp = '2016-02-29T12:00:00-03:00'
        call.end_timestamp = '2016-02-29T14:00:00-03:00'
        call.source_number = '55041991024554'
        call.destination_number = '55041997044972'
        call.save()

    @classmethod
    def tearDownClass(cls):
        cls.app.app_context().push()
        call = db.session.query(Call).filter_by(call_id=cls.call_id).first();
        if call:
            call.delete()

        db.session.query(User).filter_by(username=cls.username).first().delete()
        db.session.query(User).filter_by(username=cls.username_a).first().delete()

    def setUp(self):
        self.logger = set_logger(self)

    def test_0_get_list_call(self):
        """ Tests that API route returns 200 and JSON mimetype and minimum one call registred. """
        with self.app.app_context():
            rv = self.client.get('/api/call/', headers={
                "Authorization": "Bearer "+self.admin_access_token
            })
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(rv.mimetype, 'application/json')

            data = json.loads(rv.data)
            count = 0
            for call in data['data']['results']:
                if call.get('call_id') == self.call_id:
                    count+=1
            self.assertEqual(count, 1)
