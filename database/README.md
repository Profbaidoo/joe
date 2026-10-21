# Database Architecture & Management (MySQL 8.0)

This directory contains the database definition files for the Ghana Fintech Platform.

## Files

1. `schema.sql`: Complete normalized MySQL 8.0 DDL schema with primary keys, foreign key constraints, indexes, and decimal precision (`DECIMAL(12, 4)` and `DECIMAL(10, 2)`).
2. `seed_data.sql`: Raw SQL seeding script for default roles, telecommunication networks (MTN, Telecel, AT), products, data bundle packages, pricing rules, and default integration settings.

---

## 1. Initializing MySQL Database

```bash
# Connect to your MySQL 8.0 Server
mysql -u root -p < schema.sql

# Seed initial telco networks, products, and bundles
mysql -u root -p ghana_fintech_db < seed_data.sql
```

---

## 2. Append-Only Financial Ledger Principles

Monetary movements are recorded inside the `financial_ledger` table using double-entry style balancing:
- Direct updates (`UPDATE financial_ledger SET ...`) and deletions (`DELETE FROM financial_ledger`) are strictly prohibited in application logic.
- When an order is completed:
  1. `PROVIDER_CLEARING` is debited with the gross amount.
  2. `BUSINESS_REVENUE` is credited with the net amount.
  3. `FEE_INCOME` is credited with the platform fee (if applicable).
  4. If an agent placed the order, `COMMISSION_EXPENSE` is debited and `AGENT_WALLET` is credited.
- Reversals and refunds are recorded as explicit compensating entries (`REVERSAL_SUSPENSE` / `BUSINESS_REVENUE` debit), preserving an unbroken financial audit trail.
