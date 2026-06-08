from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token
from models.task import db
from models.user import User
from models.token import RefreshToken
from datetime import datetime, timedelta
import bcrypt
import secrets

auth = Blueprint('auth', __name__)


# -----------------------------------------------
# REGISTER — POST /auth/register
# -----------------------------------------------
@auth.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()

    # validations
    if not data:
        return jsonify({"error": "Request body is missing"}), 400
    if "username" not in data:
        return jsonify({"error": "Username is required"}), 400
    if "email" not in data:
        return jsonify({"error": "Email is required"}), 400
    if "password" not in data:
        return jsonify({"error": "Password is required"}), 400
    if len(data["password"]) < 6:
        return jsonify({"error": "Password too short (min 6 chars)"}), 400

    # check if username or email already exists
    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"error": "Username already taken"}), 409
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already registered"}), 409

    # hash password
    hashed = bcrypt.hashpw(
        data["password"].encode('utf-8'),
        bcrypt.gensalt()
    )

    new_user = User(
        username = data["username"],
        email    = data["email"],
        password = hashed.decode('utf-8')
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "message": "Account created successfully",
        "user": new_user.to_dict()
    }), 201


# -----------------------------------------------
# LOGIN — POST /auth/login
# -----------------------------------------------
@auth.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body is missing"}), 400
    if "username" not in data:
        return jsonify({"error": "Username is required"}), 400
    if "password" not in data:
        return jsonify({"error": "Password is required"}), 400

    # find user
    user = User.query.filter_by(username=data["username"]).first()

    # verify password
    if not user or not bcrypt.checkpw(
        data["password"].encode('utf-8'),
        user.password.encode('utf-8')
    ):
        return jsonify({"error": "Invalid username or password"}), 401

    # generate tokens
    access_token  = create_access_token(identity=str(user.id))
    refresh_token = secrets.token_hex(64)

    # save refresh token to DB
    token_record = RefreshToken(
        user_id    = user.id,
        token      = refresh_token,
        expires_at = datetime.utcnow() + timedelta(days=7)
    )
    db.session.add(token_record)
    db.session.commit()

    return jsonify({
        "message":       "Login successful",
        "access_token":  access_token,
        "refresh_token": refresh_token,
        "user":          user.to_dict()
    }), 200


# -----------------------------------------------
# REFRESH — POST /auth/refresh
# -----------------------------------------------
@auth.route('/auth/refresh', methods=['POST'])
def refresh():
    data = request.get_json()

    if not data or "refresh_token" not in data:
        return jsonify({"error": "Refresh token is required"}), 400

    # find token in DB
    token_record = RefreshToken.query.filter_by(
        token=data["refresh_token"]
    ).first()

    if not token_record:
        return jsonify({"error": "Invalid refresh token"}), 401
    if token_record.is_expired():
        db.session.delete(token_record)
        db.session.commit()
        return jsonify({"error": "Refresh token expired, please login again"}), 401

    # generate new access token
    new_access_token = create_access_token(identity=str(token_record.user_id))

    return jsonify({
        "access_token": new_access_token
    }), 200


# -----------------------------------------------
# LOGOUT — POST /auth/logout
# -----------------------------------------------
@auth.route('/auth/logout', methods=['POST'])
def logout():
    data = request.get_json()

    if not data or "refresh_token" not in data:
        return jsonify({"error": "Refresh token is required"}), 400

    token_record = RefreshToken.query.filter_by(
        token=data["refresh_token"]
    ).first()

    if token_record:
        db.session.delete(token_record)
        db.session.commit()

    return jsonify({"message": "Logged out successfully"}), 200