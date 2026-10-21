"""
Append-Only Financial Ledger and Accounting Verification Tests.
"""

from decimal import Decimal
from app.services.ledger_service import LedgerService
from app.models.ledger import FinancialLedger


def test_append_only_ledger_collection_and_refund(app, db_session):
    with app.app_context():
        # Initial balance
        initial_revenue = LedgerService.get_account_balance("BUSINESS_REVENUE")

        # Record collection
        LedgerService.record_successful_collection(
            transaction_id=1,
            order_id=1,
            gross_amount=Decimal("50.0000"),
            fee_amount=Decimal("1.5000"),
            provider_name="MTN_MOMO",
        )

        rev_after_coll = LedgerService.get_account_balance("BUSINESS_REVENUE")
        assert rev_after_coll == initial_revenue + Decimal("48.5000")

        clearing_bal = LedgerService.get_account_balance("PROVIDER_CLEARING")
        assert clearing_bal == Decimal("50.0000")

        # Record compensating refund entry
        LedgerService.record_refund_entry(
            order_id=1,
            refund_amount=Decimal("50.0000"),
            reason="Customer request reversal",
        )

        rev_after_refund = LedgerService.get_account_balance("BUSINESS_REVENUE")
        assert rev_after_refund == rev_after_coll - Decimal("50.0000")

        # Verify entries are strictly appended
        all_entries = FinancialLedger.query.all()
        assert len(all_entries) >= 5
