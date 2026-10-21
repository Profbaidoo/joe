"""
Append-Only Financial Ledger Service.
Maintains absolute financial integrity with double-entry style accounting records.
Prevents silent data alteration; forces compensating ledger entries.
"""

from decimal import Decimal
from typing import Optional, List
from sqlalchemy import func
from app.extensions import db
from app.models.ledger import FinancialLedger
from app.utils.currency import to_decimal
from app.utils.security import generate_reference


class LedgerService:
    @staticmethod
    def record_entry(
        account_type: str,
        entry_type: str,  # 'DEBIT' or 'CREDIT'
        amount: Decimal,
        description: str,
        transaction_id: Optional[int] = None,
        order_id: Optional[int] = None,
    ) -> FinancialLedger:
        """
        Appends an immutable entry to the financial ledger.
        Computes running balance for the specified account type.
        """
        dec_amount = to_decimal(amount)
        if dec_amount <= Decimal("0.0000"):
            raise ValueError("Ledger entry amount must be strictly greater than zero.")

        entry_type = entry_type.upper()
        if entry_type not in ("DEBIT", "CREDIT"):
            raise ValueError(f"Invalid ledger entry type: {entry_type}")

        # Compute previous running balance for this account
        latest_entry = (
            FinancialLedger.query.filter_by(account_type=account_type)
            .order_by(FinancialLedger.id.desc())
            .first()
        )
        previous_balance = latest_entry.balance_after if latest_entry else Decimal("0.0000")

        # Normal accounting convention:
        # Assets / Clearing / Expenses increase on DEBIT, decrease on CREDIT
        # Revenue / Wallets / Liabilities increase on CREDIT, decrease on DEBIT
        if account_type in ("PROVIDER_CLEARING", "COMMISSION_EXPENSE", "REVERSAL_SUSPENSE"):
            if entry_type == "DEBIT":
                new_balance = previous_balance + dec_amount
            else:
                new_balance = previous_balance - dec_amount
        else:
            # Wallets, Business Revenue, Fee Income
            if entry_type == "CREDIT":
                new_balance = previous_balance + dec_amount
            else:
                new_balance = previous_balance - dec_amount

        ledger_entry = FinancialLedger(
            entry_reference=generate_reference("LDG"),
            transaction_id=transaction_id,
            order_id=order_id,
            account_type=account_type,
            entry_type=entry_type,
            amount=dec_amount,
            balance_after=new_balance,
            description=description,
        )

        db.session.add(ledger_entry)
        return ledger_entry

    @staticmethod
    def record_successful_collection(
        transaction_id: int,
        order_id: int,
        gross_amount: Decimal,
        fee_amount: Decimal = Decimal("0.0000"),
        provider_name: str = "MTN_MOMO",
    ) -> List[FinancialLedger]:
        """
        Double-entry recording of customer payment collection:
        1. DEBIT: PROVIDER_CLEARING (Funds receivable from telco/aggregator)
        2. CREDIT: BUSINESS_REVENUE (Net revenue recognized)
        3. (Optional) CREDIT: FEE_INCOME (Platform convenience fee)
        """
        gross = to_decimal(gross_amount)
        fee = to_decimal(fee_amount)
        net_revenue = gross - fee

        entries = []
        # Debit Clearing
        entries.append(
            LedgerService.record_entry(
                account_type="PROVIDER_CLEARING",
                entry_type="DEBIT",
                amount=gross,
                description=f"Received via {provider_name} collection",
                transaction_id=transaction_id,
                order_id=order_id,
            )
        )

        # Credit Business Revenue
        entries.append(
            LedgerService.record_entry(
                account_type="BUSINESS_REVENUE",
                entry_type="CREDIT",
                amount=net_revenue,
                description=f"Revenue recognized for order {order_id}",
                transaction_id=transaction_id,
                order_id=order_id,
            )
        )

        # Credit Fee Income if applicable
        if fee > Decimal("0.0000"):
            entries.append(
                LedgerService.record_entry(
                    account_type="FEE_INCOME",
                    entry_type="CREDIT",
                    amount=fee,
                    description=f"Transaction processing fee on order {order_id}",
                    transaction_id=transaction_id,
                    order_id=order_id,
                )
            )

        return entries

    @staticmethod
    def record_commission_award(
        agent_id: int,
        order_id: int,
        commission_amount: Decimal,
        agent_code: str,
    ) -> List[FinancialLedger]:
        """
        Double-entry recording of agent commission:
        1. DEBIT: COMMISSION_EXPENSE
        2. CREDIT: AGENT_WALLET
        """
        amount = to_decimal(commission_amount)
        if amount <= Decimal("0.0000"):
            return []

        entries = [
            LedgerService.record_entry(
                account_type="COMMISSION_EXPENSE",
                entry_type="DEBIT",
                amount=amount,
                description=f"Commission incurred for agent {agent_code} on order {order_id}",
                order_id=order_id,
            ),
            LedgerService.record_entry(
                account_type="AGENT_WALLET",
                entry_type="CREDIT",
                amount=amount,
                description=f"Commission credited to agent {agent_code}",
                order_id=order_id,
            ),
        ]
        return entries

    @staticmethod
    def record_refund_entry(
        order_id: int,
        refund_amount: Decimal,
        reason: str,
        transaction_id: Optional[int] = None,
    ) -> List[FinancialLedger]:
        """
        Compensating entry for refund / reversed order:
        1. DEBIT: REVERSAL_SUSPENSE / BUSINESS_REVENUE
        2. CREDIT: PROVIDER_CLEARING or CUSTOMER_WALLET
        """
        amount = to_decimal(refund_amount)
        entries = [
            LedgerService.record_entry(
                account_type="BUSINESS_REVENUE",
                entry_type="DEBIT",
                amount=amount,
                description=f"Compensating debit: Refund on order {order_id}. Reason: {reason}",
                transaction_id=transaction_id,
                order_id=order_id,
            ),
            LedgerService.record_entry(
                account_type="PROVIDER_CLEARING",
                entry_type="CREDIT",
                amount=amount,
                description=f"Compensating credit: Refund payable on order {order_id}",
                transaction_id=transaction_id,
                order_id=order_id,
            ),
        ]
        return entries

    @staticmethod
    def get_account_balance(account_type: str) -> Decimal:
        """Returns the current running balance for any account type."""
        latest = (
            FinancialLedger.query.filter_by(account_type=account_type)
            .order_by(FinancialLedger.id.desc())
            .first()
        )
        return latest.balance_after if latest else Decimal("0.0000")
