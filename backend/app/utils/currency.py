"""
Ghana Currency Utility Module.
Handles strict decimal arithmetic for Ghana Cedis (GHS / GH₵).
Ensures zero floating-point drift across all financial calculations.
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Union

# Currency constants
CURRENCY_CODE = "GHS"
CURRENCY_SYMBOL = "GH₵"
DECIMAL_PLACES_DISPLAY = Decimal("0.01")
DECIMAL_PLACES_STORAGE = Decimal("0.0001")


def to_decimal(value: Union[str, int, float, Decimal, None]) -> Decimal:
    """
    Safely converts input to a Decimal with storage precision (4 decimal places).
    Never performs floating-point conversion directly from float if str is possible.
    """
    if value is None:
        return Decimal("0.0000")
    if isinstance(value, Decimal):
        return value.quantize(DECIMAL_PLACES_STORAGE, rounding=ROUND_HALF_UP)
    # Convert through string representation to prevent float precision artifacts
    return Decimal(str(value)).quantize(DECIMAL_PLACES_STORAGE, rounding=ROUND_HALF_UP)


def format_ghs(amount: Union[str, int, float, Decimal, None], show_symbol: bool = True) -> str:
    """
    Formats an amount to standard 2-decimal Ghanaian Cedi display.
    Example: 12.5 -> 'GH₵ 12.50' or '12.50'
    """
    dec_val = to_decimal(amount).quantize(DECIMAL_PLACES_DISPLAY, rounding=ROUND_HALF_UP)
    formatted_number = f"{dec_val:,.2f}"
    if show_symbol:
        return f"{CURRENCY_SYMBOL} {formatted_number}"
    return formatted_number


def calculate_fee_and_net(gross_amount: Decimal, fee_fixed: Decimal, fee_percent: Decimal) -> tuple[Decimal, Decimal]:
    """
    Computes fee and net amount given a gross value and pricing rules.
    net = gross - (fee_fixed + gross * fee_percent)
    """
    gross = to_decimal(gross_amount)
    fixed = to_decimal(fee_fixed)
    pct = to_decimal(fee_percent)

    calculated_fee = (fixed + (gross * pct)).quantize(DECIMAL_PLACES_STORAGE, rounding=ROUND_HALF_UP)
    net_amount = (gross - calculated_fee).quantize(DECIMAL_PLACES_STORAGE, rounding=ROUND_HALF_UP)

    return calculated_fee, net_amount


def calculate_commission(gross_amount: Decimal, commission_rate: Decimal) -> Decimal:
    """
    Calculates agent commission based on rate (e.g. 0.01 for 1%).
    """
    gross = to_decimal(gross_amount)
    rate = to_decimal(commission_rate)
    return (gross * rate).quantize(DECIMAL_PLACES_STORAGE, rounding=ROUND_HALF_UP)
