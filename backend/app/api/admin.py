"""
Administrative Financial Dashboard, Reporting, and Configuration Endpoints.
Guarded by strict @role_required('ADMIN') permission check.
"""

from datetime import datetime, date, timedelta, timezone
from decimal import Decimal
import io
import csv
from flask import Blueprint, request, jsonify, Response
from sqlalchemy import func
from app.extensions import db
from app.api.decorators import role_required
from app.models.order import Order
from app.models.transaction import Transaction
from app.models.commission import Commission
from app.models.ledger import FinancialLedger
from app.models.user import User, Agent, Role
from app.models.product import Product, DataBundlePlan, PricingRule
from app.models.audit import AuditLog, IntegrationSetting
from app.services.ledger_service import LedgerService
from app.utils.phone_validator import normalize_ghana_phone
from app.utils.security import generate_agent_code

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


@admin_bp.route("/dashboard", methods=["GET"])
@role_required("ADMIN")
def get_dashboard_kpis():
    """
    Returns high-fidelity financial KPIs and operational metrics.
    Clearly distinguishes customer funds, gross volume, and real profit.
    Excludes unfulfilled or pending transactions from completed sales figures.
    """
    today_start = datetime.combine(date.today(), datetime.min.time())

    # 1. Today's Completed Sales & Volume
    today_completed_orders = Order.query.filter(
        Order.created_at >= today_start,
        Order.status == "COMPLETED"
    ).all()

    today_sales_volume = sum((o.total_amount for o in today_completed_orders), Decimal("0.0000"))
    today_order_count = len(today_completed_orders)

    # 2. Breakdown by Category
    airtime_orders = [o for o in today_completed_orders if o.order_type == "AIRTIME"]
    data_orders = [o for o in today_completed_orders if o.order_type == "DATA_BUNDLE"]
    bill_orders = [o for o in today_completed_orders if o.order_type == "UTILITY_BILL"]

    today_airtime_sales = sum((o.total_amount for o in airtime_orders), Decimal("0.0000"))
    today_data_sales = sum((o.total_amount for o in data_orders), Decimal("0.0000"))
    today_bill_sales = sum((o.total_amount for o in bill_orders), Decimal("0.0000"))

    # 3. Transaction Counts
    successful_count = Transaction.query.filter(Transaction.created_at >= today_start, Transaction.status == "SUCCESSFUL").count()
    pending_count = Transaction.query.filter(Transaction.created_at >= today_start, Transaction.status == "PENDING").count()
    failed_count = Transaction.query.filter(Transaction.created_at >= today_start, Transaction.status == "FAILED").count()

    # 4. Total Collections & Payouts (All Time or Ledger Based)
    provider_clearing_balance = LedgerService.get_account_balance("PROVIDER_CLEARING")
    business_revenue_balance = LedgerService.get_account_balance("BUSINESS_REVENUE")
    total_fee_income = LedgerService.get_account_balance("FEE_INCOME")
    total_commission_expense = LedgerService.get_account_balance("COMMISSION_EXPENSE")

    # 5. Estimated Real Profit = (Fee Income + Margin between Retail and Wholesale - Commissions)
    estimated_net_profit = (business_revenue_balance * Decimal("0.0250")) + total_fee_income - total_commission_expense

    # 6. Active Agent Count
    active_agent_count = Agent.query.filter_by(status="ACTIVE").count()

    return jsonify({
        "today_metrics": {
            "sales_volume": float(today_sales_volume),
            "order_count": today_order_count,
            "airtime_sales": float(today_airtime_sales),
            "data_sales": float(today_data_sales),
            "bill_sales": float(today_bill_sales),
            "successful_transactions": successful_count,
            "pending_transactions": pending_count,
            "failed_transactions": failed_count,
        },
        "financial_ledger_summary": {
            "provider_clearing_balance": float(provider_clearing_balance),
            "business_revenue_accumulated": float(business_revenue_balance),
            "fee_income": float(total_fee_income),
            "commission_expense": float(total_commission_expense),
            "estimated_net_profit": float(max(estimated_net_profit, Decimal("0.0000"))),
        },
        "business_status": {
            "active_agents": active_agent_count,
            "currency": "GHS",
            "timezone": "Africa/Accra",
            "provider_alert": None if provider_clearing_balance >= Decimal("0.00") else "Clearing account negative anomaly",
        }
    }), 200


@admin_bp.route("/reports/export-csv", methods=["GET"])
@role_required("ADMIN")
def export_transactions_csv():
    """Generates downloadable CSV report of transaction records."""
    transactions = Transaction.query.order_by(Transaction.id.desc()).limit(1000).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Transaction Reference", "Order Reference", "Customer Phone",
        "Type", "Method", "Amount (GHS)", "Fee (GHS)", "Status",
        "Provider", "External ID", "Created At"
    ])

    for t in transactions:
        writer.writerow([
            t.transaction_reference,
            t.order.order_reference if t.order else "N/A",
            t.customer_phone,
            t.transaction_type,
            t.payment_method,
            f"{t.amount:.2f}",
            f"{t.fee:.2f}",
            t.status,
            t.provider_name,
            t.external_id or "N/A",
            t.created_at.strftime("%Y-%m-%d %H:%M:%S") if t.created_at else "",
        ])

    csv_data = output.getvalue()
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename=ghana_fintech_transactions_{date.today()}.csv"}
    )


@admin_bp.route("/pricing/<int:product_id>", methods=["PATCH"])
@role_required("ADMIN")
def update_pricing(product_id: int):
    """Admin endpoint to adjust selling prices and profit margins."""
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    data = request.get_json() or {}
    if "wholesale_price" in data:
        product.wholesale_price = Decimal(str(data["wholesale_price"]))
    if "retail_price" in data:
        product.retail_price = Decimal(str(data["retail_price"]))
    if "is_active" in data:
        product.is_active = bool(data["is_active"])

    db.session.commit()
    return jsonify({
        "message": "Product pricing updated successfully.",
        "product": product.to_dict(),
    }), 200


@admin_bp.route("/agents", methods=["GET"])
@role_required("ADMIN")
def list_agents():
    """List all registered business agents and their commission balances."""
    agents = Agent.query.all()
    return jsonify({
        "agents": [a.to_dict() for a in agents],
    }), 200


@admin_bp.route("/agents", methods=["POST"])
@role_required("ADMIN")
def create_agent():
    """Create a new cashier / retail agent."""
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    email = data.get("email", "").strip().lower()
    raw_phone = data.get("phone_number", "").strip()
    password = data.get("password", "")
    business_name = data.get("business_name", "").strip()
    location = data.get("location", "").strip()

    if not all([username, email, raw_phone, password, business_name, location]):
        return jsonify({"error": "All agent fields are required."}), 400

    is_valid, local_phone, _, _ = normalize_ghana_phone(raw_phone)
    if not is_valid:
        return jsonify({"error": "Invalid Ghanaian mobile number"}), 400

    agent_role = Role.query.filter_by(name="AGENT").first()
    if not agent_role:
        agent_role = Role(name="AGENT", description="POS Cashier / Agent")
        db.session.add(agent_role)
        db.session.commit()

    user = User(
        username=username,
        email=email,
        phone_number=local_phone,
        role_id=agent_role.id,
        is_active=True,
    )
    user.set_password(password)
    db.session.add(user)
    db.session.flush()

    agent = Agent(
        user_id=user.id,
        agent_code=generate_agent_code(),
        business_name=business_name,
        location=location,
    )
    db.session.add(agent)
    db.session.commit()

    return jsonify({
        "message": "Agent created successfully.",
        "agent": agent.to_dict(),
        "user": user.to_dict(),
    }), 201


@admin_bp.route("/audit-logs", methods=["GET"])
@role_required("ADMIN")
def get_audit_logs():
    """Retrieve security audit logs for sensitive actions."""
    logs = AuditLog.query.order_by(AuditLog.id.desc()).limit(100).all()
    return jsonify({
        "audit_logs": [log.to_dict() for log in logs],
    }), 200
