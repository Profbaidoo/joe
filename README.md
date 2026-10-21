# Ghana Mobile Money, Airtime & Data Bundle Platform

A secure, responsive, and production-ready fintech application tailored for Ghanaian businesses providing:
- **Mobile Money (MoMo) Services**: Official MTN MoMo Open API collections and disbursements.
- **Airtime Sales**: Instant top-ups for MTN, Telecel, and AT networks.
- **Data Bundle Purchases**: Direct activation of high-speed 4G/5G and non-expiry bundles.
- **Customer Deposits & Payments**: Automated collection prompts with callback reconciliation.
- **ECG & Utility Bill Payments**: Electricity Company of Ghana prepaid and postpaid settlement.
- **Append-Only Financial Ledger**: Double-entry accounting preventing silent data modification.
- **Agent Commissions & Reporting**: Real-time sales tracking, commission calculations, and profit analysis.
- **Standard Ghanaian Format**: Ghana Cedis (`GHS` / `GH₵`), Ghanaian phone numbers (`024...`, `054...`, `020...`, `027...`), and `Africa/Accra` timezone.

---

## 1. Technology Stack

- **Mobile Application**: React Native with Expo and TypeScript (`frontend/mobile/`).
- **Web Admin Dashboard**: React 18, TypeScript, Vite, Tailwind CSS (`frontend/web-admin/`).
- **Backend API**: Python 3 with Flask, SQLAlchemy ORM, Flask-Migrate, JWT-Extended, Flasgger OpenAPI (`backend/`).
- **Database**: MySQL 8.0 with Decimal precision (`DECIMAL(12, 4)`) and SQLite fallback for local unit tests.
- **Integrations**: MTN MoMo Open API, Hubtel Aggregator, Paystack, Universal Airtime/Data Provider Adapter (`integrations/`).
- **Background Worker**: Python reconciliation worker for payment polling, retries, and notification dispatching.

---

## 2. Directory Structure

```
├── backend/                       # Flask REST API, Models, Services & Tasks
│   ├── app/                       # Application package (Auth, Products, Orders, Payments)
│   ├── tests/                     # 100% passing Pytest automated test suite
│   ├── run.py                     # Backend entry point
│   ├── seed.py                    # Database seeding script (Admin, Cashier, Products)
│   └── requirements.txt           # Python dependencies
├── database/                      # Database DDL & Schema Definitions
│   ├── schema.sql                 # MySQL 8.0 DDL schema with constraints & indexes
│   ├── seed_data.sql              # Initial networks, products, bundle plans
│   └── README.md
├── integrations/                  # Dedicated External Provider Adapters
│   ├── momo/                      # MTN MoMo Collections, Status & Sandbox Provisioning
│   ├── hubtel/                    # Hubtel API Client & HMAC Webhook Validator
│   ├── paystack/                  # Paystack Client & Signature Verification
│   ├── airtime/                   # Universal Airtime & Data Bundle Distribution Client
│   └── README.md
├── frontend/
│   ├── web-admin/                 # React + TypeScript Web Admin Dashboard
│   └── mobile/                    # React Native + Expo Mobile Application
├── documentation/
│   ├── API_SPECIFICATION.md       # Comprehensive REST API reference with examples
│   ├── OPENAPI.json               # Full OpenAPI 3.0.0 Specification
│   ├── SANDBOX_TESTING_GUIDE.md   # MTN MoMo sandbox onboarding & testing manual
│   ├── PRODUCTION_LAUNCH_CHECKLIST.md # Bank of Ghana & cybersecurity checklist
│   └── REQUIRED_CREDENTIALS.md    # External accounts and credentials directory
├── .env.example                   # Full environment configuration template
└── README.md                      # Beginner-friendly setup manual
```

---

## 3. Quick Start (Beginner-Friendly Setup)

### Prerequisites
- Python 3.10+ installed
- Node.js v18+ and npm installed
- MySQL 8.0 (optional for local SQLite dev testing)

---

### Step 1: Backend Setup & Seeding

1. Open PowerShell / Terminal in the project root:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
3. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
4. Copy the environment variables:
   ```powershell
   cp ..\.env.example ..\.env
   ```
5. Seed the database with default networks, products, data plans, and demo users:
   ```powershell
   python seed.py
   ```
   *Created Demo Accounts:*
   - **Admin (Owner)**: Username `admin` / Password `Admin1234!` (Phone: `0240000000`)
   - **Cashier (Agent)**: Username `cashier1` / Password `Agent1234!` (Phone: `0241111111`)
   - **Customer**: Username `kwame_mensah` / Password `Customer1234!` (Phone: `0242222222`)

6. Start the Backend API:
   ```powershell
   python run.py
   ```
   The backend will be running at `http://127.0.0.1:5000`.
   Explore the interactive OpenAPI/Swagger docs at `http://127.0.0.1:5000/api/docs/`.

---

### Step 2: Running Automated Tests

Run the complete test suite to verify authentication, pricing, MoMo sandbox flows, double-entry ledgering, and fulfillment:
```powershell
$env:PYTHONPATH="C:\Users\DELL\Desktop\blessings\backend"
pytest tests -v
```
All 14 unit and integration tests will execute and pass.

---

### Step 3: Web Admin Dashboard Setup

1. Open a new terminal in the `frontend/web-admin/` folder:
   ```bash
   cd frontend/web-admin
   npm install
   npm run dev
   ```
2. Open your browser at `http://localhost:5173`.
3. Click **Admin (Owner)** on the login screen to sign in with pre-filled demo credentials.
4. Access:
   - **Financial Dashboard**: Real-time sales volume, net profit, and ledger summaries.
   - **Transactions & Receipts**: Full transaction ledger with instant digital receipts.
   - **Products & Pricing**: Adjust wholesale costs and retail margins.
   - **MoMo Sandbox Test Bench**: Live simulator for testing MTN MoMo request-to-pay prompts and status reconciliation.

---

### Step 4: Mobile Application Setup (React Native Expo)

1. Open a new terminal in the `frontend/mobile/` folder:
   ```bash
   cd frontend/mobile
   npm install
   npm start
   ```
2. Press `w` to open in your web browser, or scan the QR code using the **Expo Go** app on your Android or iOS device.

---

## 4. Key Security & Compliance Guarantees

1. **Zero Customer PIN Handling**: Customer Mobile Money PINs and OTPs are never collected, prompted for, or stored by the application. Authorizations occur strictly on subscriber handsets via official USSD prompt.
2. **Never Treat 202 as Completed**: HTTP 202 from MTN MoMo Collections indicates the prompt was sent, NOT that money was collected. Payments are marked `PAID` only after verified webhook or status polling.
3. **Double-Entry Financial Ledger**: All monetary movements append debit and credit entries to `financial_ledger`. Manual cell overwrites on completed financial records are blocked.
4. **Idempotency Protection**: Every order and transaction generates unique, non-colliding references enforced by database unique constraints.
5. **Ghana MSISDN Validation**: Strict prefix detection (MTN: 024, 054, 055...; Telecel: 020, 050; AT: 027, 026...). Mismatched phone numbers and telcos are rejected immediately before checkout.
