# OAuth 2.0 Setup Guide - Microsoft & Google Authentication

Complete step-by-step guide to configure Microsoft Entra ID and Google OAuth 2.0 authentication for the Cardea platform.

---

## Table of Contents

1. [Overview](#overview)
2. [Microsoft Entra ID Setup](#microsoft-entra-id-setup)
3. [Google Cloud OAuth Setup](#google-cloud-oauth-setup)
4. [Backend Configuration](#backend-configuration)
5. [Frontend Configuration](#frontend-configuration)
6. [Testing Authentication](#testing-authentication)
7. [Troubleshooting](#troubleshooting)
8. [Security Best Practices](#security-best-practices)

---

## Overview

This guide will help you set up OAuth 2.0 authentication with:
- **Microsoft Entra ID** (formerly Azure AD) - For Microsoft account sign-in
- **Google OAuth 2.0** - For Google account sign-in

### Prerequisites

- [ ] Active Microsoft Azure account
- [ ] Active Google Cloud account
- [ ] Node.js 18+ and npm installed
- [ ] Python 3.11+ installed
- [ ] PostgreSQL database running

---

## Microsoft Entra ID Setup

### Step 1: Access Azure Portal

1. Navigate to **https://portal.azure.com**
2. Sign in with your Microsoft account
3. Search for "Microsoft Entra ID" (or "Azure Active Directory")
4. Click on the service

### Step 2: Register Application

1. In the left sidebar, click **"App registrations"**
2. Click **"+ New registration"**
3. Fill in the registration form:

   **Name:** `Cardea Security Platform`
   
   **Supported account types:** Select one:
   - ✓ **Accounts in any organizational directory (Multi-tenant)** ← RECOMMENDED for Entra External
   - OR **Accounts in this organizational directory only (Single tenant)**
   - OR **Accounts in any organizational directory and personal Microsoft accounts**

   **Redirect URI:**
   - Platform: **Single-page application (SPA)**
   - URI: `http://localhost:5173`

4. Click **"Register"**

### Step 3: Copy Your Credentials

After registration, you'll see the **Overview** page.

**⚠️ IMPORTANT: Copy these values immediately!**

```plaintext
Application (client) ID: _____________________________________________

Directory (tenant) ID:   _____________________________________________
```

📝 **Paste these values in:**
- `dashboard/.env` → `VITE_AZURE_CLIENT_ID` and `VITE_AZURE_TENANT_ID`
- `oracle/.env` → `AZURE_CLIENT_ID` and `AZURE_TENANT_ID`

### Step 4: Create Client Secret

1. In the left sidebar, click **"Certificates & secrets"**
2. Click the **"Client secrets"** tab
3. Click **"+ New client secret"**
4. Description: `Cardea Backend Secret`
5. Expires: **24 months** (or your preference)
6. Click **"Add"**
7. **⚠️ CRITICAL**: Copy the **"Value"** immediately (you won't see it again!)

```plaintext
Client Secret Value: _________________________________________________
```

📝 **Paste this value in:**
- `oracle/.env` → `AZURE_CLIENT_SECRET`

### Step 5: Configure Authentication

1. In the left sidebar, click **"Authentication"**
2. Under **"Platform configurations" → "Single-page application"**:
   - Verify your redirect URI: `http://localhost:5173`
   - Click **"Add URI"** to add production URL: `https://your-domain.com`

3. Under **"Implicit grant and hybrid flows"**:
   - ✅ Check **"Access tokens"**
   - ✅ Check **"ID tokens"**

4. Under **"Advanced settings"**:
   - **Allow public client flows:** No
   
5. Click **"Save"**

### Step 6: Configure API Permissions

1. In the left sidebar, click **"API permissions"**
2. You should see **Microsoft Graph** with **User.Read** (default)
3. Click **"+ Add a permission"** to add more (optional):
   - Select **"Microsoft Graph"**
   - Choose **"Delegated permissions"**
   - Add these scopes:
     - `User.Read` (already there)
     - `email`
     - `profile`
     - `openid`
4. Click **"Add permissions"**
5. *(Optional)* Click **"Grant admin consent for [your tenant]"** if available

### Step 7: Expose an API

This step allows your backend to validate access tokens.

1. In the left sidebar, click **"Expose an API"**
2. Click **"+ Add"** next to **"Application ID URI"**
3. Accept the default: `api://{YOUR_CLIENT_ID}` or customize it
4. Click **"Save"**
5. Click **"+ Add a scope"**:

   **Scope name:** `access_as_user`
   
   **Who can consent?:** Admins and users
   
   **Admin consent display name:** `Access Cardea as user`
   
   **Admin consent description:** `Allows the app to access Cardea on behalf of the signed-in user`
   
   **User consent display name:** `Access Cardea`
   
   **User consent description:** `Allows the app to access Cardea on your behalf`
   
   **State:** Enabled

6. Click **"Add scope"**

### Step 8: Update Dashboard Environment

Update `dashboard/.env` with your values:

```bash
VITE_AZURE_CLIENT_ID=<paste your client ID>
VITE_AZURE_TENANT_ID=<paste your tenant ID>
VITE_AZURE_AUTHORITY=https://login.microsoftonline.com/<paste your tenant ID>
VITE_API_SCOPES=api://<paste your client ID>/access_as_user
VITE_ENABLE_AZURE_AUTH=true
```

### Step 9: Update Backend Environment

Update `oracle/.env` with your values:

```bash
AZURE_CLIENT_ID=<paste your client ID>
AZURE_TENANT_ID=<paste your tenant ID>
AZURE_CLIENT_SECRET=<paste your client secret>
AZURE_AUTHORITY=https://login.microsoftonline.com/<paste your tenant ID>
ENABLE_AZURE_AUTH=true
```

---

## Google Cloud OAuth Setup

### Step 1: Access Google Cloud Console

1. Navigate to **https://console.cloud.google.com**
2. Sign in with your Google account

### Step 2: Create or Select Project

1. Click the project dropdown at the top
2. Click **"New Project"** or select an existing one
3. If creating new:
   - **Project name:** `Cardea Security Platform`
   - **Organization:** (optional)
   - Click **"Create"**

### Step 3: Enable Google+ API (Optional but Recommended)

1. In the search bar, type "Google+ API"
2. Click on **"Google+ API"**
3. Click **"Enable"**

### Step 4: Configure OAuth Consent Screen

1. Go to **"APIs & Services" → "OAuth consent screen"**
2. Choose user type:
   - **Internal** - Only for Google Workspace organization users
   - **External** - For anyone with a Google account ← RECOMMENDED
3. Click **"Create"**

4. Fill in **App information**:
   - **App name:** `Cardea Security Platform`
   - **User support email:** Your email
   - **App logo:** (optional) Upload your logo
   
5. Fill in **Developer contact information**:
   - **Email addresses:** Your email

6. Click **"Save and Continue"**

7. **Scopes page:**
   - Click **"Add or Remove Scopes"**
   - Add these scopes:
     - `openid`
     - `email`
     - `profile`
   - Click **"Update"**
   - Click **"Save and Continue"**

8. **Test users page** (if External and not published):
   - Click **"+ Add Users"**
   - Add your test email addresses
   - Click **"Save and Continue"**

9. Review and click **"Back to Dashboard"**

### Step 5: Create OAuth 2.0 Credentials

1. Go to **"APIs & Services" → "Credentials"**
2. Click **"+ Create Credentials"** → **"OAuth client ID"**
3. **Application type:** Web application
4. **Name:** `Cardea Web Client`
5. **Authorized JavaScript origins:**
   - Click **"+ Add URI"**
   - Add: `http://localhost:5173`
   - *(For production)* Add: `https://your-domain.com`

6. **Authorized redirect URIs:**
   - Click **"+ Add URI"**
   - Add: `http://localhost:5173`
   - *(For production)* Add: `https://your-domain.com`

7. Click **"Create"**

### Step 6: Copy Your Credentials

A popup will show your credentials.

**⚠️ IMPORTANT: Copy these values!**

```plaintext
Your Client ID: __________________________________________________

Your Client Secret: _______________________________________________
```

You can also access these later from the Credentials page.

📝 **Paste these values in:**
- `dashboard/.env` → `VITE_GOOGLE_CLIENT_ID`
- `oracle/.env` → `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`

### Step 7: Update Dashboard Environment

Update `dashboard/.env`:

```bash
VITE_GOOGLE_CLIENT_ID=<paste your Google client ID>
VITE_ENABLE_GOOGLE_AUTH=true
```

### Step 8: Update Backend Environment

Update `oracle/.env`:

```bash
GOOGLE_CLIENT_ID=<paste your Google client ID>
GOOGLE_CLIENT_SECRET=<paste your Google client secret>
ENABLE_GOOGLE_AUTH=true
```

---

## Backend Configuration

### Step 1: Install Dependencies

Navigate to the oracle directory and install required packages:

```bash
cd oracle
pip install -r requirements.txt
```

Required packages:
- `msal` - Microsoft Authentication Library
- `PyJWT` - JWT token handling
- `google-auth` - Google authentication
- `cryptography` - Cryptographic utilities

### Step 2: Database Migration

Add OAuth fields to the users table:

```bash
cd oracle/migrations
psql -U your_user -d cardea -f add_azure_fields.sql
```

Or manually run this SQL:

```sql
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS oauth_provider VARCHAR(50),
ADD COLUMN IF NOT EXISTS oauth_id VARCHAR(255),
ADD COLUMN IF NOT EXISTS profile_picture VARCHAR(500);

CREATE INDEX IF NOT EXISTS idx_users_oauth ON users(oauth_provider, oauth_id);
```

### Step 3: Verify Configuration

Check that your `oracle/.env` file has all required variables:

```bash
# Microsoft
AZURE_CLIENT_ID=<your value>
AZURE_TENANT_ID=<your value>
AZURE_CLIENT_SECRET=<your value>
ENABLE_AZURE_AUTH=true

# Google
GOOGLE_CLIENT_ID=<your value>
GOOGLE_CLIENT_SECRET=<your value>
ENABLE_GOOGLE_AUTH=true

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/cardea

# Security
JWT_SECRET=your-secure-secret-key
CORS_ORIGINS=http://localhost:5173
```

### Step 4: Start the Backend

```bash
cd oracle
python src/main.py
```

You should see:
```
INFO: Azure Authentication Service initialized successfully
INFO: Google Authentication Service initialized successfully
INFO: Application startup complete
```

---

## Frontend Configuration

### Step 1: Install Dependencies

```bash
cd dashboard
npm install
```

Required packages (already in package.json):
- `@azure/msal-browser` - Microsoft authentication
- Google authentication uses Google Identity Services (loaded via CDN)

### Step 2: Copy Environment File

Make sure `dashboard/.env` exists with all credentials:

```bash
# If you don't have .env, copy from template
cp .env.template .env
# Then edit .env with your credentials
```

### Step 3: Verify Configuration

Your `dashboard/.env` should look like:

```bash
# Microsoft
VITE_AZURE_CLIENT_ID=<your client ID>
VITE_AZURE_TENANT_ID=<your tenant ID>
VITE_AZURE_AUTHORITY=https://login.microsoftonline.com/<your tenant ID>
VITE_API_SCOPES=api://<your client ID>/access_as_user
VITE_ENABLE_AZURE_AUTH=true

# Google
VITE_GOOGLE_CLIENT_ID=<your Google client ID>
VITE_ENABLE_GOOGLE_AUTH=true

# API
VITE_API_URL=http://localhost:8000
VITE_REDIRECT_URI=http://localhost:5173
```

### Step 4: Start the Frontend

```bash
cd dashboard
npm run dev
```

---

## Testing Authentication

### Test Microsoft Sign-In

1. Open `http://localhost:5173` in your browser
2. Click the **"Microsoft"** button
3. You'll be redirected to Microsoft login page
4. Sign in with your Microsoft account
5. Grant consent to the requested permissions
6. You'll be redirected back to the dashboard
7. Check browser console for authentication status

### Test Google Sign-In

1. Open `http://localhost:5173` in your browser
2. Click the **"Google"** button (or the Google One Tap prompt)
3. Select your Google account
4. You'll be logged in and redirected to the dashboard
5. Check browser console for authentication status

### Verify Backend Token Validation

Check the backend logs (`oracle` terminal):

```
INFO: Successfully validated Microsoft token for user: user@example.com
INFO: Created new user from microsoft OAuth: user@example.com
```

or

```
INFO: Successfully validated Google ID token for user: user@gmail.com
INFO: Created new user from google OAuth: user@gmail.com
```

### Check Database

Verify users were created:

```bash
psql -U your_user -d cardea
SELECT username, email, oauth_provider, oauth_id FROM users;
```

You should see entries like:
```
username              | email                | oauth_provider | oauth_id
----------------------|----------------------|----------------|----------
user@example_microsoft| user@example.com     | microsoft      | <uuid>
user_google           | user@gmail.com       | google         | <number>
```

---

## Troubleshooting

### Microsoft Authentication Issues

**Problem:** "Microsoft authentication not configured" warning

**Solution:**
- Check `dashboard/.env` has `VITE_AZURE_CLIENT_ID` and `VITE_AZURE_TENANT_ID`
- Make sure values don't contain "PASTE_YOUR"
- Restart the dev server: `npm run dev`

---

**Problem:** "AADSTS50011: The redirect URI doesn't match"

**Solution:**
- Go to Azure Portal → App registrations → Authentication
- Add `http://localhost:5173` to redirect URIs
- Make sure platform is "Single-page application"

---

**Problem:** "AADSTS700016: Invalid client secret"

**Solution:**
- Client secret in `oracle/.env` is wrong or expired
- Create new secret in Azure Portal → Certificates & secrets
- Update `AZURE_CLIENT_SECRET` in `oracle/.env`
- Restart backend

---

**Problem:** "Token audience validation failed"

**Solution:**
- Check `VITE_AZURE_CLIENT_ID` matches your app registration
- Verify `AZURE_CLIENT_ID` in backend matches frontend
- Clear browser cache and try again

---

### Google Authentication Issues

**Problem:** "Google authentication not configured" warning

**Solution:**
- Check `dashboard/.env` has `VITE_GOOGLE_CLIENT_ID`
- Make sure value doesn't contain "PASTE_YOUR"
- Restart the dev server

---

**Problem:** "Error 400: redirect_uri_mismatch"

**Solution:**
- Go to Google Cloud Console → Credentials
- Edit your OAuth 2.0 Client ID
- Add `http://localhost:5173` to "Authorized JavaScript origins"
- Add `http://localhost:5173` to "Authorized redirect URIs"

---

**Problem:** "Access blocked: This app's request is invalid"

**Solution:**
- Go to OAuth consent screen
- Make sure all required fields are filled
- Add your email as a test user (if in testing mode)
- Make sure `openid`, `email`, `profile` scopes are added

---

**Problem:** "Invalid ID token"

**Solution:**
- Check `GOOGLE_CLIENT_ID` in backend matches frontend
- Verify client secret in `oracle/.env`
- Check system clock is accurate (JWT uses timestamps)

---

### General Issues

**Problem:** No OAuth buttons visible

**Solution:**
- Check browser console for errors
- Verify `.env` file exists and has correct variables
- Make sure all variables start with `VITE_`
- Restart dev server after changing `.env`

---

**Problem:** Infinite redirect loop

**Solution:**
- Clear browser cache and cookies
- Check redirect URIs match exactly
- Verify `VITE_REDIRECT_URI` matches configured URIs
- Check for JavaScript errors in console

---

**Problem:** "Failed to fetch" or CORS errors

**Solution:**
- Check backend is running on `http://localhost:8000`
- Verify `CORS_ORIGINS` in `oracle/.env` includes `http://localhost:5173`
- Check browser console for specific CORS errors
- Restart backend after changing CORS settings

---

## Security Best Practices

### Production Deployment

1. **Use HTTPS:** Always use HTTPS in production
   - Update redirect URIs to `https://your-domain.com`
   - Update `VITE_REDIRECT_URI` and `CORS_ORIGINS`

2. **Secure Secrets:** Never commit secrets to version control
   - Add `.env` to `.gitignore`
   - Use environment variables or secret management services
   - Rotate secrets regularly

3. **Token Security:**
   - Use short token expiration times
   - Implement token refresh logic
   - Validate tokens on every request
   - Store tokens securely (localStorage or httpOnly cookies)

4. **API Security:**
   - Rate limit authentication endpoints
   - Implement CSRF protection
   - Use API keys for backend services
   - Monitor for suspicious authentication attempts

5. **User Privacy:**
   - Only request necessary OAuth scopes
   - Implement proper data retention policies
   - Provide privacy policy and terms of service
   - Allow users to delete their data

### Monitoring and Logging

1. Enable authentication logging:
   ```python
   # In oracle/.env
   LOG_LEVEL=INFO
   DEBUG=false  # Set to false in production
   ```

2. Monitor authentication metrics:
   - Login success/failure rates
   - Token validation failures
   - OAuth provider response times

3. Set up alerts for:
   - Multiple failed authentication attempts
   - Unusual login patterns
   - Token validation errors

---

## Additional Resources

### Microsoft Documentation
- [Microsoft Entra ID Overview](https://learn.microsoft.com/en-us/entra/identity/)
- [MSAL.js Documentation](https://github.com/AzureAD/microsoft-authentication-library-for-js)
- [Azure AD App Registration](https://learn.microsoft.com/en-us/entra/identity-platform/quickstart-register-app)

### Google Documentation
- [Google Identity Overview](https://developers.google.com/identity)
- [Google Sign-In for Websites](https://developers.google.com/identity/gsi/web)
- [OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)

### Support
- Check existing issues in the repository
- Review the main [MICROSOFT_ENTRA_SETUP.md](./MICROSOFT_ENTRA_SETUP.md) guide
- Contact the development team

---

## Summary Checklist

### Microsoft Entra ID
- [ ] Registered app in Azure Portal
- [ ] Copied Client ID, Tenant ID, and Client Secret
- [ ] Configured redirect URIs
- [ ] Set up API permissions
- [ ] Exposed API scope
- [ ] Updated `dashboard/.env` with Microsoft credentials
- [ ] Updated `oracle/.env` with Microsoft credentials
- [ ] Tested Microsoft login

### Google OAuth
- [ ] Created project in Google Cloud Console
- [ ] Configured OAuth consent screen
- [ ] Created OAuth 2.0 Client ID
- [ ] Copied Client ID and Client Secret
- [ ] Configured authorized origins and redirect URIs
- [ ] Updated `dashboard/.env` with Google credentials
- [ ] Updated `oracle/.env` with Google credentials
- [ ] Tested Google login

### Backend
- [ ] Installed Python dependencies
- [ ] Ran database migrations
- [ ] Verified `.env` configuration
- [ ] Started backend server
- [ ] Checked authentication logs

### Frontend
- [ ] Installed npm dependencies
- [ ] Verified `.env` configuration
- [ ] Started frontend dev server
- [ ] Both OAuth buttons visible
- [ ] Tested both auth providers

---

**🎉 Congratulations!** You've successfully configured OAuth 2.0 authentication for the Cardea platform!

For any issues, refer to the [Troubleshooting](#troubleshooting) section or check the console logs.
