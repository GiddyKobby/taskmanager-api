from flask import Flask
from .config import Config
from .extensions import db, migrate, jwt, cache, limiter
from .errors import register_error_handlers
import flask_monitoringdashboard as dashboard
import logging
from logging.handlers import RotatingFileHandler
import os
from flask_caching import Cache

cache = cache()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cache.init_app(app)
    limiter.init_app(app)
    
    # Caching setup (simple in-memory cache for dev)
    app.config["CACHE_TYPE"] = "SimpleCache"
    app.config["CACHE_DEFAULT_TIMEOUT"] = 60  # 1 min

    cache.init_app(app)
    
    # register blueprints
    from .routes.auth import auth_bp
    from .routes.tasks import task_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(task_bp, url_prefix='/tasks')

    # Bind Flask Monitoring Dashboard *after* app is created
    dashboard.bind(app)
    
    # simple root
    @app.route("/")
    def home():
        return {"status": "ok", "service": "Task Manager API"}
    
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

    app.logger.setLevel(logging.INFO)
    app.logger.info("App startup")

    # Register blueprints, db, etc...

    return app
