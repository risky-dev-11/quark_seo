import base64
from flask import jsonify, render_template, request, redirect, url_for
from models import AnalyzedWebsite, User
from flask_login import login_user, login_required, logout_user
from analyzer import analyze_website
from flask_login import current_user

def register_routes(app, db, bcrypt):

    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        if request.method == 'GET':
            return render_template('signup.html')
        elif request.method == 'POST':
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            email = request.form['email']
            password = request.form['password']
            hashed_password = bcrypt.generate_password_hash(password)
            user = User(first_name=first_name, last_name=last_name, email=email, password=hashed_password, role='user')
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('index')) #maybe redirect elsewhere - or determe if redirect to results page!!!!!

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'GET':
            return render_template('login.html')
        elif request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            user = User.query.filter_by(email=email).first()
            if bcrypt.check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('index'))
            else:
                return 'Failed to login'
    
    @app.route('/logout')
    def logout():
        logout_user()
        return redirect(url_for('index'))
    
    @app.login_manager.unauthorized_handler
    def unauthorized_callback():
        return render_template('unauthorized.html')
    
    @app.route('/api/analyze/<path:url>', methods=['GET'])
    def analyze_url(url):
        if not current_user.is_authenticated:
            user_uuid = None
        else:
            user_uuid = current_user.uuid
        try: 
            uuid = analyze_website(user_uuid, url, db)
        except Exception as e:
            print(e)
            return jsonify({"message": "There was an error while analyzing the website", "error": str(e)}), 400
        return jsonify({"message": "Website successfully analyzed", "uuid": uuid}), 200

    # Endpoint for retrieving the results
    @app.route('/api/get_results/<uuid:uuid>', methods=['GET'])
    def get_results(uuid):
        result = db.session.query(AnalyzedWebsite).filter_by(uuid=str(uuid)).first()
        if result:
            if result.screenshot is None:
                screenshot_blob = None
            else:
                screenshot_blob = base64.b64encode(result.screenshot).decode('utf-8')
            return jsonify({"results": result.results, "screenshot": screenshot_blob}), 200
        else:
            return jsonify({"error": "Not Found"}), 404
        
    @app.route('/profile/get_analyses')
    @login_required
    def get_users_analysis():
        user_uuid = current_user.uuid
        result = db.session.query(AnalyzedWebsite).filter_by(user_uuid=user_uuid).all()

        results = []
        for analysis in result:
            data = analysis.results
            overall_rating = data['overall_results']['overall_rating']
            improvement_count = data['overall_results']['improvement_count']
            
            results.append({
                "uuid": analysis.uuid,
                "time": analysis.time if analysis.time is not None else "Unknown",
                "url": analysis.url,
                "overall_rating": overall_rating,
                "improvement_count": improvement_count
            })
        return jsonify(results), 200

    # Routes for the templates
    @app.route('/results/<path:url>/<uuid:uuid>', methods=['GET'])
    def show_results(url, uuid):
        return render_template("seo-analytics-page.html", url=url, uuid=uuid)
    @app.route('/results/<path:url>/error', methods=['GET'])
    def show_results_error(url):
        return render_template("seo-analytics-error-page.html", url=url)
    @app.route('/seo/analyze/<path:url>', methods=['GET'])
    def show_loading_page(url):
        return render_template("seo-analytics-loading-page.html")
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

