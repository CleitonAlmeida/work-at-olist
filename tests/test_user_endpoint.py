import unittest

from call_records import create_app, db
from call_records.model.user import User
from tests import set_logger
from flask import json


class TestApi(unittest.TestCase):

    """ Tests for API. """
    username = 'teste'
    password = 'teste123'

    def setUp(self):
        self.app = create_app(config_name="testing")
        self.logger = set_logger(self)

        with self.app.app_context():
            self.client = self.app.test_client()

    def test_0_index(self):
        """ Tests that API route returns 200 and JSON mimetype. """
        with self.app.app_context():
            rv = self.client.get('/user/')
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(rv.mimetype, 'application/json')

    def test_1_post_user(self):
        with self.app.app_context():
            rv = self.client.post('/user/', data=dict(
                username=self.username,
                password=self.password
            ))
            self.assertEqual(rv.status_code, 201)
            self.assertEqual(rv.mimetype, 'application/json')

            data = json.loads(rv.data)
            self.assertEqual(data['status'], 'success')

    def test_2_get_specific_user(self):
        with self.app.app_context():
            rv = self.client.get('/user/'+self.username)
            self.logger.info('address /user/%s', self.username)

            data = json.loads(rv.data)
            self.logger.info('data %s', data)
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(rv.mimetype, 'application/json')
            self.assertEqual(data['username'], self.username)

            db.session.query(User).filter_by(username=self.username).delete()
            db.session.commit()


if __name__ == '__main__':
    unittest.main()
