# Microsoft Entra External ID Integration - Documentation

Complete documentation for integrating Microsoft Entra External ID (formerly Azure AD B2C) authentication into the Cardea security platform.

---

## 📚 Documentation Index

### 🚀 Getting Started

1. **[Quick Start Guide](./QUICKSTART_ENTRA.md)** ⭐ **START HERE**
   - Get up and running in 15 minutes
   - Step-by-step instructions
   - Perfect for first-time setup
   - Includes troubleshooting

2. **[Azure Portal Checklist](./AZURE_PORTAL_CHECKLIST.md)**
   - Complete configuration checklist
   - Verification steps
   - Common mistakes to avoid
   - Maintenance schedule

### 📖 Complete Documentation

3. **[Full Setup Guide](./MICROSOFT_ENTRA_SETUP.md)**
   - Comprehensive documentation
   - Architecture overview
   - Backend and frontend configuration
   - Database schema updates
   - Security best practices
   - Production deployment guide
   - Detailed troubleshooting

4. **[Authentication Flow Diagrams](./AUTHENTICATION_FLOW_DIAGRAMS.md)**
   - Visual authentication flows
   - Architecture diagrams
   - Token validation process
   - User journey maps

5. **[Common Error Solutions](./ERROR_SOLUTIONS.md)**
   - Azure AD error codes explained
   - MSAL error troubleshooting
   - Application-specific issues
   - Quick fixes and solutions

---

## 🎯 Which Guide Should I Use?

### I want to get started quickly
→ **[Quick Start Guide](./QUICKSTART_ENTRA.md)**

### I'm configuring Azure Portal
→ **[Azure Portal Checklist](./AZURE_PORTAL_CHECKLIST.md)**

### I need complete documentation
→ **[Full Setup Guide](./MICROSOFT_ENTRA_SETUP.md)**

### I'm having issues
→ **[Common Error Solutions](./ERROR_SOLUTIONS.md)** or troubleshooting sections in any guide

### I'm deploying to production
→ **[Full Setup Guide](./MICROSOFT_ENTRA_SETUP.md)** (Production section)

---

## 📦 What's Been Integrated

### Backend (Oracle)
- ✅ `azure_auth.py` - Azure token validation service
- ✅ `config.py` - Updated with Azure configuration
- ✅ `requirements.txt` - Added MSAL and dependencies
- ✅ `.env.template` - Credential placeholders

### Frontend (Dashboard)
- ✅ `authConfig.ts` - MSAL configuration
- ✅ `contexts/AuthContext.tsx` - React auth provider
- ✅ `main.tsx` - MSAL wrapper
- ✅ `LoginPage.tsx` - Microsoft sign-in button
- ✅ `package.json` - MSAL dependencies
- ✅ `.env.template` - Credential placeholders

### Documentation
- ✅ Quick start guide (15 minutes)
- ✅ Complete setup guide
- ✅ Azure Portal checklist
- ✅ This index

---

## 🔐 Security Features

### Implemented
- ✅ OAuth 2.0 / OpenID Connect
- ✅ JWT token validation
- ✅ Signature verification with Microsoft's public keys
- ✅ Token caching (24-hour TTL)
- ✅ Automatic user provisioning
- ✅ Role-based access control (RBAC)
- ✅ Secure credential storage (environment variables)

### Recommended for Production
- 🔒 HTTPS enforcement
- 🔒 Rate limiting
- 🔒 Azure Key Vault for secrets
- 🔒 Conditional Access policies
- 🔒 Multi-factor authentication (MFA)
- 🔒 Application Insights monitoring

---

## 🛠️ Prerequisites

### Required
- Azure account with active subscription
- Microsoft Entra ID tenant (free with Azure)
- Node.js 18+ and npm
- Python 3.11+
- PostgreSQL database

### Recommended
- Basic understanding of OAuth 2.0
- Familiarity with React and FastAPI
- Access to Azure Portal

---

## 📋 Configuration Placeholders

Both `.env.template` files contain placeholders you need to fill in:

### Required from Azure Portal
```
AZURE_TENANT_ID=PASTE_YOUR_TENANT_ID_HERE
AZURE_CLIENT_ID=PASTE_YOUR_CLIENT_ID_HERE
AZURE_CLIENT_SECRET=PASTE_YOUR_CLIENT_SECRET_HERE
```

### How to Get These
See **[Quick Start Guide - Step 1](./QUICKSTART_ENTRA.md#step-1-azure-portal-configuration-5-minutes)**

---

## 🧪 Testing Your Integration

### Quick Test (2 minutes)

1. **Start backend**:
   ```bash
   cd oracle
   python src/main.py
   ```

2. **Start frontend**:
   ```bash
   cd dashboard
   npm run dev
   ```

3. **Test login**:
   - Open http://localhost:5173
   - Click "Microsoft" button
   - Sign in with Microsoft account
   - Should redirect to dashboard

### Verification

```bash
# Check if user was created
psql -U oracle -d cardea_oracle -c "SELECT email, azure_oid FROM users;"
```

---

## 🐛 Common Issues

### Issue: Microsoft button is greyed out
**Cause**: Environment variables not set  
**Fix**: See [Quick Start - Troubleshooting](./QUICKSTART_ENTRA.md#-microsoft-button-is-greyed-out)

### Issue: "Reply URL does not match"
**Cause**: Redirect URI mismatch  
**Fix**: See [Azure Portal Checklist - Common Mistakes](./AZURE_PORTAL_CHECKLIST.md#-mistake-3-incorrect-redirect-uri)

### Issue: CORS errors
**Cause**: Backend not allowing frontend origin  
**Fix**: See [Quick Start - Troubleshooting](./QUICKSTART_ENTRA.md#-cors-error-in-browser-console)

### More Help
See full [Troubleshooting Guide](./MICROSOFT_ENTRA_SETUP.md#troubleshooting)

---

## 🏗️ Architecture Overview

```
┌──────────────────┐
│  User's Browser  │
└────────┬─────────┘
         │
         │ 1. Click "Microsoft"
         ▼
┌──────────────────────────┐
│  React Frontend (MSAL)   │
│  http://localhost:5173   │
└────────┬─────────────────┘
         │
         │ 2. Redirect to Microsoft
         ▼
┌──────────────────────────────┐
│  Microsoft Entra ID          │
│  login.microsoftonline.com   │
└────────┬─────────────────────┘
         │
         │ 3. User authenticates
         │ 4. Returns with token
         ▼
┌──────────────────────────┐
│  React Frontend          │
│  + Access Token          │
└────────┬─────────────────┘
         │
         │ 5. API calls with token
         ▼
┌──────────────────────────┐
│  Oracle Backend (FastAPI)│
│  http://localhost:8000   │
│  - Validates token       │
│  - Creates/updates user  │
└────────┬─────────────────┘
         │
         │ 6. Store user
         ▼
┌──────────────────────────┐
│  PostgreSQL Database     │
│  - Users table           │
│  - azure_oid column      │
└──────────────────────────┘
```

---

## 🔄 User Flow

### First-Time Login
1. User clicks "Microsoft" button
2. Redirected to Microsoft login page
3. User signs in with Microsoft account
4. Consents to permissions (if first time)
5. Redirected back with access token
6. Frontend stores token in session
7. Frontend calls backend API with token
8. Backend validates token with Microsoft
9. Backend creates user in database
10. User sees dashboard

### Subsequent Logins
1. User clicks "Microsoft" button
2. Token already exists (if not expired)
3. Or quick re-authentication with Microsoft
4. User sees dashboard immediately

---

## 📊 File Structure

```
cardea/
├── .env.template                    # Backend credentials (copy to .env)
├── dashboard/
│   ├── .env.template               # Frontend credentials (copy to .env)
│   ├── package.json                # Updated with MSAL dependencies
│   └── src/
│       ├── authConfig.ts           # MSAL configuration
│       ├── main.tsx                # MSAL provider wrapper
│       ├── contexts/
│       │   └── AuthContext.tsx     # React auth context
│       └── components/
│           └── LoginPage.tsx       # Updated with MS button
├── oracle/
│   ├── requirements.txt            # Updated with MSAL
│   └── src/
│       ├── azure_auth.py           # New: Azure authentication
│       ├── config.py               # Updated with Azure settings
│       └── main.py                 # (may need CORS update)
└── docs/
    ├── README.md                   # This file
    ├── QUICKSTART_ENTRA.md         # Quick start guide
    ├── MICROSOFT_ENTRA_SETUP.md    # Complete guide
    └── AZURE_PORTAL_CHECKLIST.md   # Azure checklist
```

---

## 📚 Additional Resources

### Microsoft Documentation
- [Microsoft Entra ID Overview](https://learn.microsoft.com/entra/identity/)
- [App Registration Guide](https://learn.microsoft.com/azure/active-directory/develop/quickstart-register-app)
- [MSAL.js Documentation](https://github.com/AzureAD/microsoft-authentication-library-for-js)
- [MSAL React Guide](https://github.com/AzureAD/microsoft-authentication-library-for-js/tree/dev/lib/msal-react)

### Tools
- [JWT Debugger](https://jwt.ms/) - Decode and inspect tokens
- [Graph Explorer](https://developer.microsoft.com/graph/graph-explorer) - Test Microsoft Graph API
- [Azure CLI](https://learn.microsoft.com/cli/azure/) - Automate Azure tasks

### Community
- [Stack Overflow [azure-ad]](https://stackoverflow.com/questions/tagged/azure-ad)
- [Microsoft Q&A](https://learn.microsoft.com/answers/)
- [GitHub Issues](https://github.com/AzureAD/microsoft-authentication-library-for-js/issues)

---

## 🤝 Contributing

Found an issue with the integration? Have suggestions?

1. Check existing issues
2. Document the problem clearly
3. Include error messages and logs
4. Mention which guide you were following

---

## 📝 Version History

### Version 1.0.0 (January 5, 2026)
- ✅ Initial integration complete
- ✅ Backend token validation
- ✅ Frontend MSAL integration
- ✅ Automatic user provisioning
- ✅ Complete documentation

---

## ⚡ Quick Links

- **[Quick Start](./QUICKSTART_ENTRA.md)** - Get started in 15 minutes
- **[Azure Checklist](./AZURE_PORTAL_CHECKLIST.md)** - Configuration checklist
- **[Full Guide](./MICROSOFT_ENTRA_SETUP.md)** - Complete documentation
- **[Azure Portal](https://portal.azure.com)** - Configure your app
- **[JWT Debugger](https://jwt.ms)** - Debug tokens

---

**Last Updated**: January 5, 2026  
**Status**: ✅ Integration Complete  
**Tested**: January 2026  
**Next Review**: June 2026
