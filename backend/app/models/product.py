"""
Product, Telecommunication Network, Data Bundle, and Pricing Models.
"""

from datetime import datetime, timezone
from decimal import Decimal
from app.extensions import db


class Network(db.Model):
    __tablename__ = "networks"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)  # MTN, TELECEL, AT
    name = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    airtime_supported = db.Column(db.Boolean, default=True, nullable=False)
    data_supported = db.Column(db.Boolean, default=True, nullable=False)
    bill_supported = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    products = db.relationship("Product", back_populates="network", lazy="dynamic")
    data_bundles = db.relationship("DataBundlePlan", back_populates="network", lazy="dynamic")

    def to_dict(self):
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "is_active": self.is_active,
            "airtime_supported": self.airtime_supported,
            "data_supported": self.data_supported,
            "bill_supported": self.bill_supported,
        }


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(30), nullable=False)  # AIRTIME, DATA_BUNDLE, MOMO_TRANSFER, MOMO_CASHOUT, UTILITY_BILL
    network_id = db.Column(db.Integer, db.ForeignKey("networks.id", ondelete="SET NULL"), nullable=True)
    wholesale_price = db.Column(db.Numeric(12, 4), default=Decimal("0.0000"), nullable=False)
    retail_price = db.Column(db.Numeric(12, 4), default=Decimal("0.0000"), nullable=False)
    min_amount = db.Column(db.Numeric(10, 2), default=Decimal("1.00"), nullable=False)
    max_amount = db.Column(db.Numeric(10, 2), default=Decimal("5000.00"), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    network = db.relationship("Network", back_populates="products")
    pricing_rules = db.relationship("PricingRule", back_populates="product", lazy="dynamic")

    def to_dict(self):
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "category": self.category,
            "network_code": self.network.code if self.network else None,
            "wholesale_price": float(self.wholesale_price),
            "retail_price": float(self.retail_price),
            "min_amount": float(self.min_amount),
            "max_amount": float(self.max_amount),
            "is_active": self.is_active,
        }


class DataBundlePlan(db.Model):
    __tablename__ = "data_bundle_plans"

    id = db.Column(db.Integer, primary_key=True)
    network_id = db.Column(db.Integer, db.ForeignKey("networks.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id", ondelete="SET NULL"), nullable=True)
    plan_code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    volume_mb = db.Column(db.Integer, nullable=False)
    validity_days = db.Column(db.Integer, default=30, nullable=False)  # 0 indicates Non-Expiry
    wholesale_price = db.Column(db.Numeric(12, 4), nullable=False)
    retail_price = db.Column(db.Numeric(12, 4), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    network = db.relationship("Network", back_populates="data_bundles")

    def to_dict(self):
        return {
            "id": self.id,
            "plan_code": self.plan_code,
            "name": self.name,
            "network_code": self.network.code if self.network else None,
            "volume_mb": self.volume_mb,
            "validity_days": self.validity_days,
            "wholesale_price": float(self.wholesale_price),
            "retail_price": float(self.retail_price),
            "is_active": self.is_active,
        }


class PricingRule(db.Model):
    __tablename__ = "pricing_rules"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id", ondelete="CASCADE"), nullable=True)
    network_id = db.Column(db.Integer, db.ForeignKey("networks.id", ondelete="CASCADE"), nullable=True)
    min_amount = db.Column(db.Numeric(10, 2), default=Decimal("0.00"), nullable=False)
    max_amount = db.Column(db.Numeric(10, 2), default=Decimal("100000.00"), nullable=False)
    fee_fixed = db.Column(db.Numeric(10, 2), default=Decimal("0.00"), nullable=False)
    fee_percent = db.Column(db.Numeric(5, 4), default=Decimal("0.0000"), nullable=False)  # e.g., 0.0100 for 1%
    agent_commission_percent = db.Column(db.Numeric(5, 4), default=Decimal("0.0050"), nullable=False)  # 0.5%
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    product = db.relationship("Product", back_populates="pricing_rules")

    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "network_id": self.network_id,
            "min_amount": float(self.min_amount),
            "max_amount": float(self.max_amount),
            "fee_fixed": float(self.fee_fixed),
            "fee_percent": float(self.fee_percent),
            "agent_commission_percent": float(self.agent_commission_percent),
        }
