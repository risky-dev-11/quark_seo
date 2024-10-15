from flask import Blueprint, render_template

template_routes = Blueprint('template_routes_blueprint', __name__)

@template_routes.route('/results/<path:url>', methods=['GET'])
def show_results(url):
    return render_template("seo-analytics-page.html")
@template_routes.route('/seo/analyze/<path:url>', methods=['GET'])
def show_loading_page(url):
    return render_template("seo-analytics-loading-page.html")
@template_routes.route('/about')
def about():
    return render_template('about.html')
@template_routes.route('/contact')
def contact():
    return render_template('contact.html')
@template_routes.route('/get-a-quote')
def get_a_quote():
    return render_template('get-a-quote.html')
@template_routes.route('/')
def index():
    return render_template('index.html')
@template_routes.route('/pricing')
def pricing():
    return render_template('pricing.html')
@template_routes.route('/service-details')
def service_details():
    return render_template('service-details.html')
@template_routes.route('/starter-page')
def starter_page():
    return render_template('starter-page.html')


