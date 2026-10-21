"""
Append-Only Financial Ledger Model.
Enforces double-entry style accounting principles for Ghanaian financial movements.
Direct edits/deletions on historical ledger records are strictly forbidden.
Compensating entries must be recorded for reversals, refunds, or adjustments.
"""

from datetime import datetime, timezone
from decimal import Decimal
from app.extensions import db
from app.models.types import BigIntPK


class FinancialLedger(db.Model):
    __tablename__ = "financial_ledger"
    __table_args__ = {"sqlite_autoincrement": True}

    id = BigIntPK()
    entry_reference = db.Column(db.String(64), unique=True, nullable=False, index=True)
    transaction_id = db.Column(db.BigInteger, db.ForeignKey("transactions.id", ondelete="SET NULL"), nullable=True)
    order_id = db.Column(db.BigInteger, db.ForeignKey("orders.id", ondelete="SET NULL"), nullable=True)
    account_type = db.Column(db.String(50), nullable=False, index=True)
    # Account types:
    # 'CUSTOMER_WALLET'
    # 'AGENT_WALLET'
    # 'BUSINESS_REVENUE'
    # 'PROVIDER_CLEARING'
    # 'FEE_INCOME'
    # 'COMMISSION_EXPENSE'
    # 'REVERSAL_SUSPENSE'
    entry_type = db.Column(db.String(10), nullable=False)  # 'DEBIT' or 'CREDIT'
    amount = db.Column(db.Numeric(12, 4), nullable=False)
    balance_after = db.Column(db.Numeric(12, 4), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    transaction = db.relationship("Transaction", back_populates="ledger_entries")
    order = db.relationship("Order")

    def to_dict(self):
        return {
            "id": self.id,
            "entry_reference": self.entry_reference,
            "transaction_id": self.transaction_id,
            "order_id": self.order_id,
            "account_type": self.account_type,
            "entry_type": self.entry_type,
            "amount": float(self.amount),
            "balance_after": float(self.balance_after),
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
