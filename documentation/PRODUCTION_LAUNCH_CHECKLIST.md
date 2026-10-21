# Production Launch & Go-Live Checklist

This checklist must be satisfied before enabling real-money transactions on the Ghana Fintech Platform.

---

## 1. Regulatory & Commercial Approvals (Ghana)

- [ ] **Bank of Ghana (BoG) Licensing**: Confirm compliance as a Dedicated Electronic Money Issuer (DEMI) or Payment Service Provider (PSP) partner under the Payment Systems and Services Act, 2019 (Act 987).
- [ ] **Data Protection Commission (DPC) Registration**: Register business with the Ghana Data Protection Commission pursuant to the Data Protection Act, 2012 (Act 843).
- [ ] **MTN Business MoMo Agreement**: Execute official merchant onboarding contract with MTN Ghana.
- [ ] **Airtime Aggregator SLA**: Execute developer SLA with Hubtel, Reloadly, or direct Telco aggregators for wholesale airtime discounts and API access.

---

## 2. API Credentials & Environment Variables

- [ ] Transition `APP_ENV` from `development` to `production`.
- [ ] Generate cryptographically secure `SECRET_KEY` (minimum 64 characters hex).
- [ ] Generate cryptographically secure `JWT_SECRET_KEY` (minimum 64 characters hex).
- [ ] Set `MOMO_BASE_URL` to `https://proxy.momoapi.mtn.com` (Live Production URL).
- [ ] Set `MOMO_TARGET_ENVIRONMENT` to `mtnghana` (or official production environment string).
- [ ] Verify `MOMO_COLLECTION_SUBSCRIPTION_KEY` is production-approved.
- [ ] Verify `AIRTIME_PROVIDER` is set to live provider (`HUBTEL`, `RELOADLY`, or direct telco) with verified API credentials.
- [ ] Ensure `MOCK` provider is strictly prohibited in production.

---

## 3. Infrastructure & Cybersecurity

- [ ] **HTTPS / SSL Enforced**: Valid TLS 1.3 certificate configured with automatic renewal.
- [ ] **No Client Secrets**: Confirm no API keys or database connection strings are embedded in frontend web or React Native Expo bundles.
- [ ] **Zero PIN Storage**: Guarantee that customer Mobile Money PINs and OTPs are NEVER collected or logged on server storage.
- [ ] **Database Backups**: Automated daily encrypted MySQL backups with offsite replication.
- [ ] **Rate Limiting**: NGINX / Cloudflare rate limiting enabled to prevent brute-force attacks on `/api/auth/login` and `/api/payments/momo/request`.
- [ ] **Log Scrubbing**: Verify logging masks all sensitive customer identifiers and transaction secrets.

---

## 4. Financial Reconciliation

- [ ] Automated background reconciliation worker running via systemd or supervisord.
- [ ] Daily automated check comparing `financial_ledger` balances against MTN MoMo Merchant settlement statements.
- [ ] Alerting configured for discrepancies exceeding GH₵ 0.00.
