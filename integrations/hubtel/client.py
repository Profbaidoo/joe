"""
Hubtel Ghana Aggregator API Client.
Supports Mobile Money Collections, Airtime/Data dispatch, and ECG Utility bills.
"""

import os
import base64
import requests
from typing import Dict, Any, Optional
from app.utils.security import verify_hmac_signature


class HubtelClient:
    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        merchant_account_number: Optional[str] = None,
        webhook_secret: Optional[str] = None,
        base_url: str = "https://api-momo.hubtel.com/v1/merchantaccount",
        timeout: int = 30,
    ):
        self.client_id = client_id or os.getenv("HUBTEL_CLIENT_ID", "")
        self.client_secret = client_secret or os.getenv("HUBTEL_CLIENT_SECRET", "")
        self.merchant_account = merchant_account_number or os.getenv("HUBTEL_MERCHANT_ACCOUNT_NUMBER", "")
        self.webhook_secret = webhook_secret or os.getenv("HUBTEL_WEBHOOK_SECRET", "")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _get_auth_headers(self) -> Dict[str, str]:
        auth_string = f"{self.client_id}:{self.client_secret}"
        encoded = base64.b64encode(auth_string.encode()).decode()
        return {
            "Authorization": f"Basic {encoded}",
            "Content-Type": "application/json",
        }

    def is_configured(self) -> bool:
        return bool(self.client_id and self.client_secret and "YOUR_" not in self.client_id)

    def request_mobile_money_payment(
        self,
        customer_phone: str,
        amount: float,
        order_reference: str,
        channel: str = "mtn-gh",  # 'mtn-gh', 'vodafone-gh', 'tigo-gh'
        description: str = "Order Payment",
    ) -> Dict[str, Any]:
        """Initiates a Mobile Money Receive Mobile Money (RMM) prompt via Hubtel."""
        if not self.is_configured():
            return {
                "status": "PENDING",
                "message": "Hubtel Sandbox Mock: Prompt dispatched.",
                "hubtel_transaction_id": f"HUBTEL-MOCK-{order_reference}",
                "is_mock": True,
            }

        url = f"{self.base_url}/merchants/{self.merchant_account}/receive/mobilemoney"
        headers = self._get_auth_headers()
        payload = {
            "CustomerName": "Valued Customer",
            "CustomerMsisdn": customer_phone,
            "CustomerEmail": "customer@blessingstelecom.com.gh",
            "Channel": channel,
            "Amount": amount,
            "PrimaryCallbackUrl": f"{os.getenv('MOMO_CALLBACK_BASE_URL', '')}/api/webhooks/hubtel",
            "Description": description,
            "ClientReference": order_reference,
        }

        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
            return resp.json()
        except requests.RequestException as e:
            return {"status": "FAILED", "error": str(e)}

    def verify_webhook_signature(self, raw_body: bytes, signature_header: str) -> bool:
        if not self.webhook_secret:
            return True  # If secret not set in dev, bypass
        return verify_hmac_signature(raw_body, signature_header, self.webhook_secret, algorithm="sha256")
