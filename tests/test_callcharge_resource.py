import unittest

from call_records import create_app, db
from call_records.model.callcharge import CallCharge
from call_records.model.user import User
from call_records import fixed
from tests import set_logger
from flask import json
from datetime import datetime
from sqlalchemy.orm import exc as sa_exc


class TestCallCharge(unittest.TestCase):
    """ Tests for API - Resource CallCharge. """
    # Users for tests (normal 'username' and admin 'username_a')
    username = 'teste'
    password = 'teste123'

    username_a = 'teste_admin'
    password_a = 'teste123a'

    # CallCharge Id for tests
    callcharge_id = 9999

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

        # Clean the database
        cls.tearDownClass()

        # Admin User
        user_a = User()
        user_a.is_admin = True
        user_a.username = cls.username_a
        user_a.gen_hash(password=cls.password_a)
        user_a.save()

        # Normal User
        user = User()
        user.username = cls.username
        user.gen_hash(password=cls.password)
        user.save()

        # Get tokens
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

    @classmethod
    def tearDownClass(cls):
        try:
            user = db.session.query(User).filter_by(
                username=cls.username).one().delete()
        except sa_exc.NoResultFound as e:
            pass
        try:
            user = db.session.query(User).filter_by(
                username=cls.username_a).one().delete()
        except sa_exc.NoResultFound as e:
            pass
        try:
            callcharge = db.session.query(CallCharge).filter_by(
                charge_id=cls.callcharge_id).one().delete()
        except sa_exc.NoResultFound as e:
            pass

    def setUp(self):
        self.logger = set_logger(self)

    def test_0_0_post_callcharge_invalid_hour(self):
        """Test post a callcharge with from_time invalid"""
        with self.app.app_context():
            rv = self.client.post('/api/callcharge/', data=dict(
                charge_id=self.callcharge_id,
                from_time='2200',
                to_time='06:00',
                standing_charge=0.36,
                minute_charge=0.00
            ), headers={
                "Authorization": "Bearer "+self.admin_access_token
            })
            data = json.loads(rv.data)
            self.assertEqual(rv.status_code, 400)
            self.assertEqual(rv.mimetype, 'application/json')

    def test_0_1_post_callcharge_normal_user(self):
        """Test post a callcharge by a normal user (not admin)"""
        with self.app.app_context():
            rv = self.client.post('/api/callcharge/', data=dict(
                charge_id=self.callcharge_id,
                from_time='22:00',
                to_time='06:00',
                standing_charge=0.36,
                minute_charge=0.00
            ), headers={
                "Authorization": "Bearer "+self.normal_access_token
            })
            data = json.loads(rv.data)
            self.assertEqual(rv.status_code, 403)
            self.assertEqual(rv.mimetype, 'application/json')
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], fixed.MSG_ONLY_ADMIN)

    def test_0_2_post_callcharge_admin_user(self):
        """Test post a callcharge by an admin user"""
        with self.app.app_context():
            rv = self.client.post('/api/callcharge/', data=dict(
                charge_id=self.callcharge_id,
                from_time='22:00',
                to_time='06:00',
                standing_charge=0.36,
                minute_charge=0.00
            ), headers={
                "Authorization": "Bearer "+self.admin_access_token
            })
            data = json.loads(rv.data)
            self.assertEqual(rv.status_code, 201)
            self.assertEqual(rv.mimetype, 'application/json')
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['message'], fixed.MSG_SUCCESSFULLY_REGISTRED)

    def test_0_3_try_update_via_post(self):
        """Test update a callcharger via post"""
        with self.app.app_context():
            rv = self.client.post('/api/callcharge/', data=dict(
                charge_id=self.callcharge_id,
                from_time='22:00',
                to_time='06:00',
                standing_charge=0.36,
                minute_charge=0.00
            ), headers={
                "Authorization": "Bearer "+self.admin_access_token
            })
            data = json.loads(rv.data)
            self.assertEqual(rv.status_code, 405)
            self.assertEqual(rv.mimetype, 'application/json')
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], fixed.MSG_ACTION_NOT_ALLOWED)

    def test_1_0_get_list_callcharges(self):
        """ Tests get callcharges with pagination. """
        with self.app.app_context():
            count = 0
            page = 1
            next_page = ' '
            while count == 0 and len(next_page) > 0:
                rv = self.client.get('/api/callcharge/?start=' +
                                     str(page)+'&limit=2', headers={
                                         "Authorization": "Bearer " +
                                         self.admin_access_token
                                     })
                self.assertEqual(rv.status_code, 200)
                data = json.loads(rv.data)
                self.assertEqual(rv.mimetype, 'application/json')
                next_page = data['data']['next']
                for callcharge in data['data']['results']:
                    if callcharge.get('charge_id') == self.callcharge_id:
                        count += 1
                        break
                page += 1

            self.assertEqual(count, 1)
