from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

    app.secret_key  = 'super secret key'

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    migrate = Migrate(app, db)

    from models import User
    @login_manager.user_loader
    def load_user(uuid):
        return User.query.get(uuid)

    bycrypt = Bcrypt(app)

    from routes import register_routes
    register_routes(app, db, bycrypt)

    # import the api & template endpoints
    from api import api
    from template_routes import template_routes

    # add the api & template endpoints to the app
    app.register_blueprint(api)
    app.register_blueprint(template_routes)

    # enable CORS
    #CORS(app)

    return app

   
