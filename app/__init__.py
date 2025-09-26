from flask import Flask
from .config import Config
from .extensions import db, migrate, jwt, cache, limiter
from .models import User, Task  # 🔹 import models BEFORE create_all
from .errors import register_error_handlers
import flask_monitoringdashboard as dashboard
import logging
from logging.handlers import RotatingFileHandler
import os


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # --- Security / JWT ---
    app.config["JWT_SECRET_KEY"] = "super-secret-key"  # ⚠️ change in production

    # --- Cache defaults (set BEFORE init_app) ---
    app.config.setdefault("CACHE_TYPE", "SimpleCache")
    app.config.setdefault("CACHE_DEFAULT_TIMEOUT", 60)

    # --- Initialize extensions ---
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cache.init_app(app)
    limiter.init_app(app)

    # 🔹 Rebuild tables (make sure models are imported before this!)
    with app.app_context():
        db.create_all()

    # --- Blueprints ---
    from .routes import task_bp
    from .auth.routes import auth_bp

    app.register_blueprint(task_bp, url_prefix="/tasks")
    app.register_blueprint(auth_bp, url_prefix="/auth")

    # --- Flask Monitoring Dashboard ---
    dashboard.bind(app)

    # --- Root health check ---
    @app.route("/")
    def home():
        return {"status": "ok", "service": "Task Manager API"}

    # --- Error handlers ---
    register_error_handlers(app)

    # --- Logging Setup ---
    if not os.path.exists("logs"):
        os.mkdir("logs")

    file_handler = RotatingFileHandler(
        "logs/app.log", maxBytes=10240, backupCount=5
    )
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
    ))
    file_handler.setLevel(logging.INFO)

    # Prevent duplicate handlers in debug/reload
    if not app.logger.handlers:
        app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info("App startup")

    return app
