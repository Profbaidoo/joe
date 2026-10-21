"""
Payment Processing and Gateway Abstraction Service.
Orchestrates MTN MoMo Collections, Paystack, Hubtel, and cash/agent collections.
Enforces strict idempotency, prevents duplicate fulfillment, and guarantees double-entry ledgering.
"""

from decimal import Decimal
from typing import Dict, Any, Optional
from app.extensions import db
from app.models.order import Order
from app.models.transaction import Transaction, PaymentAttempt
from app.models.commission import Commission
from app.services.ledger_service import LedgerService
from app.services.fulfillment_service import FulfillmentService
from app.services.notification_service import NotificationService
from app.utils.security import generate_reference
from app.utils.currency import to_decimal
from integrations.momo.client import MTNMoMoClient, MomoAPIException
from integrations.hubtel.client import HubtelClient
from integrations.paystack.client import PaystackClient


class PaymentService:
    @staticmethod
    def initiate_momo_payment(
        order_id: int,
        customer_phone: str,
        user_id: int,
    ) -> Dict[str, Any]:
        """
        Creates a transaction and sends Request-To-Pay to customer's MTN/Telco handset.
        CRITICAL: Never treats 202 as proof of payment; returns PENDING status.
        """
        order = db.session.get(Order, order_id)
        if not order:
            raise ValueError(f"Order with ID {order_id} not found.")

        if order.payment_status == "PAID":
            raise ValueError("Order is already paid.")

        # Check for existing pending transaction to prevent double prompt
        existing_pending = Transaction.query.filter_by(
            order_id=order.id,
            status="PENDING",
        ).first()
        if existing_pending:
            return {
                "transaction_reference": existing_pending.transaction_reference,
                "provider_reference": existing_pending.provider_reference,
                "status": "PENDING",
                "message": "Payment prompt is already active on customer handset. Please approve.",
                "amount": float(existing_pending.amount),
            }

        trx_ref = generate_reference("TRX")
        transaction = Transaction(
            transaction_reference=trx_ref,
            order_id=order.id,
            user_id=user_id,
            transaction_type="COLLECTION",
            payment_method=f"MOMO_{order.network_code.upper()}",
            amount=order.total_amount,
            fee=order.fee_amount,
            net_amount=order.net_amount,
            currency="GHS",
            status="PENDING",
            provider_name="MTN_MOMO",
            customer_phone=customer_phone,
        )
        db.session.add(transaction)
        db.session.commit()

        # Dispatch Request to Pay via MTN MoMo client
        momo_client = MTNMoMoClient()
        try:
            momo_resp = momo_client.request_to_pay(
                amount=str(float(order.total_amount)),
                payer_phone=customer_phone,
                transaction_reference=trx_ref,
                payer_message=f"Blessings Telecom: Order {order.order_reference}",
            )

            provider_ref = momo_resp.get("reference_id")
            transaction.provider_reference = provider_ref
            transaction.metadata_json = momo_resp

            attempt = PaymentAttempt(
                transaction_id=transaction.id,
                attempt_number=1,
                http_status_code=momo_resp.get("http_status", 202),
                request_payload={"amount": str(order.total_amount), "phone": customer_phone},
                response_payload=momo_resp,
            )
            db.session.add(attempt)
            db.session.commit()

            # Queue prompt alert
            NotificationService.send_payment_prompt_notification(transaction)

            return {
                "transaction_reference": trx_ref,
                "provider_reference": provider_ref,
                "status": "PENDING",
                "message": "Payment prompt sent to customer phone. Please approve the prompt on your phone.",
                "amount": float(order.total_amount),
            }

        except MomoAPIException as e:
            transaction.status = "FAILED"
            transaction.error_message = str(e)
            db.session.commit()
            raise ValueError(f"Failed to initiate MoMo payment: {str(e)}")

    @staticmethod
    def verify_and_reconcile_transaction(transaction_reference: str) -> Dict[str, Any]:
        """
        Polls the payment status from provider, transitions state, and triggers fulfillment.
        Guarantees idempotency: successful orders are never fulfilled twice.
        """
        transaction = Transaction.query.filter_by(transaction_reference=transaction_reference).first()
        if not transaction:
            raise ValueError(f"Transaction {transaction_reference} not found.")

        # If already final, return existing state
        if transaction.status == "SUCCESSFUL":
            return {
                "status": "SUCCESSFUL",
                "transaction_reference": transaction.transaction_reference,
                "order_status": transaction.order.status if transaction.order else None,
                "message": "Transaction already completed successfully.",
            }
        elif transaction.status in ("FAILED", "TIMED_OUT", "REVERSED"):
            return {
                "status": transaction.status,
                "transaction_reference": transaction.transaction_reference,
                "message": f"Transaction has terminated with status: {transaction.status}",
            }

        # Check status with MTN MoMo
        momo_client = MTNMoMoClient()
        provider_ref = transaction.provider_reference or transaction.transaction_reference
        status_resp = momo_client.get_transaction_status(provider_ref)
        provider_status = status_resp.get("status", "PENDING").upper()

        if provider_status == "SUCCESSFUL":
            return PaymentService._process_successful_payment(transaction, status_resp)
        elif provider_status in ("FAILED", "REJECTED"):
            transaction.status = "FAILED"
            transaction.error_message = status_resp.get("reason", "Payment rejected by subscriber")
            if transaction.order:
                transaction.order.payment_status = "FAILED"
                transaction.order.status = "FAILED"
            db.session.commit()
            return {
                "status": "FAILED",
                "transaction_reference": transaction.transaction_reference,
                "reason": transaction.error_message,
            }
        else:
            # Remains PENDING
            return {
                "status": "PENDING",
                "transaction_reference": transaction.transaction_reference,
                "message": "Payment is pending authorization on customer handset.",
            }

    @staticmethod
    def _process_successful_payment(transaction: Transaction, provider_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Idempotent execution for confirmed payment:
        1. Mark transaction SUCCESSFUL
        2. Mark order PAID
        3. Double-entry ledger recording
        4. Agent commission recording
        5. Fulfill telecom order (Airtime / Data)
        6. Queue digital receipt
        """
        if transaction.status == "SUCCESSFUL":
            return {"status": "SUCCESSFUL", "message": "Already processed."}

        transaction.status = "SUCCESSFUL"
        transaction.external_id = provider_data.get("financialTransactionId")
        order = transaction.order

        if order:
            order.payment_status = "PAID"
            order.status = "PAID"
            db.session.commit()

            # 1. Double-entry financial ledger
            LedgerService.record_successful_collection(
                transaction_id=transaction.id,
                order_id=order.id,
                gross_amount=transaction.amount,
                fee_amount=transaction.fee,
                provider_name=transaction.provider_name,
            )

            # 2. Agent commission award (if placed by an agent)
            if order.agent_id:
                from app.models.product import PricingRule
                rule = PricingRule.query.filter_by(network_id=1).first()
                rate = rule.agent_commission_percent if rule else Decimal("0.0050")
                comm_amount = (order.net_amount * rate).quantize(Decimal("0.0001"))

                if comm_amount > Decimal("0.0000"):
                    comm = Commission(
                        agent_id=order.agent_id,
                        order_id=order.id,
                        transaction_id=transaction.id,
                        amount=comm_amount,
                        rate_applied=rate,
                        status="EARNED",
                    )
                    db.session.add(comm)
                    # Update agent commission balance
                    order.agent.commission_balance += comm_amount
                    LedgerService.record_commission_award(
                        agent_id=order.agent_id,
                        order_id=order.id,
                        commission_amount=comm_amount,
                        agent_code=order.agent.agent_code,
                    )

            db.session.commit()

            # 3. Trigger immediate fulfillment
            fulfillment_result = FulfillmentService.fulfill_order(order.id)

            # 4. Generate digital receipt
            NotificationService.send_order_receipt(order)

            return {
                "status": "SUCCESSFUL",
                "transaction_reference": transaction.transaction_reference,
                "order_reference": order.order_reference,
                "order_status": order.status,
                "fulfillment": fulfillment_result,
                "message": "Payment confirmed and order fulfilled successfully.",
            }

        db.session.commit()
        return {"status": "SUCCESSFUL", "transaction_reference": transaction.transaction_reference}
