-- Migration: Add OAuth fields to users table
-- Date: 2026-01-06
-- Description: Add support for OAuth authentication providers (Microsoft, Google)

-- Add OAuth provider fields
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS oauth_provider VARCHAR(50),
ADD COLUMN IF NOT EXISTS oauth_id VARCHAR(255),
ADD COLUMN IF NOT EXISTS profile_picture VARCHAR(500);

-- Add index for faster OAuth lookups
CREATE INDEX IF NOT EXISTS idx_users_oauth ON users(oauth_provider, oauth_id);

-- Add index for email lookups (useful for OAuth user matching)
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Add comments for documentation
COMMENT ON COLUMN users.oauth_provider IS 'OAuth provider: microsoft, google, or NULL for traditional auth';
COMMENT ON COLUMN users.oauth_id IS 'Unique user ID from OAuth provider';
COMMENT ON COLUMN users.profile_picture IS 'URL to user profile picture from OAuth provider';

-- Make hashed_password optional for OAuth users (they don't need a password)
ALTER TABLE users 
ALTER COLUMN hashed_password DROP NOT NULL;

-- Add constraint to ensure OAuth users have both provider and ID
ALTER TABLE users 
ADD CONSTRAINT check_oauth_complete 
CHECK (
    (oauth_provider IS NULL AND oauth_id IS NULL) OR 
    (oauth_provider IS NOT NULL AND oauth_id IS NOT NULL)
);

-- Verify the changes
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'users' 
AND column_name IN ('oauth_provider', 'oauth_id', 'profile_picture', 'hashed_password');

-- Success message
DO $$ 
BEGIN 
    RAISE NOTICE 'OAuth fields successfully added to users table';
END $$;
