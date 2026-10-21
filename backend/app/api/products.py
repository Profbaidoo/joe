"""
Products, Networks, Data Bundle Plans, and Pricing Quote Endpoints.
"""

from decimal import Decimal
from flask import Blueprint, request, jsonify
from app.models.product import Network, Product, DataBundlePlan
from app.services.pricing_service import PricingService
from app.utils.phone_validator import normalize_ghana_phone

products_bp = Blueprint("products", __name__, url_prefix="/api")


@products_bp.route("/networks", methods=["GET"])
def get_networks():
    """List all active telecommunication networks in Ghana."""
    networks = Network.query.filter_by(is_active=True).all()
    return jsonify({
        "networks": [net.to_dict() for net in networks],
    }), 200


@products_bp.route("/products", methods=["GET"])
def get_products():
    """List products with optional category or network filter."""
    category = request.args.get("category")
    network_code = request.args.get("network")

    query = Product.query.filter_by(is_active=True)
    if category:
        query = query.filter_by(category=category.upper())
    if network_code:
        net = Network.query.filter_by(code=network_code.upper()).first()
        if net:
            query = query.filter_by(network_id=net.id)

    products = query.all()
    return jsonify({
        "products": [prod.to_dict() for prod in products],
    }), 200


@products_bp.route("/data-bundles", methods=["GET"])
def get_data_bundles():
    """List available data bundle plans, optionally filtered by network."""
    network_code = request.args.get("network")
    query = DataBundlePlan.query.filter_by(is_active=True)

    if network_code:
        net = Network.query.filter_by(code=network_code.upper()).first()
        if net:
            query = query.filter_by(network_id=net.id)

    bundles = query.all()
    return jsonify({
        "data_bundles": [bundle.to_dict() for bundle in bundles],
    }), 200


@products_bp.route("/pricing/quote", methods=["POST"])
def get_pricing_quote():
    """
    Get a transparent pricing quote including wholesale cost, retail total, platform fees,
    and agent commissions.
    """
    data = request.get_json() or {}
    order_type = data.get("order_type", "AIRTIME").upper()
    network_code = data.get("network_code", "MTN").upper()
    amount = data.get("amount")
    data_bundle_plan_id = data.get("data_bundle_plan_id")
    is_agent = data.get("is_agent", False)

    try:
        quote = PricingService.get_pricing_quote(
            order_type=order_type,
            network_code=network_code,
            amount=Decimal(str(amount)) if amount is not None else None,
            data_bundle_plan_id=int(data_bundle_plan_id) if data_bundle_plan_id else None,
            is_agent_order=bool(is_agent),
        )
        # Format response with float values for JSON serialization
        return jsonify({
            "retail_amount": float(quote["retail_amount"]),
            "wholesale_cost": float(quote["wholesale_cost"]),
            "fee_amount": float(quote["fee_amount"]),
            "total_payable": float(quote["total_payable"]),
            "agent_commission": float(quote["agent_commission"]),
            "estimated_profit": float(quote["estimated_profit"]),
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@products_bp.route("/networks/detect", methods=["POST"])
def detect_network():
    """Auto-detect network from Ghanaian mobile number."""
    data = request.get_json() or {}
    phone = data.get("phone", "")
    is_valid, local_phone, e164_phone, network = normalize_ghana_phone(phone)
    if not is_valid:
        return jsonify({"is_valid": False, "error": "Invalid Ghanaian mobile number"}), 400
    return jsonify({
        "is_valid": True,
        "local_phone": local_phone,
        "e164_phone": e164_phone,
        "network": network,
    }), 200
