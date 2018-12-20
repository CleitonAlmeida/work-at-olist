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

        cls.client = cls.app.test_client()
        rv = cls.login_request(cls, cls.username, cls.password)

        data = json.loads(rv.data)
        cls.normal_access_token = data['access_token']

    @classmethod
    def tearDownClass(cls):
        cls.app.app_context().push()
        user = db.session.query(User).filter_by(username='test_1').first();
        if user:
            user.delete()
        user = db.session.query(User).filter_by(username='test_2').first();
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
            for user in data['data']['results']:
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
            self.assertEqual(rv.status_code, 403)
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
            self.assertEqual(rv.status_code, 403)
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
            #self.app.logger.info('test_1_post_user_empty_fields %s',rv.data)
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
            #self.app.logger.info('test_1_post_user_already_exists %s',rv.data)
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
            #self.logger.info('data %s', data)
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
            #self.logger.info('data %s', data)
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
            #self.logger.info('data %s', data)
            self.assertEqual(rv.status_code, 403)
            self.assertEqual(rv.mimetype, 'application/json')
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'You must be admin')

    def test_2_get_wrong_user(self):
        with self.app.app_context():
            #self.logger.info('address /api/user/blablabla')
            rv = self.client.get('/api/user/blablabla', headers={
                "Authorization": "Bearer "+self.admin_access_token
            })
            data = json.loads(rv.data)
            #self.logger.info('data %s', data)
            self.assertEqual(rv.status_code, 404)
            self.assertEqual(rv.mimetype, 'application/json')

    def test_3_refresh_token_admin(self):
        """ Tests that API get a refresh token (admin). """
        with self.app.app_context():
            old_token = self.admin_access_token
            rv = self.client.post('/api/refresh', headers={
                "Authorization": "Bearer "+self.admin_access_token
            })
            data = json.loads(rv.data)
            #self.logger.info('data %s', data)
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
            rv = self.client.post('/api/refresh', headers={
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
            rv = self.client.post('/api/refresh', headers={
                "Authorization": "Bearer "+self.normal_access_token
            })
            data = json.loads(rv.data)
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(rv.mimetype, 'application/json')
            self.assertEqual(data['status'], 'success')
            self.assertIsNotNone(data['access_token'])
            self.__class__.normal_access_token = data['access_token']

            #Another request with old token (invalid)
            rv = self.client.post('/api/refresh', headers={
                "Authorization": "Bearer "+old_token
            })
            self.assertEqual(rv.status_code, 401)
            self.assertEqual(rv.mimetype, 'application/json')
            data = json.loads(rv.data)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Token has been revoked')

    def test_4_update_user_admin(self):
        """Tests update password user (admin - sucessfully)"""
        with self.app.app_context():
            user = db.session.query(User).filter_by(username=self.username_a).first()
            new_pass = user.generate_password(length=10)

            rv = self.client.put('/api/user/'+self.username_a, headers={
                "Authorization": "Bearer "+self.admin_access_token
            }, json={
                "password": new_pass
            })
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(rv.mimetype, 'application/json')
            data = json.loads(rv.data)
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['message'], 'Successfully updated')
            user = db.session.query(User).filter_by(username=self.username_a).first()
            result = user.verify_password(password=new_pass)
            print(result)
            self.assertTrue(result)
            self.__class__.password_a = new_pass

            #Another request with the new password
            rv = self.login_request(self.username_a, self.password_a)
            data = json.loads(rv.data)
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(data['status'], 'success')

    def test_4_admin_user_cannot_update_role_admin(self):
        """
        Tests update role (admin or normal user) user
        Admin user can't update your own role (is_admin field)
        """
        with self.app.app_context():
            #New request to update access_token
            rv = self.login_request(self.username_a, self.password_a)
            data = json.loads(rv.data)
            self.__class__.admin_access_token = data['access_token']

            user = db.session.query(User).filter_by(username=self.username_a).first()
            new_pass = user.generate_password(length=10)
            #Request to update your own user
            rv = self.client.put('/api/user/'+self.username_a, headers={
                "Authorization": "Bearer "+self.admin_access_token
            }, json={
                "password": new_pass,
                "is_admin": False
            })
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(rv.mimetype, 'application/json')
            data = json.loads(rv.data)
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['message'], 'Successfully updated')
            user = db.session.query(User).filter_by(username=self.username_a).first()
            result = user.verify_password(password=new_pass)
            self.assertTrue(result)
            self.assertTrue(user.is_admin)
            self.__class__.password_a = new_pass

    def test_4_admin_user_update_other_user(self):
        """Test admin user make updates on normal user registry"""
        with self.app.app_context():
            #New request to update access_token
            rv = self.login_request(self.username_a, self.password_a)
            data = json.loads(rv.data)
            self.__class__.admin_access_token = data['access_token']

            #Normal user
            user = db.session.query(User).filter_by(username=self.username).first()
            self.assertFalse(user.is_admin)
            new_pass = user.generate_password(length=10)
            #Change password and the role
            rv = self.client.put('/api/user/'+self.username, headers={
                "Authorization": "Bearer "+self.admin_access_token
            }, json={
                "password": new_pass,
                "is_admin": True
            })
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(rv.mimetype, 'application/json')
            data = json.loads(rv.data)
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['message'], 'Successfully updated')
            user = db.session.query(User).filter_by(username=self.username).first()
            result = user.verify_password(password=new_pass)
            self.assertTrue(result)
            self.assertTrue(user.is_admin)
            self.__class__.password = new_pass

            #Update normal user, field is_admin to False, to dont mess others test
            user.is_admin = False
            user.save()

    def test_4_update_user_normal(self):
        """Tests update password user (normal - sucessfully)"""
        with self.app.app_context():
            user = db.session.query(User).filter_by(username=self.username).first()
            self.assertFalse(user.is_admin)
            new_pass = user.generate_password(length=10)

            rv = self.client.put('/api/user/'+self.username, headers={
                "Authorization": "Bearer "+self.normal_access_token
            }, json={
                "password": new_pass,
                "is_admin": True
            })
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(rv.mimetype, 'application/json')
            data = json.loads(rv.data)
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['message'], 'Successfully updated')
            user = db.session.query(User).filter_by(username=self.username).first()
            result = user.verify_password(password=new_pass)
            self.assertTrue(result)
            """
            Despite the attempt, normal user can't change their own role
            """
            self.assertFalse(user.is_admin)
            self.__class__.password = new_pass

            #Another request with the new password
            rv = self.login_request(self.username, self.password)
            data = json.loads(rv.data)
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(data['status'], 'success')

    def test_4_normal_user_cannot_update_other_user(self):
        """Test normal user cannot updates others users registry"""
        with self.app.app_context():
            #New request to update access_token admin
            rv = self.login_request(self.username_a, self.password_a)
            data = json.loads(rv.data)
            self.__class__.admin_access_token = data['access_token']

            #Creating another user by admin
            rv = self.client.post('/api/user/', data=dict(
                username='test_2',
                password=self.password
            ), headers={
                "Authorization": "Bearer "+self.admin_access_token
            })
            self.assertEqual(rv.status_code, 201)
            self.assertEqual(rv.mimetype, 'application/json')

            #New request to update access_token
            rv = self.login_request(self.username, self.password)
            data = json.loads(rv.data)
            self.__class__.normal_access_token = data['access_token']

            #Normal user try to change the test_2 (created before)
            user = db.session.query(User).filter_by(username='test_2').first()
            self.assertFalse(user.is_admin)
            new_pass = user.generate_password(length=10)
            rv = self.client.put('/api/user/test_2', headers={
                "Authorization": "Bearer "+self.normal_access_token
            }, json={
                "password": new_pass
            })
            self.assertEqual(rv.status_code, 403)
            self.assertEqual(rv.mimetype, 'application/json')
            data = json.loads(rv.data)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'You must be admin')
            user = db.session.query(User).filter_by(username=self.username).first()
            result = user.verify_password(password=new_pass)
            self.assertFalse(result)
            self.assertFalse(user.is_admin)

    def test_5_logout(self):
        """ Tests logout. """
        with self.app.app_context():
            #New request to update access_token
            rv = self.login_request(self.username, self.password)
            data = json.loads(rv.data)
            self.__class__.normal_access_token = data['access_token']

            #Request to logout
            rv = self.client.post('/api/logout', headers={
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
