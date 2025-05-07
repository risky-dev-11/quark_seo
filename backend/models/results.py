from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSON
import uuid

from . import db        

class AnalyzedWebsite(db.Model):
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
        return self.uuid

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
            'bool': '',  # exclude it from the point calculation
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
