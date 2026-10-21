"""
Environment Variable Validator Module.
Safely audits required environment configuration settings.
Reports missing variable names WITHOUT exposing sensitive secret values.
"""

import os
from typing import List, Dict, Tuple


# Configuration specifications by category
REQUIRED_CORE_ENV = [
    "SECRET_KEY",
    "JWT_SECRET_KEY",
    "DATABASE_URL",
]

OPTIONAL_CORE_ENV = [
    "APP_ENV",
    "LOG_LEVEL",
    "CORS_ORIGINS",
    "SQLITE_FALLBACK_URL",
]

MOMO_SANDBOX_ENV = [
    "MOMO_BASE_URL",
    "MOMO_TARGET_ENVIRONMENT",
    "MOMO_COLLECTION_SUBSCRIPTION_KEY",
    "MOMO_API_USER",
    "MOMO_API_KEY",
]

HUBTEL_ENV = [
    "HUBTEL_CLIENT_ID",
    "HUBTEL_CLIENT_SECRET",
]

PAYSTACK_ENV = [
    "PAYSTACK_SECRET_KEY",
    "PAYSTACK_PUBLIC_KEY",
]

AIRTIME_PROVIDER_ENV = [
    "AIRTIME_PROVIDER",
]


def validate_environment(strict_production: bool = False) -> Tuple[bool, Dict[str, List[str]]]:
    """
    Audits the current os.environ for required keys.
    Returns: (is_valid, report_dict)
    where report_dict contains categorized lists of missing variable names.
    Note: Values are never inspected or returned in the report to prevent leakage.
    """
    report = {
        "missing_core": [],
        "missing_momo": [],
        "missing_hubtel": [],
        "missing_paystack": [],
        "missing_airtime": [],
        "active_providers": [],
    }

    # 1. Validate Core Application Secrets
    for var_name in REQUIRED_CORE_ENV:
        val = os.getenv(var_name)
        if not val or val.startswith("generate_") or val == "YOUR_SECRET":
            # For development, allow fallback if SQLITE_FALLBACK_URL is present for DATABASE_URL
            if var_name == "DATABASE_URL" and not strict_production:
                fallback = os.getenv("SQLITE_FALLBACK_URL")
                if not fallback and not val:
                    report["missing_core"].append(var_name)
            else:
                report["missing_core"].append(var_name)

    # 2. Check MTN MoMo Sandbox/Live status
    momo_missing = [var for var in MOMO_SANDBOX_ENV if not os.getenv(var) or "YOUR_" in os.getenv(var, "")]
    if momo_missing:
        report["missing_momo"] = momo_missing
    else:
        report["active_providers"].append("MTN_MOMO")

    # 3. Check Hubtel credentials
    hubtel_missing = [var for var in HUBTEL_ENV if not os.getenv(var) or "YOUR_" in os.getenv(var, "")]
    if hubtel_missing:
        report["missing_hubtel"] = hubtel_missing
    else:
        report["active_providers"].append("HUBTEL")

    # 4. Check Paystack credentials
    paystack_missing = [var for var in PAYSTACK_ENV if not os.getenv(var) or "YOUR_" in os.getenv(var, "")]
    if paystack_missing:
        report["missing_paystack"] = paystack_missing
    else:
        report["active_providers"].append("PAYSTACK")

    # 5. Check Airtime Provider
    provider = os.getenv("AIRTIME_PROVIDER", "MOCK").upper()
    report["active_providers"].append(f"AIRTIME_{provider}")
    if provider not in ("MOCK", "HUBTEL", "RELOADLY", "AT_BUSINESS", "CUSTOM_AGGREGATOR"):
        report["missing_airtime"].append(f"Unknown AIRTIME_PROVIDER: '{provider}'")

    is_valid = len(report["missing_core"]) == 0
    if strict_production:
        is_valid = is_valid and (
            len(report["missing_momo"]) == 0 or
            len(report["missing_hubtel"]) == 0 or
            len(report["missing_paystack"]) == 0
        )

    return is_valid, report


def print_env_status_summary():
    """Prints a secure configuration status report without logging any secret values."""
    is_valid, report = validate_environment()
    print("==================================================")
    print("      GHANA FINTECH ENVIRONMENT STATUS REPORT     ")
    print("==================================================")
    print(f"Overall Configuration Valid: {'YES' if is_valid else 'NO (Missing required keys)'}")

    if report["missing_core"]:
        print(f"[!] MISSING CORE SETTINGS: {', '.join(report['missing_core'])}")
    else:
        print("[+] Core environment variables present.")

    print(f"[*] Active Provider Modules: {', '.join(report['active_providers'])}")

    if report["missing_momo"]:
        print(f"[*] MTN MoMo Sandbox unconfigured items: {len(report['missing_momo'])} variable(s)")
    if report["missing_hubtel"]:
        print(f"[*] Hubtel unconfigured items: {len(report['missing_hubtel'])} variable(s)")
    if report["missing_paystack"]:
        print(f"[*] Paystack unconfigured items: {len(report['missing_paystack'])} variable(s)")
    print("==================================================")
