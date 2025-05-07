from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

from backend.models.user import db, User
from backend.routes import register_routes

from backend.config.env import POSTGRES_DATABASE_URL, FLASK_SECRET_KEY

def create_app():
    app = Flask(__name__, 
            static_folder="../frontend/static",
            template_folder="../frontend/templates")

    app.config['SQLALCHEMY_DATABASE_URI'] = POSTGRES_DATABASE_URL
    app.secret_key = FLASK_SECRET_KEY

    app.json.sort_keys = False

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, user_id)

    bcrypt = Bcrypt(app)

    register_routes(app, db, bcrypt)

    CORS(app)

    return app