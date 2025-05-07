import base64
from flask import jsonify, render_template, request, redirect, url_for
from backend.models.models import AnalyzedWebsite, User, UserHierarchy
from flask_login import login_user, login_required, logout_user
from backend.analysis.analyzer import analyze_website
from flask_login import current_user

from flask import Response, stream_with_context
import time
import threading

def register_routes(app, db, bcrypt):

    @app.route('/check_email')
    def check_email():
        email = request.args.get('email', '').strip().lower()
        exists = User.query.filter_by(email=email).first() is not None
        return jsonify({ 'exists': exists })

    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        if request.method == 'GET':
            return render_template('signup.html')

        # POST
        data = request.get_json() if request.is_json else request.form
        first_name = data.get('first_name', '').strip()
        last_name  = data.get('last_name', '').strip()
        email      = data.get('email', '').strip().lower()
        password   = data.get('password', '')

        # 1) E-Mail-Duplikat?
        if User.query.filter_by(email=email).first():
            payload = {
                'success': False,
                'field': 'email',
                'error': 'Diese E-Mail ist bereits in Verwendung.'
            }
            return jsonify(payload)

        # 2) Passwortstärke serverseitig prüfen (z.B. gleiche Regex)
        import re
        if not re.match(r'^(?=.*[A-Z])(?=.*\d).{8,}$', password):
            return jsonify({
                'success': False,
                'field': 'password',
                'error': 'Passwort entspricht nicht den Mindestanforderungen.'
            })

        # 3) Neuen User anlegen
        hashed = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(first_name=first_name, last_name=last_name,
                    email=email, password=hashed, role='basic')
        db.session.add(user)
        db.session.commit()

        # 4) Automatisch einloggen und zurückmelden
        login_user(user, remember=True)
        return jsonify({ 'success': True, 'redirect': url_for('index') })


    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'GET':
            return render_template('login.html')

        # AJAX-POST
        if request.is_json:
            data = request.get_json()
            email = data.get('email', '').strip()
            password = data.get('password', '')
            user = User.query.filter_by(email=email).first()

            if user is None or not bcrypt.check_password_hash(user.password, password):
                return jsonify({'success': False, 'error': 'E-Mail oder Passwort ist falsch.'})

            login_user(user, remember=True)
            return jsonify({'success': True, 'redirect': url_for('index')})

        return '', 400  # Bad request if not JSON
    
    @app.route('/logout')
    def logout():
        logout_user()
        return redirect(url_for('index'))
    
    @app.route('/api/analyze/<path:url>', methods=['GET'])
    def analyze_url(url):
        if not current_user.is_authenticated:
            user_uuid = None
            is_premium_user = False
        else:
            user_uuid = current_user.uuid
            is_premium_user = UserHierarchy.is_higher_than_basic(current_user)
        try: 
            uuid = analyze_website(user_uuid, url, db, is_premium_user)
        except Exception as e:
            return jsonify({"message": "There was an error while analyzing the website", "error": str(e)}), 400
        return jsonify({"message": "Website successfully analyzed", "uuid": uuid}), 200

    @app.route('/api/analyze/stream/<path:url>', methods=['GET'])
    def stream_analyze_url(url):
        if not current_user.is_authenticated:
            user_uuid = None
            is_premium_user = False
        else:
            user_uuid = current_user.uuid
            is_premium_user = UserHierarchy.is_higher_than_basic(current_user)

        @stream_with_context
        def generate():
            yield from analyze_website(user_uuid, url, db, is_premium_user, send_progress=True)

        return Response(generate(), mimetype='text/event-stream')


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
        
    @app.route('/api/profile/get_analyses', methods=['POST'])
    @login_required
    def get_users_analysis():
        draw = int(request.form.get('draw', 1))
        start = int(request.form.get('start', 0))
        length = int(request.form.get('length', 10))
        search_value = request.form.get('search[value]', '').lower()
        url_filter = request.form.get('url_filter', '').lower()  # ⬅️ Neue Filtervariable

        user_uuid = current_user.uuid

        query = db.session.query(AnalyzedWebsite).filter_by(user_uuid=user_uuid)

        # globale Suche
        if search_value:
            query = query.filter(AnalyzedWebsite.url.ilike(f'%{search_value}%'))

        # gezielter URL-Filter
        if url_filter:
            query = query.filter(AnalyzedWebsite.url.ilike(f'%{url_filter}%'))

        records_filtered = query.count()
        results_paginated = query.order_by(AnalyzedWebsite.time.desc()).offset(start).limit(length).all()

        data = []
        for analysis in results_paginated:
            results_data = analysis.results
            overall_rating = results_data['overall_results']['overall_rating']
            improvement_count = results_data['overall_results']['improvement_count']
            data.append({
                "uuid": analysis.uuid,
                "time": analysis.time.isoformat() if analysis.time else "Unknown",
                "url": analysis.url,
                "overall_rating": overall_rating,
                "improvement_count": improvement_count
            })

        records_total = db.session.query(AnalyzedWebsite).filter_by(user_uuid=user_uuid).count()

        return jsonify({
            "draw": draw,
            "recordsTotal": records_total,
            "recordsFiltered": records_filtered,
            "data": data
        })
    @app.route('/api/profile/get_all_urls', methods=['GET'])
    @login_required
    def get_all_urls():
        user_uuid = current_user.uuid

        urls = (
            db.session.query(AnalyzedWebsite.url)
            .filter_by(user_uuid=user_uuid)
            .distinct()
            .all()
        )

        # Liste aus Tupeln extrahieren
        url_list = [url[0] for url in urls]
        return jsonify(url_list)
    

    @app.route('/api/profile/get_analyses_by_url', methods=['GET'])
    @login_required
    def get_analyses_by_url():
        user_uuid = current_user.uuid
        url = request.args.get('url', type=str)

        # Fetch all analyses for this user + URL, ordered by time
        analyses = (
            db.session
            .query(AnalyzedWebsite)
            .filter_by(user_uuid=user_uuid, url=url)
            .order_by(AnalyzedWebsite.time)
            .all()
        )

        # Build the JSON response
        data = []
        for analysis in analyses:
            # `analysis.results` is your JSON/dict column
            rd = analysis.results.get('overall_results', {})
            overall_rating    = rd.get('overall_rating', None)
            improvement_count = rd.get('improvement_count', None)

            data.append({
                'time':             analysis.time.isoformat() if analysis.time else None,
                'overall_rating':   overall_rating,
                'improvement_count':improvement_count
            })

        return jsonify(data)

    @app.route('/api/roles/upgrade_user', methods=['POST'])
    def upgrade_user():
        if not current_user.is_authenticated:
            return redirect(url_for('signup'))
        user_uuid = current_user.uuid
        user = db.session.query(User).filter_by(uuid=user_uuid).first()
        user.role = 'premium'
        db.session.commit()
        return jsonify({"message": "User upgraded to premium"}), 200

    # Routes for the templates
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

