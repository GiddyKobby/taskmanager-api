from .extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # store hashed pw
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # One-to-many: a user can have many tasks
    tasks = db.relationship("Task", backref="owner", lazy=True)

    def set_password(self, password: str):
        """Hash and store password."""
        self.password = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify password hash."""
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f"<User {self.username}>"


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    done = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign key to users
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    def __repr__(self):
        return f"<Task {self.title}>"
