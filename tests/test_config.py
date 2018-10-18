import unittest
import os
import logging
from call_records import create_app

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
        """ Stores environment variables, which will be removed by tests and restored in tearDown. """
        self.environs = {
            'SQLALCHEMY_DATABASE_URI': os.environ['SQLALCHEMY_DATABASE_URI'],
            'SECRET_KEY': os.environ['SECRET_KEY'],
        }
        set_logger(self)

    def tearDown(self):
        """ Restores environment variables removed by tests. """
        os.environ['SQLALCHEMY_DATABASE_URI'] = self.environs['SQLALCHEMY_DATABASE_URI']
        os.environ['SECRET_KEY'] = self.environs['SECRET_KEY']
        #logging.warning('SQLALCHEMY_DATABASE_URI variable %s', os.environ.get('SQLALCHEMY_DATABASE_URI'))

    def test_db_uri_requirement(self):
        """ Tests SQLALCHEMY_DATABASE_URI environ is not set. """
        self.logger.info('SQLALCHEMY_DATABASE_URI %s', os.environ['SQLALCHEMY_DATABASE_URI'])
        del os.environ['SQLALCHEMY_DATABASE_URI']
        self.logger.info('SQLALCHEMY_DATABASE_URI %s', os.environ.get('SQLALCHEMY_DATABASE_URI'))
        # 'sqlite:///:memory:' is the default value that SQLAlchemy set to SQLALCHEMY_DATABASE_URI when is None
        self.assertNotEqual(os.environ.get('SQLALCHEMY_DATABASE_URI'), 'sqlite:///:memory:')

    def test_secret_key_requirement(self):
        """ Tests SECRET_KEY environ is not set. """
        del os.environ['SECRET_KEY']
        self.assertIsNone(os.environ.get('SECRET_KEY', None))


if __name__ == '__main__':
    unittest.main()
