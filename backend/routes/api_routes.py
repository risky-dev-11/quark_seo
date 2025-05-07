from flask import jsonify, redirect, request, url_for
from flask_login import login_required, current_user
from backend.models.user import User
from backend.models.results import AnalyzedWebsite

def register_api_routes(app, db):
    @app.route('/api/profile/get_analyses', methods=['POST'])
    @login_required
    def get_users_analysis():
        draw = int(request.form.get('draw', 1))
        start = int(request.form.get('start', 0))
        length = int(request.form.get('length', 10))
        search_value = request.form.get('search[value]', '').lower()
        url_filter = request.form.get('url_filter', '').lower()

        user_uuid = current_user.uuid
        query = db.session.query(AnalyzedWebsite).filter_by(user_uuid=user_uuid)

        if search_value:
            query = query.filter(AnalyzedWebsite.url.ilike(f'%{search_value}%'))
        if url_filter:
            query = query.filter(AnalyzedWebsite.url.ilike(f'%{url_filter}%'))

        records_filtered = query.count()
        results_paginated = query.order_by(AnalyzedWebsite.time.desc()).offset(start).limit(length).all()

        data = [{
            "uuid": a.uuid,
            "time": a.time.isoformat() if a.time else "Unknown",
            "url": a.url,
            "overall_rating": a.results['overall_results']['overall_rating'],
            "improvement_count": a.results['overall_results']['improvement_count']
        } for a in results_paginated]

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
        urls = db.session.query(AnalyzedWebsite.url).filter_by(user_uuid=current_user.uuid).distinct().all()
        return jsonify([url[0] for url in urls])

    @app.route('/api/profile/get_analyses_by_url', methods=['GET'])
    @login_required
    def get_analyses_by_url():
        url = request.args.get('url', type=str)
        analyses = db.session.query(AnalyzedWebsite).filter_by(user_uuid=current_user.uuid, url=url).order_by(AnalyzedWebsite.time).all()

        data = [{
            'time': a.time.isoformat() if a.time else None,
            'overall_rating': a.results.get('overall_results', {}).get('overall_rating'),
            'improvement_count': a.results.get('overall_results', {}).get('improvement_count')
        } for a in analyses]

        return jsonify(data)

    @app.route('/api/roles/upgrade_user', methods=['POST'])
    def upgrade_user():
        if not current_user.is_authenticated:
            return redirect(url_for('signup'))
        user = db.session.query(User).filter_by(uuid=current_user.uuid).first()
        user.role = 'premium'
        db.session.commit()
        return jsonify({"message": "User upgraded to premium"}), 200