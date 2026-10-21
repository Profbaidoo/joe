"""
Transaction, Payment Attempt, and Webhook Callback Models.
"""

from datetime import datetime, timezone
from decimal import Decimal
from app.extensions import db
from app.models.types import BigIntPK


class Transaction(db.Model):
    __tablename__ = "transactions"
    __table_args__ = {"sqlite_autoincrement": True}

    id = BigIntPK()
    transaction_reference = db.Column(db.String(64), unique=True, nullable=False, index=True)
    order_id = db.Column(db.BigInteger, db.ForeignKey("orders.id", ondelete="SET NULL"), nullable=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey("users.id"), nullable=False)
    transaction_type = db.Column(db.String(30), nullable=False)  # COLLECTION, DISBURSEMENT, TRANSFER, COMMISSION_PAYOUT, REFUND
    payment_method = db.Column(db.String(30), nullable=False)  # MOMO_MTN, MOMO_TELECEL, MOMO_AT, PAYSTACK_CARD, CASH_AGENT, WALLET
    amount = db.Column(db.Numeric(12, 4), nullable=False)
    fee = db.Column(db.Numeric(12, 4), default=Decimal("0.0000"), nullable=False)
    net_amount = db.Column(db.Numeric(12, 4), nullable=False)
    currency = db.Column(db.String(5), default="GHS", nullable=False)
    status = db.Column(db.String(20), default="PENDING", nullable=False, index=True)  # PENDING, PROCESSING, SUCCESSFUL, FAILED, TIMED_OUT, REVERSED
    provider_name = db.Column(db.String(50), nullable=False)  # MTN_MOMO, HUBTEL, PAYSTACK, INTERNAL
    provider_reference = db.Column(db.String(100), nullable=True, index=True)
    external_id = db.Column(db.String(100), nullable=True)
    customer_phone = db.Column(db.String(20), nullable=False)
    error_message = db.Column(db.String(255), nullable=True)
    metadata_json = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    order = db.relationship("Order", back_populates="transactions")
    user = db.relationship("User", back_populates="transactions")
    attempts = db.relationship("PaymentAttempt", back_populates="transaction", cascade="all, delete-orphan")
    ledger_entries = db.relationship("FinancialLedger", back_populates="transaction")

    def to_dict(self):
        return {
            "id": self.id,
            "transaction_reference": self.transaction_reference,
            "order_id": self.order_id,
            "user_id": self.user_id,
            "transaction_type": self.transaction_type,
            "payment_method": self.payment_method,
            "amount": float(self.amount),
            "fee": float(self.fee),
            "net_amount": float(self.net_amount),
            "currency": self.currency,
            "status": self.status,
            "provider_name": self.provider_name,
            "provider_reference": self.provider_reference,
            "customer_phone": self.customer_phone,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class PaymentAttempt(db.Model):
    __tablename__ = "payment_attempts"
    __table_args__ = {"sqlite_autoincrement": True}

    id = BigIntPK()
    transaction_id = db.Column(db.BigInteger, db.ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False)
    attempt_number = db.Column(db.Integer, default=1, nullable=False)
    http_status_code = db.Column(db.Integer, nullable=True)
    request_headers = db.Column(db.JSON, nullable=True)
    request_payload = db.Column(db.JSON, nullable=True)
    response_payload = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    transaction = db.relationship("Transaction", back_populates="attempts")


class ProviderCallback(db.Model):
    __tablename__ = "provider_callbacks"
    __table_args__ = {"sqlite_autoincrement": True}

    id = BigIntPK()
    provider_name = db.Column(db.String(50), nullable=False)
    event_type = db.Column(db.String(100), nullable=False)
    provider_reference = db.Column(db.String(100), nullable=True, index=True)
    payload_json = db.Column(db.JSON, nullable=False)
    signature = db.Column(db.String(255), nullable=True)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    processed = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
