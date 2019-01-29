from call_records import db


class CallCharge(db.Model):

    __tablename__ = 'call_charge'

    id = db.Column(db.Integer, primary_key=True)
    from_time = db.Column(db.Time(timezone=False))
    to_time = db.Column(db.Time(timezone=False))
    standing_charge = db.Column(db.Float(precision=6,
                                        decimal_return_scale=2,
                                        asdecimal=True))
    minute_charge = db.Column(db.Float(precision=6,
                                      decimal_return_scale=2,
                                      asdecimal=True))
    date_created = db.Column(
        db.DateTime(timezone=True),
        default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime(timezone=True), default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return CallCharge.query.all()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return "<CallCharge: {}>".format(self.id)
