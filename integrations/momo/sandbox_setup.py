"""
MTN MoMo Sandbox Automated Provisioning Utility.
Automates creating a Sandbox API User UUID and generating an API Key.
Run this script to generate working credentials for your .env file.
"""

import uuid
import requests


def provision_momo_sandbox(subscription_key: str, callback_host: str = "webhook.site") -> dict:
    """
    Provisions a new API User and API Key on the MTN MoMo Sandbox environment.
    """
    base_url = "https://sandbox.momodeveloper.mtn.com"
    api_user_uuid = str(uuid.uuid4())

    print(f"[*] Step 1: Creating Sandbox API User: {api_user_uuid}")
    user_url = f"{base_url}/v1_0/apiuser"
    user_headers = {
        "X-Reference-Id": api_user_uuid,
        "Ocp-Apim-Subscription-Key": subscription_key,
        "Content-Type": "application/json",
    }
    user_payload = {
        "providerCallbackHost": callback_host,
    }

    resp = requests.post(user_url, json=user_payload, headers=user_headers, timeout=30)
    if resp.status_code != 201:
        raise RuntimeError(f"Failed to create Sandbox API User: HTTP {resp.status_code} - {resp.text}")

    print("[+] Step 1 Successful: API User created.")

    print(f"[*] Step 2: Generating Sandbox API Key for user: {api_user_uuid}")
    key_url = f"{base_url}/v1_0/apiuser/{api_user_uuid}/apikey"
    key_headers = {
        "Ocp-Apim-Subscription-Key": subscription_key,
    }

    key_resp = requests.post(key_url, headers=key_headers, timeout=30)
    if key_resp.status_code != 201:
        raise RuntimeError(f"Failed to create Sandbox API Key: HTTP {key_resp.status_code} - {key_resp.text}")

    api_key = key_resp.json().get("apiKey")
    print("[+] Step 2 Successful: API Key received.")

    result = {
        "MOMO_BASE_URL": base_url,
        "MOMO_TARGET_ENVIRONMENT": "sandbox",
        "MOMO_COLLECTION_SUBSCRIPTION_KEY": subscription_key,
        "MOMO_API_USER": api_user_uuid,
        "MOMO_API_KEY": api_key,
    }

    print("\n========================================================")
    print("      MTN MOMO SANDBOX CONFIGURATION GENERATED          ")
    print("========================================================")
    for k, v in result.items():
        print(f"{k}={v}")
    print("========================================================\n")

    return result


if __name__ == "__main__":
    import sys

    sub_key = sys.argv[1] if len(sys.argv) > 1 else input("Enter your MTN MoMo Primary/Secondary Subscription Key: ").strip()
    if not sub_key:
        print("Error: Subscription key is required.")
        sys.exit(1)

    try:
        provision_momo_sandbox(sub_key)
    except Exception as e:
        print(f"[-] Error: {e}")
        sys.exit(1)
