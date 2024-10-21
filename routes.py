from flask import jsonify, render_template, request, redirect, url_for
from models import AnalyzedWebsite, User
from flask_login import login_user, login_required, logout_user, current_user
from analyzer import analyze_website

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
    
    @app.route('/api/count_of_analyzed_websites', methods=['GET'])
    def count_of_analyzed_websites():
        count = db.session.query(AnalyzedWebsite).count()
        return jsonify({"count": count}), 200
    
    @app.route('/api/analyze/<path:url>', methods=['GET'])
    def analyze_url(url):
        try: 
            analyze_website(url, db)
        except Exception as e:
            return jsonify({"error": str(e)}), 400
        return jsonify({"message": "Website successfully analyzed"}), 200

    # Endpoint for retrieving the results
    @app.route('/get_results/<path:url>', methods=['GET'])
    def get_results(url):
        result = db.session.query(AnalyzedWebsite).filter(AnalyzedWebsite.url == url).order_by(AnalyzedWebsite.uuid.desc()).first()
        if result:
            return jsonify(result.results), 200
        else:
            return jsonify({"error": "Not Found"}), 404

 