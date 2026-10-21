"""
Background Payment Reconciliation and Retry Worker.
Safely checks pending MoMo payments, retries fulfillment where appropriate,
and transitions timed-out requests.
"""

import time
import logging
from datetime import datetime, timezone, timedelta
from app.extensions import db
from app.models.transaction import Transaction
from app.services.payment_service import PaymentService

logger = logging.getLogger(__name__)


def reconcile_pending_transactions(app):
    """
    Executes a single reconciliation sweep across pending payment transactions.
    """
    with app.app_context():
        # Look for pending transactions created more than 15 seconds ago
        cutoff = datetime.now(timezone.utc) - timedelta(seconds=15)
        pending_transactions = (
            Transaction.query.filter(
                Transaction.status == "PENDING",
                Transaction.created_at <= cutoff
            )
            .limit(20)
            .all()
        )

        for txn in pending_transactions:
            try:
                logger.info(f"Checking pending transaction: {txn.transaction_reference}")
                result = PaymentService.verify_and_reconcile_transaction(txn.transaction_reference)
                logger.info(f"Reconciled {txn.transaction_reference}: {result.get('status')}")
            except Exception as e:
                logger.error(f"Error reconciling {txn.transaction_reference}: {str(e)}")

        # Timeout transactions pending for more than 15 minutes
        timeout_cutoff = datetime.now(timezone.utc) - timedelta(minutes=15)
        stale_transactions = (
            Transaction.query.filter(
                Transaction.status == "PENDING",
                Transaction.created_at <= timeout_cutoff
            )
            .all()
        )
        for stale in stale_transactions:
            stale.status = "TIMED_OUT"
            stale.error_message = "Payment prompt expired: Customer did not approve on mobile money handset within 15 minutes."
            if stale.order:
                stale.order.status = "FAILED"
                stale.order.payment_status = "FAILED"
            db.session.commit()
            logger.warning(f"Transaction {stale.transaction_reference} timed out.")


def start_background_worker(app, interval_seconds: int = 30):
    """Starts the reconciliation loop in a non-blocking daemon thread."""
    import threading

    def loop():
        logger.info(f"Starting Background Reconciliation Worker (Interval: {interval_seconds}s)")
        while True:
            try:
                reconcile_pending_transactions(app)
            except Exception as e:
                logger.error(f"Reconciliation worker loop error: {e}")
            time.sleep(interval_seconds)

    thread = threading.Thread(target=loop, daemon=True, name="PaymentReconciler")
    thread.start()
    return thread
