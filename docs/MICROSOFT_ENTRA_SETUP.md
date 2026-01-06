# Microsoft Entra External ID Integration Guide

Complete guide to integrating Microsoft Entra External ID (formerly Azure AD B2C) with the Cardea security platform.

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Azure Portal Setup](#azure-portal-setup)
4. [Backend Configuration](#backend-configuration)
5. [Frontend Configuration](#frontend-configuration)
6. [Database Updates](#database-updates)
7. [Testing the Integration](#testing-the-integration)
8. [Troubleshooting](#troubleshooting)
9. [Security Best Practices](#security-best-practices)

---

## Overview

This integration enables:
- **Single Sign-On (SSO)** with Microsoft accounts
- **Secure authentication** using OAuth 2.0 and OpenID Connect
- **Automatic user provisioning** from Azure AD to your local database
- **Token-based API authentication** for the Oracle backend
- **Seamless user experience** with MSAL.js in React

### Architecture

```
┌─────────────────┐         ┌──────────────────────┐         ┌─────────────────┐
│  React Frontend │ ←────→  │ Microsoft Entra ID   │         │ Oracle Backend  │
│  (MSAL.js)      │         │  (Identity Provider) │         │  (FastAPI)      │
└─────────────────┘         └──────────────────────┘         └─────────────────┘
        │                              │                              │
        │                              │                              │
        └──────────── Access Token ─────────────────────────────────→│
                                       │                              │
                                       └─── Validate Token ──────────┘
```

---

## Prerequisites

Before starting, ensure you have:

- [ ] **Azure Account** with an active subscription
- [ ] **Microsoft Entra ID** tenant (comes free with Azure subscription)
- [ ] **Global Administrator** or **Application Administrator** role in Azure AD
- [ ] **Node.js** (v18 or higher) and **npm** installed
- [ ] **Python** 3.11+ installed
- [ ] **PostgreSQL** database running

---

## Azure Portal Setup

### Step 1: Access Azure Portal

1. Navigate to [https://portal.azure.com](https://portal.azure.com)
2. Sign in with your Microsoft account
3. Search for **"Microsoft Entra ID"** (or **"Azure Active Directory"**)

### Step 2: Register Your Application

1. In the left sidebar, click **"App registrations"**
2. Click **"+ New registration"**
3. Fill in the registration form:

   ```
   Name: Cardea Security Platform
   
   Supported account types: 
   ○ Accounts in this organizational directory only (Single tenant)
   ● Accounts in any organizational directory (Multi-tenant)  ← RECOMMENDED
   ○ Accounts in any organizational directory and personal Microsoft accounts
   
   Redirect URI:
   Platform: Single-page application (SPA)
   URI: http://localhost:5173
   ```

4. Click **"Register"**

### Step 3: Note Your Credentials

After registration, you'll see the **Overview** page. **COPY THESE VALUES**:

```
Application (client) ID: ___________________________________
Directory (tenant) ID:   ___________________________________
```

### Step 4: Create a Client Secret

1. In the left sidebar, click **"Certificates & secrets"**
2. Click **"+ New client secret"**
3. Add a description: `Cardea Backend Secret`
4. Set expiration: **24 months** (or custom)
5. Click **"Add"**
6. **⚠️ IMPORTANT**: Copy the **"Value"** immediately (you won't see it again!)

   ```
   Client Secret Value: ___________________________________
   ```

### Step 5: Configure Authentication Settings

1. In the left sidebar, click **"Authentication"**
2. Under **"Platform configurations"**, find your SPA redirect URI
3. Click **"Add URI"** and add production URI: `https://yourdomain.com`
4. Scroll to **"Implicit grant and hybrid flows"**:
   - ✅ Check **"Access tokens"** (for implicit flow)
   - ✅ Check **"ID tokens"** (for implicit flow)
5. Under **"Advanced settings"**:
   - Set **"Allow public client flows"** to **No**
6. Click **"Save"**

### Step 6: Configure API Permissions

1. In the left sidebar, click **"API permissions"**
2. You should see **"Microsoft Graph"** with **"User.Read"** (default)
3. (Optional) Add additional permissions:
   - Click **"+ Add a permission"**
   - Select **"Microsoft Graph"**
   - Choose **"Delegated permissions"**
   - Search and add:
     - `User.Read` (already there)
     - `email`
     - `profile`
     - `openid`
4. Click **"Grant admin consent for [your tenant]"** (if available)
5. Click **"Yes"** to confirm

### Step 7: Expose an API (For Backend Token Validation)

This allows your backend to validate access tokens:

1. In the left sidebar, click **"Expose an API"**
2. Next to **"Application ID URI"**, click **"Add"**
3. Accept the default (`api://{CLIENT_ID}`) or customize
4. Click **"Save"**
5. Click **"+ Add a scope"**:
   ```
   Scope name: access_as_user
   Who can consent?: Admins and users
   Admin consent display name: Access Cardea as user
   Admin consent description: Allows the app to access Cardea on behalf of the signed-in user
   User consent display name: Access Cardea
   User consent description: Allows the app to access Cardea on your behalf
   State: Enabled
   ```
6. Click **"Add scope"**

### Step 8: Configure Token Settings (Optional)

1. In the left sidebar, click **"Token configuration"**
2. Click **"+ Add optional claim"**
3. Select **"ID"** token type
4. Add these claims:
   - `email`
   - `family_name`
   - `given_name`
5. Click **"Add"**
6. Repeat for **"Access"** token type

---

## Backend Configuration

### Step 1: Update Requirements

The `requirements.txt` has already been updated with:
```txt
msal==1.26.0
cryptography==41.0.7
```

Install the packages:

```bash
cd oracle
pip install -r requirements.txt
```

### Step 2: Configure Environment Variables

1. Copy the template file:
   ```bash
   cd /home/jonrheym/Documents/Project/Web\ Development/cardea
   cp .env.template .env
   ```

2. Open `.env` and fill in your Azure credentials:

   ```bash
   # ============================================================================
   # MICROSOFT ENTRA EXTERNAL ID CONFIGURATION
   # ============================================================================
   AZURE_TENANT_ID=<paste your Directory (tenant) ID>
   AZURE_CLIENT_ID=<paste your Application (client) ID>
   AZURE_CLIENT_SECRET=<paste your Client Secret Value>
   AZURE_AUTHORITY=https://login.microsoftonline.com/<paste your tenant ID>
   
   # ============================================================================
   # SECURITY CONFIGURATION
   # ============================================================================
   SECRET_KEY=<generate a strong random string - at least 32 characters>
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   
   # Database
   DATABASE_URL=postgresql+asyncpg://oracle:oracle_dev_password@localhost:5432/cardea_oracle
   
   # Redis
   REDIS_URL=redis://localhost:6379/0
   
   # Sentry
   SENTRY_WEBHOOK_TOKEN=<generate a random token>
   ```

3. **Generate SECRET_KEY** (run in terminal):
   ```bash
   python3 -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

### Step 3: Update Database Schema

Add Azure-specific fields to the users table:

```bash
cd oracle
```

Create a migration file `migrations/add_azure_fields.sql`:

```sql
-- Add Azure AD integration fields to users table
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS azure_oid VARCHAR(255) UNIQUE,
ADD COLUMN IF NOT EXISTS hashed_password VARCHAR(255) NULL;  -- Make optional for SSO users

-- Create index for faster Azure OID lookups
CREATE INDEX IF NOT EXISTS idx_users_azure_oid ON users(azure_oid);

-- Update existing users to allow NULL passwords (for SSO-only accounts)
COMMENT ON COLUMN users.hashed_password IS 'NULL for SSO-only accounts, hashed password for local accounts';
```

Apply the migration:

```bash
# If using psql directly (use -h localhost to force TCP/IP connection)
PGPASSWORD=oracle_dev_password psql -h localhost -U oracle -d cardea_oracle -f migrations/add_azure_fields.sql

# Or if using Alembic
alembic revision --autogenerate -m "Add Azure AD fields"
alembic upgrade head
```

### Step 4: Update API Endpoints

The backend already has `azure_auth.py` configured. Now add the endpoint to your main API:

Edit `oracle/src/oracle_service.py` (or wherever you define routes):

```python
from fastapi import Depends
from azure_auth import get_current_user_from_azure_token, azure_auth_service
from models import User

# Add this endpoint for user profile
@app.get("/api/auth/me")
async def get_current_user_profile(
    current_user: User = Depends(get_current_user_from_azure_token)
):
    """Get current authenticated user profile"""
    return {
        "username": current_user.username,
        "email": current_user.email,
        "name": current_user.full_name,
        "roles": current_user.roles
    }

# Protect existing endpoints with Azure auth
@app.get("/api/analytics")
async def get_analytics(
    current_user: User = Depends(get_current_user_from_azure_token)
):
    """Get analytics - now requires Azure authentication"""
    # Your existing analytics logic
    pass
```

---

## Frontend Configuration

### Step 1: Install Dependencies

```bash
cd dashboard
npm install @azure/msal-browser@^3.7.1 @azure/msal-react@^2.0.10 --legacy-peer-deps
```

> **Note**: The `--legacy-peer-deps` flag is required because @azure/msal-react doesn't yet officially support React 19. This is safe as React 19 is backward compatible with React 18.

### Step 2: Configure Environment Variables

1. Copy the template:
   ```bash
   cp .env.template .env
   ```

2. Fill in your Azure credentials in `.env`:

   ```bash
   # ============================================================================
   # MICROSOFT ENTRA EXTERNAL ID - FRONTEND CONFIGURATION
   # ============================================================================
   VITE_AZURE_CLIENT_ID=<paste your Application (client) ID>
   VITE_AZURE_TENANT_ID=<paste your Directory (tenant) ID>
   VITE_AZURE_AUTHORITY=https://login.microsoftonline.com/<paste your tenant ID>
   
   # Redirect URIs
   VITE_REDIRECT_URI=http://localhost:5173
   VITE_POST_LOGOUT_REDIRECT_URI=http://localhost:5173
   
   # API Configuration
   VITE_API_URL=http://localhost:8000
   VITE_ORACLE_URL=http://localhost:8000
   VITE_API_SCOPES=api://<paste your Application (client) ID>/access_as_user
   
   # Enable Azure Auth
   VITE_ENABLE_AZURE_AUTH=true
   VITE_DEBUG=true
   ```

### Step 3: Build and Test

```bash
npm run dev
```

The dashboard should now start on `http://localhost:5173`

---

## Database Updates

### Manual Database Setup (if needed)

If you need to create the users table from scratch:

```sql
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    hashed_password VARCHAR(255),  -- NULL for SSO-only accounts
    azure_oid VARCHAR(255) UNIQUE,  -- Azure Object ID
    roles TEXT[] DEFAULT ARRAY['user'],
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    CONSTRAINT check_auth_method CHECK (
        hashed_password IS NOT NULL OR azure_oid IS NOT NULL
    )
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_azure_oid ON users(azure_oid);
CREATE INDEX idx_users_username ON users(username);
```

---

## Testing the Integration

### Step 1: Start the Backend

```bash
cd oracle
source venv/bin/activate  # If using virtual environment
python src/main.py
```

The backend should start on `http://localhost:8000`

### Step 2: Start the Frontend

```bash
cd dashboard
npm run dev
```

The frontend should start on `http://localhost:5173`

### Step 3: Test Microsoft Sign-In

1. Navigate to `http://localhost:5173`
2. Click the **"Microsoft"** button
3. You should be redirected to Microsoft login
4. Sign in with your Microsoft account
5. Grant consent if prompted
6. You should be redirected back to your app
7. Check that you're logged in and redirected to `/dashboard`

### Step 4: Verify Backend Authentication

Open browser DevTools (F12) > Network tab:

1. Look for requests to `http://localhost:8000/api/analytics`
2. Check the **Request Headers** for:
   ```
   Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
   ```
3. Check the response - it should be **200 OK** (not 401 Unauthorized)

### Step 5: Check Database

```sql
SELECT username, email, full_name, azure_oid, roles, last_login 
FROM users 
ORDER BY last_login DESC 
LIMIT 10;
```

You should see your Microsoft account user created automatically.

---

## Troubleshooting

### Issue: "Application is not configured" error

**Solution**: Check that all environment variables are set:

```bash
cd dashboard
cat .env | grep VITE_AZURE
```

Make sure none of the values are `PASTE_YOUR_...`

### Issue: "AADSTS50011: The reply URL does not match"

**Cause**: The redirect URI in your code doesn't match Azure portal configuration.

**Solution**:
1. Go to Azure Portal > App registrations > Your app > Authentication
2. Add the exact URI from the error message
3. Make sure platform type is correct (SPA vs Web)

### Issue: "AADSTS650053: The application is disabled or deleted"

**Solution**: Your app registration might be deleted. Create a new one.

### Issue: CORS errors in browser console

**Solution**: Update your backend CORS settings in `oracle/src/main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: Token validation fails with "Invalid signature"

**Possible causes**:
1. Clock skew between servers
2. Using wrong tenant ID
3. Token expired

**Solution**:
1. Ensure system time is synchronized (NTP)
2. Verify `AZURE_TENANT_ID` matches your Azure portal
3. Check token expiration in JWT debugger: https://jwt.ms

### Issue: "User not found" after successful login

**Solution**: Check that the `create_or_update_user_from_azure` function is working:

1. Check backend logs for errors
2. Verify database connection
3. Check that users table has `azure_oid` column

### Enable Debug Logging

**Backend** (`oracle/src/main.py`):
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Frontend** (`.env`):
```bash
VITE_DEBUG=true
```

---

## Security Best Practices

### ✅ DO:

1. **Never commit `.env` files** to version control
   - Add `.env` to `.gitignore`
   - Use `.env.template` for documentation

2. **Rotate client secrets regularly**
   - Set expiration to 6-12 months
   - Create new secret before old one expires

3. **Use HTTPS in production**
   - Update redirect URIs to `https://`
   - Enable HSTS headers

4. **Validate all tokens**
   - Check issuer, audience, expiration
   - Verify signature with public keys

5. **Implement rate limiting**
   - Protect login endpoints
   - Use Azure AD throttling

6. **Use short-lived tokens**
   - Access tokens: 1 hour (default)
   - Refresh tokens: Yes, for better UX

7. **Monitor authentication logs**
   - Azure AD Sign-in logs
   - Application logs for failed validations

### ❌ DON'T:

1. **Don't expose client secrets in frontend**
   - Only use in backend code
   - Never in JavaScript

2. **Don't use implicit flow for sensitive data**
   - Use authorization code flow with PKCE

3. **Don't trust tokens without validation**
   - Always verify signature and claims

4. **Don't store tokens in localStorage**
   - Use sessionStorage or memory (MSAL handles this)

5. **Don't hardcode credentials**
   - Always use environment variables

---

## Production Deployment Checklist

- [ ] Update redirect URIs to production URLs in Azure Portal
- [ ] Set `VITE_ENABLE_AZURE_AUTH=true`
- [ ] Configure HTTPS certificates
- [ ] Set up environment variables in production environment
- [ ] Rotate default client secrets
- [ ] Enable application insights (Azure Monitor)
- [ ] Set up alerts for failed authentications
- [ ] Configure backup admin accounts
- [ ] Document disaster recovery procedures
- [ ] Test token refresh flow
- [ ] Verify CORS settings for production domain
- [ ] Enable Azure AD audit logs
- [ ] Set up monitoring dashboards

---

## Additional Resources

- [Microsoft Entra ID Documentation](https://learn.microsoft.com/en-us/entra/identity/)
- [MSAL.js Documentation](https://github.com/AzureAD/microsoft-authentication-library-for-js)
- [MSAL React Guide](https://github.com/AzureAD/microsoft-authentication-library-for-js/tree/dev/lib/msal-react)
- [Azure AD OAuth 2.0](https://learn.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-auth-code-flow)
- [JWT Debugger](https://jwt.ms/)
- [Azure AD Token Reference](https://learn.microsoft.com/en-us/azure/active-directory/develop/access-tokens)

---

## Support

For issues specific to this integration:
1. Check the troubleshooting section above
2. Review logs in both frontend (browser console) and backend
3. Verify Azure Portal configuration matches this guide
4. Check that all environment variables are set correctly

For Azure-specific issues:
- [Microsoft Q&A](https://learn.microsoft.com/en-us/answers/products/)
- [Stack Overflow [azure-ad]](https://stackoverflow.com/questions/tagged/azure-ad)

---

**Last Updated**: January 5, 2026  
**Version**: 1.0.0  
**Tested with**: 
- Microsoft Entra ID (Azure AD) - January 2026
- MSAL.js v3.7.1
- MSAL React v2.0.10
- Python MSAL v1.26.0
