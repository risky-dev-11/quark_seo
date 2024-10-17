from flask_login import UserMixin
from app import db

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    uuid = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    role = db.Column(db.String)

    def __repr__(self):
        return f'<User {self.email}, Role {self.role}>'
    
    def get_id(self):
        return (self.uuid)

class AnalyzedWebsite(db.Model, UserMixin):
    __tablename__ = 'analyzed_websites'
    uuid = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String)
    results = db.Column(db.JSON)

    def __repr__(self):
        return f'<AnalyzedWebsite {self.website}>'

    def get_id(self):
        return (self.uuid)