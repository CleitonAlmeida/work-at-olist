import unittest
import os
from tests import set_logger

class TestConfig(unittest.TestCase):

    def setUp(self):
        self.logger = set_logger(self)

    def test_flask_env(self):
        """ Tests FLASK_ENV environ is not set. """
        self.logger.info('FLASK_ENV %s', os.environ.get('FLASK_ENV'))
        self.assertIsNotNone(os.environ.get('FLASK_ENV', None))
        self.assertIn(os.environ.get('FLASK_ENV', None), ['development', 'testing', 'production'])

    def test_db_uri_requirement(self):
        """ Tests SQLALCHEMY_DATABASE_URI environ is not set. """
        # 'sqlite:///:memory:' is the default value that SQLAlchemy set to SQLALCHEMY_DATABASE_URI when is None
        self.assertIsNotNone(os.environ.get('SQLALCHEMY_DATABASE_URI', None))
        self.assertNotEqual(os.environ.get('SQLALCHEMY_DATABASE_URI'), 'sqlite:///:memory:')

    def test_secret_key_requirement(self):
        """ Tests SECRET_KEY environ is not set. """
        self.assertIsNotNone(os.environ.get('SECRET_KEY', None))

    def test_flask_app_requirement(self):
        self.assertIsNotNone(os.environ.get('FLASK_APP', None))


if __name__ == '__main__':
    unittest.main()
