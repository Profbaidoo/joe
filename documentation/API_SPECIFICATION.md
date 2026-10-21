# REST API Specification

This document describes the complete REST API for the Ghana Fintech Mobile Money, Airtime & Data Bundle Platform.

- **Base URL (Local)**: `http://127.0.0.1:5000`
- **Swagger Interactive UI**: `http://127.0.0.1:5000/api/docs/`
- **Default Currency**: Ghana Cedis (`GHS` / `GH₵`)
- **Default Timezone**: `Africa/Accra` (GMT)

---

## Authentication & Headers

Protected endpoints require a JWT Bearer token:
```http
Authorization: Bearer <access_token>
Content-Type: application/json
```

---

## 1. Authentication Endpoints

### 1.1 Customer Registration
- **Endpoint**: `POST /api/auth/register`
- **Access**: Public
- **Request Body**:
```json
{
  "username": "kwame_boateng",
  "email": "kwame@example.com",
  "phone_number": "0241234567",
  "password": "SecurePassword2026!",
  "full_name": "Kwame Boateng",
  "momo_network": "MTN"
}
```
- **Response `201 Created`**:
```json
{
  "message": "Registration successful.",
  "user": {
    "id": 1,
    "username": "kwame_boateng",
    "email": "kwame@example.com",
    "phone_number": "0241234567",
    "role": "CUSTOMER"
  },
  "access_token": "eyJhbGciOiJIUzI1Ni...",
  "refresh_token": "eyJhbGciOiJIUzI1Ni..."
}
```

### 1.2 User Login
- **Endpoint**: `POST /api/auth/login`
- **Access**: Public
- **Request Body**: Accepts Username, Email, or Ghanaian Mobile Number:
```json
{
  "login": "0241234567",
  "password": "SecurePassword2026!"
}
```
- **Response `200 OK`**:
```json
{
  "message": "Login successful.",
  "user": {
    "id": 1,
    "username": "kwame_boateng",
    "role": "CUSTOMER"
  },
  "access_token": "eyJhbGciOiJIUzI1Ni...",
  "refresh_token": "eyJhbGciOiJIUzI1Ni..."
}
```

---

## 2. Telecom Products & Data Bundles

### 2.1 Get Active Networks
- **Endpoint**: `GET /api/networks`
- **Access**: Public
- **Response `200 OK`**:
```json
{
  "networks": [
    { "code": "MTN", "name": "MTN Ghana", "is_active": true },
    { "code": "TELECEL", "name": "Telecel Ghana", "is_active": true },
    { "code": "AT", "name": "AT Ghana", "is_active": true }
  ]
}
```

### 2.2 Get Data Bundle Packages
- **Endpoint**: `GET /api/data-bundles?network=MTN`
- **Access**: Public
- **Response `200 OK`**:
```json
{
  "data_bundles": [
    {
      "id": 1,
      "plan_code": "MTN_1GB",
      "name": "MTN 1GB Data Bundle",
      "network_code": "MTN",
      "volume_mb": 1024,
      "validity_days": 30,
      "wholesale_price": 10.50,
      "retail_price": 12.00
    },
    {
      "id": 4,
      "plan_code": "MTN_10GB",
      "name": "MTN 10GB Non-Expiry Bundle",
      "network_code": "MTN",
      "volume_mb": 10240,
      "validity_days": 0,
      "wholesale_price": 68.00,
      "retail_price": 75.00
    }
  ]
}
```

---

## 3. Orders & Payment Flow

### 3.1 Create Order
- **Endpoint**: `POST /api/orders`
- **Access**: Authenticated (`CUSTOMER`, `AGENT`, `ADMIN`)
- **Request Body**:
```json
{
  "order_type": "AIRTIME",
  "recipient_phone": "0241234567",
  "network_code": "MTN",
  "amount": 10.00
}
```
- **Response `201 Created`**:
```json
{
  "message": "Order created successfully. Proceed to payment authorization.",
  "order": {
    "id": 10,
    "order_reference": "ORD-18F3B0-A97A",
    "order_type": "AIRTIME",
    "recipient_phone": "0241234567",
    "network_code": "MTN",
    "total_amount": 10.00,
    "fee_amount": 0.00,
    "net_amount": 10.00,
    "status": "PENDING",
    "payment_status": "UNPAID",
    "fulfillment_status": "UNFULFILLED"
  }
}
```

### 3.2 Request Mobile Money Payment
- **Endpoint**: `POST /api/payments/momo/request`
- **Access**: Authenticated
- **Request Body**:
```json
{
  "order_id": 10,
  "momo_phone": "0241234567"
}
```
- **Response `200 OK`**:
```json
{
  "status": "PENDING",
  "transaction_reference": "TRX-18F3B0-2C4D",
  "provider_reference": "9c12e8b0-a08b-4c07-96a1-63857e33527b",
  "amount": 10.00,
  "message": "Payment prompt sent to customer phone. Please approve the prompt on your phone."
}
```

### 3.3 Verify & Reconcile Payment
- **Endpoint**: `GET /api/payments/momo/status/{reference}`
- **Access**: Authenticated
- **Response `200 OK` (when subscriber has confirmed)**:
```json
{
  "status": "SUCCESSFUL",
  "transaction_reference": "TRX-18F3B0-2C4D",
  "order_reference": "ORD-18F3B0-A97A",
  "order_status": "COMPLETED",
  "fulfillment": {
    "status": "SUCCESSFUL",
    "details": {
      "success": true,
      "provider_transaction_id": "AIRTIME-MOCK-A1B2C3",
      "recipient_phone": "0241234567",
      "network": "MTN",
      "amount": 10.00
    }
  },
  "message": "Payment confirmed and order fulfilled successfully."
}
```

---

## 4. Administrative Dashboard

### 4.1 Executive Financial KPIs
- **Endpoint**: `GET /api/admin/dashboard`
- **Access**: `ADMIN` role only
- **Response `200 OK`**:
```json
{
  "today_metrics": {
    "sales_volume": 450.00,
    "order_count": 25,
    "airtime_sales": 200.00,
    "data_sales": 250.00,
    "successful_transactions": 25,
    "pending_transactions": 2,
    "failed_transactions": 1
  },
  "financial_ledger_summary": {
    "provider_clearing_balance": 450.00,
    "business_revenue_accumulated": 450.00,
    "fee_income": 0.00,
    "commission_expense": 4.50,
    "estimated_net_profit": 15.75
  },
  "business_status": {
    "active_agents": 3,
    "currency": "GHS",
    "timezone": "Africa/Accra"
  }
}
```

### 4.2 Export Transactions CSV
- **Endpoint**: `GET /api/admin/reports/export-csv`
- **Access**: `ADMIN` role only
- **Response**: Downloadable `ghana_fintech_transactions_YYYY-MM-DD.csv`.
