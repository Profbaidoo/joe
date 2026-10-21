"""
Universal Airtime and Data Bundle Distribution Adapter.
Routes fulfillment requests to authorized Ghanaian aggregators (Hubtel, Reloadly, Direct Telco).
Enforces phone number verification, network matching, and delivery tracking.
"""

import os
import uuid
import requests
from typing import Dict, Any, Optional
from app.utils.phone_validator import normalize_ghana_phone


class AirtimeProviderException(Exception):
    pass


class AirtimeDataClient:
    def __init__(
        self,
        provider: Optional[str] = None,
        api_base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        timeout: int = 30,
    ):
        self.provider = (provider or os.getenv("AIRTIME_PROVIDER", "MOCK")).upper()
        self.api_base_url = api_base_url or os.getenv("AIRTIME_API_BASE_URL", "")
        self.api_key = api_key or os.getenv("AIRTIME_API_KEY", "")
        self.api_secret = api_secret or os.getenv("AIRTIME_API_SECRET", "")
        self.timeout = timeout
        self.app_env = os.getenv("APP_ENV", "development").lower()

    def is_configured(self) -> bool:
        if self.provider == "MOCK":
            return True
        return bool(self.api_key and "YOUR_" not in self.api_key and self.api_base_url)

    def vend_airtime(
        self,
        recipient_phone: str,
        network_code: str,
        amount_ghs: float,
        order_reference: str,
    ) -> Dict[str, Any]:
        """
        Dispatches airtime top-up to customer phone.
        Enforces validation: never simulates success in production when unconfigured.
        """
        is_valid, local_phone, e164_phone, detected_network = normalize_ghana_phone(recipient_phone)
        if not is_valid:
            raise AirtimeProviderException(f"Invalid Ghanaian phone number: {recipient_phone}")

        if detected_network != network_code.upper():
            raise AirtimeProviderException(
                f"Network mismatch: Phone number {recipient_phone} belongs to {detected_network}, but order requested {network_code}."
            )

        # Check configuration
        if not self.is_configured():
            if self.app_env == "production":
                raise AirtimeProviderException(
                    "CRITICAL: Airtime provider API is not configured in production. "
                    "Configure AIRTIME_PROVIDER, AIRTIME_API_KEY, and AIRTIME_API_BASE_URL."
                )

        # Handle Mock Sandbox Mode
        if self.provider == "MOCK" or not self.is_configured():
            provider_txn_id = f"AIRTIME-MOCK-{uuid.uuid4().hex[:10].upper()}"
            return {
                "success": True,
                "status": "DELIVERED",
                "provider_transaction_id": provider_txn_id,
                "recipient_phone": local_phone,
                "network": network_code,
                "amount": amount_ghs,
                "provider": "MOCK_SANDBOX",
                "message": f"Successfully delivered GH₵ {amount_ghs:.2f} {network_code} airtime to {local_phone}.",
            }

        # Live Provider Dispatch (e.g. Hubtel or Reloadly)
        url = f"{self.api_base_url.rstrip('/')}/topup"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "recipient": e164_phone,
            "operator": network_code.upper(),
            "amount": amount_ghs,
            "currency": "GHS",
            "client_reference": order_reference,
        }

        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
            data = resp.json() if resp.content else {}
            if resp.status_code in (200, 201):
                return {
                    "success": True,
                    "status": "DELIVERED",
                    "provider_transaction_id": data.get("transaction_id", str(uuid.uuid4())),
                    "recipient_phone": local_phone,
                    "network": network_code,
                    "amount": amount_ghs,
                    "provider": self.provider,
                    "raw_response": data,
                }
            else:
                return {
                    "success": False,
                    "status": "FAILED",
                    "error": data.get("message", f"HTTP {resp.status_code}"),
                    "raw_response": data,
                }
        except requests.RequestException as e:
            raise AirtimeProviderException(f"Network error communicating with airtime provider: {str(e)}")

    def vend_data_bundle(
        self,
        recipient_phone: str,
        network_code: str,
        plan_code: str,
        order_reference: str,
    ) -> Dict[str, Any]:
        """Dispatches data bundle to customer phone."""
        is_valid, local_phone, e164_phone, detected_network = normalize_ghana_phone(recipient_phone)
        if not is_valid:
            raise AirtimeProviderException(f"Invalid Ghanaian phone number: {recipient_phone}")

        if detected_network != network_code.upper():
            raise AirtimeProviderException(
                f"Network mismatch: Phone number {recipient_phone} belongs to {detected_network}, but plan requested {network_code}."
            )

        if not self.is_configured():
            if self.app_env == "production":
                raise AirtimeProviderException(
                    "CRITICAL: Data bundle provider API is not configured in production. "
                    "Configure AIRTIME_PROVIDER, AIRTIME_API_KEY, and AIRTIME_API_BASE_URL."
                )

        if self.provider == "MOCK" or not self.is_configured():
            provider_txn_id = f"DATA-MOCK-{uuid.uuid4().hex[:10].upper()}"
            return {
                "success": True,
                "status": "DELIVERED",
                "provider_transaction_id": provider_txn_id,
                "recipient_phone": local_phone,
                "network": network_code,
                "plan_code": plan_code,
                "provider": "MOCK_SANDBOX",
                "message": f"Successfully activated {plan_code} for {local_phone}.",
            }

        url = f"{self.api_base_url.rstrip('/')}/databundle"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "recipient": e164_phone,
            "operator": network_code.upper(),
            "plan_code": plan_code,
            "client_reference": order_reference,
        }

        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
            data = resp.json() if resp.content else {}
            if resp.status_code in (200, 201):
                return {
                    "success": True,
                    "status": "DELIVERED",
                    "provider_transaction_id": data.get("transaction_id", str(uuid.uuid4())),
                    "recipient_phone": local_phone,
                    "network": network_code,
                    "plan_code": plan_code,
                    "provider": self.provider,
                    "raw_response": data,
                }
            else:
                return {
                    "success": False,
                    "status": "FAILED",
                    "error": data.get("message", f"HTTP {resp.status_code}"),
                    "raw_response": data,
                }
        except requests.RequestException as e:
            raise AirtimeProviderException(f"Network error communicating with data provider: {str(e)}")
