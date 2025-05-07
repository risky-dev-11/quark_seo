from flask import request, render_template, jsonify, redirect, url_for
from flask_login import login_user, logout_user
from backend.models.user import User

def register_auth_routes(app, db, bcrypt):
    @app.route('/check_email')
    def check_email():
        email = request.args.get('email', '').strip().lower()
        exists = User.query.filter_by(email=email).first() is not None
        return jsonify({ 'exists': exists })

    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        if request.method == 'GET':
            return render_template('signup.html')

        data = request.get_json() if request.is_json else request.form
        first_name = data.get('first_name', '').strip()
        last_name  = data.get('last_name', '').strip()
        email      = data.get('email', '').strip().lower()
        password   = data.get('password', '')

        if User.query.filter_by(email=email).first():
            return jsonify({'success': False, 'field': 'email', 'error': 'Diese E-Mail ist bereits in Verwendung.'})

        import re
        if not re.match(r'^(?=.*[A-Z])(?=.*\d).{8,}$', password):
            return jsonify({'success': False, 'field': 'password', 'error': 'Passwort entspricht nicht den Mindestanforderungen.'})

        hashed = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(first_name=first_name, last_name=last_name, email=email, password=hashed, role='basic')
        db.session.add(user)
        db.session.commit()

        login_user(user, remember=True)
        return jsonify({ 'success': True, 'redirect': url_for('index') })

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'GET':
            return render_template('login.html')
        if request.is_json:
            data = request.get_json()
            user = User.query.filter_by(email=data.get('email', '').strip()).first()
            if user is None or not bcrypt.check_password_hash(user.password, data.get('password', '')):
                return jsonify({'success': False, 'error': 'E-Mail oder Passwort ist falsch.'})
            login_user(user, remember=True)
            return jsonify({'success': True, 'redirect': url_for('index') })
        return '', 400

    @app.route('/logout')
    def logout():
        logout_user()
        return redirect(url_for('index'))