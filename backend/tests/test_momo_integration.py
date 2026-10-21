"""
MTN Mobile Money Integration, Webhook, and Reconciliation Tests.
"""

from app.extensions import db
from app.models.transaction import Transaction
from app.models.order import Order


def test_momo_request_to_pay_creates_pending_transaction(client, customer_headers, db_session):
    # 1. Create order
    order_resp = client.post("/api/orders", json={
        "order_type": "AIRTIME",
        "recipient_phone": "0241234567",
        "network_code": "MTN",
        "amount": 10.00,
    }, headers=customer_headers)
    assert order_resp.status_code == 201
    order_id = order_resp.get_json()["order"]["id"]

    # 2. Initiate MoMo Request-to-Pay
    pay_resp = client.post("/api/payments/momo/request", json={
        "order_id": order_id,
        "momo_phone": "0241234567",
    }, headers=customer_headers)

    assert pay_resp.status_code == 200
    data = pay_resp.get_json()
    assert data["status"] == "PENDING"
    assert "prompt sent to customer phone" in data["message"].lower()

    # 3. Verify in DB
    trx = Transaction.query.filter_by(transaction_reference=data["transaction_reference"]).first()
    assert trx is not None
    assert trx.status == "PENDING"
    assert trx.order_id == order_id


def test_momo_status_check_reconciles_and_fulfills(client, customer_headers, db_session):
    # 1. Create order
    order_resp = client.post("/api/orders", json={
        "order_type": "AIRTIME",
        "recipient_phone": "0241234567",
        "network_code": "MTN",
        "amount": 15.00,
    }, headers=customer_headers)
    order_id = order_resp.get_json()["order"]["id"]

    # 2. Request MoMo
    pay_resp = client.post("/api/payments/momo/request", json={
        "order_id": order_id,
        "momo_phone": "0241234567",
    }, headers=customer_headers)
    trx_ref = pay_resp.get_json()["transaction_reference"]

    # 3. Reconcile transaction status (in sandbox mock, simulates successful verification)
    status_resp = client.get(f"/api/payments/momo/status/{trx_ref}", headers=customer_headers)
    assert status_resp.status_code == 200
    data = status_resp.get_json()
    assert data["status"] == "SUCCESSFUL"

    # 4. Check Order status has transitioned to COMPLETED and FULFILLED
    order = db.session.get(Order, order_id)
    assert order.payment_status == "PAID"
    assert order.status == "COMPLETED"
    assert order.fulfillment_status == "FULFILLED"


def test_webhook_idempotency(client, customer_headers, db_session):
    # 1. Create order and initiate
    order_resp = client.post("/api/orders", json={
        "order_type": "AIRTIME",
        "recipient_phone": "0241234567",
        "network_code": "MTN",
        "amount": 5.00,
    }, headers=customer_headers)
    order_id = order_resp.get_json()["order"]["id"]
    pay_resp = client.post("/api/payments/momo/request", json={
        "order_id": order_id,
        "momo_phone": "0241234567",
    }, headers=customer_headers)
    trx_ref = pay_resp.get_json()["transaction_reference"]

    # 2. First Webhook
    wb_resp1 = client.post("/api/webhooks/momo", json={
        "externalId": trx_ref,
        "status": "SUCCESSFUL",
        "amount": "5.00",
    })
    assert wb_resp1.status_code == 200

    # 3. Duplicate Webhook replay should not error or double-fulfill
    wb_resp2 = client.post("/api/webhooks/momo", json={
        "externalId": trx_ref,
        "status": "SUCCESSFUL",
        "amount": "5.00",
    })
    assert wb_resp2.status_code == 200

    order = db.session.get(Order, order_id)
    assert order.status == "COMPLETED"
