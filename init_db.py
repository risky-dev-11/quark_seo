from app import db
from run import flask_app
from models import User
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(flask_app)

def init_db():
    with flask_app.app_context():
        db.create_all()
        print("Database tables created.")
        
        # Create an example user
        hashed_password = bcrypt.generate_password_hash('Timer640').decode('utf-8')
        example_user = User(email='n11werthmann@gmail.com', password=hashed_password, role='user')
        db.session.add(example_user)
        db.session.commit()
        print("Example user created.")

if __name__ == "__main__":
    init_db()