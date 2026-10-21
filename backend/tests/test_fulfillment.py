"""
Airtime and Data Bundle Telecom Fulfillment Tests.
"""

from decimal import Decimal
import pytest
from app.models.order import Order
from app.services.fulfillment_service import FulfillmentService
from integrations.airtime.client import AirtimeDataClient, AirtimeProviderException


def test_airtime_client_phone_validation():
    client = AirtimeDataClient(provider="MOCK")
    # Valid MTN
    res = client.vend_airtime(
        recipient_phone="0241234567",
        network_code="MTN",
        amount_ghs=10.00,
        order_reference="ORD-TEST-1",
    )
    assert res["success"] is True
    assert res["status"] == "DELIVERED"

    # Mismatch network
    with pytest.raises(AirtimeProviderException) as excinfo:
        client.vend_airtime(
            recipient_phone="0201234567",  # Telecel
            network_code="MTN",
            amount_ghs=10.00,
            order_reference="ORD-TEST-2",
        )
    assert "Network mismatch" in str(excinfo.value)


def test_fulfillment_service_blocks_unpaid_order(app, db_session):
    with app.app_context():
        order = Order(
            order_reference="ORD-UNPAID-1",
            user_id=1,
            order_type="AIRTIME",
            recipient_phone="0241234567",
            network_code="MTN",
            total_amount=Decimal("10.0000"),
            net_amount=Decimal("10.0000"),
            status="PENDING",
            payment_status="UNPAID",
        )
        from app.extensions import db
        db.session.add(order)
        db.session.commit()

        with pytest.raises(ValueError) as excinfo:
            FulfillmentService.fulfill_order(order.id)
        assert "Payment status is UNPAID" in str(excinfo.value)
