"""
Authentication and User Management Endpoints.
Implements JWT tokens with refresh token rotation and Ghanaian phone validation.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
)
from app.extensions import db
from app.models.user import User, Role, Customer, Agent
from app.models.audit import AuditLog
from app.utils.phone_validator import normalize_ghana_phone
from app.utils.security import generate_agent_code

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Register a new customer account.
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - username
            - email
            - phone_number
            - password
            - full_name
          properties:
            username:
              type: string
              example: kwame_mensah
            email:
              type: string
              example: kwame@example.com
            phone_number:
              type: string
              example: "0241234567"
            password:
              type: string
              example: "SecureP@ss2026!"
            full_name:
              type: string
              example: "Kwame Mensah"
            momo_network:
              type: string
              enum: [MTN, TELECEL, AT]
              example: MTN
    responses:
      201:
        description: Customer registered successfully
      400:
        description: Validation error
    """
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    email = data.get("email", "").strip().lower()
    raw_phone = data.get("phone_number", "").strip()
    password = data.get("password", "")
    full_name = data.get("full_name", "").strip()
    momo_network = data.get("momo_network", "").upper()

    if not all([username, email, raw_phone, password, full_name]):
        return jsonify({"error": "All fields (username, email, phone_number, password, full_name) are required."}), 400

    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters long."}), 400

    # Validate Ghanaian phone
    is_valid, local_phone, _, detected_network = normalize_ghana_phone(raw_phone)
    if not is_valid:
        return jsonify({"error": f"Invalid Ghanaian phone number format: {raw_phone}. Use 024XXXXXXX or +233XXXXXXXXX."}), 400

    # Ensure uniqueness
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username is already taken."}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email address is already registered."}), 400
    if User.query.filter_by(phone_number=local_phone).first():
        return jsonify({"error": "Phone number is already registered."}), 400

    # Assign default CUSTOMER role
    customer_role = Role.query.filter_by(name="CUSTOMER").first()
    if not customer_role:
        customer_role = Role(name="CUSTOMER", description="End customer")
        db.session.add(customer_role)
        db.session.commit()

    user = User(
        username=username,
        email=email,
        phone_number=local_phone,
        role_id=customer_role.id,
        is_active=True,
        is_verified=True,
    )
    user.set_password(password)
    db.session.add(user)
    db.session.flush()

    customer = Customer(
        user_id=user.id,
        full_name=full_name,
        momo_number=local_phone,
        momo_network=momo_network or detected_network,
    )
    db.session.add(customer)

    # Audit log
    audit = AuditLog(
        user_id=user.id,
        action="USER_REGISTRATION",
        ip_address=request.remote_addr,
        details_json={"username": username, "network": customer.momo_network},
    )
    db.session.add(audit)
    db.session.commit()

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return jsonify({
        "message": "Registration successful.",
        "user": user.to_dict(),
        "access_token": access_token,
        "refresh_token": refresh_token,
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Authenticate user and issue JWT access and refresh tokens.
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - login
            - password
          properties:
            login:
              type: string
              description: Username, Email, or Ghanaian Phone Number
              example: "0241234567"
            password:
              type: string
              example: "SecureP@ss2026!"
    responses:
      200:
        description: Authentication successful
      401:
        description: Invalid credentials
    """
    data = request.get_json() or {}
    login_identifier = data.get("login", "").strip()
    password = data.get("password", "")

    if not login_identifier or not password:
        return jsonify({"error": "Login identifier and password are required."}), 400

    # Search by username, email, or normalized phone
    user = User.query.filter(
        (User.username == login_identifier) |
        (User.email == login_identifier.lower()) |
        (User.phone_number == login_identifier)
    ).first()

    # Also try normalizing if it's a phone format
    if not user:
        is_valid, local_phone, _, _ = normalize_ghana_phone(login_identifier)
        if is_valid:
            user = User.query.filter_by(phone_number=local_phone).first()

    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid username, phone number, or password."}), 401

    if not user.is_active:
        return jsonify({"error": "This account has been deactivated. Please contact support."}), 403

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    audit = AuditLog(
        user_id=user.id,
        action="USER_LOGIN",
        ip_address=request.remote_addr,
        details_json={"login_identifier": login_identifier},
    )
    db.session.add(audit)
    db.session.commit()

    return jsonify({
        "message": "Login successful.",
        "user": user.to_dict(),
        "access_token": access_token,
        "refresh_token": refresh_token,
    }), 200


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """Rotate and issue a new access token using a valid refresh token."""
    user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=str(user_id))
    return jsonify({
        "access_token": new_access_token,
    }), 200


@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    """Client-side token invalidation / logout acknowledgment."""
    return jsonify({"message": "Logout successful."}), 200


@auth_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    """Retrieve the current authenticated user's profile and account balances."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"user": user.to_dict()}), 200
