"""
Paystack Payment Gateway Integration.
Supports Card Payments and Ghanaian Mobile Money (MTN, Telecel, AT) collections in GHS.
"""

import os
import requests
from typing import Dict, Any, Optional
from app.utils.security import verify_hmac_signature


class PaystackClient:
    def __init__(
        self,
        secret_key: Optional[str] = None,
        public_key: Optional[str] = None,
        webhook_secret: Optional[str] = None,
        base_url: str = "https://api.paystack.co",
        timeout: int = 30,
    ):
        self.secret_key = secret_key or os.getenv("PAYSTACK_SECRET_KEY", "")
        self.public_key = public_key or os.getenv("PAYSTACK_PUBLIC_KEY", "")
        self.webhook_secret = webhook_secret or os.getenv("PAYSTACK_WEBHOOK_SECRET", "")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def is_configured(self) -> bool:
        return bool(self.secret_key and "YOUR_" not in self.secret_key)

    def initialize_transaction(
        self,
        email: str,
        amount_in_pesewas: int,  # 1 GHS = 100 pesewas
        reference: str,
        callback_url: Optional[str] = None,
        channels: Optional[list] = None,
    ) -> Dict[str, Any]:
        """Initializes a Paystack transaction and returns authorization URL."""
        if not self.is_configured():
            return {
                "status": True,
                "data": {
                    "authorization_url": f"https://checkout.paystack.com/mock-{reference}",
                    "access_code": f"access_mock_{reference}",
                    "reference": reference,
                },
                "is_mock": True,
            }

        url = f"{self.base_url}/transaction/initialize"
        headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "email": email,
            "amount": amount_in_pesewas,
            "currency": "GHS",
            "reference": reference,
            "callback_url": callback_url,
            "channels": channels or ["card", "mobile_money"],
        }

        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
            return resp.json()
        except requests.RequestException as e:
            return {"status": False, "message": str(e)}

    def verify_transaction(self, reference: str) -> Dict[str, Any]:
        """Verifies a transaction's final outcome with Paystack servers."""
        if not self.is_configured():
            return {
                "status": True,
                "data": {
                    "status": "success",
                    "reference": reference,
                    "amount": 1000,
                    "currency": "GHS",
                    "channel": "mobile_money",
                },
                "is_mock": True,
            }

        url = f"{self.base_url}/transaction/verify/{reference}"
        headers = {
            "Authorization": f"Bearer {self.secret_key}",
        }

        try:
            resp = requests.get(url, headers=headers, timeout=self.timeout)
            return resp.json()
        except requests.RequestException as e:
            return {"status": False, "message": str(e)}

    def verify_webhook_signature(self, raw_body: bytes, signature_header: str) -> bool:
        secret = self.webhook_secret or self.secret_key
        if not secret:
            return True
        return verify_hmac_signature(raw_body, signature_header, secret, algorithm="sha512")
