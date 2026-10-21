-- ==============================================================================
-- GHANA FINTECH PLATFORM: SEED DATA
-- Default Roles, Permissions, Networks, Products, Data Bundles & Settings
-- ==============================================================================

USE ghana_fintech_db;

-- 1. Default Roles
INSERT INTO roles (id, name, description) VALUES
(1, 'ADMIN', 'Business Owner / System Administrator with full operational & financial control'),
(2, 'AGENT', 'Cashier or Retail Agent permitted to sell airtime, data and process transactions'),
(3, 'CUSTOMER', 'Registered end customer purchasing services directly')
ON DUPLICATE KEY UPDATE description=VALUES(description);

-- 2. Permissions
INSERT INTO permissions (name, description) VALUES
('dashboard:view', 'View business KPIs, revenues and profits'),
('orders:create', 'Create and submit airtime/data/momo orders'),
('orders:view_all', 'View all transactions and customer orders'),
('products:manage', 'Configure catalog, products and data bundle plans'),
('pricing:manage', 'Adjust retail prices, margins and commissions'),
('agents:manage', 'Create and oversee agents, cashiers and settlements'),
('reconciliation:run', 'Trigger manual and automated payment reconciliation'),
('settings:configure', 'Manage API keys and integration settings')
ON DUPLICATE KEY UPDATE description=VALUES(description);

-- 3. Telecommunication Networks in Ghana
INSERT INTO networks (id, code, name, is_active, airtime_supported, data_supported, bill_supported) VALUES
(1, 'MTN', 'MTN Ghana (Scancom PLC)', TRUE, TRUE, TRUE, FALSE),
(2, 'TELECEL', 'Telecel Ghana (Formerly Vodafone Ghana)', TRUE, TRUE, TRUE, FALSE),
(3, 'AT', 'AT Ghana (Formerly AirtelTigo)', TRUE, TRUE, TRUE, FALSE)
ON DUPLICATE KEY UPDATE name=VALUES(name);

-- 4. Products Catalog
INSERT INTO products (id, code, name, category, network_id, wholesale_price, retail_price, min_amount, max_amount, is_active) VALUES
(1, 'AIRTIME_MTN', 'MTN Airtime Top-up', 'AIRTIME', 1, 0.9800, 1.0000, 1.00, 2000.00, TRUE),
(2, 'AIRTIME_TELECEL', 'Telecel Airtime Top-up', 'AIRTIME', 2, 0.9700, 1.0000, 1.00, 2000.00, TRUE),
(3, 'AIRTIME_AT', 'AT Airtime Top-up', 'AIRTIME', 3, 0.9600, 1.0000, 1.00, 2000.00, TRUE),
(4, 'DATA_MTN', 'MTN High-Speed Internet Bundle', 'DATA_BUNDLE', 1, 0.0000, 0.0000, 5.00, 500.00, TRUE),
(5, 'DATA_TELECEL', 'Telecel Broadband & Mobile Data', 'DATA_BUNDLE', 2, 0.0000, 0.0000, 5.00, 500.00, TRUE),
(6, 'DATA_AT', 'AT Big Time Data Bundle', 'DATA_BUNDLE', 3, 0.0000, 0.0000, 5.00, 500.00, TRUE),
(7, 'MOMO_TRANSFER', 'Mobile Money Peer-to-Peer Transfer', 'MOMO_TRANSFER', NULL, 0.0000, 0.0000, 1.00, 5000.00, TRUE),
(8, 'MOMO_CASHOUT', 'Agent MoMo Cash-out / Withdrawal', 'MOMO_CASHOUT', NULL, 0.0000, 0.0000, 5.00, 5000.00, TRUE),
(9, 'BILL_ECG', 'Electricity Company of Ghana (ECG) Prepaid/Postpaid', 'UTILITY_BILL', NULL, 0.0000, 0.0000, 5.00, 2000.00, TRUE)
ON DUPLICATE KEY UPDATE name=VALUES(name);

-- 5. Standard Ghanaian Data Bundle Packages
INSERT INTO data_bundle_plans (network_id, product_id, plan_code, name, volume_mb, validity_days, wholesale_price, retail_price, is_active) VALUES
-- MTN Packages
(1, 4, 'MTN_1GB', 'MTN 1GB Data Bundle', 1024, 30, 10.5000, 12.0000, TRUE),
(1, 4, 'MTN_2_5GB', 'MTN 2.5GB Data Bundle', 2560, 30, 22.0000, 25.0000, TRUE),
(1, 4, 'MTN_5GB', 'MTN 5GB Data Bundle', 5120, 30, 36.0000, 40.0000, TRUE),
(1, 4, 'MTN_10GB', 'MTN 10GB Non-Expiry Bundle', 10240, 0, 68.0000, 75.0000, TRUE),
(1, 4, 'MTN_20GB', 'MTN 20GB Non-Expiry Bundle', 20480, 0, 122.0000, 135.0000, TRUE),
(1, 4, 'MTN_50GB', 'MTN 50GB Mega Bundle', 51200, 60, 230.0000, 250.0000, TRUE),

-- Telecel Packages
(2, 5, 'TELECEL_1_5GB', 'Telecel 1.5GB Data Bundle', 1536, 30, 10.0000, 12.0000, TRUE),
(2, 5, 'TELECEL_3GB', 'Telecel 3GB Data Bundle', 3072, 30, 19.5000, 22.0000, TRUE),
(2, 5, 'TELECEL_6GB', 'Telecel 6GB Non-Expiry Bundle', 6144, 0, 34.0000, 38.0000, TRUE),
(2, 5, 'TELECEL_12GB', 'Telecel 12GB Non-Expiry Bundle', 12288, 0, 62.0000, 70.0000, TRUE),
(2, 5, 'TELECEL_25GB', 'Telecel 25GB Super Bundle', 25600, 30, 118.0000, 130.0000, TRUE),

-- AT Packages
(3, 6, 'AT_2GB', 'AT 2GB Big Time Data', 2048, 0, 8.5000, 10.0000, TRUE),
(3, 6, 'AT_4_5GB', 'AT 4.5GB Big Time Data', 4608, 0, 17.0000, 20.0000, TRUE),
(3, 6, 'AT_10GB', 'AT 10GB Big Time Data', 10240, 0, 30.0000, 35.0000, TRUE),
(3, 6, 'AT_25GB', 'AT 25GB Non-Expiry Data', 25600, 0, 70.0000, 80.0000, TRUE),
(3, 6, 'AT_50GB', 'AT 50GB Heavy User Data', 51200, 0, 135.0000, 150.0000, TRUE)
ON DUPLICATE KEY UPDATE name=VALUES(name), retail_price=VALUES(retail_price);

-- 6. Pricing Rules & Commission Tier Settings
INSERT INTO pricing_rules (product_id, network_id, min_amount, max_amount, fee_fixed, fee_percent, agent_commission_percent) VALUES
(1, 1, 1.00, 5000.00, 0.00, 0.0000, 0.0080), -- 0.8% agent commission on MTN airtime
(2, 2, 1.00, 5000.00, 0.00, 0.0000, 0.0100), -- 1.0% agent commission on Telecel airtime
(3, 3, 1.00, 5000.00, 0.00, 0.0000, 0.0120), -- 1.2% agent commission on AT airtime
(4, 1, 5.00, 500.00, 0.00, 0.0000, 0.0150),  -- 1.5% commission on MTN data
(5, 2, 5.00, 500.00, 0.00, 0.0000, 0.0180),  -- 1.8% commission on Telecel data
(6, 3, 5.00, 500.00, 0.00, 0.0000, 0.0200)   -- 2.0% commission on AT data
ON DUPLICATE KEY UPDATE agent_commission_percent=VALUES(agent_commission_percent);

-- 7. Integration Settings (Initial Defaults)
INSERT INTO integration_settings (provider_name, is_enabled, is_sandbox, config_json) VALUES
('MTN_MOMO', TRUE, TRUE, '{"mode": "sandbox", "currency": "GHS", "target_env": "sandbox"}'),
('HUBTEL', FALSE, TRUE, '{"mode": "sandbox"}'),
('PAYSTACK', FALSE, TRUE, '{"mode": "test", "channels": ["card", "mobile_money"]}'),
('AIRTIME_AGGREGATOR', TRUE, TRUE, '{"provider": "MOCK", "auto_retry": true, "max_retries": 3}')
ON DUPLICATE KEY UPDATE is_sandbox=VALUES(is_sandbox);
