from call_records import db
from passlib.hash import pbkdf2_sha256
from passlib import pwd

class User(db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(32), index = True, unique=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean(), nullable=False, default=False)
    date_created = db.Column(db.DateTime(timezone=True), default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime(timezone=True), default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())

    def gen_hash(self, password):
        self.password_hash = pbkdf2_sha256.hash(password)

    def verify_password(self, password):
        return pbkdf2_sha256.verify(password, self.password_hash)

    def generate_password(self, length):
        return pwd.genword(length=length)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return "<User: {}>".format(self.username)
