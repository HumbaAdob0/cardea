# 📝 OAuth Credentials - Fill This Out

Use this document to keep track of your OAuth credentials as you set them up.

---

## Microsoft Entra ID / Azure AD

### Where to Get These:
1. Go to: https://portal.azure.com
2. Search for "Microsoft Entra ID"
3. Click "App registrations" → "New registration"

### Your Credentials:

```
Application (client) ID: _________________________________________________

Directory (tenant) ID:   _________________________________________________

Client Secret Value:     _________________________________________________
```

### Where to Paste:

**Frontend** (`dashboard/.env`):
```bash
VITE_AZURE_CLIENT_ID=<paste client ID>
VITE_AZURE_TENANT_ID=<paste tenant ID>
VITE_AZURE_AUTHORITY=https://login.microsoftonline.com/<paste tenant ID>
VITE_API_SCOPES=api://<paste client ID>/access_as_user
```

**Backend** (`oracle/.env`):
```bash
AZURE_CLIENT_ID=<paste client ID>
AZURE_TENANT_ID=<paste tenant ID>
AZURE_CLIENT_SECRET=<paste client secret>
AZURE_AUTHORITY=https://login.microsoftonline.com/<paste tenant ID>
```

---

## Google OAuth 2.0

### Where to Get These:
1. Go to: https://console.cloud.google.com
2. Go to "APIs & Services" → "Credentials"
3. Click "Create Credentials" → "OAuth client ID"

### Your Credentials:

```
Client ID:     __________________________________________________________

Client Secret: __________________________________________________________
```

### Where to Paste:

**Frontend** (`dashboard/.env`):
```bash
VITE_GOOGLE_CLIENT_ID=<paste client ID>
```

**Backend** (`oracle/.env`):
```bash
GOOGLE_CLIENT_ID=<paste client ID>
GOOGLE_CLIENT_SECRET=<paste client secret>
```

---

## Important Configuration URLs

### Microsoft Azure Portal:
- [ ] **Redirect URI:** `http://localhost:5173` (configured as SPA)
- [ ] **Platform:** Single-page application
- [ ] **Implicit grants:** Access tokens ✅, ID tokens ✅
- [ ] **API Permissions:** User.Read, email, profile, openid
- [ ] **Exposed API scope:** `api://{CLIENT_ID}/access_as_user`

### Google Cloud Console:
- [ ] **Authorized JavaScript origins:** `http://localhost:5173`
- [ ] **Authorized redirect URIs:** `http://localhost:5173`
- [ ] **OAuth consent screen:** Configured with app name and support email
- [ ] **Scopes:** openid, email, profile

---

## Production URLs (Update When Deploying)

### Your Production Domain:
```
Production URL: https://______________________________________
```

### Update These:

**Microsoft Azure:**
- [ ] Add production redirect URI: `https://your-domain.com`

**Google Cloud:**
- [ ] Add production authorized origin: `https://your-domain.com`
- [ ] Add production redirect URI: `https://your-domain.com`

**Environment Files:**
```bash
# Production .env
VITE_REDIRECT_URI=https://your-domain.com
CORS_ORIGINS=https://your-domain.com
```

---

## Verification Checklist

After pasting credentials, verify:

### Frontend (.env file exists):
- [ ] `dashboard/.env` file created
- [ ] `VITE_AZURE_CLIENT_ID` set (not "PASTE_YOUR...")
- [ ] `VITE_AZURE_TENANT_ID` set (not "PASTE_YOUR...")
- [ ] `VITE_GOOGLE_CLIENT_ID` set (not "PASTE_YOUR...")
- [ ] `VITE_API_URL` set to `http://localhost:8000`
- [ ] `VITE_ENABLE_AZURE_AUTH` set to `true`
- [ ] `VITE_ENABLE_GOOGLE_AUTH` set to `true`

### Backend (.env file exists):
- [ ] `oracle/.env` file created
- [ ] `AZURE_CLIENT_ID` set (not "PASTE_YOUR...")
- [ ] `AZURE_TENANT_ID` set (not "PASTE_YOUR...")
- [ ] `AZURE_CLIENT_SECRET` set (not "PASTE_YOUR...")
- [ ] `GOOGLE_CLIENT_ID` set (not "PASTE_YOUR...")
- [ ] `GOOGLE_CLIENT_SECRET` set (not "PASTE_YOUR...")
- [ ] `DATABASE_URL` configured
- [ ] `ENABLE_AZURE_AUTH` set to `true`
- [ ] `ENABLE_GOOGLE_AUTH` set to `true`

### Azure Portal:
- [ ] App registered
- [ ] Redirect URIs configured
- [ ] API permissions granted
- [ ] API scope exposed (`access_as_user`)
- [ ] Client secret created and copied

### Google Cloud Console:
- [ ] Project created
- [ ] OAuth consent screen configured
- [ ] OAuth 2.0 Client ID created
- [ ] Authorized origins configured
- [ ] Credentials copied

---

## Testing

After configuration:

1. **Start Backend:**
   ```bash
   cd oracle
   python src/main.py
   ```
   Look for:
   ```
   ✓ Azure Authentication Service initialized successfully
   ✓ Google Authentication Service initialized successfully
   ```

2. **Start Frontend:**
   ```bash
   cd dashboard
   npm run dev
   ```

3. **Test Login:**
   - Open http://localhost:5173
   - Click "Microsoft" button → Should redirect to Microsoft login
   - Click "Google" button → Should show Google sign-in
   - After login → Should redirect to dashboard

---

## Security Reminders

- ⚠️ **NEVER** commit `.env` files to git
- ⚠️ **NEVER** share client secrets publicly
- ⚠️ Add `.env` to `.gitignore`
- ⚠️ Use different credentials for development and production
- ⚠️ Rotate secrets regularly (every 6-12 months)
- ⚠️ Use HTTPS in production
- ⚠️ Monitor authentication logs for suspicious activity

---

## Need Help?

Refer to the complete setup guides:
- [OAUTH_QUICK_START.md](./OAUTH_QUICK_START.md) - Quick reference
- [docs/OAUTH_SETUP_GUIDE.md](./docs/OAUTH_SETUP_GUIDE.md) - Detailed instructions
- [docs/MICROSOFT_ENTRA_SETUP.md](./docs/MICROSOFT_ENTRA_SETUP.md) - Microsoft-specific guide

---

## Notes

Use this space to add your own notes or special configuration details:

```
___________________________________________________________________________

___________________________________________________________________________

___________________________________________________________________________

___________________________________________________________________________
```
