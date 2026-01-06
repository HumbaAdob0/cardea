# Quick Start: Microsoft Entra External ID Integration

**⚡ Get up and running with Microsoft authentication in 15 minutes**

---

## Prerequisites Checklist

- [ ] Azure account with active subscription
- [ ] Node.js 18+ and npm installed
- [ ] Python 3.11+ installed
- [ ] PostgreSQL database running

---

## Step 1: Azure Portal Configuration (5 minutes)

### 1.1 Create App Registration

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Microsoft Entra ID** → **App registrations** → **New registration**
3. Fill in:
   - **Name**: `Cardea Security Platform`
   - **Supported account types**: Multi-tenant
   - **Redirect URI**: Platform = SPA, URI = `http://localhost:5173`
4. Click **Register**

### 1.2 Get Your Credentials

Copy these values from the Overview page:
```
Application (client) ID: _______________________________
Directory (tenant) ID:   _______________________________
```

### 1.3 Create Client Secret

1. Go to **Certificates & secrets** → **New client secret**
2. Description: `Cardea Backend`
3. Expires: 24 months
4. Click **Add** and **COPY THE VALUE IMMEDIATELY**:
```
Client Secret: _______________________________
```

### 1.4 Configure Authentication

1. Go to **Authentication**
2. Under **Implicit grant and hybrid flows**, check:
   - ✅ Access tokens
   - ✅ ID tokens
3. Click **Save**

### 1.5 Set API Permissions

1. Go to **API permissions**
2. Verify **Microsoft Graph** → **User.Read** is present
3. Click **Grant admin consent** (if available)

---

## Step 2: Backend Configuration (3 minutes)

### 2.1 Install Python Dependencies

```bash
cd oracle
pip install msal==1.26.0 cryptography==41.0.7
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

### 2.2 Configure Environment Variables

```bash
cd /path/to/cardea
cp .env.template .env
nano .env  # or use your favorite editor
```

Fill in these values:

```bash
# PASTE YOUR AZURE CREDENTIALS HERE
AZURE_TENANT_ID=your-tenant-id-from-step-1.2
AZURE_CLIENT_ID=your-client-id-from-step-1.2
AZURE_CLIENT_SECRET=your-client-secret-from-step-1.3
AZURE_AUTHORITY=https://login.microsoftonline.com/your-tenant-id

# Generate a secure secret key
SECRET_KEY=run-this-command-to-generate: python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Database (adjust if needed)
DATABASE_URL=postgresql+asyncpg://oracle:oracle_dev_password@localhost:5432/cardea_oracle
```

### 2.3 Update Database Schema

```bash
cd oracle
psql -U oracle -d cardea_oracle << EOF
ALTER TABLE users ADD COLUMN IF NOT EXISTS azure_oid VARCHAR(255) UNIQUE;
CREATE INDEX IF NOT EXISTS idx_users_azure_oid ON users(azure_oid);
EOF
```

---

## Step 3: Frontend Configuration (3 minutes)

### 3.1 Install JavaScript Dependencies

```bash
cd dashboard
npm install @azure/msal-browser@^3.7.1 @azure/msal-react@^2.0.10
```

### 3.2 Configure Environment Variables

```bash
cp .env.template .env
nano .env  # or use your favorite editor
```

Fill in these values:

```bash
# PASTE YOUR AZURE CREDENTIALS HERE
VITE_AZURE_CLIENT_ID=your-client-id-from-step-1.2
VITE_AZURE_TENANT_ID=your-tenant-id-from-step-1.2
VITE_AZURE_AUTHORITY=https://login.microsoftonline.com/your-tenant-id

# These should work as-is for local development
VITE_REDIRECT_URI=http://localhost:5173
VITE_POST_LOGOUT_REDIRECT_URI=http://localhost:5173
VITE_API_URL=http://localhost:8000
VITE_API_SCOPES=api://your-client-id/access_as_user
VITE_ENABLE_AZURE_AUTH=true
```

---

## Step 4: Test It! (4 minutes)

### 4.1 Start Backend

```bash
cd oracle
python src/main.py
```

Expected output:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
✅ Azure Entra ID authentication initialized
```

### 4.2 Start Frontend

Open a new terminal:

```bash
cd dashboard
npm run dev
```

Expected output:
```
  VITE v7.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

### 4.3 Test Login

1. Open browser to `http://localhost:5173`
2. Click the **Microsoft** button
3. Sign in with your Microsoft account
4. You should be redirected to the dashboard!

---

## Verification Checklist

✅ **Backend is running** on http://localhost:8000  
✅ **Frontend is running** on http://localhost:5173  
✅ **Microsoft button is enabled** (not greyed out)  
✅ **Clicking Microsoft redirects** to login.microsoftonline.com  
✅ **After login, redirected back** to your app  
✅ **Dashboard loads** without errors  
✅ **User created in database**:

```bash
psql -U oracle -d cardea_oracle -c "SELECT email, azure_oid FROM users ORDER BY created_at DESC LIMIT 1;"
```

---

## Troubleshooting

### ❌ Microsoft button is greyed out

**Problem**: Environment variables not loaded

**Fix**:
```bash
cd dashboard
cat .env | grep VITE_AZURE_CLIENT_ID
```

If it shows `PASTE_YOUR_...`, you need to fill in the actual value.

**Then restart**:
```bash
npm run dev
```

### ❌ "Reply URL does not match" error

**Problem**: Redirect URI mismatch

**Fix**:
1. Go to Azure Portal → Your App → Authentication
2. Add exactly: `http://localhost:5173` (no trailing slash)
3. Platform: **Single-page application (SPA)**

### ❌ CORS error in browser console

**Problem**: Backend not allowing frontend origin

**Fix**: Add to `oracle/src/main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### ❌ Token validation fails (401 Unauthorized)

**Problem**: Backend can't validate Azure tokens

**Fix**: Check backend logs for specific error. Common issues:
- Wrong `AZURE_TENANT_ID` (must match Azure Portal)
- Clock skew (sync system time)
- Missing `azure_oid` column in database

---

## Next Steps

### 🔒 Secure Your Application

1. **Generate strong SECRET_KEY**:
   ```bash
   python3 -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Add `.env` to `.gitignore`**:
   ```bash
   echo ".env" >> .gitignore
   ```

3. **Rotate client secrets** every 6-12 months

### 🚀 Production Deployment

See [MICROSOFT_ENTRA_SETUP.md](./MICROSOFT_ENTRA_SETUP.md) for:
- Production redirect URI configuration
- HTTPS setup
- Security best practices
- Monitoring and logging

### 📚 Learn More

- [Full Setup Guide](./MICROSOFT_ENTRA_SETUP.md) - Complete documentation
- [Microsoft Entra ID Docs](https://learn.microsoft.com/en-us/entra/)
- [MSAL.js Guide](https://github.com/AzureAD/microsoft-authentication-library-for-js)

---

## Support

**Not working?** Check the [Troubleshooting section](./MICROSOFT_ENTRA_SETUP.md#troubleshooting) in the full guide.

**Still stuck?** Make sure:
1. All environment variables are set (no `PASTE_YOUR_...`)
2. Both backend and frontend are running
3. Redirect URI in Azure Portal matches exactly
4. Database has `azure_oid` column

---

**Time to complete**: ~15 minutes  
**Difficulty**: Beginner-friendly  
**Last updated**: January 5, 2026
