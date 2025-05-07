from backend.server import create_app
from gevent.pywsgi import WSGIServer

from backend.config.env import FLASK_ENV

if __name__ == "__main__":
    
    flask_app = create_app()

    if FLASK_ENV == "prod":
        http_server = WSGIServer(("0.0.0.0", 5000), flask_app)
        http_server.serve_forever()
    elif FLASK_ENV == "dev":
        flask_app.run(debug=True)
    else:
        raise ValueError("Invalid FLASK_ENV value. Use 'prod' or 'dev'.")