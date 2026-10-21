"""
Pricing Engine, Commission Rules, and Order Lifecycle Tests.
"""

def test_pricing_quote_airtime(client, db_session):
    resp = client.post("/api/pricing/quote", json={
        "order_type": "AIRTIME",
        "network_code": "MTN",
        "amount": 20.00,
        "is_agent": True,
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["retail_amount"] == 20.00
    assert data["wholesale_cost"] < 20.00  # Wholesale discount applied
    assert data["agent_commission"] > 0.00  # Commission awarded


def test_order_creation_success(client, customer_headers, db_session):
    payload = {
        "order_type": "AIRTIME",
        "recipient_phone": "0241234567",
        "network_code": "MTN",
        "amount": 10.00,
    }
    resp = client.post("/api/orders", json=payload, headers=customer_headers)
    assert resp.status_code == 201
    data = resp.get_json()
    assert "order" in data
    assert data["order"]["status"] == "PENDING"
    assert data["order"]["payment_status"] == "UNPAID"
    assert data["order"]["network_code"] == "MTN"


def test_order_network_phone_mismatch_rejected(client, customer_headers, db_session):
    # 020 is Telecel, but user selected MTN
    payload = {
        "order_type": "AIRTIME",
        "recipient_phone": "0201234567",
        "network_code": "MTN",
        "amount": 10.00,
    }
    resp = client.post("/api/orders", json=payload, headers=customer_headers)
    assert resp.status_code == 400
    assert "Network mismatch" in resp.get_json()["error"]
