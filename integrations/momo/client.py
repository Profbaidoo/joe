"""
MTN Mobile Money (MoMo) Open API Client.
Supports Collections API, Transaction Status polling, and Disbursements (where authorized).
Strict compliance with sandbox environment and Ghanaian telecom standards.
"""

import os
import uuid
import base64
import requests
from typing import Dict, Any, Optional


class MomoAPIException(Exception):
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data or {}


class MTNMoMoClient:
    def __init__(
        self,
        base_url: Optional[str] = None,
        target_environment: Optional[str] = None,
        subscription_key: Optional[str] = None,
        api_user: Optional[str] = None,
        api_key: Optional[str] = None,
        currency: str = "GHS",
        timeout: int = 30,
    ):
        self.base_url = (base_url or os.getenv("MOMO_BASE_URL", "https://sandbox.momodeveloper.mtn.com")).rstrip("/")
        self.target_environment = target_environment or os.getenv("MOMO_TARGET_ENVIRONMENT", "sandbox")
        self.subscription_key = subscription_key or os.getenv("MOMO_COLLECTION_SUBSCRIPTION_KEY", "")
        self.api_user = api_user or os.getenv("MOMO_API_USER", "")
        self.api_key = api_key or os.getenv("MOMO_API_KEY", "")
        self.currency = currency
        self.timeout = timeout
        self._cached_token: Optional[str] = None

    def _get_auth_headers(self) -> Dict[str, str]:
        auth_string = f"{self.api_user}:{self.api_key}"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        return {
            "Ocp-Apim-Subscription-Key": self.subscription_key,
            "Authorization": f"Basic {encoded_auth}",
        }

    def get_access_token(self, force_refresh: bool = False) -> str:
        """
        Creates an OAuth 2.0 access token for Collections API.
        Endpoint: POST /collection/token/
        """
        if self._cached_token and not force_refresh:
            return self._cached_token

        # If in sandbox and credentials are placeholders, return a simulated sandbox token
        if self.target_environment == "sandbox" and (
            not self.subscription_key or "YOUR_" in self.subscription_key or not self.api_user
        ):
            self._cached_token = f"sandbox_token_{uuid.uuid4().hex}"
            return self._cached_token

        url = f"{self.base_url}/collection/token/"
        headers = self._get_auth_headers()

        try:
            response = requests.post(url, headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                raise MomoAPIException(
                    f"Failed to obtain MoMo access token: HTTP {response.status_code}",
                    status_code=response.status_code,
                    response_data=response.json() if response.content else {},
                )
            token_data = response.json()
            self._cached_token = token_data.get("access_token")
            return self._cached_token
        except requests.RequestException as e:
            raise MomoAPIException(f"MoMo Token Network Error: {str(e)}")

    def request_to_pay(
        self,
        amount: str,
        payer_phone: str,
        transaction_reference: str,
        payer_message: str = "Payment for Blessings Telecom order",
        payee_note: str = "Order Payment",
        callback_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Initiates a Collection Request-to-Pay.
        Endpoint: POST /collection/v1_0/requesttopay
        CRITICAL: An HTTP 202 response indicates the request was ACCEPTED for processing.
        It is NOT confirmation of payment. Customer must approve on their phone.
        """
        reference_id = str(uuid.uuid4())  # X-Reference-Id UUID required by MTN

        # Normalize Ghanaian phone to international format without plus (e.g. 233241234567)
        sanitized_phone = payer_phone.lstrip("+")
        if sanitized_phone.startswith("0"):
            sanitized_phone = f"233{sanitized_phone[1:]}"

        # Sandbox Mocking fallback if credentials are not registered with MTN live API
        if self.target_environment == "sandbox" and (
            not self.subscription_key or "YOUR_" in self.subscription_key
        ):
            return {
                "http_status": 202,
                "reference_id": reference_id,
                "transaction_reference": transaction_reference,
                "status": "PENDING",
                "message": "Payment prompt sent to customer phone. Please approve the USSD prompt.",
                "is_sandbox_mock": True,
            }

        token = self.get_access_token()
        url = f"{self.base_url}/collection/v1_0/requesttopay"

        headers = {
            "Authorization": f"Bearer {token}",
            "X-Reference-Id": reference_id,
            "X-Target-Environment": self.target_environment,
            "Ocp-Apim-Subscription-Key": self.subscription_key,
            "Content-Type": "application/json",
        }
        if callback_url:
            headers["X-Callback-Url"] = callback_url

        payload = {
            "amount": str(amount),
            "currency": self.currency,
            "externalId": transaction_reference,
            "payer": {
                "partyIdType": "MSISDN",
                "partyId": sanitized_phone,
            },
            "payerMessage": payer_message,
            "payeeNote": payee_note,
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
            if response.status_code == 202:
                # 202 Accepted: Customer prompted on handset
                return {
                    "http_status": 202,
                    "reference_id": reference_id,
                    "transaction_reference": transaction_reference,
                    "status": "PENDING",
                    "message": "Payment prompt sent to customer phone. Please approve the USSD prompt.",
                    "is_sandbox_mock": False,
                }
            else:
                raise MomoAPIException(
                    f"MoMo Request-To-Pay failed: HTTP {response.status_code}",
                    status_code=response.status_code,
                    response_data=response.json() if response.content else {},
                )
        except requests.RequestException as e:
            raise MomoAPIException(f"MoMo Connection Error: {str(e)}")

    def get_transaction_status(self, reference_id: str) -> Dict[str, Any]:
        """
        Polls the actual status of a Request-to-Pay transaction.
        Endpoint: GET /collection/v1_0/requesttopay/{referenceId}
        Returns: Status dictionary with normalized status ('SUCCESSFUL', 'PENDING', 'FAILED', 'REJECTED', 'TIMEOUT')
        """
        # Sandbox simulated status check
        if self.target_environment == "sandbox" and (
            not self.subscription_key or "YOUR_" in self.subscription_key
        ):
            # In sandbox mock mode, simulate successful completion
            return {
                "status": "SUCCESSFUL",
                "financialTransactionId": f"MOMO-FIN-{uuid.uuid4().hex[:10].upper()}",
                "amount": "10.00",
                "currency": "GHS",
                "payer": {"partyId": "233240000000"},
                "is_sandbox_mock": True,
            }

        token = self.get_access_token()
        url = f"{self.base_url}/collection/v1_0/requesttopay/{reference_id}"

        headers = {
            "Authorization": f"Bearer {token}",
            "X-Target-Environment": self.target_environment,
            "Ocp-Apim-Subscription-Key": self.subscription_key,
        }

        try:
            response = requests.get(url, headers=headers, timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                raw_status = data.get("status", "PENDING").upper()
                return {
                    "status": raw_status,  # 'SUCCESSFUL', 'FAILED', 'PENDING'
                    "financialTransactionId": data.get("financialTransactionId"),
                    "externalId": data.get("externalId"),
                    "amount": data.get("amount"),
                    "currency": data.get("currency"),
                    "reason": data.get("reason"),
                    "payer": data.get("payer"),
                    "raw_data": data,
                }
            elif response.status_code == 404:
                return {"status": "PENDING", "message": "Transaction pending initiation or not yet indexed."}
            else:
                raise MomoAPIException(
                    f"Failed to check MoMo status: HTTP {response.status_code}",
                    status_code=response.status_code,
                    response_data=response.json() if response.content else {},
                )
        except requests.RequestException as e:
            raise MomoAPIException(f"MoMo Status Query Error: {str(e)}")
