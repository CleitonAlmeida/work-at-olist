# app/models.py

from app import db

class Call(db.Model):

    __tablename__ = 'calls'

    id = db.Column(db.Integer, primary_key=True)
    initial_timestamp = db.Column(db.DateTime(timezone=True))
    end_timestamp = db.Column(db.DateTime(timezone=True))
    call_id = db.Column(db.Integer, unique=True)
    source_number = db.Column(db.String(15))
    destination_number = db.Column(db.String(15))
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime, default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return Call.query.all()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return "<Call: {}>".format(self.call_id)

class Bill(db.Model):

    __tablename__ = 'bills'

    id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.Integer, unique=True)
    initial_period = db.Column(db.DateTime(timezone=True))
    end_period = db.Column(db.DateTime(timezone=True))
    subscriber_number = db.Column(db.String(15))
    price = db.Column(db.Float())

    def __init__(self, call_id):
        self.bill_id = bill_id

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

class User(db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(32), index = True)
    password_hash = db.Column(db.String(128))
