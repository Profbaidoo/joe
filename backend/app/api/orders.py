"""
Order Creation, History, and Status Inspection Endpoints.
Enforces strict ownership checks: customers can only view their own orders.
"""

from decimal import Decimal
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.user import User, Agent
from app.models.order import Order, OrderItem
from app.models.product import Product, DataBundlePlan
from app.services.pricing_service import PricingService
from app.utils.phone_validator import normalize_ghana_phone
from app.utils.security import generate_reference

orders_bp = Blueprint("orders", __name__, url_prefix="/api/orders")


@orders_bp.route("", methods=["POST"])
@jwt_required()
def create_order():
    """
    Place a new Airtime, Data Bundle, or Utility Bill order.
    ---
    tags:
      - Orders
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - order_type
            - recipient_phone
            - network_code
          properties:
            order_type:
              type: string
              enum: [AIRTIME, DATA_BUNDLE, MOMO_TRANSFER, MOMO_CASHOUT, UTILITY_BILL]
              example: AIRTIME
            recipient_phone:
              type: string
              example: "0241234567"
            network_code:
              type: string
              enum: [MTN, TELECEL, AT]
              example: MTN
            amount:
              type: number
              example: 10.00
            data_bundle_plan_id:
              type: integer
              example: 1
    responses:
      201:
        description: Order created with PENDING payment status
    """
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json() or {}
    order_type = data.get("order_type", "").upper()
    raw_recipient = data.get("recipient_phone", "").strip()
    network_code = data.get("network_code", "").upper()
    amount = data.get("amount")
    data_bundle_plan_id = data.get("data_bundle_plan_id")

    if not order_type or not raw_recipient or not network_code:
        return jsonify({"error": "order_type, recipient_phone, and network_code are required."}), 400

    # Validate phone and verify it matches the chosen network
    is_valid, local_phone, _, detected_net = normalize_ghana_phone(raw_recipient)
    if not is_valid:
        return jsonify({"error": f"Invalid Ghanaian phone number format: {raw_recipient}"}), 400

    if detected_net != network_code and order_type in ("AIRTIME", "DATA_BUNDLE"):
        return jsonify({
            "error": f"Network mismatch: Phone {raw_recipient} belongs to {detected_net}, but {network_code} was selected."
        }), 400

    is_agent = user.has_role("AGENT")
    agent_id = user.agent_profile.id if is_agent and user.agent_profile else None

    try:
        quote = PricingService.get_pricing_quote(
            order_type=order_type,
            network_code=network_code,
            amount=Decimal(str(amount)) if amount is not None else None,
            data_bundle_plan_id=int(data_bundle_plan_id) if data_bundle_plan_id else None,
            is_agent_order=is_agent,
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    order_ref = generate_reference("ORD")
    order = Order(
        order_reference=order_ref,
        user_id=user.id,
        agent_id=agent_id,
        order_type=order_type,
        recipient_phone=local_phone,
        network_code=network_code,
        total_amount=quote["total_payable"],
        fee_amount=quote["fee_amount"],
        net_amount=quote["retail_amount"],
        status="PENDING",
        payment_status="UNPAID",
        fulfillment_status="UNFULFILLED",
    )
    db.session.add(order)
    db.session.flush()

    # Create Order Item
    product_id = None
    if order_type == "AIRTIME":
        product = Product.query.filter_by(code=f"AIRTIME_{network_code}").first()
        product_id = product.id if product else None

    item = OrderItem(
        order_id=order.id,
        product_id=product_id,
        data_bundle_plan_id=int(data_bundle_plan_id) if data_bundle_plan_id else None,
        quantity=1,
        unit_price=quote["retail_amount"],
        total_price=quote["retail_amount"],
    )
    db.session.add(item)
    db.session.commit()

    return jsonify({
        "message": "Order created successfully. Proceed to payment authorization.",
        "order": order.to_dict(),
    }), 201


@orders_bp.route("/<int:order_id>", methods=["GET"])
@jwt_required()
def get_order(order_id: int):
    """Retrieve an order by ID, enforcing ownership restrictions."""
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    order = db.session.get(Order, order_id)

    if not order:
        return jsonify({"error": "Order not found"}), 404

    # Allow ADMIN, or order owner, or placing agent
    is_admin = user.has_role("ADMIN")
    is_owner = order.user_id == user.id
    is_agent = (order.agent_id and user.agent_profile and order.agent_id == user.agent_profile.id)

    if not (is_admin or is_owner or is_agent):
        return jsonify({"error": "Access denied: You do not have permission to view this order."}), 403

    return jsonify({"order": order.to_dict()}), 200


@orders_bp.route("", methods=["GET"])
@jwt_required()
def list_orders():
    """List paginated orders with filters. Customers only see their own orders."""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))
    status = request.args.get("status")
    order_type = request.args.get("order_type")

    query = Order.query

    # Enforce role restriction
    if not user.has_role("ADMIN"):
        if user.has_role("AGENT") and user.agent_profile:
            query = query.filter((Order.user_id == user.id) | (Order.agent_id == user.agent_profile.id))
        else:
            query = query.filter_by(user_id=user.id)

    if status:
        query = query.filter_by(status=status.upper())
    if order_type:
        query = query.filter_by(order_type=order_type.upper())

    orders_pagination = query.order_by(Order.id.desc()).paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "orders": [o.to_dict() for o in orders_pagination.items],
        "total": orders_pagination.total,
        "page": orders_pagination.page,
        "pages": orders_pagination.pages,
    }), 200
