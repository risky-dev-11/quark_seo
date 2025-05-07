def register_routes(app, db, bcrypt):
    from .auth_routes import register_auth_routes
    from .api_routes import register_api_routes
    from .template_routes import register_template_routes
    from .analysis_routes import register_analysis_routes

    register_auth_routes(app, db, bcrypt)
    register_api_routes(app, db)
    register_template_routes(app)
    register_analysis_routes(app, db)