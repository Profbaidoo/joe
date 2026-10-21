"""
Order and OrderItem Models.
Represents purchase intent, network recipient, and fulfillment lifecycle.
"""

from datetime import datetime, timezone
from decimal import Decimal
from app.extensions import db
from app.models.types import BigIntPK


class Order(db.Model):
    __tablename__ = "orders"
    __table_args__ = {"sqlite_autoincrement": True}

    id = BigIntPK()
    order_reference = db.Column(db.String(64), unique=True, nullable=False, index=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey("users.id"), nullable=False, index=True)
    agent_id = db.Column(db.BigInteger, db.ForeignKey("agents.id"), nullable=True)
    order_type = db.Column(db.String(30), nullable=False)  # AIRTIME, DATA_BUNDLE, MOMO_TRANSFER, MOMO_CASHOUT, UTILITY_BILL
    recipient_phone = db.Column(db.String(20), nullable=False)
    network_code = db.Column(db.String(20), nullable=False)  # MTN, TELECEL, AT
    total_amount = db.Column(db.Numeric(12, 4), nullable=False)
    fee_amount = db.Column(db.Numeric(12, 4), default=Decimal("0.0000"), nullable=False)
    net_amount = db.Column(db.Numeric(12, 4), nullable=False)
    status = db.Column(db.String(20), default="PENDING", nullable=False, index=True)  # PENDING, PAID, PROCESSING, COMPLETED, FAILED, CANCELLED, REFUNDED
    payment_status = db.Column(db.String(20), default="UNPAID", nullable=False)  # UNPAID, PENDING, PAID, FAILED, REFUNDED
    fulfillment_status = db.Column(db.String(20), default="UNFULFILLED", nullable=False)  # UNFULFILLED, QUEUED, FULFILLED, FAILED, NOT_APPLICABLE
    fulfillment_provider = db.Column(db.String(50), nullable=True)
    fulfillment_reference = db.Column(db.String(100), nullable=True)
    failure_reason = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = db.relationship("User", back_populates="orders")
    agent = db.relationship("Agent", back_populates="orders")
    items = db.relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    transactions = db.relationship("Transaction", back_populates="order", lazy="dynamic")
    commissions = db.relationship("Commission", back_populates="order", lazy="dynamic")
    refunds = db.relationship("Refund", back_populates="order", lazy="dynamic")

    def to_dict(self):
        return {
            "id": self.id,
            "order_reference": self.order_reference,
            "user_id": self.user_id,
            "agent_id": self.agent_id,
            "order_type": self.order_type,
            "recipient_phone": self.recipient_phone,
            "network_code": self.network_code,
            "total_amount": float(self.total_amount),
            "fee_amount": float(self.fee_amount),
            "net_amount": float(self.net_amount),
            "status": self.status,
            "payment_status": self.payment_status,
            "fulfillment_status": self.fulfillment_status,
            "fulfillment_provider": self.fulfillment_provider,
            "fulfillment_reference": self.fulfillment_reference,
            "failure_reason": self.failure_reason,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "items": [item.to_dict() for item in self.items],
        }


class OrderItem(db.Model):
    __tablename__ = "order_items"
    __table_args__ = {"sqlite_autoincrement": True}

    id = BigIntPK()
    order_id = db.Column(db.BigInteger, db.ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=True)
    data_bundle_plan_id = db.Column(db.Integer, db.ForeignKey("data_bundle_plans.id"), nullable=True)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    unit_price = db.Column(db.Numeric(12, 4), nullable=False)
    total_price = db.Column(db.Numeric(12, 4), nullable=False)

    order = db.relationship("Order", back_populates="items")
    product = db.relationship("Product")
    data_bundle_plan = db.relationship("DataBundlePlan")

    def to_dict(self):
        return {
            "id": self.id,
            "product_name": self.product.name if self.product else (self.data_bundle_plan.name if self.data_bundle_plan else "Custom Item"),
            "data_bundle_plan_code": self.data_bundle_plan.plan_code if self.data_bundle_plan else None,
            "quantity": self.quantity,
            "unit_price": float(self.unit_price),
            "total_price": float(self.total_price),
        }
