"""
Payment Processing, MoMo Push Request, and Status Reconciliation Endpoints.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.models.order import Order
from app.models.transaction import Transaction
from app.services.payment_service import PaymentService
from app.utils.phone_validator import normalize_ghana_phone

payments_bp = Blueprint("payments", __name__, url_prefix="/api/payments")


@payments_bp.route("/momo/request", methods=["POST"])
@jwt_required()
def request_momo_payment():
    """
    Initiate MTN MoMo Request-To-Pay prompt.
    ---
    tags:
      - Payments
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - order_id
            - momo_phone
          properties:
            order_id:
              type: integer
              example: 1
            momo_phone:
              type: string
              example: "0241234567"
    responses:
      200:
        description: Request-to-pay initiated; prompt sent to customer handset
      400:
        description: Payment validation error
    """
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    order_id = data.get("order_id")
    raw_phone = data.get("momo_phone", "").strip()

    if not order_id or not raw_phone:
        return jsonify({"error": "order_id and momo_phone are required."}), 400

    is_valid, local_phone, _, _ = normalize_ghana_phone(raw_phone)
    if not is_valid:
        return jsonify({"error": f"Invalid Ghanaian mobile number: {raw_phone}"}), 400

    try:
        result = PaymentService.initiate_momo_payment(
            order_id=int(order_id),
            customer_phone=local_phone,
            user_id=user_id,
        )
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@payments_bp.route("/momo/status/<reference>", methods=["GET"])
@jwt_required()
def get_momo_payment_status(reference: str):
    """
    Check and reconcile status of a MoMo transaction.
    Triggers fulfillment and double-entry ledgering when payment is confirmed.
    """
    try:
        result = PaymentService.verify_and_reconcile_transaction(reference)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@payments_bp.route("/transactions", methods=["GET"])
@jwt_required()
def list_transactions():
    """List transactions with role enforcement and pagination."""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))
    status = request.args.get("status")

    query = Transaction.query
    if not user.has_role("ADMIN"):
        query = query.filter_by(user_id=user.id)

    if status:
        query = query.filter_by(status=status.upper())

    pagination = query.order_by(Transaction.id.desc()).paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "transactions": [t.to_dict() for t in pagination.items],
        "total": pagination.total,
        "page": pagination.page,
        "pages": pagination.pages,
    }), 200
