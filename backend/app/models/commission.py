"""
Agent Commission and Refund Models.
"""

from datetime import datetime, timezone
from decimal import Decimal
from app.extensions import db
from app.models.types import BigIntPK


class Commission(db.Model):
    __tablename__ = "commissions"
    __table_args__ = {"sqlite_autoincrement": True}

    id = BigIntPK()
    agent_id = db.Column(db.BigInteger, db.ForeignKey("agents.id"), nullable=False)
    order_id = db.Column(db.BigInteger, db.ForeignKey("orders.id"), nullable=False)
    transaction_id = db.Column(db.BigInteger, db.ForeignKey("transactions.id", ondelete="SET NULL"), nullable=True)
    amount = db.Column(db.Numeric(12, 4), nullable=False)
    rate_applied = db.Column(db.Numeric(5, 4), nullable=False)
    status = db.Column(db.String(20), default="EARNED", nullable=False)  # EARNED, PAID, CLAWED_BACK
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    agent = db.relationship("Agent", back_populates="commissions")
    order = db.relationship("Order", back_populates="commissions")
    transaction = db.relationship("Transaction")

    def to_dict(self):
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "order_id": self.order_id,
            "order_reference": self.order.order_reference if self.order else None,
            "amount": float(self.amount),
            "rate_applied": float(self.rate_applied),
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Refund(db.Model):
    __tablename__ = "refunds"
    __table_args__ = {"sqlite_autoincrement": True}

    id = BigIntPK()
    order_id = db.Column(db.BigInteger, db.ForeignKey("orders.id"), nullable=False)
    original_transaction_id = db.Column(db.BigInteger, db.ForeignKey("transactions.id"), nullable=False)
    refund_transaction_id = db.Column(db.BigInteger, db.ForeignKey("transactions.id", ondelete="SET NULL"), nullable=True)
    amount = db.Column(db.Numeric(12, 4), nullable=False)
    reason = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), default="REQUESTED", nullable=False)  # REQUESTED, APPROVED, PROCESSED, REJECTED
    approved_by = db.Column(db.BigInteger, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    order = db.relationship("Order", back_populates="refunds")
    original_transaction = db.relationship("Transaction", foreign_keys=[original_transaction_id])
    refund_transaction = db.relationship("Transaction", foreign_keys=[refund_transaction_id])
    approver = db.relationship("User", foreign_keys=[approved_by])

    def to_dict(self):
        return {
            "id": self.id,
            "order_id": self.order_id,
            "amount": float(self.amount),
            "reason": self.reason,
            "status": self.status,
            "approved_by": self.approver.username if self.approver else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
