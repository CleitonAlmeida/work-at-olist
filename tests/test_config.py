import unittest
import os
import logging
from call_records.config import app_config

def set_logger(self):
    self.logger = logging.getLogger()
    fh = logging.handlers.RotatingFileHandler('logs/call_records.log', maxBytes=10240, backupCount=5)
    #fh.setLevel(logging.INFO)#no matter what level I set here
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s: %(message)s')
    fh.setFormatter(formatter)
    self.logger.addHandler(fh)
    self.logger.setLevel(logging.INFO)

class TestConfig(unittest.TestCase):

    def setUp(self):
        #app_config[os.environ['APP_SETTINGS']].
        set_logger(self)

    def test_app_settings(self):
        """ Tests APP_SETTINGS environ is not set. """
        self.logger.info('app_settings %s', os.environ.get('APP_SETTINGS'))
        self.assertIsNotNone(os.environ.get('APP_SETTINGS', None))
        self.assertIn(os.environ.get('APP_SETTINGS', None), ['development', 'testing', 'production'])

    def test_db_uri_requirement(self):
        """ Tests SQLALCHEMY_DATABASE_URI environ is not set. """
        # 'sqlite:///:memory:' is the default value that SQLAlchemy set to SQLALCHEMY_DATABASE_URI when is None
        self.assertIsNotNone(os.environ.get('SQLALCHEMY_DATABASE_URI', None))
        self.assertNotEqual(os.environ.get('SQLALCHEMY_DATABASE_URI'), 'sqlite:///:memory:')

    def test_secret_key_requirement(self):
        """ Tests SECRET_KEY environ is not set. """
        self.assertIsNotNone(os.environ.get('SECRET_KEY', None))


if __name__ == '__main__':
    unittest.main()
