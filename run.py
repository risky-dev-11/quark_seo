from backend.server import create_app

from backend.config.env import FLASK_ENV

flask_app = create_app()

if __name__ == "__main__":

    if FLASK_ENV == "prod":
        raise RuntimeError("This script should not be executed in production. The Flask app is served by Gunicorn via Docker, which imports the flask_app from this file.")
    elif FLASK_ENV == "dev":
        flask_app.run(debug=True)
    else:
        raise ValueError("Invalid FLASK_ENV value. Use 'prod' or 'dev'.")