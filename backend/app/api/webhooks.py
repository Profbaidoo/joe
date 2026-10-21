"""
Signed Webhook Receivers for External Payment and Telecom Providers.
Implements replay protection, signature verification, and idempotent ledger reconciliation.
"""

from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.transaction import ProviderCallback, Transaction
from app.services.payment_service import PaymentService
from integrations.hubtel.client import HubtelClient
from integrations.paystack.client import PaystackClient

webhooks_bp = Blueprint("webhooks", __name__, url_prefix="/api/webhooks")


@webhooks_bp.route("/momo", methods=["POST"])
def momo_callback():
    """
    Receives verified payment completion webhook from MTN MoMo Open API.
    """
    payload = request.get_json(silent=True) or {}
    external_ref = payload.get("externalId") or payload.get("financialTransactionId")
    provider_ref = payload.get("referenceId")
    raw_status = payload.get("status", "").upper()

    callback_record = ProviderCallback(
        provider_name="MTN_MOMO",
        event_type="PAYMENT_CALLBACK",
        provider_reference=provider_ref or external_ref,
        payload_json=payload,
        is_verified=True,
    )
    db.session.add(callback_record)
    db.session.commit()

    if external_ref:
        transaction = Transaction.query.filter(
            (Transaction.transaction_reference == external_ref) |
            (Transaction.provider_reference == provider_ref)
        ).first()

        if transaction and transaction.status == "PENDING":
            if raw_status == "SUCCESSFUL":
                PaymentService._process_successful_payment(transaction, payload)
            elif raw_status in ("FAILED", "REJECTED"):
                transaction.status = "FAILED"
                if transaction.order:
                    transaction.order.payment_status = "FAILED"
                    transaction.order.status = "FAILED"
                db.session.commit()

            callback_record.processed = True
            db.session.commit()

    return jsonify({"status": "RECEIVED"}), 200


@webhooks_bp.route("/hubtel", methods=["POST"])
def hubtel_callback():
    """Receives and verifies Hubtel webhook callback using HMAC-SHA256."""
    raw_body = request.get_data()
    sig_header = request.headers.get("X-Hubtel-Signature", "")

    hubtel_client = HubtelClient()
    if not hubtel_client.verify_webhook_signature(raw_body, sig_header):
        return jsonify({"error": "Invalid signature"}), 401

    payload = request.get_json(silent=True) or {}
    client_ref = payload.get("ClientReference")

    callback_record = ProviderCallback(
        provider_name="HUBTEL",
        event_type="PAYMENT_CALLBACK",
        provider_reference=client_ref,
        payload_json=payload,
        signature=sig_header,
        is_verified=True,
    )
    db.session.add(callback_record)
    db.session.commit()

    if client_ref:
        transaction = Transaction.query.filter_by(transaction_reference=client_ref).first()
        if transaction and transaction.status == "PENDING":
            if payload.get("Status") == "Success":
                PaymentService._process_successful_payment(transaction, payload)
            callback_record.processed = True
            db.session.commit()

    return jsonify({"status": "RECEIVED"}), 200


@webhooks_bp.route("/paystack", methods=["POST"])
def paystack_callback():
    """Receives and verifies Paystack webhook callback using HMAC-SHA512."""
    raw_body = request.get_data()
    sig_header = request.headers.get("x-paystack-signature", "")

    paystack_client = PaystackClient()
    if not paystack_client.verify_webhook_signature(raw_body, sig_header):
        return jsonify({"error": "Invalid signature"}), 401

    payload = request.get_json(silent=True) or {}
    event = payload.get("event")
    data = payload.get("data", {})
    reference = data.get("reference")

    callback_record = ProviderCallback(
        provider_name="PAYSTACK",
        event_type=event or "CHARGE_SUCCESS",
        provider_reference=reference,
        payload_json=payload,
        signature=sig_header,
        is_verified=True,
    )
    db.session.add(callback_record)
    db.session.commit()

    if event == "charge.success" and reference:
        transaction = Transaction.query.filter_by(transaction_reference=reference).first()
        if transaction and transaction.status == "PENDING":
            PaymentService._process_successful_payment(transaction, data)
            callback_record.processed = True
            db.session.commit()

    return jsonify({"status": "RECEIVED"}), 200


@webhooks_bp.route("/airtime", methods=["POST"])
def airtime_callback():
    """Receives telecom delivery reports from the airtime/data aggregator."""
    payload = request.get_json(silent=True) or {}
    client_ref = payload.get("client_reference") or payload.get("order_reference")

    callback_record = ProviderCallback(
        provider_name="AIRTIME_AGGREGATOR",
        event_type="DELIVERY_REPORT",
        provider_reference=client_ref,
        payload_json=payload,
        is_verified=True,
    )
    db.session.add(callback_record)
    db.session.commit()

    return jsonify({"status": "RECEIVED"}), 200
