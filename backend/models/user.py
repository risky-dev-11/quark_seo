from flask_login import UserMixin

from . import db        

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    uuid = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    role = db.Column(db.String)
    authenticated = db.Column(db.Boolean, default=False)
    analyzed_websites = db.relationship('AnalyzedWebsite', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.email}, Role {self.role}>'
    
    def get_id(self):
        return self.uuid

class UserHierarchy:
    ROLES = {
        'basic': 1,
        'premium': 2,
        'admin': 3
    }

    @staticmethod
    def is_higher_than_basic(user):
        """
        Check if the given user's role is higher than a basic user.
        If the user's role is unknown, assign 'basic'.

        :param user: The user object to check.
        :return: True if the user's role is higher than 'basic', False otherwise.
        """
        role = user.role if user.role in UserHierarchy.ROLES else 'basic'
        return UserHierarchy.ROLES.get(role, 0) > UserHierarchy.ROLES['basic']

