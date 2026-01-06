# 🔐 OAuth 2.0 Authentication - Quick Start

This project now supports **Microsoft Entra ID** and **Google OAuth 2.0** authentication!

## 📋 Quick Setup Checklist

### 1. Get Your Credentials

#### Microsoft Entra ID:
- [ ] Go to [Azure Portal](https://portal.azure.com) → Microsoft Entra ID → App registrations
- [ ] Copy: Client ID, Tenant ID, Client Secret
- [ ] Set redirect URI: `http://localhost:5173`

#### Google OAuth:
- [ ] Go to [Google Cloud Console](https://console.cloud.google.com) → APIs & Services → Credentials
- [ ] Copy: Client ID, Client Secret
- [ ] Set authorized origins: `http://localhost:5173`

### 2. Configure Environment Files

#### Frontend (`dashboard/.env`):
```bash
# Microsoft
VITE_AZURE_CLIENT_ID=your_microsoft_client_id_here
VITE_AZURE_TENANT_ID=your_microsoft_tenant_id_here
VITE_AZURE_AUTHORITY=https://login.microsoftonline.com/your_tenant_id_here
VITE_ENABLE_AZURE_AUTH=true

# Google
VITE_GOOGLE_CLIENT_ID=your_google_client_id_here
VITE_ENABLE_GOOGLE_AUTH=true

# API
VITE_API_URL=http://localhost:8000
VITE_REDIRECT_URI=http://localhost:5173
```

#### Backend (`oracle/.env`):
```bash
# Microsoft
AZURE_CLIENT_ID=your_microsoft_client_id_here
AZURE_TENANT_ID=your_microsoft_tenant_id_here
AZURE_CLIENT_SECRET=your_microsoft_client_secret_here
ENABLE_AZURE_AUTH=true

# Google
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
ENABLE_GOOGLE_AUTH=true

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/cardea

# Security
JWT_SECRET=your-secure-secret-key
CORS_ORIGINS=http://localhost:5173
```

### 3. Install Dependencies

#### Backend:
```bash
cd oracle
pip install -r requirements.txt
```

New packages installed:
- `msal` - Microsoft Authentication Library
- `PyJWT` - JWT token handling
- `google-auth` - Google authentication

#### Frontend:
```bash
cd dashboard
npm install
```

Already includes `@azure/msal-browser` for Microsoft auth. Google auth uses Google Identity Services (loaded via CDN).

### 4. Database Migration

Add OAuth fields to users table:

```bash
psql -U your_user -d cardea
```

```sql
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS oauth_provider VARCHAR(50),
ADD COLUMN IF NOT EXISTS oauth_id VARCHAR(255),
ADD COLUMN IF NOT EXISTS profile_picture VARCHAR(500);

CREATE INDEX IF NOT EXISTS idx_users_oauth ON users(oauth_provider, oauth_id);
```

### 5. Start Services

#### Backend:
```bash
cd oracle
python src/main.py
```

Should see:
```
INFO: Azure Authentication Service initialized successfully
INFO: Google Authentication Service initialized successfully
```

#### Frontend:
```bash
cd dashboard
npm run dev
```

### 6. Test Authentication

1. Open `http://localhost:5173`
2. Click **"Microsoft"** or **"Google"** button
3. Sign in with your account
4. You'll be redirected to the dashboard

---

## 📚 Full Documentation

For complete step-by-step setup instructions, see:

### [OAUTH_SETUP_GUIDE.md](./docs/OAUTH_SETUP_GUIDE.md)

This comprehensive guide includes:
- ✅ Detailed Azure Portal configuration
- ✅ Detailed Google Cloud Console setup
- ✅ API permissions and scopes
- ✅ Redirect URI configuration
- ✅ Token validation setup
- ✅ Troubleshooting common issues
- ✅ Security best practices
- ✅ Production deployment checklist

---

## 🎯 What's Implemented

### Frontend (`dashboard/`)
- ✅ `src/authConfig.ts` - MSAL and Google OAuth configuration
- ✅ `src/contexts/AuthContext.tsx` - Unified authentication context
- ✅ `src/components/LoginPage.tsx` - OAuth buttons with Google Sign-In

### Backend (`oracle/`)
- ✅ `src/azure_auth.py` - Microsoft token validation
- ✅ `src/google_auth.py` - Google token validation
- ✅ `src/auth.py` - Enhanced with OAuth support
- ✅ `src/oracle_service.py` - OAuth validation endpoint

### Configuration
- ✅ `dashboard/.env` - Frontend OAuth credentials
- ✅ `oracle/.env` - Backend OAuth credentials
- ✅ Database schema updated for OAuth users

---

## 🔧 Environment Variables Reference

### Required Frontend Variables (dashboard/.env)

| Variable | Description | Example |
|----------|-------------|---------|
| `VITE_AZURE_CLIENT_ID` | Microsoft application client ID | `12345678-1234-...` |
| `VITE_AZURE_TENANT_ID` | Microsoft tenant ID | `87654321-4321-...` |
| `VITE_GOOGLE_CLIENT_ID` | Google OAuth client ID | `123456789.apps.googleusercontent.com` |
| `VITE_API_URL` | Backend API URL | `http://localhost:8000` |
| `VITE_REDIRECT_URI` | OAuth redirect URI | `http://localhost:5173` |

### Required Backend Variables (oracle/.env)

| Variable | Description | Example |
|----------|-------------|---------|
| `AZURE_CLIENT_ID` | Microsoft application client ID | `12345678-1234-...` |
| `AZURE_TENANT_ID` | Microsoft tenant ID | `87654321-4321-...` |
| `AZURE_CLIENT_SECRET` | Microsoft client secret | `abc123~...` |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | `123456789.apps.googleusercontent.com` |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret | `GOCSPX-...` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@localhost/cardea` |

---

## 🚨 Common Issues & Solutions

### "Microsoft authentication not configured"
- ✅ Check that `VITE_AZURE_CLIENT_ID` is set in `dashboard/.env`
- ✅ Make sure it doesn't contain "PASTE_YOUR"
- ✅ Restart the dev server: `npm run dev`

### "redirect_uri_mismatch"
- ✅ Verify redirect URIs match exactly in Azure/Google console
- ✅ Check `http://` vs `https://`
- ✅ Ensure no trailing slashes

### "Token validation failed"
- ✅ Check client IDs match between frontend and backend
- ✅ Verify client secrets are correct
- ✅ Check system clock is accurate

### OAuth buttons not visible
- ✅ Check browser console for errors
- ✅ Verify `.env` file exists and has `VITE_` prefix
- ✅ Clear cache and restart dev server

---

## 🔐 Security Notes

### Development
- ✅ Never commit `.env` files to version control
- ✅ Use different credentials for dev and production
- ✅ Keep client secrets secure

### Production
- ✅ Use HTTPS only
- ✅ Update redirect URIs to production domains
- ✅ Rotate secrets regularly
- ✅ Enable rate limiting
- ✅ Monitor authentication logs

---

## 📞 Support

For detailed troubleshooting and setup instructions:
- See [OAUTH_SETUP_GUIDE.md](./docs/OAUTH_SETUP_GUIDE.md)
- Check [MICROSOFT_ENTRA_SETUP.md](./docs/MICROSOFT_ENTRA_SETUP.md)
- Review [ERROR_SOLUTIONS.md](./docs/ERROR_SOLUTIONS.md)

---

## ✅ Post-Setup Verification

After setup, verify:

1. **Backend logs show:**
   ```
   ✓ Azure Authentication Service initialized successfully
   ✓ Google Authentication Service initialized successfully
   ```

2. **Frontend shows:**
   - Microsoft and Google buttons on login page
   - No warning messages about missing configuration

3. **Can successfully:**
   - Click Microsoft button → Sign in → Redirect to dashboard
   - Click Google button → Sign in → Redirect to dashboard
   - See user info in console logs

4. **Database has:**
   ```sql
   SELECT username, email, oauth_provider FROM users;
   ```
   - New users with `oauth_provider` = 'microsoft' or 'google'

---

**🎉 You're all set!** Users can now sign in with Microsoft or Google accounts.
