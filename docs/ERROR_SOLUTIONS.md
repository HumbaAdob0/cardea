# Common Error Messages and Solutions

Quick reference guide for troubleshooting Microsoft Entra External ID integration issues.

---

## 🔍 How to Use This Guide

1. Find your error message in the table of contents
2. Check the "Symptoms" to confirm it matches your issue
3. Follow the "Solution" steps
4. If still not working, see "Additional Debugging"

---

## Table of Contents

### Azure AD Errors
- [AADSTS50011: Reply URL Mismatch](#aadsts50011-reply-url-mismatch)
- [AADSTS650053: Application Disabled](#aadsts650053-application-disabled)
- [AADSTS50012: Invalid Client Secret](#aadsts50012-invalid-client-secret)
- [AADSTS700016: Application Not Found](#aadsts700016-application-not-found)
- [AADSTS90002: Tenant Not Found](#aadsts90002-tenant-not-found)
- [AADSTS65001: User or Admin Not Consented](#aadsts65001-user-or-admin-not-consented)

### MSAL Errors
- [MSAL: InteractionRequiredAuthError](#msal-interactionrequiredautherror)
- [MSAL: Client Authentication Failed](#msal-client-authentication-failed)
- [MSAL: No Account Chosen](#msal-no-account-chosen)

### Application Errors
- [Microsoft Button is Greyed Out](#microsoft-button-is-greyed-out)
- [CORS Errors](#cors-errors)
- [401 Unauthorized from Backend](#401-unauthorized-from-backend)
- [Token Validation Failed](#token-validation-failed)
- [User Not Created in Database](#user-not-created-in-database)
- [Environment Variables Not Loading](#environment-variables-not-loading)

---

## Azure AD Errors

### AADSTS50011: Reply URL Mismatch

**Full Error:**
```
AADSTS50011: The reply URL specified in the request does not match the reply URLs configured for the application
```

**Symptoms:**
- Redirected to error page after Microsoft login
- URL in error message shows the redirect_uri

**Cause:**
The redirect URI in your application code doesn't exactly match what's configured in Azure Portal.

**Solution:**

1. **Check the exact URL in the error message**
   - Look for `redirect_uri=` parameter
   - Example: `redirect_uri=http://localhost:5173`

2. **Go to Azure Portal**
   ```
   Portal → Microsoft Entra ID → App registrations 
   → Your app → Authentication
   ```

3. **Add the exact URI**
   - Platform: **Single-page application (SPA)**
   - URI: Copy exactly from error message
   - Common mistakes:
     - ❌ `http://localhost:5173/` (trailing slash)
     - ✅ `http://localhost:5173` (no trailing slash)
     - ❌ `https://` when using `http://`
     - ❌ Wrong port number

4. **Click Save**

5. **Clear browser cache** (Ctrl+Shift+Del)

6. **Try again**

---

### AADSTS650053: Application Disabled

**Full Error:**
```
AADSTS650053: The application '{app_name}' is disabled or deleted.
```

**Symptoms:**
- Can't sign in
- Error immediately after clicking Microsoft button

**Cause:**
- App registration was deleted
- App is disabled in Azure AD

**Solution:**

**Option 1: Restore Deleted App** (within 30 days)
1. Azure Portal → Microsoft Entra ID → App registrations
2. Click **"Deleted applications"** tab
3. Find your app → Click **"Restore"**

**Option 2: Create New App Registration**
1. Follow [Quick Start Guide - Step 1](./QUICKSTART_ENTRA.md#step-1-azure-portal-configuration-5-minutes)
2. Update both `.env` files with new Client ID and Tenant ID

---

### AADSTS50012: Invalid Client Secret

**Full Error:**
```
AADSTS50012: Invalid client secret is provided.
```

**Symptoms:**
- Backend can't authenticate with Microsoft
- Error when backend tries to validate tokens

**Cause:**
- Client secret expired
- Client secret incorrect in `.env` file
- Wrong client secret value

**Solution:**

1. **Create New Client Secret**
   ```
   Azure Portal → Microsoft Entra ID → App registrations
   → Your app → Certificates & secrets → New client secret
   ```

2. **Copy the VALUE immediately** (you can't see it again!)

3. **Update Backend `.env`**
   ```bash
   cd /path/to/cardea
   nano .env
   
   # Update this line:
   AZURE_CLIENT_SECRET=<paste new secret value>
   ```

4. **Restart Backend**
   ```bash
   cd oracle
   python src/main.py
   ```

---

### AADSTS700016: Application Not Found

**Full Error:**
```
AADSTS700016: Application with identifier '{client_id}' was not found in the directory
```

**Symptoms:**
- Error immediately after clicking Microsoft button
- "Application not found" message

**Cause:**
- Wrong Client ID in configuration
- App deleted from Azure AD
- Wrong tenant

**Solution:**

1. **Verify Client ID in Azure Portal**
   ```
   Azure Portal → Microsoft Entra ID → App registrations
   → Your app → Overview
   ```
   Copy the **Application (client) ID**

2. **Update Frontend `.env`**
   ```bash
   cd dashboard
   nano .env
   
   # Update this line:
   VITE_AZURE_CLIENT_ID=<paste correct client ID>
   ```

3. **Update Backend `.env`**
   ```bash
   cd ..
   nano .env
   
   # Update this line:
   AZURE_CLIENT_ID=<paste correct client ID>
   ```

4. **Restart Both**
   ```bash
   # Terminal 1
   cd oracle
   python src/main.py
   
   # Terminal 2
   cd dashboard
   npm run dev
   ```

---

### AADSTS90002: Tenant Not Found

**Full Error:**
```
AADSTS90002: Tenant '{tenant_id}' not found.
```

**Symptoms:**
- Can't sign in
- Tenant ID error

**Cause:**
- Wrong Tenant ID in configuration
- Typo in Tenant ID

**Solution:**

1. **Get Correct Tenant ID**
   ```
   Azure Portal → Microsoft Entra ID → Overview
   ```
   Copy **Directory (tenant) ID**

2. **Update Frontend `.env`**
   ```bash
   VITE_AZURE_TENANT_ID=<paste correct tenant ID>
   VITE_AZURE_AUTHORITY=https://login.microsoftonline.com/<paste tenant ID>
   ```

3. **Update Backend `.env`**
   ```bash
   AZURE_TENANT_ID=<paste correct tenant ID>
   AZURE_AUTHORITY=https://login.microsoftonline.com/<paste tenant ID>
   ```

4. **Restart and test**

---

### AADSTS65001: User or Admin Not Consented

**Full Error:**
```
AADSTS65001: The user or administrator has not consented to use the application
```

**Symptoms:**
- Error after entering credentials
- "Permissions requested" screen doesn't show
- Admin consent required but not granted

**Cause:**
- App requires admin consent
- User can't consent themselves

**Solution:**

**Option 1: Grant Admin Consent** (Recommended)
1. Azure Portal → Your app → API permissions
2. Click **"Grant admin consent for [your organization]"**
3. Click **"Yes"**
4. Wait 5 minutes for propagation

**Option 2: Allow User Consent**
1. Azure Portal → Microsoft Entra ID → Enterprise applications
2. Click **"Consent and permissions"**
3. Click **"User consent settings"**
4. Select **"Allow user consent for apps"**

**Option 3: Have Admin Log In First**
1. Ask your Azure AD admin to sign in to the app first
2. They will see consent screen
3. They click "Consent on behalf of organization"
4. All users can then sign in

---

## MSAL Errors

### MSAL: InteractionRequiredAuthError

**Full Error:**
```
InteractionRequiredAuthError: AADSTS50058: A silent sign-in request was sent but no user is signed in.
```

**Symptoms:**
- Silent token acquisition fails
- User redirected to login unexpectedly

**Cause:**
- Token expired and can't be refreshed silently
- User session timed out
- No refresh token available

**Solution:**

This is **expected behavior**. MSAL will automatically handle it:

1. **MSAL.js will:**
   - Catch the error
   - Fall back to interactive authentication
   - Redirect user to Microsoft login

2. **If it doesn't auto-redirect:**
   ```typescript
   // In your auth code
   try {
     const response = await msalInstance.acquireTokenSilent(request);
   } catch (error) {
     if (error instanceof InteractionRequiredAuthError) {
       // Redirect to login
       await msalInstance.acquireTokenRedirect(request);
     }
   }
   ```

3. **To prevent frequent occurrences:**
   - Use refresh tokens (enable in Azure Portal)
   - Increase session timeout if possible

---

### MSAL: Client Authentication Failed

**Full Error:**
```
ClientAuthError: Token renewal operation failed due to timeout
```

**Symptoms:**
- Login hangs
- Timeout after 30-60 seconds

**Cause:**
- Network issues
- Popup blocked
- CORS issues
- Hidden iframe blocked

**Solution:**

1. **Check Network Connection**
   - Verify internet connectivity
   - Check firewall/proxy settings

2. **Check Browser Console** for:
   - Popup blocker messages
   - CORS errors
   - Network failures

3. **Clear Browser Cache**
   ```
   Ctrl+Shift+Del → Clear all data
   ```

4. **Try Different Browser** (to rule out browser-specific issues)

5. **Verify CORS Settings** on backend (see [CORS Errors](#cors-errors))

---

### MSAL: No Account Chosen

**Full Error:**
```
BrowserAuthError: no_account_error
```

**Symptoms:**
- Login completes but app doesn't recognize user
- "Not authenticated" after login

**Cause:**
- MSAL couldn't determine which account to use
- Multiple accounts signed in

**Solution:**

1. **Set Active Account** after login:

   ```typescript
   // In contexts/AuthContext.tsx
   const accounts = msalInstance.getAllAccounts();
   if (accounts.length > 0) {
     msalInstance.setActiveAccount(accounts[0]);
   }
   ```

2. **Clear All Accounts** and try again:
   ```typescript
   msalInstance.getAllAccounts().forEach(account => {
     msalInstance.logout({ account });
   });
   ```

3. **Restart Browser** (to clear all sessions)

---

## Application Errors

### Microsoft Button is Greyed Out

**Symptoms:**
- Microsoft button is disabled/greyed out
- Clicking does nothing
- Tooltip says "not configured"

**Cause:**
- Environment variables not set
- `.env` file has placeholder values
- Frontend not reading `.env` file

**Solution:**

1. **Check `.env` file exists**
   ```bash
   cd dashboard
   ls -la .env
   ```
   If not found: `cp .env.template .env`

2. **Check values are filled in**
   ```bash
   cat .env | grep VITE_AZURE
   ```
   
   Should show:
   ```
   VITE_AZURE_CLIENT_ID=<actual GUID>
   VITE_AZURE_TENANT_ID=<actual GUID>
   ```
   
   NOT:
   ```
   VITE_AZURE_CLIENT_ID=PASTE_YOUR_CLIENT_ID_HERE ❌
   ```

3. **Restart Frontend** (important!)
   ```bash
   # Stop the dev server (Ctrl+C)
   npm run dev
   ```
   Vite only reads `.env` at startup

4. **Verify in Browser Console**
   ```javascript
   // Open DevTools Console (F12)
   console.log(import.meta.env.VITE_AZURE_CLIENT_ID)
   ```
   Should show your actual Client ID, not "undefined"

---

### CORS Errors

**Symptoms:**
```
Access to XMLHttpRequest at 'http://localhost:8000/api/analytics' 
from origin 'http://localhost:5173' has been blocked by CORS policy
```

**Cause:**
- Backend not configured to allow frontend origin
- Missing CORS middleware

**Solution:**

1. **Add CORS Middleware** to backend:

   Edit `oracle/src/main.py`:
   ```python
   from fastapi.middleware.cors import CORSMiddleware
   
   app = FastAPI()
   
   # Add this right after creating app
   app.add_middleware(
       CORSMiddleware,
       allow_origins=[
           "http://localhost:5173",  # Frontend dev server
           "http://localhost:5174",  # Backup port
           # Add your production URLs here
       ],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

2. **Restart Backend**
   ```bash
   cd oracle
   python src/main.py
   ```

3. **Clear Browser Cache** (Ctrl+Shift+Del)

4. **Test Again**

**Security Note:** In production, replace `allow_origins=["*"]` with your actual domain:
```python
allow_origins=["https://yourdomain.com"]
```

---

### 401 Unauthorized from Backend

**Symptoms:**
- API calls return 401 Unauthorized
- "Could not validate credentials" error
- User can log in but can't access API

**Cause:**
- Token not included in request
- Token validation failing
- Wrong API endpoint configuration

**Solution:**

1. **Check Token is Sent** (Browser DevTools):
   - Open DevTools (F12) → Network tab
   - Find API request (e.g., `/api/analytics`)
   - Check Request Headers:
     ```
     Authorization: Bearer eyJ0eXAiOiJKV1Qi...
     ```
   - If missing, check `AuthContext.tsx` is providing token

2. **Check Backend Logs** for specific error:
   ```bash
   cd oracle
   python src/main.py
   ```
   Look for token validation errors

3. **Verify Tenant ID Matches**:
   - Frontend `.env`: `VITE_AZURE_TENANT_ID`
   - Backend `.env`: `AZURE_TENANT_ID`
   - Azure Portal: Directory (tenant) ID
   - All three must match exactly

4. **Check Token Expiration**:
   - Go to https://jwt.ms
   - Paste your access token
   - Check `exp` claim (expiration)
   - If expired, clear browser cache and login again

5. **Verify Audience Claim**:
   - In jwt.ms, check `aud` claim
   - Should match your `AZURE_CLIENT_ID`

---

### Token Validation Failed

**Symptoms:**
- Backend logs show "Invalid token signature"
- "Could not fetch JWKS keys" error
- Token validation timing out

**Cause:**
- Can't fetch Microsoft's public keys
- Network/firewall blocking JWKS endpoint
- Clock skew between servers

**Solution:**

1. **Check Backend Can Reach Microsoft**:
   ```bash
   curl https://login.microsoftonline.com/{TENANT_ID}/discovery/v2.0/keys
   ```
   Should return JSON with keys

2. **Check System Time** (clock skew):
   ```bash
   date
   ```
   If wrong, sync with NTP:
   ```bash
   sudo ntpdate -s time.nist.gov
   # or
   sudo timedatectl set-ntp true
   ```

3. **Check Firewall/Proxy**:
   - Allow outbound HTTPS to `login.microsoftonline.com`
   - Allow outbound HTTPS to `graph.microsoft.com`

4. **Enable Debug Logging** in `oracle/src/azure_auth.py`:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```
   Check logs for detailed error

---

### User Not Created in Database

**Symptoms:**
- User can log in
- But querying database shows no user
- "User not found" errors

**Cause:**
- Database column `azure_oid` missing
- Database connection failure
- Error in user creation logic

**Solution:**

1. **Check Database Schema**:
   ```bash
   psql -U oracle -d cardea_oracle -c "\d users"
   ```
   
   Should include:
   ```
   azure_oid | character varying(255) |
   ```

2. **If column missing**, add it:
   ```bash
   psql -U oracle -d cardea_oracle << EOF
   ALTER TABLE users ADD COLUMN IF NOT EXISTS azure_oid VARCHAR(255) UNIQUE;
   CREATE INDEX IF NOT EXISTS idx_users_azure_oid ON users(azure_oid);
   EOF
   ```

3. **Check Backend Logs** for database errors:
   ```bash
   cd oracle
   python src/main.py
   ```
   Look for errors after "Creating user from Azure"

4. **Test Database Connection**:
   ```bash
   psql -U oracle -d cardea_oracle -c "SELECT 1;"
   ```

5. **Check Environment Variable**:
   ```bash
   grep DATABASE_URL .env
   ```

---

### Environment Variables Not Loading

**Symptoms:**
- `undefined` or `null` values
- "Environment variable not set" errors
- Default values being used

**Cause:**
- `.env` file doesn't exist
- `.env` file in wrong location
- Syntax error in `.env` file
- Server not restarted after changes

**Solution:**

**Backend:**

1. **Check file exists**:
   ```bash
   ls -la /path/to/cardea/.env
   ```

2. **Check format** (no quotes needed):
   ```bash
   # ✅ Correct:
   AZURE_CLIENT_ID=abc123-def456-ghi789
   
   # ❌ Wrong:
   AZURE_CLIENT_ID="abc123-def456-ghi789"
   AZURE_CLIENT_ID='abc123-def456-ghi789'
   ```

3. **Test loading**:
   ```python
   import os
   from dotenv import load_dotenv
   
   load_dotenv()
   print(os.getenv("AZURE_CLIENT_ID"))
   ```

**Frontend:**

1. **Check file exists**:
   ```bash
   ls -la dashboard/.env
   ```

2. **Check variables start with `VITE_`**:
   ```bash
   # ✅ Correct:
   VITE_AZURE_CLIENT_ID=abc123
   
   # ❌ Wrong (Vite won't load it):
   AZURE_CLIENT_ID=abc123
   ```

3. **Restart dev server** (Vite only reads at startup):
   ```bash
   # Stop: Ctrl+C
   npm run dev
   ```

4. **Verify in browser console**:
   ```javascript
   console.log(import.meta.env.VITE_AZURE_CLIENT_ID)
   ```

---

## 🛠️ General Debugging Steps

### 1. Enable Debug Logging

**Frontend** (Browser Console):
```javascript
// Check MSAL logs
localStorage.setItem('msal.log.level', '3');  // Verbose
```

**Backend** (`oracle/src/main.py`):
```python
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### 2. Check All Credentials Match

| Location | Variable | Must Match |
|----------|----------|------------|
| Azure Portal | Application (client) ID | `AZURE_CLIENT_ID` (backend)<br>`VITE_AZURE_CLIENT_ID` (frontend) |
| Azure Portal | Directory (tenant) ID | `AZURE_TENANT_ID` (backend)<br>`VITE_AZURE_TENANT_ID` (frontend) |
| Azure Portal | Client Secret | `AZURE_CLIENT_SECRET` (backend only) |

### 3. Test Connectivity

**Microsoft Login Endpoint:**
```bash
curl https://login.microsoftonline.com/{TENANT_ID}/.well-known/openid-configuration
```

**Microsoft JWKS:**
```bash
curl https://login.microsoftonline.com/{TENANT_ID}/discovery/v2.0/keys
```

### 4. Clear All Caches

**Browser:**
- Ctrl+Shift+Del → Clear all data
- Or use Incognito mode

**MSAL Cache:**
```javascript
// In browser console
sessionStorage.clear();
localStorage.clear();
```

**Backend:**
```bash
# Remove Python cache
find . -type d -name "__pycache__" -exec rm -r {} +
find . -type f -name "*.pyc" -delete
```

### 5. Verify Services are Running

```bash
# Backend
curl http://localhost:8000/api/analytics
# Should return 401 (not 404 or connection refused)

# Frontend
curl http://localhost:5173
# Should return HTML
```

---

## 📞 Still Not Working?

1. **Check Documentation**:
   - [Quick Start Guide](./QUICKSTART_ENTRA.md)
   - [Complete Setup Guide](./MICROSOFT_ENTRA_SETUP.md)
   - [Azure Portal Checklist](./AZURE_PORTAL_CHECKLIST.md)

2. **Collect Information**:
   - Exact error message
   - Browser console logs
   - Backend server logs
   - Steps to reproduce

3. **Verify Prerequisites**:
   - Node.js 18+ installed
   - Python 3.11+ installed
   - PostgreSQL running
   - Azure account with app registration

4. **Try Clean Setup**:
   - Delete `.env` files
   - Copy from templates
   - Fill in values again
   - Restart everything

5. **Check Azure Status**:
   - https://status.azure.com/
   - Check for outages

---

**Last Updated**: January 5, 2026  
**Coverage**: Common errors as of January 2026
