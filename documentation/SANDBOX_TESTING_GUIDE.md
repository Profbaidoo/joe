# MTN MoMo Sandbox & Telecom Testing Guide

This guide provides end-to-end instructions for testing the Ghana Mobile Money, Airtime, and Data bundle flows using the official MTN MoMo Sandbox and local testing tools.

---

## 1. Quick Sandbox Provisioning (Automated)

The project includes an automated provisioning script that interfaces with MTN MoMo Developer portal to generate your Sandbox API User UUID and API Key:

```bash
# Activate backend environment
cd backend
source venv/Scripts/activate  # (Windows: .\venv\Scripts\Activate.ps1)

# Run provisioning script with your MTN MoMo Collection Subscription Key
python ../integrations/momo/sandbox_setup.py <YOUR_COLLECTIONS_SUBSCRIPTION_KEY>
```

The script will output:
```env
MOMO_BASE_URL=https://sandbox.momodeveloper.mtn.com
MOMO_TARGET_ENVIRONMENT=sandbox
MOMO_COLLECTION_SUBSCRIPTION_KEY=...
MOMO_API_USER=...
MOMO_API_KEY=...
```
Copy these into your `.env` file.

---

## 2. Testing Mobile Money Request-To-Pay

In the MTN Sandbox, payments require:
1. `amount`: Currency in GHS (e.g. "10.00").
2. `currency`: Must be `GHS` for Ghana.
3. `payer.partyId`: Valid Ghanaian phone number format (e.g., `0241234567` or `233241234567`).

### Expected Response Behavior:
- When you dispatch `POST /api/payments/momo/request`, MTN returns **HTTP 202 Accepted**.
- **Important**: In compliance with Bank of Ghana fintech standards, an HTTP 202 is **NOT** a completed payment. The backend records transaction state as `PENDING`.
- The customer handset receives a USSD prompt.

---

## 3. Reconciling Payment Status

Once the subscriber enters their PIN:
- The backend polls `/api/payments/momo/status/{reference}` or receives the verified callback.
- In sandbox mock mode, the transaction status transitions immediately to `SUCCESSFUL`.
- This automatically triggers:
  1. `financial_ledger` double-entry records:
     - `DEBIT PROVIDER_CLEARING`
     - `CREDIT BUSINESS_REVENUE`
  2. Order status transitions from `PENDING` -> `PAID` -> `COMPLETED`.
  3. Fulfillment engine triggers `AirtimeDataClient` to deliver the airtime or data bundle.
  4. Digital receipt is generated and accessible via `/api/orders/{id}` or the Web Dashboard.

---

## 4. Testing via Web Admin Test Bench

1. Start the Flask backend:
   ```bash
   cd backend
   python run.py
   ```
2. Navigate to `http://localhost:5173` (or open the admin portal).
3. Log in with:
   - **Username**: `admin`
   - **Password**: `Admin1234!`
4. Click **MoMo Sandbox Test** in the sidebar.
5. Enter any Ghanaian phone number (e.g. `0241234567`) and amount `GH₵ 10.00`.
6. Click **Send MoMo Payment Request**.
7. Observe the live status transition: **Created** -> **Prompt Pending** -> **Reconciled & Delivered** -> **Digital Receipt Generated**!
