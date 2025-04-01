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
    
if __name__ == "__main__":
    flask_app = create_app()

    #from waitress import serve
    #serve(flask_app, host="0.0.0.0", port=5000) # for prod
    flask_app.run(debug=True) #for development

# Next Implementation steps: add screenshot, more and more specific improvement suggestions, wiki and links to it, fix comments & other stuff in html (picture on log in page), server routing with log in and registration system - false password redirect to error site instead of outputting a error, etc.  

# an bewertungsparameter wirtschaftlichkeit - wie kunden gewinnnen, etc. mit einbauen

# wissenschaftliche neutrale ausarbeitung der grundlagen von seo

# wirtschaftliche betrachtung

# wo habe ich fehler gemacvht und wo habe ich draus gelern

   
