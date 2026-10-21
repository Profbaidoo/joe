"""
Role-Based Access Control (RBAC) Decorators.
Enforces permissions on the backend API layer.
"""

from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from app.extensions import db
from app.models.user import User


def role_required(*allowed_roles):
    """
    Decorator that checks whether the authenticated user has one of the allowed roles.
    Example: @role_required('ADMIN') or @role_required('ADMIN', 'AGENT')
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = db.session.get(User, user_id)
            if not user or not user.is_active:
                return jsonify({"error": "User account inactive or not found"}), 403

            user_role = user.role.name.upper() if user.role else ""
            allowed_upper = [r.upper() for r in allowed_roles]

            if user_role not in allowed_upper:
                return jsonify({
                    "error": "Access denied: Insufficient permissions for this resource",
                    "required_roles": allowed_upper,
                    "your_role": user_role,
                }), 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator
