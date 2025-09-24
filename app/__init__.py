from flask import Flask
from .config import Config
from .extensions import db, migrate, jwt, cache, limiter
from .errors import register_error_handlers

def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cache.init_app(app)
    limiter.init_app(app)

    # register blueprints
    from .routes.auth import auth_bp
    from .routes.tasks import task_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(task_bp, url_prefix='/tasks')

    # simple root
    @app.route("/")
    def home():
        return {"status": "ok", "service": "Task Manager API"}
    
    register_error_handlers(app)

    return app
