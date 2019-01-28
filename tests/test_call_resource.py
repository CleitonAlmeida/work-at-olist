import unittest

from call_records import create_app, db
from call_records.model.call import Call
from call_records.model.user import User
from call_records import fixed
from tests import set_logger
from flask import json
from datetime import datetime, timedelta
from sqlalchemy.orm import exc as sa_exc
import pytz


class TestApi(unittest.TestCase):

    """ Tests for API - Resource Call. """
    # Users for tests (normal 'username' and admin 'username_a')
    username = 'teste'
    password = 'teste123'

    username_a = 'teste_admin'
    password_a = 'teste123a'

    # For test the call_id`s will start from
    main_call_id = 99999

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

        # Main call
        call = Call()
        call.call_id = cls.main_call_id
        call.initial_timestamp = datetime.strptime(
            '2016-02-29T12:00:00Z', '%Y-%m-%dT%H:%M:%SZ')
        call.end_timestamp = datetime.strptime(
            '2016-02-29T14:00:00Z', '%Y-%m-%dT%H:%M:%SZ')
        call.source_number = '41991024554'
        call.destination_number = '41997044972'
        call.save()

    @classmethod
    def tearDownClass(cls):
        cls.app.app_context().push()
        try:
            call = db.session.query(Call).filter(
                Call.call_id >= cls.main_call_id)
            for c in call.all():
                c.delete()
                # pass
        except sa_exc.NoResultFound as e:
            call = None

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

    def setUp(self):
        self.logger = set_logger(self)

    """def test_create_data_volume(self):
        # Creates data volume for test pagination
        with self.app.app_context():
            dt = datetime.now()

            for i in range(1, 30):
                call = Call()
                call.call_id = self.main_call_id+i
                dt = dt + timedelta(minutes=i)
                dt = dt.replace(tzinfo=None)
                call.initial_timestamp = dt + timedelta(minutes=i)
                dt = call.initial_timestamp + timedelta(minutes=i)
                dt = dt.replace(tzinfo=None)
                print(dt)
                call.end_timestamp = dt
                call.source_number = '55041991024554'
                call.destination_number = '55041997044972'
                call.save()
        self.assertEqual(1, 1)"""

    def test_0_0_post_call_invalid_number(self):
        """Test post a call with a phone number invalid"""
        with self.app.app_context():
            dt = datetime.now()
            dt = dt.replace(tzinfo=None)
            call_id = self.main_call_id+1

            rv = self.client.post('/api/call/', data=dict(
                call_id=call_id,
                type='start',
                source=41999885999887,
                destination=41999886099,
                timestamp=dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            ), headers={
                "Authorization": "Bearer "+self.normal_access_token
            })
            self.assertEqual(rv.status_code, 400)
            self.assertEqual(rv.mimetype, 'application/json')
            data = json.loads(rv.data)
            self.assertEqual(data['errors']['source'],
                             fixed.MSG_INVALID_PHONE_NUMBER)

    def test_0_1_post_call_start_timestamp(self):
        """Test post a call start"""
        with self.app.app_context():
            dt = datetime.now()
            dt = dt.replace(tzinfo=None)
            call_id = self.main_call_id+1

            rv = self.client.post('/api/call/', data=dict(
                call_id=call_id,
                type='start',
                source=41999885999,
                destination=41999886099,
                timestamp=dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            ), headers={
                "Authorization": "Bearer "+self.normal_access_token
            })
            self.assertEqual(rv.status_code, 201)
            self.assertEqual(rv.mimetype, 'application/json')
            data = json.loads(rv.data)
            self.assertEqual(data['status'], 'success')

    def test_0_2_post_start_already_exists(self):
        """Test post a call start that already exists"""
        with self.app.app_context():
            dt = datetime.now()
            dt = dt.replace(tzinfo=None)
            call_id = self.main_call_id+1

            rv = self.client.post('/api/call/', data=dict(
                call_id=call_id,
                type='start',
                source=41999885999,
                destination=41999886099,
                timestamp=dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            ), headers={
                "Authorization": "Bearer "+self.normal_access_token
            })
            self.assertEqual(rv.status_code, 405)
            self.assertEqual(rv.mimetype, 'application/json')
            data = json.loads(rv.data)
            self.assertEqual(data['status'], 'fail')

    def test_0_3_post_call_end_timestamp(self):
        """Test post a call end"""
        with self.app.app_context():
            dt = datetime.now()
            dt = dt + timedelta(minutes=3)
            dt = dt.replace(tzinfo=None)
            call_id = self.main_call_id+1

            rv = self.client.post('/api/call/', data=dict(
                call_id=call_id,
                type='end',
                timestamp=dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            ), headers={
                "Authorization": "Bearer "+self.normal_access_token
            })
            data = json.loads(rv.data)
            self.assertEqual(rv.status_code, 201)
            self.assertEqual(rv.mimetype, 'application/json')
            self.assertEqual(data['status'], 'success')

    def test_0_4_post_end_already_exists(self):
        """Test post a call end that already exists"""
        with self.app.app_context():
            dt = datetime.now()
            dt = dt + timedelta(minutes=3)
            call_id = self.main_call_id+1

            dt = dt.replace(tzinfo=None)
            rv = self.client.post('/api/call/', data=dict(
                call_id=call_id,
                type='end',
                timestamp=dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            ), headers={
                "Authorization": "Bearer "+self.normal_access_token
            })
            self.assertEqual(rv.status_code, 405)
            self.assertEqual(rv.mimetype, 'application/json')
            data = json.loads(rv.data)
            self.assertEqual(data['status'], 'fail')

    def test_0_5_put_start(self):
        """Test put a call start"""
        with self.app.app_context():
            call_id = self.main_call_id+1

            call_test = Call.query.filter(Call.call_id == call_id).one()
            old_start = call_test.initial_timestamp
            old_source = call_test.source_number
            old_destination = call_test.destination_number

            new_source = int(old_source) - 2
            new_destination = int(old_destination) - 2
            new_start = old_start + timedelta(minutes=-3)
            new_start = new_start.replace(tzinfo=None)
            rv = self.client.put('/api/call/'+str(call_id), data=dict(
                type='start',
                source=new_source,
                destination=new_destination,
                timestamp=new_start.strftime("%Y-%m-%dT%H:%M:%SZ")
            ), headers={
                "Authorization": "Bearer "+self.normal_access_token
            })
            data = json.loads(rv.data)
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(rv.mimetype, 'application/json')
            self.assertEqual(data['status'], 'success')

            call_test = Call.query.filter(Call.call_id == call_id).one()
            self.assertNotEqual(old_start, new_start)
            self.assertNotEqual(new_source, old_source)
            self.assertNotEqual(new_destination, old_destination)

    def test_1_0_post_period_invalid(self):
        """Test post a call with invalid period.
        The initial_timestamp is between the connection period of main_call"""
        with self.app.app_context():
            main_call = Call.query.filter(
                Call.call_id == self.main_call_id).one()

            dt = main_call.initial_timestamp
            dt = dt + timedelta(minutes=1)
            rv = self.client.post('/api/call/', data=dict(
                call_id=main_call.call_id+10,
                type='start',
                source=main_call.source_number,
                destination=41999886099,
                timestamp=dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            ), headers={
                "Authorization": "Bearer "+self.normal_access_token
            })
            self.assertEqual(rv.status_code, 409)
            self.assertEqual(rv.mimetype, 'application/json')
            data = json.loads(rv.data)
            self.assertEqual(data['status'], 'fail')

    def test_1_1_post_period_invalid(self):
        """Test post a call with invalid period.
        Test if i can put a call that starts before the main_call,
        BUT ends between the connection period of main_call"""
        with self.app.app_context():
            main_call = Call.query.filter(
                Call.call_id == self.main_call_id).one()
            call_id = main_call.call_id+10
            dt = main_call.initial_timestamp
            dt = dt + timedelta(minutes=-1)
            rv = self.client.post('/api/call/', data=dict(
                call_id=call_id,
                type='start',
                source=main_call.source_number,
                destination=41999886099,
                timestamp=dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            ), headers={
                "Authorization": "Bearer "+self.normal_access_token
            })
            self.assertEqual(rv.status_code, 201)

            dt = dt + timedelta(hours=3)
            rv = self.client.post('/api/call/', data=dict(
                call_id=call_id,
                type='end',
                source=main_call.source_number,
                destination=41999886099,
                timestamp=dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            ), headers={
                "Authorization": "Bearer "+self.normal_access_token
            })
            self.assertEqual(rv.status_code, 409)
            self.assertEqual(rv.mimetype, 'application/json')
            data = json.loads(rv.data)
            self.assertEqual(data['status'], 'fail')

    def test_1_2_post_period_invalid(self):
        """Test post a call with invalid period.
        Test if i can put a call with period between the
        connection period of main_call.
        End timestamp is informed first"""
        with self.app.app_context():
            main_call = Call.query.filter(
                Call.call_id == self.main_call_id).one()
            call_id = main_call.call_id+11
            dt = main_call.initial_timestamp
            dt = dt + timedelta(minutes=1)
            rv = self.client.post('/api/call/', data=dict(
                call_id=call_id,
                type='end',
                source=main_call.source_number,
                destination=41999886099,
                timestamp=dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            ), headers={
                "Authorization": "Bearer "+self.normal_access_token
            })
            self.assertEqual(rv.status_code, 201)

            dt = dt + timedelta(minutes=-3)
            dt = dt.astimezone(pytz.utc)
            rv = self.client.post('/api/call/', data=dict(
                call_id=call_id,
                type='start',
                source=main_call.source_number,
                destination=41999886099,
                timestamp=dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            ), headers={
                "Authorization": "Bearer "+self.normal_access_token
            })
            self.assertEqual(rv.status_code, 409)
            self.assertEqual(rv.mimetype, 'application/json')
            data = json.loads(rv.data)
            self.assertEqual(data['status'], 'fail')

    def test_1_3_post_period_invalid(self):
        """Test post a call with invalid period.
        Test if i can put a call with period between the
        connection period of main_call.
        Start timestamp is informed first"""
        with self.app.app_context():
            call_id = self.main_call_id+12
            dt = datetime.now().replace(tzinfo=None)
            rv = self.client.post('/api/call/', data=dict(
                call_id=call_id,
                type='start',
                source=41999886098,
                destination=41999886019,
                timestamp=dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            ), headers={
                "Authorization": "Bearer "+self.normal_access_token
            })
            self.assertEqual(rv.status_code, 201)

            dt = dt + timedelta(minutes=-3)
            dt = dt.replace(tzinfo=None)
            rv = self.client.post('/api/call/', data=dict(
                call_id=call_id,
                type='end',
                source=41999886098,
                destination=41999886099,
                timestamp=dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            ), headers={
                "Authorization": "Bearer "+self.normal_access_token
            })
            self.assertEqual(rv.status_code, 409)
            self.assertEqual(rv.mimetype, 'application/json')
            data = json.loads(rv.data)
            self.assertEqual(data['status'], 'fail')

    def test_2_0_get_list_call(self):
        """ Tests get calls with pagination. """
        with self.app.app_context():
            count = 0
            page = 1
            next_page = ' '
            while count == 0 and len(next_page) > 0:
                rv = self.client.get('/api/call/?start='+str(page)+'&limit=2', headers={
                    "Authorization": "Bearer "+self.normal_access_token
                })
                self.assertEqual(rv.status_code, 200)
                data = json.loads(rv.data)
                self.assertEqual(rv.mimetype, 'application/json')
                next_page = data['data']['next']
                for call in data['data']['results']:
                    if call.get('call_id') == self.main_call_id:
                        count += 1
                        break
                page += 1

            self.assertEqual(count, 1)

    def test_2_1_get_specific_call(self):
        """ Tests get a specific call. """
        with self.app.app_context():
            main_call = Call.query.\
                filter(Call.call_id == self.main_call_id).one()

            rv = self.client.get('/api/call/'+str(main_call.call_id),
                                 headers={
                "Authorization": "Bearer "+self.normal_access_token
            })

            data = json.loads(rv.data)
            #self.logger.info('data %s', data)
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(rv.mimetype, 'application/json')
            self.assertEqual(data['call_id'], main_call.call_id)
            self.assertEqual(data['source_number'], main_call.source_number)
            self.assertEqual(data['destination_number'],
                             main_call.destination_number)
            self.assertEqual(data['initial_timestamp'],
                             main_call.initial_timestamp.strftime("%Y-%m-%dT%H:%M:%S+00:00"))
            self.assertEqual(data['end_timestamp'],
                             main_call.end_timestamp.strftime("%Y-%m-%dT%H:%M:%S+00:00"))
            self.assertEqual(data['date_created'],
                             main_call.date_created.strftime("%Y-%m-%dT%H:%M:%S.%f-03:00"))
            self.assertEqual(data['date_modified'],
                             main_call.date_modified.strftime("%Y-%m-%dT%H:%M:%S.%f-03:00"))

    def test_2_2_get_nonexistent_call(self):
        """ Tests get a specific call that doesnt exist """
        with self.app.app_context():
            rv = self.client.get('/api/call/23', headers={
                "Authorization": "Bearer "+self.normal_access_token
            })
            data = json.loads(rv.data)
            self.assertEqual(rv.status_code, 404)
            self.assertEqual(rv.mimetype, 'application/json')

    def test_3_0_delete_call(self):
        """ Test delete a call """
        with self.app.app_context():
            rv = self.client.delete('/api/call/'+str(self.main_call_id), headers={
                "Authorization": "Bearer "+self.normal_access_token
            })
            data = json.loads(rv.data)
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(rv.mimetype, 'application/json')

            try:
                call = db.session.query(Call).filter(
                    Call.call_id == self.main_call_id).one()
            except sa_exc.NoResultFound as e:
                call = None

            self.assertEqual(call, None)

    def test_3_1_delete_nonexistent_call(self):
        """ Test delete a nonexistent call """
        with self.app.app_context():
            rv = self.client.delete('/api/call/'+str(self.main_call_id), headers={
                "Authorization": "Bearer "+self.normal_access_token
            })
            data = json.loads(rv.data)
            self.assertEqual(rv.status_code, 404)
            self.assertEqual(rv.mimetype, 'application/json')
            self.assertEqual(data['message'], fixed.MSG_CALL_NOT_FOUND)
