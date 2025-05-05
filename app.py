from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
import os
from gevent.pywsgi import WSGIServer

from models import db, User
from routes import register_routes

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('POSTGRES_DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = os.getenv('FLASK_SECRET_KEY')
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
    
if __name__ == "__main__":
    flask_app = create_app()

    http_server = WSGIServer(("0.0.0.0", 5000), flask_app)
    http_server.serve_forever()
    
    #flask_app.run(debug=True) #for development
