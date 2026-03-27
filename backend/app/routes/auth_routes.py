from flask import Blueprint, request, jsonify
from app import db
from app.models import User
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity
)
from sqlalchemy.exc import IntegrityError

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    username = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'msg': 'All fields are required'}), 400

    try:
        new_user = User(name=username, email=email)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        return jsonify({'msg': 'User registered successfully'}), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({'msg': 'Username or email already exists'}), 409


@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()

        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'msg': 'Email and password required'}), 400

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            return jsonify({'msg': 'Invalid email or password'}), 401

        # Generate JWT token - FORCE identity to be string
        access_token = create_access_token(identity=str(user.id))

        # Return token in JSON response
        return jsonify({
            "msg": "Login successful",
            "access_token": access_token,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email
            }
        }), 200
    
    except Exception as e:
        print(f"❌ LOGIN ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'msg': f'Server error: {str(e)}'}), 500


@auth_bp.route("/logout", methods=["POST"])
def logout():
    # Since we're using token-based auth, just return success
    # Token removal happens on frontend
    return jsonify({"msg": "Logged out successfully"}), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    try:
        current_user_id = get_jwt_identity()
        # Convert to int since we stored it as string
        user = User.query.get(int(current_user_id))

        if not user:
            return jsonify({'msg': 'User not found'}), 404

        return jsonify({
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'created_at': user.created_at.isoformat() if user.created_at else None
        }), 200
        
    except Exception as e:
        print(f"❌ GET USER ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'msg': str(e)}), 422