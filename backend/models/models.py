# Classes for the database
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import uuid
from sqlalchemy.dialects.postgresql import JSON

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    uuid = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    role = db.Column(db.String)
    authenticated = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<User {self.email}, Role {self.role}>'
    
    def get_id(self):
        return (self.uuid)

class AnalyzedWebsite(db.Model, UserMixin):
    __tablename__ = 'analyzed_websites'
    user_uuid = db.Column(db.Integer, db.ForeignKey('users.uuid'))
    uuid = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    url = db.Column(db.String)
    results = db.Column(JSON)  # <-- Wichtig: Nicht db.JSON!
    computation_time = db.Column(db.String)
    time = db.Column(db.DateTime)
    screenshot = db.Column(db.BLOB)

    def __repr__(self):
        return f'<AnalyzedWebsite {self.website}>'

    def get_id(self):
        return (self.uuid)
    
###########################################################

# Classes for the analyzer

def calculate_overall_points(results):
    overall_points = 0
    achieved_points = 0
    for card in results.values():
        if 'points' in card:
            overall_points += 100
            achieved_points += int(card.get('points', 0) or 0)
    return round((achieved_points / overall_points) * 100) if overall_points != 0 else 0

def calculate_improvement_count(results):
    false_count = 0
    for _, card in results.items():
        if card.get('isCard', False):
            false_count += count_false_in_card(card)
    return false_count

def count_false_in_card(card):
    false_count = 0
    for category in card.values():
        if isinstance(category, dict) and 'content' in category: 
            false_count += count_false_in_category(category)
    return false_count

def count_false_in_category(category):
    return sum(1 for content in category['content'] if content['bool'] is False)

class Content:
    def __init__(self, bool, text):
        self.bool = bool
        self.text = text

    def to_dict(self):
        return {
            'bool': self.bool,
            'text': self.text
        }
    
class ChartContent:
    def __init__(self, chart_type, threshold1, threshold2, threshold_unit, value):
        self.is_chart = True
        self.chart_type = chart_type
        self.threshold1 = threshold1
        self.threshold2 = threshold2
        self.threshold_unit = threshold_unit
        self.value = value

    def to_dict(self):
        return {
            'bool': '', # exclude it from the the point calculation
            'isChart': self.is_chart,
            'chartType': self.chart_type,
            'threshold1': self.threshold1,
            'threshold2': self.threshold2,
            'thresholdUnit': self.threshold_unit,
            'value': self.value
        }

class Category:
    def __init__(self, category_name):
        self.category_name = category_name
        self.content = []

    def add_content(self, bool, text):
        self.content.append(Content(bool, text).to_dict())

    def add_chart_content(self, chart_type, threshold1, threshold2, threshold_unit, value):
        self.content.append(ChartContent(chart_type, threshold1, threshold2, threshold_unit, value).to_dict())

    def to_dict(self):
        return {
            'category_name': self.category_name,
            'content': self.content
        }

class Card:
    def __init__(self, card_name):
        self.card_name = card_name
        self.points = 0
        self.is_card = True
        self.categories = {}

    def add_category(self, category):
        self.categories[category.category_name.lower()] = category.to_dict()

    def to_dict(self):
        return {
            'isCard': self.is_card,
            'card_name': self.card_name,
            'points': self.points,
            **self.categories
        }

    def add_to_results(self, results, index, manual_points=None):
        if manual_points is not None:
            self.update_points(manual_points)
        else:
            self.calculate_points()
        results[index] = self.to_dict()
    
    def update_points(self, points):
        self.points = points
        
    def calculate_points(self):
        true_count = 0
        false_count = 0
        for category in self.categories.values():
            for content in category['content']:
                if content['bool'] is True:
                    true_count += 1
                elif content['bool'] is False:
                    false_count += 1
        total_points = true_count + false_count

        points_percentage = (true_count / total_points) * 100 if total_points != 0 else 0
        self.update_points(points_percentage)

# User hierarchy

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