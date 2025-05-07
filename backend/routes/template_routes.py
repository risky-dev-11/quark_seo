from flask import render_template
from flask_login import login_required

def register_template_routes(app):
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.login_manager.unauthorized_handler
    def unauthorized_callback():
        return render_template('unauthorized.html')

    @app.route('/results/<path:url>/<uuid:uuid>', methods=['GET'])
    def show_results(url, uuid):
        return render_template("seo-analytics-page.html", url=url, uuid=uuid)

    @app.route('/results/<path:url>/error', methods=['GET'])
    def show_results_error(url):
        return render_template("seo-analytics-error-page.html", url=url)

    @app.route('/profile')
    @login_required
    def profile():
        return render_template('profile.html')

    @app.route('/about')
    def about():
        return render_template('about.html')

    @app.route('/contact')
    def contact():
        return render_template('contact.html')

    @app.route('/pricing')
    def pricing():
        return render_template('pricing.html')

    @app.route('/service-details')
    def service_details():
        return render_template('service-details.html')

    @app.route('/starter-page')
    def starter_page():
        return render_template('starter-page.html')