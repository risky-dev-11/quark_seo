from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
from urllib.parse import urlparse

app = Flask(__name__)

# import the api & template endpoints
from api import api
from template_routes import template_routes

# add the api & template endpoints to the app
app.register_blueprint(api)
app.register_blueprint(template_routes)

# enable CORS
CORS(app)

if __name__ == "__main__":
    #from waitress import serve
    #serve(app, host="0.0.0.0", port=5000) # for prod
    app.run(debug=True) #for development
   
