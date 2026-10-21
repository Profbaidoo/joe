# Required External Accounts, Approvals & API Credentials

The table below outlines all third-party registrations, external developer portals, and credentials required to operate the application in sandbox and production.

---

| Provider / Entity | Required Account / Portal | Portal URL | Required Credentials | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **MTN MoMo Developer** (Sandbox) | MTN MoMo Developer Portal | [momodeveloper.mtn.com](https://momodeveloper.mtn.com) | `MOMO_COLLECTION_SUBSCRIPTION_KEY`, `MOMO_API_USER`, `MOMO_API_KEY` | Testing collections & payment status |
| **MTN MoMo Business** (Production) | MTN Ghana Corporate Portal | Direct Business Relationship | `MOMO_COLLECTION_SUBSCRIPTION_KEY` (Prod), Production API User, KYC Merchant Onboarding | Live GHS collection from MTN subscribers |
| **Hubtel Developer** | Hubtel Merchant Portal | [hubtel.com](https://hubtel.com) | `HUBTEL_CLIENT_ID`, `HUBTEL_CLIENT_SECRET`, `HUBTEL_MERCHANT_ACCOUNT_NUMBER` | Alternative collections, Airtime dispatch & ECG Bills |
| **Paystack Ghana** | Paystack Dashboard | [dashboard.paystack.com](https://dashboard.paystack.com) | `PAYSTACK_PUBLIC_KEY`, `PAYSTACK_SECRET_KEY`, `PAYSTACK_WEBHOOK_SECRET` | Bank Cards & Multi-network MoMo |
| **Airtime Aggregator** | Reloadly / Hubtel / Telco Partner | Merchant API Dashboard | `AIRTIME_API_KEY`, `AIRTIME_API_SECRET`, `AIRTIME_API_BASE_URL` | Live airtime top-up & data bundle activation |
| **SMS Gateway** | Arkesel / MNotify / Hubtel SMS | Developer SMS Portal | `SMS_API_KEY`, `SMS_SENDER_ID` | Sending customer order receipts & prompt alerts |
| **Bank of Ghana** | BoG Fintech Regulatory Sandbox | [bog.gov.gh](https://www.bog.gov.gh) | Regulatory Certificate / License | Commercial DFS compliance in Ghana |
| **Data Protection Commission** | Ghana DPC Portal | [dataprotection.org.gh](https://dataprotection.org.gh) | DPC Registration Certificate | Customer privacy compliance |
