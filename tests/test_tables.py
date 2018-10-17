# test_tables.py
import unittest
import os
import json
from app import create_app, db
from app.models import Call, Bill, User

import unittest

class TestCallModel(unittest.TestCase):

    def create_call(self):
        call = Call()
        call.call_id = 1
        call.source_number = '55041991024554'
        call.destination_number = '55041997044972'
        db.session.add(call)
        db.session.commit()

    def setUp(self):
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client

        with self.app.app_context():
            # create all tables
            db.create_all()
            self.create_call()

    def tearDown(self):
        """
        Ensures that the database is emptied for next unit test
        """
        self.app = create_app(config_name="testing")
        with self.app.app_context():
            #db.drop_all()
            db.session.query(Call).delete()
            db.session.commit()
            pass

    def test_call(self):
        pass

if __name__ == '__main__':
    unittest.main()
