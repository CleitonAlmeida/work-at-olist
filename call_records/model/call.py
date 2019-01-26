from call_records import db
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime
import pytz


class Call(db.Model):

    __tablename__ = 'calls'
    timezone = pytz.UTC

    id = db.Column(db.Integer, primary_key=True)
    _initial_timestamp = db.Column(db.DateTime(timezone=True))
    _end_timestamp = db.Column(db.DateTime(timezone=True))
    call_id = db.Column(db.Integer, unique=True)
    source_number = db.Column(db.String(15))
    destination_number = db.Column(db.String(15))
    date_created = db.Column(
        db.DateTime(timezone=True),
        default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime(timezone=True), default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())

    @hybrid_property
    def initial_timestamp(self):
        if isinstance(self._initial_timestamp, datetime):
            return self._initial_timestamp.astimezone(pytz.utc)
        else:
            return self._initial_timestamp

    @initial_timestamp.setter
    def initial_timestamp(self, timestamp):
        self._initial_timestamp = pytz.utc.localize(timestamp)

    @hybrid_property
    def end_timestamp(self):
        if isinstance(self._end_timestamp, datetime):
            return self._end_timestamp.astimezone(pytz.utc)
        else:
            return self._end_timestamp

    @end_timestamp.setter
    def end_timestamp(self, timestamp):
        self._end_timestamp = pytz.utc.localize(timestamp)

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
