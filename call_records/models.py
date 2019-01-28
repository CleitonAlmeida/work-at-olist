# app/models.py

from . import db
from passlib.hash import pbkdf2_sha256
from passlib import pwd

class Bill(db.Model):

    __tablename__ = 'bills'

    id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.Integer, unique=True)
    initial_period = db.Column(db.DateTime(timezone=True))
    end_period = db.Column(db.DateTime(timezone=True))
    subscriber_number = db.Column(db.String(15))
    price = db.Column(db.Float())
    date_created = db.Column(db.DateTime(timezone=True), default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime(timezone=True), default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return Bill.query.all()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return "<Bill: {}>".format(self.bill_id)
