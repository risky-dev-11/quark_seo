from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
import os

db = SQLAlchemy()

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.json.sort_keys = False
    
    app.secret_key  = os.getenv('FLASK_SECRET_KEY')

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)

    from models import User
    @login_manager.user_loader
    def load_user(uuid):
        return User.query.get(uuid)

    bycrypt = Bcrypt(app)

    from routes import register_routes
    register_routes(app, db, bycrypt)

    # enable CORS
    CORS(app)

    return app

   
