"""
Ghana Utility Bill Payment Endpoints (ECG, Ghana Water, etc.).
"""

from decimal import Decimal
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User

utility_bp = Blueprint("utility", __name__, url_prefix="/api/utility")


@utility_bp.route("/ecg/verify", methods=["POST"])
@jwt_required()
def verify_ecg_meter():
    """
    Validates Electricity Company of Ghana (ECG) meter account.
    """
    data = request.get_json() or {}
    meter_number = data.get("meter_number", "").strip()
    meter_type = data.get("meter_type", "PREPAID").upper()  # PREPAID or POSTPAID

    if not meter_number or len(meter_number) < 6:
        return jsonify({"error": "Valid meter number (minimum 6 digits) is required."}), 400

    # In sandbox, return verified Ghanaian customer details
    return jsonify({
        "is_valid": True,
        "meter_number": meter_number,
        "meter_type": meter_type,
        "customer_name": "Kofi Mensah",
        "district": "Accra West / Dansoman",
        "outstanding_balance": 0.00 if meter_type == "PREPAID" else 142.50,
    }), 200
