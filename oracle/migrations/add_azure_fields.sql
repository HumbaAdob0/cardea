ALTER TABLE users 
ADD COLUMN IF NOT EXISTS azure_oid VARCHAR(255) UNIQUE,
ADD COLUMN IF NOT EXISTS hashed_password VARCHAR(255) NULL;

CREATE INDEX IF NOT EXISTS idx_users_azure_oid ON users(azure_oid);

COMMENT ON COLUMN users.hashed_password IS 'NULL for SSO-only accounts, hashed password for local accounts';