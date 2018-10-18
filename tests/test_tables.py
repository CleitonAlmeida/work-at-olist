# test_tables.py
import unittest
import os
import json
from call_records import create_app, db
from call_records.models import Call, Bill, User

import unittest

class TestCallModel(unittest.TestCase):

    def create_call(self):
        call = Call()
        call.call_id = 4
        call.initial_timestamp = '2016-02-29T12:00:00-03:00'
        call.end_timestamp = '2016-02-29T14:00:00-03:00'
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

    def test_populate_db(self):
        with self.app.app_context():
            self.assertEqual(db.session.query(Call).filter_by(call_id=4).first().destination_number, '55041997044972')

class TestBillModel(unittest.TestCase):

    def create_bill(self):
        bill = Bill()
        bill.bill_id = 2
        bill.initial_period = '2018-10-01T00:00:00-03:00'
        bill.end_period = '2018-10-31T23:59:59-03:00'
        bill.subscriber_number = '55041991024554'
        bill.price = 117.68
        db.session.add(bill)
        db.session.commit()

    def setUp(self):
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client

        with self.app.app_context():
            # create all tables
            db.create_all()
            self.create_bill()

    def tearDown(self):
        """
        Ensures that the database is emptied for next unit test
        """
        self.app = create_app(config_name="testing")
        with self.app.app_context():
            #db.drop_all()
            db.session.query(Bill).delete()
            db.session.commit()

    def test_populate_db(self):
        with self.app.app_context():
            self.assertEqual(db.session.query(Bill).filter_by(price=117.68).first().subscriber_number, '55041991024554')

class TestUserModel(unittest.TestCase):

    def create_user(self):
        user = User()
        user.username = 'cleitonalmeida'
        user.hash_password = user.hash_password(user.generate_password(10))
        print(user.hash_password)
        user.save()

    def setUp(self):
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client

        with self.app.app_context():
            # create all tables
            db.create_all()
            self.create_user()

    def tearDown(self):
        """
        Ensures that the database is emptied for next unit test
        """
        self.app = create_app(config_name="testing")
        with self.app.app_context():
            #db.drop_all()
            db.session.query(User).delete()
            db.session.commit()

    def test_populate_db(self):
        with self.app.app_context():
            self.assertEqual(db.session.query(User).filter_by(username='cleitonalmeida').first().username, 'cleitonalmeida')

if __name__ == '__main__':
    unittest.main()
