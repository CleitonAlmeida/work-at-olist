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
            callcharge = db.session.query(CallCharge).filter(
                CallCharge.charge_id >= cls.callcharge_id)
            for c in callcharge.all():
                c.delete()
                # pass
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
                from_time='06:00',
                to_time='22:00',
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
                from_time='06:00',
                to_time='22:00',
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

    def test_0_3_post_callcharge_invalid_period(self):
        """ Test post a callcharge with invalid period """
        with self.app.app_context():
            new_charge_id = self.callcharge_id+1
            # Try to post callcharge with a different periods
            # all of them invalid
            periods = (
                ('03:00', '03:00'),
                ('03:00', '06:00'),
                ('03:00', '06:05'),
                ('06:00', '22:00'),
                ('06:30', '21:30'),
                ('22:00', '23:59'),
                ('20:00', '23:59'),
            )
            for period in periods:
                rv = self.client.post('/api/callcharge/', data=dict(
                    charge_id=new_charge_id,
                    from_time=period[0],
                    to_time=period[1],
                    standing_charge=0,
                    minute_charge=0
                ), headers={
                    "Authorization": "Bearer "+self.admin_access_token
                })
                data = json.loads(rv.data)
                self.assertEqual(rv.status_code, 409)
                self.assertEqual(data['status'], 'fail')
                self.assertEqual(
                    data['message'], fixed.MSG_CONFLICT_CALL_CHARGER)

    def test_0_4_try_update_via_post(self):
        """Test update a callcharger via post"""
        with self.app.app_context():
            rv = self.client.post('/api/callcharge/', data=dict(
                charge_id=self.callcharge_id,
                from_time='06:00',
                to_time='22:00',
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

    def test_1_1_get_specific_callcharges(self):
        """ Tests get a specific callcharge """
        with self.app.app_context():
            callcharge = CallCharge.query.filter(
                CallCharge.charge_id == self.callcharge_id).one()
            rv = self.client.get('/api/callcharge/'+str(self.callcharge_id),
                                 headers={
                "Authorization": "Bearer "+self.admin_access_token
            })

            data = json.loads(rv.data)
            #self.logger.info('data %s', data)
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(rv.mimetype, 'application/json')
            self.assertEqual(data['charge_id'], self.callcharge_id)
            self.assertEqual(data['from_time'],
                             callcharge.from_time.strftime('%H:%M'))
            self.assertEqual(
                data['to_time'], callcharge.to_time.strftime('%H:%M'))
            self.assertEqual(data['standing_charge'],
                             float(callcharge.standing_charge))
            self.assertEqual(data['minute_charge'],
                             float(callcharge.minute_charge))

    def test_1_2_get_specific_callcharges_nonexistent(self):
        """ Tests get a specific callcharge nonexistent"""
        with self.app.app_context():

            rv = self.client.get('/api/callcharge/7777',
                                 headers={
                                     "Authorization": "Bearer " +
                                     self.admin_access_token
                                 })

            data = json.loads(rv.data)
            #self.logger.info('data %s', data)
            self.assertEqual(rv.status_code, 404)

    def test_2_0_put_callcharge(self):
        """ Tests put a callcharge """
        with self.app.app_context():
            # Create another one
            new_charge_id = self.callcharge_id+1

            rv = self.client.post('/api/callcharge/', data=dict(
                charge_id=new_charge_id,
                from_time='22:01',
                to_time='23:59',
                standing_charge=0.36,
                minute_charge=0.10
            ), headers={
                "Authorization": "Bearer "+self.admin_access_token
            })
            data = json.loads(rv.data)
            self.assertEqual(rv.status_code, 201)

            # Try to update
            rv = self.client.put('/api/callcharge/'+str(new_charge_id),
                                 data=dict(
                from_time='22:30',
                to_time='23:00',
                standing_charge=0.38,
                minute_charge=0.11
            ), headers={
                "Authorization": "Bearer "+self.admin_access_token
            })
            data = json.loads(rv.data)
            self.assertEqual(rv.status_code, 200)

            callcharge = CallCharge.query.filter(
                CallCharge.charge_id == new_charge_id).one()
            self.assertEqual(callcharge.from_time.strftime('%H:%M'), '22:30')
            self.assertEqual(callcharge.to_time.strftime('%H:%M'), '23:00')
            self.assertEqual(float(callcharge.standing_charge), 0.38)
            self.assertEqual(float(callcharge.minute_charge), 0.11)

    def test_2_1_put_callcharge_invalid_period(self):
        """ Test put a callcharge with invalid period """
        with self.app.app_context():
            # Create another one
            new_charge_id = self.callcharge_id+2

            rv = self.client.post('/api/callcharge/', data=dict(
                charge_id=new_charge_id,
                from_time='23:30',
                to_time='23:59',
                standing_charge=0.36,
                minute_charge=0.10
            ), headers={
                "Authorization": "Bearer "+self.admin_access_token
            })
            data = json.loads(rv.data)
            self.assertEqual(rv.status_code, 201)
            # Try to update callcharge with a different periods
            # all of them invalid
            periods = (
                ('03:00', '03:00'),
                ('03:00', '06:00'),
                ('03:00', '06:05'),
                ('06:00', '22:00'),
                ('06:30', '21:30'),
                ('22:00', '23:59'),
                ('20:00', '23:59'),
            )
            for period in periods:
                rv = self.client.put('/api/callcharge/'+str(new_charge_id),
                                     data=dict(
                    from_time=period[0],
                    to_time=period[1],
                    standing_charge=0,
                    minute_charge=0
                ), headers={
                    "Authorization": "Bearer "+self.admin_access_token
                })
                data = json.loads(rv.data)
                self.assertEqual(rv.status_code, 409)
                self.assertEqual(data['status'], 'fail')
                self.assertEqual(
                    data['message'], fixed.MSG_CONFLICT_CALL_CHARGER)

    def test_3_0_delete_callcharge(self):
        """ Test delete a call """
        with self.app.app_context():
            rv = self.client.delete('/api/callcharge/'+str(self.callcharge_id),
                                    headers={
                "Authorization": "Bearer "+self.admin_access_token
            })
            data = json.loads(rv.data)
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(rv.mimetype, 'application/json')
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['message'], fixed.MSG_SUCCESSFULLY_DELETED)

            try:
                callcharge = db.session.query(CallCharge).filter(
                    CallCharge.charge_id == self.callcharge_id).one()
            except sa_exc.NoResultFound as e:
                callcharge = None
            self.assertEqual(callcharge, None)

    def test_3_1_delete_nonexistent_call(self):
        """ Test delete a nonexistent call """
        with self.app.app_context():
            rv = self.client.delete('/api/callcharge/'+str(self.callcharge_id),
                                    headers={
                "Authorization": "Bearer "+self.admin_access_token
            })
            data = json.loads(rv.data)
            self.assertEqual(rv.status_code, 404)
            self.assertEqual(rv.mimetype, 'application/json')
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], fixed.MSG_CALL_CHARGER_NOT_FOUND)
