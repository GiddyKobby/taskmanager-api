from flask import Flask
from extensions import jwt


def create_app():
    app = Flask(__name__)
    app.config["JWT_SECRET_KEY"] = "super-secret-key"  # change in production

    jwt.init_app(app)

    app.register_blueprint(auth_bp, url_prefix="/auth")

    # register blueprints
    from .routes.auth import auth_bp
    from .routes.tasks import tasks_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(tasks_bp)

    return app
