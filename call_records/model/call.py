from call_records import db

class Call(db.Model):

    __tablename__ = 'calls'

    id = db.Column(db.Integer, primary_key=True)
    initial_timestamp = db.Column(db.DateTime(timezone=True))
    end_timestamp = db.Column(db.DateTime(timezone=True))
    call_id = db.Column(db.Integer, unique=True)
    source_number = db.Column(db.String(15))
    destination_number = db.Column(db.String(15))
    date_created = db.Column(db.DateTime(timezone=True), default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime(timezone=True), default=db.func.current_timestamp(),
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
