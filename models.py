# Classes for the database

import uuid
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
    results = db.Column(db.JSON)
    computation_time = db.Column(db.String)
    time = db.Column(db.DateTime)

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
            achieved_points += card.get('points', 0)
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

class Category:
    def __init__(self, category_name):
        self.category_name = category_name
        self.content = []

    def add_content(self, bool, text):
        self.content.append(Content(bool, text).to_dict())

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

    def add_to_results(self, results):
        self.calculate_points()
        results[self.card_name.lower()] = self.to_dict()
    
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


# Snippet retriever

import json
import os

class TextProvider:
    def __init__(self, file_path):
        """
        Initialize the TextProvider with the path to the JSON file containing the texts.

        :param file_path: Path to the JSON file.
        """
        self.file_path = file_path
        self.texts = {}
        self._load_texts()

    def _load_texts(self):
        """
        Load texts from the JSON file into memory.
        """
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"File not found: {self.file_path}")
        with open(self.file_path, "r", encoding="utf-8") as f:
            self.texts = json.load(f)

    def get_text(self, category, key, **kwargs):
        """
        Retrieve a specific text from the JSON structure.

        :param category: The top-level category in the JSON file.
        :param key: The specific key within the category.
        :param kwargs: Optional placeholders to be replaced in the text.
        :return: The formatted text.
        """
        try:
            text = self.texts[category][key]
            return text.format(**kwargs)
        except KeyError as e:
            raise KeyError(f"Missing key: {e}") from e
        except ValueError as e:
            raise ValueError(f"Formatting error with placeholders: {e}") from e