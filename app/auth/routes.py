from flask import Blueprint, request
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity
)
from app.models import User
from app.extensions import db

auth_bp = Blueprint("auth", __name__)

# 🔹 Register user
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return {"errors": {"form": "Username and password required"}}, 400

    if User.query.filter_by(username=username).first():
        return {"errors": {"username": "User already exists"}}, 409

    user = User(username=username)
    user.set_password(password)  # 👈 use model method
    db.session.add(user)
    db.session.commit()

    return {"message": "User registered successfully"}, 201


# 🔹 Login user
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):  # 👈 use model method
        return {"errors": {"credentials": "Invalid username or password"}}, 401

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {"id": user.id, "username": user.username}
    }, 200


# 🔹 Refresh token
@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=user_id)
    return {"access_token": new_access_token}, 200


# 🔹 Get current user
@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return {"errors": {"user": "Not found"}}, 404
    return {"id": user.id, "username": user.username}, 200
