import base64
from flask import jsonify, Response, stream_with_context
from flask_login import current_user
from backend.models.results import AnalyzedWebsite
from backend.models.user import UserHierarchy
from backend.analysis.analyzer import analyze_website

def register_analysis_routes(app, db):
    @app.route('/api/analyze/<path:url>', methods=['GET'])
    def analyze_url(url):
        if not current_user.is_authenticated:
            user_uuid, is_premium_user = None, False
        else:
            user_uuid = current_user.uuid
            is_premium_user = UserHierarchy.is_higher_than_basic(current_user)

        try:
            uuid = analyze_website(user_uuid, url, db, is_premium_user)
        except Exception as e:
            return jsonify({"message": "Error during analysis", "error": str(e)}), 400
        return jsonify({"message": "Analysis started", "uuid": uuid}), 200

    @app.route('/api/analyze/stream/<path:url>', methods=['GET'])
    def stream_analyze_url(url):
        if not current_user.is_authenticated:
            user_uuid, is_premium_user = None, False
        else:
            user_uuid = current_user.uuid
            is_premium_user = UserHierarchy.is_higher_than_basic(current_user)

        @stream_with_context
        def generate():
            yield from analyze_website(user_uuid, url, db, is_premium_user, send_progress=True)

        return Response(generate(), mimetype='text/event-stream')

    @app.route('/api/get_results/<uuid:uuid>', methods=['GET'])
    def get_results(uuid):
        result = db.session.query(AnalyzedWebsite).filter_by(uuid=str(uuid)).first()
        if not result:
            return jsonify({"error": "Not Found"}), 404
        screenshot_blob = base64.b64encode(result.screenshot).decode('utf-8') if result.screenshot else None
        return jsonify({"results": result.results, "screenshot": screenshot_blob}), 200