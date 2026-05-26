-- RADIUS System Database Schema
-- FreeRADIUS standard tables + management tables

-- ============================================================
-- Users (web management + RADIUS users)
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id              SERIAL PRIMARY KEY,
    username        VARCHAR(64) NOT NULL UNIQUE,
    email           VARCHAR(255),
    password_hash   VARCHAR(255) NOT NULL,
    role            VARCHAR(16) NOT NULL DEFAULT 'user'
                        CHECK (role IN ('admin', 'user')),
    enabled         BOOLEAN NOT NULL DEFAULT TRUE,
    note            TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_users_username ON users (username);
CREATE INDEX IF NOT EXISTS idx_users_role ON users (role);

-- ============================================================
-- OTP Devices
-- ============================================================
CREATE TABLE IF NOT EXISTS otp_devices (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    secret      VARCHAR(255) NOT NULL,
    enabled     BOOLEAN NOT NULL DEFAULT FALSE,
    device_name VARCHAR(64) NOT NULL DEFAULT 'default',
    last_used_at TIMESTAMPTZ,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_otp_devices_user_id ON otp_devices (user_id);

-- ============================================================
-- NAS Clients (RADIUS clients)
-- ============================================================
CREATE TABLE IF NOT EXISTS nas_clients (
    id          SERIAL PRIMARY KEY,
    shortname   VARCHAR(64) NOT NULL UNIQUE,
    ip_address  INET NOT NULL,
    secret      VARCHAR(255) NOT NULL,
    radsecret   VARCHAR(255),
    nas_type    VARCHAR(32) NOT NULL DEFAULT 'other',
    description TEXT,
    enabled     BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_nas_clients_ip ON nas_clients (ip_address);

-- ============================================================
-- Readonly Gateways (PAN-OS firewalls for VPN online user queries)
-- ============================================================
CREATE TABLE IF NOT EXISTS readonly_gateways (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(128) NOT NULL,
    host        VARCHAR(255) NOT NULL,
    username    VARCHAR(128) NOT NULL,
    password    VARCHAR(512) NOT NULL,
    description TEXT,
    enabled     BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_readonly_gateways_host ON readonly_gateways (host);

-- ============================================================
-- LDAP Configs (AD server connections for user import)
-- ============================================================
CREATE TABLE IF NOT EXISTS ldap_configs (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(128) NOT NULL,
    host            VARCHAR(255) NOT NULL,
    port            INTEGER NOT NULL DEFAULT 389,
    base_dn         VARCHAR(512) NOT NULL,
    bind_dn         VARCHAR(512) NOT NULL,
    bind_password   VARCHAR(512) NOT NULL,
    use_tls         BOOLEAN NOT NULL DEFAULT FALSE,
    description     TEXT,
    enabled         BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_ldap_configs_host ON ldap_configs (host);

-- ============================================================
-- Refresh Tokens
-- ============================================================
CREATE TABLE IF NOT EXISTS refresh_tokens (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash  VARCHAR(255) NOT NULL UNIQUE,
    expires_at  TIMESTAMPTZ NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user_id ON refresh_tokens (user_id);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_hash ON refresh_tokens (token_hash);

-- ============================================================
-- FreeRADIUS standard tables
-- ============================================================

-- radcheck: authorization check attributes
CREATE TABLE IF NOT EXISTS radcheck (
    id          SERIAL PRIMARY KEY,
    username    VARCHAR(64) NOT NULL DEFAULT '',
    attribute   VARCHAR(64) NOT NULL DEFAULT '',
    op          VARCHAR(2) NOT NULL DEFAULT '==',
    value       VARCHAR(253) NOT NULL DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_radcheck_username ON radcheck (username);

-- radreply: authorization reply attributes
CREATE TABLE IF NOT EXISTS radreply (
    id          SERIAL PRIMARY KEY,
    username    VARCHAR(64) NOT NULL DEFAULT '',
    attribute   VARCHAR(64) NOT NULL DEFAULT '',
    op          VARCHAR(2) NOT NULL DEFAULT '==',
    value       VARCHAR(253) NOT NULL DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_radreply_username ON radreply (username);

-- radgroupcheck: group check attributes
CREATE TABLE IF NOT EXISTS radgroupcheck (
    id          SERIAL PRIMARY KEY,
    groupname   VARCHAR(64) NOT NULL DEFAULT '',
    attribute   VARCHAR(64) NOT NULL DEFAULT '',
    op          VARCHAR(2) NOT NULL DEFAULT '==',
    value       VARCHAR(253) NOT NULL DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_radgroupcheck_groupname ON radgroupcheck (groupname);

-- radgroupreply: group reply attributes
CREATE TABLE IF NOT EXISTS radgroupreply (
    id          SERIAL PRIMARY KEY,
    groupname   VARCHAR(64) NOT NULL DEFAULT '',
    attribute   VARCHAR(64) NOT NULL DEFAULT '',
    op          VARCHAR(2) NOT NULL DEFAULT '==',
    value       VARCHAR(253) NOT NULL DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_radgroupreply_groupname ON radgroupreply (groupname);

-- usergroup: user-group mapping
CREATE TABLE IF NOT EXISTS usergroup (
    id          SERIAL PRIMARY KEY,
    username    VARCHAR(64) NOT NULL DEFAULT '',
    groupname   VARCHAR(64) NOT NULL DEFAULT '',
    priority    INTEGER NOT NULL DEFAULT 1
);
CREATE INDEX IF NOT EXISTS idx_usergroup_username ON usergroup (username);

-- radacct: accounting records
CREATE TABLE IF NOT EXISTS radacct (
    radacctid               BIGSERIAL PRIMARY KEY,
    acctsessionid           VARCHAR(64) NOT NULL DEFAULT '',
    acctuniqueid            VARCHAR(32) NOT NULL DEFAULT '',
    username                VARCHAR(64) DEFAULT NULL,
    groupname               VARCHAR(64) DEFAULT NULL,
    realm                   VARCHAR(64) DEFAULT NULL,
    nasipaddress            INET NOT NULL DEFAULT '0.0.0.0',
    nasportid               VARCHAR(15) DEFAULT NULL,
    nasporttype             VARCHAR(32) DEFAULT NULL,
    acctstarttime           TIMESTAMPTZ DEFAULT NULL,
    acctupdatetime          TIMESTAMPTZ DEFAULT NULL,
    acctstoptime            TIMESTAMPTZ DEFAULT NULL,
    acctinterval            INTEGER DEFAULT NULL,
    acctinputoctets         BIGINT DEFAULT NULL,
    acctoutputoctets        BIGINT DEFAULT NULL,
    acctinputgigawords      BIGINT DEFAULT NULL,
    acctoutputgigawords     BIGINT DEFAULT NULL,
    accttotalgigawords      BIGINT DEFAULT NULL,
    calledstationid         VARCHAR(50) DEFAULT NULL,
    callingstationid        VARCHAR(50) DEFAULT NULL,
    connectinfo_start       VARCHAR(50) DEFAULT NULL,
    connectinfo_stop        VARCHAR(50) DEFAULT NULL,
    acctterminatecause      VARCHAR(32) DEFAULT NULL,
    servicetype             VARCHAR(32) DEFAULT NULL,
    framedprotocol          VARCHAR(32) DEFAULT NULL,
    framedipaddress         INET DEFAULT NULL
);
CREATE INDEX IF NOT EXISTS idx_radacct_username ON radacct (username);
CREATE INDEX IF NOT EXISTS idx_radacct_starttime ON radacct (acctstarttime);
CREATE INDEX IF NOT EXISTS idx_radacct_nas_ip ON radacct (nasipaddress);
CREATE UNIQUE INDEX IF NOT EXISTS idx_radacct_unique ON radacct (acctuniqueid);

-- radpostauth: post-authentication logs
CREATE TABLE IF NOT EXISTS radpostauth (
    id              BIGSERIAL PRIMARY KEY,
    username        VARCHAR(64) NOT NULL DEFAULT '',
    pass            VARCHAR(64) DEFAULT NULL,
    reply           VARCHAR(32) DEFAULT NULL,
    calledstationid VARCHAR(50) DEFAULT NULL,
    callingstationid VARCHAR(50) DEFAULT NULL,
    authdate        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_radpostauth_username ON radpostauth (username);
CREATE INDEX IF NOT EXISTS idx_radpostauth_authdate ON radpostauth (authdate);

-- ============================================================
-- Groups
-- ============================================================
CREATE TABLE IF NOT EXISTS groups (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(64) NOT NULL UNIQUE,
    description TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- Insert default admin user (password: admin123)
-- bcrypt hash generated for 'admin123'
-- ============================================================
INSERT INTO users (username, password_hash, role, enabled, note)
VALUES ('admin', '$2b$12$AmOBz8s2kDQocoafwFYUUeIrKssRIMUyYSQRCWptfg587xD00npSa', 'admin', TRUE, 'Default admin account')
ON CONFLICT (username) DO NOTHING;

-- Sync admin to radcheck (for RADIUS auth if needed)
INSERT INTO radcheck (username, attribute, op, value)
VALUES ('admin', 'Cleartext-Password', ':=', 'admin123')
ON CONFLICT DO NOTHING;
