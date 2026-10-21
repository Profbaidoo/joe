"""
Flask Application Configuration.
Supports Development, Testing, and Production environments with strict defaults.
"""

import os
import sys
from datetime import timedelta
from dotenv import load_dotenv

# Ensure both backend and project root are in sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
project_root = os.path.dirname(backend_dir)
for p in (backend_dir, project_root):
    if p not in sys.path:
        sys.path.insert(0, p)

# Load root .env or backend .env
load_dotenv(os.path.join(project_root, ".env"))
load_dotenv()


class BaseConfig:
    APP_NAME = os.getenv("APP_NAME", "Ghana MoMo & Telecom Hub")
    BUSINESS_NAME = os.getenv("BUSINESS_NAME", "Blessings Telecom & Financial Services Ltd.")
    BUSINESS_PHONE = os.getenv("BUSINESS_PHONE", "+233240000000")
    BUSINESS_EMAIL = os.getenv("BUSINESS_EMAIL", "support@blessingstelecom.com.gh")

    # Security Keys
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-insecure-secret-key-change-in-production-1234567890")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-insecure-jwt-key-change-in-production-1234567890")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES_MINUTES", "30")))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES_DAYS", "14")))
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_HEADER_NAME = "Authorization"
    JWT_HEADER_TYPE = "Bearer"

    # Database
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 280,
        "pool_pre_ping": True,
    }

    # Timezone & Currency
    TIMEZONE = "Africa/Accra"
    DEFAULT_CURRENCY = "GHS"

    # Swagger / Flasgger Specs
    SWAGGER = {
        "title": "Ghana Fintech MoMo, Airtime & Data API",
        "description": "Production-ready REST API for Ghanaian Mobile Money, Telecom & Digital Financial Services",
        "version": "1.0.0",
        "uiversion": 3,
        "specs_route": "/api/docs/",
        "headers": [],
        "specs": [
            {
                "endpoint": "apispec_1",
                "route": "/api/docs/apispec_1.json",
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
    }

    # CORS
    CORS_ORIGINS = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173,http://localhost:8081").split(",")
        if origin.strip()
    ]


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    APP_ENV = "development"
    # Use MySQL if configured, otherwise fallback to SQLite for immediate local dev
    db_url = os.getenv("DATABASE_URL")
    if db_url and not db_url.startswith("mysql+pymysql://USER@HOST"):
        SQLALCHEMY_DATABASE_URI = db_url
    else:
        sqlite_fallback = os.getenv("SQLITE_FALLBACK_URL", "sqlite:///ghana_fintech_dev.db")
        SQLALCHEMY_DATABASE_URI = sqlite_fallback


class TestingConfig(BaseConfig):
    TESTING = True
    DEBUG = True
    APP_ENV = "testing"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)
    SECRET_KEY = "test-secret-key-super-secure-32bytes-minimum"
    JWT_SECRET_KEY = "test-jwt-secret-key-super-secure-32bytes-minimum"


class ProductionConfig(BaseConfig):
    DEBUG = False
    TESTING = False
    APP_ENV = "production"
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")

    @classmethod
    def init_app(cls, app):
        BaseConfig.init_app(app) if hasattr(BaseConfig, "init_app") else None
        # Strict validation of secrets in production
        secret = os.getenv("SECRET_KEY", "")
        jwt_secret = os.getenv("JWT_SECRET_KEY", "")
        if not secret or len(secret) < 32 or secret.startswith("generate_"):
            raise ValueError("CRITICAL: Production SECRET_KEY must be a random secret of at least 32 characters.")
        if not jwt_secret or len(jwt_secret) < 32 or jwt_secret.startswith("generate_"):
            raise ValueError("CRITICAL: Production JWT_SECRET_KEY must be a random secret of at least 32 characters.")


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
