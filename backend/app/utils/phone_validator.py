"""
Ghana Mobile Number (MSISDN) Validation and Telco Detection.
Supports MTN, Telecel (Vodafone), and AT (AirtelTigo) networks.
Validates formats: 0XXXXXXXXX, +233XXXXXXXXX, 233XXXXXXXXX.
"""

import re
from typing import Optional, Tuple

NETWORK_PREFIXES = {
    "MTN": ("024", "025", "053", "054", "055", "059"),
    "TELECEL": ("020", "050"),
    "AT": ("026", "027", "056", "057"),
}


def sanitize_phone_number(raw_phone: str) -> str:
    """Removes all non-digit characters except leading plus sign."""
    if not raw_phone:
        return ""
    cleaned = re.sub(r"[^\d+]", "", raw_phone.strip())
    return cleaned


def normalize_ghana_phone(raw_phone: str) -> Tuple[bool, Optional[str], Optional[str], Optional[str]]:
    """
    Validates and normalizes a Ghanaian phone number.
    Returns: (is_valid, local_format_0XX, e164_format_+233, detected_network)

    Examples:
        '0241234567' -> (True, '0241234567', '+233241234567', 'MTN')
        '+233201234567' -> (True, '0201234567', '+233201234567', 'TELECEL')
        '233271234567' -> (True, '0271234567', '+233271234567', 'AT')
    """
    cleaned = sanitize_phone_number(raw_phone)
    if not cleaned:
        return False, None, None, None

    digits = cleaned.lstrip("+")

    # If it starts with 233, check if total digits == 12 (e.g. 233 + 9 digits)
    if digits.startswith("233"):
        if len(digits) != 12:
            return False, None, None, None
        local_digits = "0" + digits[3:]
    elif digits.startswith("0"):
        if len(digits) != 10:
            return False, None, None, None
        local_digits = digits
    else:
        # User entered 9 digits without leading 0 (e.g. 241234567)
        if len(digits) == 9:
            local_digits = "0" + digits
        else:
            return False, None, None, None

    prefix = local_digits[:3]
    detected_network = None

    for network, prefixes in NETWORK_PREFIXES.items():
        if prefix in prefixes:
            detected_network = network
            break

    if not detected_network:
        # Invalid Ghanaian mobile prefix
        return False, None, None, None

    e164_format = f"+233{local_digits[1:]}"
    return True, local_digits, e164_format, detected_network


def is_valid_network_phone(phone_number: str, expected_network: str) -> bool:
    """Checks if a phone number matches the expected telecommunication network."""
    is_valid, _, _, detected = normalize_ghana_phone(phone_number)
    if not is_valid:
        return False
    return detected == expected_network.upper()
