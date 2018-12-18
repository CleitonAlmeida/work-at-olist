import unittest

from call_records import create_app, db
from call_records.model.user import User
from tests import set_logger
from flask import json


class TestApi(unittest.TestCase):

    """ Tests for API. """
    #Users for tests (normal and admin)
    username = 'teste'
    password = 'teste123'

    username_a = 'teste_admin'
    password_a = 'teste123a'

    admin_access_token = None
    normal_access_token = None

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
        rv = cls.client.post('/api/user/login', data=dict(
            username=cls.username_a,
            password=cls.password_a
        ))
        data = json.loads(rv.data)
        cls.admin_access_token = data['access_token']

        cls.client = cls.app.test_client()
        rv = cls.client.post('/api/user/login', data=dict(
            username=cls.username,
            password=cls.password
        ))
        data = json.loads(rv.data)
        cls.normal_access_token = data['access_token']

    @classmethod
    def tearDownClass(cls):
        cls.app.app_context().push()
        user = db.session.query(User).filter_by(username='test_1').first();
        if user:
            user.delete()
        db.session.query(User).filter_by(username=cls.username).first().delete()
        db.session.query(User).filter_by(username=cls.username_a).first().delete()

    def setUp(self):
        self.logger = set_logger(self)

    def test_0_get_list_user(self):
        """ Tests that API route returns 200 and JSON mimetype and minimum two users registred. """
        with self.app.app_context():
            #self.app.logger.info('test_0 token %s', self.access_token)
            rv = self.client.get('/api/user/', headers={
                "Authorization": "Bearer "+self.admin_access_token
            })
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(rv.mimetype, 'application/json')

            data = json.loads(rv.data)
            count = 0
            for user in data['data']:
                #self.app.logger.info('FOR test_0_get_list_user %s', user.get('username'))
                if user.get('username') == 'teste' or user.get('username') == 'teste_admin':
                    count+=1
            self.assertEqual(count, 2)
            #self.app.logger.info('test_0_get_list_user %s', data['data'][0])

    def test_0_get_list_user_unauthorized(self):
        """ Tests if the endpoint is protected by non-admin user access """
        with self.app.app_context():
            #self.app.logger.info('test_0 token %s', self.access_token)
            rv = self.client.get('/api/user/', headers={
                "Authorization": "Bearer "+self.normal_access_token
            })
            self.assertEqual(rv.status_code, 401)
            self.assertEqual(rv.mimetype, 'application/json')
            data = json.loads(rv.data)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'You must be admin')

    def test_1_post_user(self):
        """ Tests that API route post an user. """
        with self.app.app_context():
            #db.session.query(User).filter_by(username='test_1').first().delete()
            rv = self.client.post('/api/user/', data=dict(
                username='test_1',
                password=self.password
            ), headers={
                "Authorization": "Bearer "+self.admin_access_token
            })
            #self.app.logger.info('test_1_post_user %s',rv.data)
            self.assertEqual(rv.status_code, 201)
            self.assertEqual(rv.mimetype, 'application/json')

            data = json.loads(rv.data)
            self.assertEqual(data['status'], 'success')

    def test_1_post_user_unauthorized(self):
        """ Tests that API route post an user with an non-admin user. """
        with self.app.app_context():
            #db.session.query(User).filter_by(username='test_1').first().delete()
            rv = self.client.post('/api/user/', data=dict(
                username='test_1',
                password=self.password
            ), headers={
                "Authorization": "Bearer "+self.normal_access_token
            })
            #self.app.logger.info('test_1_post_user %s',rv.data)
            self.assertEqual(rv.status_code, 401)
            self.assertEqual(rv.mimetype, 'application/json')

            data = json.loads(rv.data)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'You must be admin')

    def test_1_post_user_empty_fields(self):
        """ Tests that API inform empty fields. """
        with self.app.app_context():
            rv = self.client.post('/api/user/', data=dict(
                username=self.username
            ), headers={
                "Authorization": "Bearer "+self.admin_access_token
            })
            self.app.logger.info('test_1_post_user_empty_fields %s',rv.data)
            self.assertEqual(rv.status_code, 400)
            self.assertEqual(rv.mimetype, 'application/json')

            data = json.loads(rv.data)
            self.assertEqual(data['errors'].get('password'), 'Missing required parameter in the JSON body or the post body or the query string')

    def test_1_post_user_already_exists(self):
        """ Tests that API route post an user already exists. """
        with self.app.app_context():
            rv = self.client.post('/api/user/', data=dict(
                username=self.username,
                password=self.password
            ), headers={
                "Authorization": "Bearer "+self.admin_access_token
            })
            self.app.logger.info('test_1_post_user_already_exists %s',rv.data)
            self.assertEqual(rv.status_code, 409)
            self.assertEqual(rv.mimetype, 'application/json')

            data = json.loads(rv.data)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'User already exists. Please Log in')

    def test_2_get_specific_user_admin(self):
        """ Tests that API get a specific user (admin). """
        with self.app.app_context():
            rv = self.client.get('/api/user/'+self.username_a, headers={
                "Authorization": "Bearer "+self.admin_access_token
            })

            data = json.loads(rv.data)
            self.logger.info('data %s', data)
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(rv.mimetype, 'application/json')
            self.assertEqual(data['username'], self.username_a)

    def test_2_get_specific_user(self):
        """ Tests that API get a specific user. """
        with self.app.app_context():
            rv = self.client.get('/api/user/'+self.username, headers={
                "Authorization": "Bearer "+self.admin_access_token
            })

            data = json.loads(rv.data)
            self.logger.info('data %s', data)
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(rv.mimetype, 'application/json')
            self.assertEqual(data['username'], self.username)

    def test_2_get_specific_user_unauthorized(self):
        """ Tests that API get a specific user with an non-admin user. """
        with self.app.app_context():
            rv = self.client.get('/api/user/'+self.username, headers={
                "Authorization": "Bearer "+self.normal_access_token
            })

            data = json.loads(rv.data)
            self.logger.info('data %s', data)
            self.assertEqual(rv.status_code, 401)
            self.assertEqual(rv.mimetype, 'application/json')
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'You must be admin')

    def test_2_get_wrong_user(self):
        with self.app.app_context():
            self.logger.info('address /api/user/blablabla')
            rv = self.client.get('/api/user/blablabla', headers={
                "Authorization": "Bearer "+self.admin_access_token
            })
            data = json.loads(rv.data)
            self.logger.info('data %s', data)
            self.assertEqual(rv.status_code, 404)
            self.assertEqual(rv.mimetype, 'application/json')

    def test_3_refresh_token_admin(self):
        """ Tests that API get a refresh token (admin). """
        with self.app.app_context():
            old_token = self.admin_access_token
            rv = self.client.post('/api/user/refresh', headers={
                "Authorization": "Bearer "+self.admin_access_token
            })
            data = json.loads(rv.data)
            self.logger.info('data %s', data)
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(rv.mimetype, 'application/json')

            self.assertEqual(data['status'], 'success')
            self.assertIsNotNone(data['access_token'])
            self.admin_access_token = data['access_token']

            #Another request with the new token
            rv = self.client.get('/api/user/', headers={
                "Authorization": "Bearer "+self.admin_access_token
            })
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(rv.mimetype, 'application/json')

            #Another request with old token (invalid)
            rv = self.client.get('/api/user/', headers={
                "Authorization": "Bearer "+old_token
            })
            self.assertEqual(rv.status_code, 401)
            self.assertEqual(rv.mimetype, 'application/json')
            data = json.loads(rv.data)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Token has been revoked')

    def test_3_1_refresh_token(self):
        """ Tests that API get a refresh token. """
        with self.app.app_context():
            old_token = self.normal_access_token
            rv = self.client.post('/api/user/refresh', headers={
                "Authorization": "Bearer "+self.normal_access_token
            })
            data = json.loads(rv.data)
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(rv.mimetype, 'application/json')

            self.assertEqual(data['status'], 'success')
            self.assertIsNotNone(data['access_token'])
            """self.normal_access_token = data['access_token']
            I dont update normal_access_token var (lookup)
            because of this problem
            https://stackoverflow.com/questions/21447740/persist-variable-changes-between-tests-in-unittest
            So I did by this way
            """
            self.__class__.normal_access_token = data['access_token']

            #Another request with the new token
            rv = self.client.post('/api/user/refresh', headers={
                "Authorization": "Bearer "+self.normal_access_token
            })
            data = json.loads(rv.data)
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(rv.mimetype, 'application/json')
            self.assertEqual(data['status'], 'success')
            self.assertIsNotNone(data['access_token'])
            self.__class__.normal_access_token = data['access_token']

            #Another request with old token (invalid)
            rv = self.client.post('/api/user/refresh', headers={
                "Authorization": "Bearer "+old_token
            })
            self.assertEqual(rv.status_code, 401)
            self.assertEqual(rv.mimetype, 'application/json')
            data = json.loads(rv.data)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Token has been revoked')

    def test_4_logout(self):
        """ Tests logout. """
        with self.app.app_context():
            #old_token = self.normal_access_token
            rv = self.client.post('/api/user/logout', headers={
                "Authorization": "Bearer "+self.normal_access_token
            })
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(rv.mimetype, 'application/json')
            data = json.loads(rv.data)
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['message'], 'Logout Successfully')

            #Another request with the token revoked
            rv = self.client.get('/api/user/', headers={
                "Authorization": "Bearer "+self.normal_access_token
            })
            self.assertEqual(rv.status_code, 401)
            self.assertEqual(rv.mimetype, 'application/json')
            data = json.loads(rv.data)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Token has been revoked')

if __name__ == '__main__':
    unittest.main()
