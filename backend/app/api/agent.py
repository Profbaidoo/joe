"""
Agent POS and Cashier Operations Endpoints.
Allows authorized agents to process over-the-counter airtime, data sales, and view commissions.
"""

from decimal import Decimal
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.api.decorators import role_required
from app.models.user import User, Agent
from app.models.order import Order, OrderItem
from app.models.commission import Commission
from app.services.pricing_service import PricingService
from app.services.payment_service import PaymentService
from app.services.fulfillment_service import FulfillmentService
from app.utils.phone_validator import normalize_ghana_phone
from app.utils.security import generate_reference

agent_bp = Blueprint("agent", __name__, url_prefix="/api/agent")


@agent_bp.route("/pos-summary", methods=["GET"])
@role_required("AGENT", "ADMIN")
def get_pos_summary():
    """Retrieve cashier POS summary, wallet balance, and total earned commissions."""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    agent = user.agent_profile
    if not agent:
        return jsonify({"error": "No agent profile associated with this account."}), 404

    commissions = Commission.query.filter_by(agent_id=agent.id).all()
    total_earned = sum((c.amount for c in commissions), Decimal("0.0000"))

    orders = Order.query.filter_by(agent_id=agent.id, status="COMPLETED").all()
    total_sales = sum((o.total_amount for o in orders), Decimal("0.0000"))

    return jsonify({
        "agent": agent.to_dict(),
        "total_earned_commissions": float(total_earned),
        "total_sales_volume": float(total_sales),
        "completed_orders_count": len(orders),
    }), 200


@agent_bp.route("/commissions", methods=["GET"])
@role_required("AGENT", "ADMIN")
def get_agent_commissions():
    """List detailed breakdown of commissions earned by this agent."""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    agent = user.agent_profile
    if not agent:
        return jsonify({"error": "No agent profile found."}), 404

    commissions = Commission.query.filter_by(agent_id=agent.id).order_by(Commission.id.desc()).all()
    return jsonify({
        "commissions": [c.to_dict() for c in commissions],
        "commission_balance": float(agent.commission_balance),
    }), 200
