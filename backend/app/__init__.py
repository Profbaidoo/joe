"""
Flask Application Factory.
Initializes extensions, registers REST blueprints, configures OpenAPI documentation,
and mounts health endpoints.
"""

import os
from flask import Flask, jsonify
from app.config import config_by_name
from app.extensions import db, migrate, jwt, cors, swagger
from app.utils.env_validator import validate_environment


def create_app(config_name: str = None) -> Flask:
    if config_name is None:
        config_name = os.getenv("APP_ENV", "development").lower()

    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, config_by_name["development"]))

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": app.config.get("CORS_ORIGINS", "*")}})
    swagger.init_app(app)

    # JWT Error Handlers
    @jwt.unauthorized_loader
    def unauthorized_callback(callback):
        return jsonify({"error": "Missing or invalid authorization header (Bearer token required)."}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(callback):
        return jsonify({"error": "Signature verification failed: Invalid JWT token."}), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"error": "JWT access token has expired. Use /api/auth/refresh to rotate."}), 401

    # Register Blueprints
    from app.api.auth import auth_bp
    from app.api.products import products_bp
    from app.api.orders import orders_bp
    from app.api.payments import payments_bp
    from app.api.webhooks import webhooks_bp
    from app.api.admin import admin_bp
    from app.api.agent import agent_bp
    from app.api.utility import utility_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(webhooks_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(agent_bp)
    app.register_blueprint(utility_bp)

    # Health and Metadata Check
    @app.route("/api/health", methods=["GET"])
    def health_check():
        is_env_valid, env_report = validate_environment()
        return jsonify({
            "status": "HEALTHY",
            "app_name": app.config["APP_NAME"],
            "business_name": app.config["BUSINESS_NAME"],
            "environment": app.config["APP_ENV"],
            "currency": app.config["DEFAULT_CURRENCY"],
            "timezone": app.config["TIMEZONE"],
            "environment_valid": is_env_valid,
            "active_providers": env_report["active_providers"],
        }), 200

    # Global Error Handlers
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"error": "Bad Request", "details": str(e)}), 400

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"error": "An internal server error occurred."}), 500

    # Start Background Task Worker if explicitly enabled in production or WSGI
    if os.getenv("TASK_WORKER_ENABLED", "false").lower() == "true" and not app.config.get("TESTING"):
        from app.tasks.worker import start_background_worker
        try:
            start_background_worker(app, interval_seconds=int(os.getenv("PAYMENT_RECONCILIATION_INTERVAL_SECONDS", "30")))
        except Exception:
            pass

    return app
