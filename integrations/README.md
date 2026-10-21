# External Integrations Guide

This directory contains standalone, modular client adapters for payment gateways and telecom aggregators operating in Ghana.

## 1. MTN Mobile Money Open API (`integrations/momo/`)
- **API Spec**: MTN MoMo Open API v1.0
- **Sandbox URL**: `https://sandbox.momodeveloper.mtn.com`
- **Modules**:
  - `client.py`: Handles token generation, Request-to-Pay (Collection API), and transaction status verification.
  - `sandbox_setup.py`: Automates Sandbox API User UUID creation and API Key extraction.
- **Rules**:
  - `HTTP 202` is treated strictly as an acknowledgment that the push notification was sent to the subscriber's phone. It is **never** considered proof of payment.
  - Transactions are verified via `/collection/v1_0/requesttopay/{referenceId}` polling and signed webhook callbacks.
  - Customer MoMo PINs and OTPs are never handled or collected.

## 2. Hubtel API Adapter (`integrations/hubtel/`)
- **Functions**: Alternative mobile money collection, Airtime top-up, and ECG utility bills.
- **Security**: Verifies webhook signatures using HMAC-SHA256.

## 3. Paystack Adapter (`integrations/paystack/`)
- **Functions**: Bank cards (Visa/Mastercard) and Mobile Money collections in Ghana Cedis (GHS).
- **Security**: Verifies `x-paystack-signature` using HMAC-SHA512.

## 4. Airtime & Data Distribution Adapter (`integrations/airtime/`)
- **Supported Networks**: MTN Ghana, Telecel Ghana (formerly Vodafone), AT Ghana (formerly AirtelTigo).
- **Validation**: Strict Ghanaian phone number prefix verification. Phone numbers mismatched with selected networks are rejected immediately.
- **Fail-Safe**: In production (`APP_ENV=production`), unconfigured provider credentials raise explicit runtime exceptions rather than simulating success.
