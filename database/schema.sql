-- ==============================================================================
-- GHANA FINTECH PLATFORM: DATABASE SCHEMA (MySQL 8.0)
-- Currency: Ghana Cedis (GHS) | Africa/Accra Timezone
-- Precision: DECIMAL(12, 4) for accounting, DECIMAL(10, 2) for standard currency
-- ==============================================================================

CREATE DATABASE IF NOT EXISTS ghana_fintech_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE ghana_fintech_db;

-- 1. Roles & Permissions
CREATE TABLE IF NOT EXISTS roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(255) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS permissions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description VARCHAR(255) NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS role_permissions (
    role_id INT NOT NULL,
    permission_id INT NOT NULL,
    PRIMARY KEY (role_id, permission_id),
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 2. Users Table
CREATE TABLE IF NOT EXISTS users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(191) NOT NULL UNIQUE,
    phone_number VARCHAR(20) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role_id INT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_phone (phone_number),
    INDEX idx_user_email (email),
    FOREIGN KEY (role_id) REFERENCES roles(id)
) ENGINE=InnoDB;

-- 3. Customer & Agent Profiles
CREATE TABLE IF NOT EXISTS customers (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL UNIQUE,
    full_name VARCHAR(150) NOT NULL,
    momo_number VARCHAR(20) NULL,
    momo_network ENUM('MTN', 'TELECEL', 'AT') NULL,
    wallet_balance DECIMAL(12, 4) NOT NULL DEFAULT 0.0000,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS agents (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL UNIQUE,
    agent_code VARCHAR(30) NOT NULL UNIQUE,
    business_name VARCHAR(150) NOT NULL,
    location VARCHAR(200) NOT NULL,
    commission_balance DECIMAL(12, 4) NOT NULL DEFAULT 0.0000,
    wallet_balance DECIMAL(12, 4) NOT NULL DEFAULT 0.0000,
    status ENUM('ACTIVE', 'SUSPENDED', 'PENDING') NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_agent_code (agent_code),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 4. Networks & Products
CREATE TABLE IF NOT EXISTS networks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(20) NOT NULL UNIQUE, -- MTN, TELECEL, AT
    name VARCHAR(100) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    airtime_supported BOOLEAN NOT NULL DEFAULT TRUE,
    data_supported BOOLEAN NOT NULL DEFAULT TRUE,
    bill_supported BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(150) NOT NULL,
    category ENUM('AIRTIME', 'DATA_BUNDLE', 'MOMO_TRANSFER', 'MOMO_CASHOUT', 'UTILITY_BILL') NOT NULL,
    network_id INT NULL,
    wholesale_price DECIMAL(12, 4) NOT NULL DEFAULT 0.0000,
    retail_price DECIMAL(12, 4) NOT NULL DEFAULT 0.0000,
    min_amount DECIMAL(10, 2) NOT NULL DEFAULT 1.00,
    max_amount DECIMAL(10, 2) NOT NULL DEFAULT 5000.00,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (network_id) REFERENCES networks(id) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS data_bundle_plans (
    id INT AUTO_INCREMENT PRIMARY KEY,
    network_id INT NOT NULL,
    product_id INT NULL,
    plan_code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    volume_mb INT NOT NULL, -- in Megabytes (e.g., 1000 for 1GB)
    validity_days INT NOT NULL DEFAULT 30, -- 0 for non-expiry / flexi
    wholesale_price DECIMAL(12, 4) NOT NULL,
    retail_price DECIMAL(12, 4) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_bundle_network (network_id),
    FOREIGN KEY (network_id) REFERENCES networks(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS pricing_rules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NULL,
    network_id INT NULL,
    min_amount DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    max_amount DECIMAL(10, 2) NOT NULL DEFAULT 100000.00,
    fee_fixed DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    fee_percent DECIMAL(5, 4) NOT NULL DEFAULT 0.0000, -- e.g., 0.0100 for 1%
    agent_commission_percent DECIMAL(5, 4) NOT NULL DEFAULT 0.0050, -- 0.5%
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (network_id) REFERENCES networks(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 5. Orders & Order Items
CREATE TABLE IF NOT EXISTS orders (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    order_reference VARCHAR(64) NOT NULL UNIQUE,
    user_id BIGINT NOT NULL,
    agent_id BIGINT NULL,
    order_type ENUM('AIRTIME', 'DATA_BUNDLE', 'MOMO_TRANSFER', 'MOMO_CASHOUT', 'UTILITY_BILL') NOT NULL,
    recipient_phone VARCHAR(20) NOT NULL,
    network_code VARCHAR(20) NOT NULL,
    total_amount DECIMAL(12, 4) NOT NULL,
    fee_amount DECIMAL(12, 4) NOT NULL DEFAULT 0.0000,
    net_amount DECIMAL(12, 4) NOT NULL,
    status ENUM('PENDING', 'PAID', 'PROCESSING', 'COMPLETED', 'FAILED', 'CANCELLED', 'REFUNDED') NOT NULL DEFAULT 'PENDING',
    payment_status ENUM('UNPAID', 'PENDING', 'PAID', 'FAILED', 'REFUNDED') NOT NULL DEFAULT 'UNPAID',
    fulfillment_status ENUM('UNFULFILLED', 'QUEUED', 'FULFILLED', 'FAILED', 'NOT_APPLICABLE') NOT NULL DEFAULT 'UNFULFILLED',
    fulfillment_provider VARCHAR(50) NULL,
    fulfillment_reference VARCHAR(100) NULL,
    failure_reason VARCHAR(255) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_order_ref (order_reference),
    INDEX idx_order_user (user_id),
    INDEX idx_order_status (status),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (agent_id) REFERENCES agents(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS order_items (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    order_id BIGINT NOT NULL,
    product_id INT NULL,
    data_bundle_plan_id INT NULL,
    quantity INT NOT NULL DEFAULT 1,
    unit_price DECIMAL(12, 4) NOT NULL,
    total_price DECIMAL(12, 4) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (data_bundle_plan_id) REFERENCES data_bundle_plans(id)
) ENGINE=InnoDB;

-- 6. Transactions & Payment Attempts
CREATE TABLE IF NOT EXISTS transactions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    transaction_reference VARCHAR(64) NOT NULL UNIQUE,
    order_id BIGINT NULL,
    user_id BIGINT NOT NULL,
    transaction_type ENUM('COLLECTION', 'DISBURSEMENT', 'TRANSFER', 'COMMISSION_PAYOUT', 'REFUND') NOT NULL,
    payment_method ENUM('MOMO_MTN', 'MOMO_TELECEL', 'MOMO_AT', 'PAYSTACK_CARD', 'CASH_AGENT', 'WALLET') NOT NULL,
    amount DECIMAL(12, 4) NOT NULL,
    fee DECIMAL(12, 4) NOT NULL DEFAULT 0.0000,
    net_amount DECIMAL(12, 4) NOT NULL,
    currency VARCHAR(5) NOT NULL DEFAULT 'GHS',
    status ENUM('PENDING', 'PROCESSING', 'SUCCESSFUL', 'FAILED', 'TIMED_OUT', 'REVERSED') NOT NULL DEFAULT 'PENDING',
    provider_name VARCHAR(50) NOT NULL, -- MTN_MOMO, HUBTEL, PAYSTACK
    provider_reference VARCHAR(100) NULL, -- Gateway UUID / ID
    external_id VARCHAR(100) NULL,
    customer_phone VARCHAR(20) NOT NULL,
    error_message VARCHAR(255) NULL,
    metadata_json JSON NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_trx_ref (transaction_reference),
    INDEX idx_trx_provider_ref (provider_reference),
    INDEX idx_trx_status (status),
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE SET NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS payment_attempts (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    transaction_id BIGINT NOT NULL,
    attempt_number INT NOT NULL DEFAULT 1,
    http_status_code INT NULL,
    request_headers JSON NULL,
    request_payload JSON NULL,
    response_payload JSON NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (transaction_id) REFERENCES transactions(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS provider_callbacks (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    provider_name VARCHAR(50) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    provider_reference VARCHAR(100) NULL,
    payload_json JSON NOT NULL,
    signature VARCHAR(255) NULL,
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    processed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_cb_prov_ref (provider_reference)
) ENGINE=InnoDB;

-- 7. APPEND-ONLY FINANCIAL LEDGER
-- Ensures double-entry consistency; records debit and credit entries with running balances.
CREATE TABLE IF NOT EXISTS financial_ledger (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    entry_reference VARCHAR(64) NOT NULL UNIQUE,
    transaction_id BIGINT NULL,
    order_id BIGINT NULL,
    account_type ENUM(
        'CUSTOMER_WALLET',
        'AGENT_WALLET',
        'BUSINESS_REVENUE',
        'PROVIDER_CLEARING',
        'FEE_INCOME',
        'COMMISSION_EXPENSE',
        'REVERSAL_SUSPENSE'
    ) NOT NULL,
    entry_type ENUM('DEBIT', 'CREDIT') NOT NULL,
    amount DECIMAL(12, 4) NOT NULL,
    balance_after DECIMAL(12, 4) NOT NULL,
    description VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_ledger_account (account_type),
    INDEX idx_ledger_trx (transaction_id),
    FOREIGN KEY (transaction_id) REFERENCES transactions(id) ON DELETE SET NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- 8. Agent Commissions & Settlements
CREATE TABLE IF NOT EXISTS commissions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    agent_id BIGINT NOT NULL,
    order_id BIGINT NOT NULL,
    transaction_id BIGINT NULL,
    amount DECIMAL(12, 4) NOT NULL,
    rate_applied DECIMAL(5, 4) NOT NULL,
    status ENUM('EARNED', 'PAID', 'CLAWED_BACK') NOT NULL DEFAULT 'EARNED',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (agent_id) REFERENCES agents(id),
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (transaction_id) REFERENCES transactions(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- 9. Refunds & Reversals
CREATE TABLE IF NOT EXISTS refunds (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    order_id BIGINT NOT NULL,
    original_transaction_id BIGINT NOT NULL,
    refund_transaction_id BIGINT NULL,
    amount DECIMAL(12, 4) NOT NULL,
    reason VARCHAR(255) NOT NULL,
    status ENUM('REQUESTED', 'APPROVED', 'PROCESSED', 'REJECTED') NOT NULL DEFAULT 'REQUESTED',
    approved_by BIGINT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (original_transaction_id) REFERENCES transactions(id),
    FOREIGN KEY (refund_transaction_id) REFERENCES transactions(id) ON DELETE SET NULL,
    FOREIGN KEY (approved_by) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- 10. Audit Logs, Notifications & Settings
CREATE TABLE IF NOT EXISTS audit_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NULL,
    action VARCHAR(100) NOT NULL,
    ip_address VARCHAR(45) NULL,
    user_agent VARCHAR(255) NULL,
    details_json JSON NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_audit_user (user_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS notifications (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NULL,
    recipient VARCHAR(100) NOT NULL,
    channel ENUM('SMS', 'PUSH', 'EMAIL') NOT NULL DEFAULT 'SMS',
    template VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    status ENUM('PENDING', 'SENT', 'FAILED') NOT NULL DEFAULT 'PENDING',
    provider_response VARCHAR(255) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS integration_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    provider_name VARCHAR(50) NOT NULL UNIQUE,
    is_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    is_sandbox BOOLEAN NOT NULL DEFAULT TRUE,
    config_json JSON NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;
