from .. import db
from . import bcrypt

class User(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(255), nullable=False, index=True, unique=True)
    password = db.Column(db.String(255), nullable=False)

    @property
    def password(self):
        raise AttributeError('password is not a readble attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password)
    
    def verify_password(self, password):
        return bcrypt.check_password_hash(self.password, password)