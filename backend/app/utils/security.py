"""
Security, Cryptography, and Token Utilities.
Implements password hashing, HMAC webhook verification, and reference generators.
"""

import hashlib
import hmac
import secrets
import string
import time
from typing import Optional
from werkzeug.security import generate_password_hash, check_password_hash


def hash_password(password: str) -> str:
    """Hashes a password using PBKDF2-SHA256 with 600,000 rounds and random salt."""
    return generate_password_hash(password, method="pbkdf2:sha256:600000")


def verify_password(password: str, password_hash: str) -> bool:
    """Secure constant-time verification of password against stored hash."""
    if not password or not password_hash:
        return False
    return check_password_hash(password_hash, password)


def generate_reference(prefix: str = "REF") -> str:
    """
    Generates a cryptographically random, collision-resistant reference token.
    Format: {PREFIX}-{TIMESTAMP_HEX}-{RANDOM_HEX}
    Example: TRX-18F3B0A9-7A8E2C4D
    """
    timestamp_hex = hex(int(time.time()))[2:].upper()
    random_hex = secrets.token_hex(4).upper()
    return f"{prefix.upper()}-{timestamp_hex}-{random_hex}"


def generate_agent_code() -> str:
    """Generates an alphanumeric agent identification code (e.g., AGT-78241)."""
    digits = "".join(secrets.choice(string.digits) for _ in range(5))
    return f"AGT-{digits}"


def verify_hmac_signature(raw_payload: bytes, signature_header: str, secret_key: str, algorithm: str = "sha256") -> bool:
    """
    Verifies a webhook HMAC signature using constant-time comparison.
    Supports sha256 (standard for Paystack, Hubtel, etc.).
    """
    if not signature_header or not secret_key:
        return False

    try:
        hash_func = getattr(hashlib, algorithm.lower(), hashlib.sha256)
        computed_hmac = hmac.new(
            secret_key.encode("utf-8"),
            raw_payload,
            hash_func
        ).hexdigest()

        # Constant-time comparison prevents timing attacks
        return hmac.compare_digest(computed_hmac.lower(), signature_header.strip().lower())
    except Exception:
        return False


def mask_phone_number(phone_number: str) -> str:
    """Masks a phone number for privacy display (e.g. 0241234567 -> 024****567)."""
    if not phone_number or len(phone_number) < 7:
        return phone_number
    return f"{phone_number[:3]}****{phone_number[-3:]}"
