# Azure Portal Configuration Checklist

**Complete reference for configuring Microsoft Entra External ID in Azure Portal**

---

## 📋 Configuration Checklist

Use this checklist to ensure you've configured everything correctly in the Azure Portal.

---

### ✅ App Registration

- [ ] Created new app registration
- [ ] Named it descriptively (e.g., "Cardea Security Platform")
- [ ] Selected appropriate account type (recommended: Multi-tenant)
- [ ] Added SPA redirect URI: `http://localhost:5173`
- [ ] Recorded Application (client) ID
- [ ] Recorded Directory (tenant) ID

---

### ✅ Certificates & Secrets

- [ ] Created new client secret
- [ ] Added description (e.g., "Backend API Secret")
- [ ] Set expiration (recommended: 24 months)
- [ ] **COPIED and SAVED** the secret value immediately
- [ ] Stored secret securely (password manager or `.env` file)

---

### ✅ Authentication Settings

**Platform Configurations:**
- [ ] Added SPA platform with redirect URI: `http://localhost:5173`
- [ ] Added production redirect URI (when deploying)
- [ ] No Web platform configured (unless using backend-driven flow)

**Implicit Grant and Hybrid Flows:**
- [ ] ✅ Access tokens (checked)
- [ ] ✅ ID tokens (checked)

**Advanced Settings:**
- [ ] Allow public client flows: **No**
- [ ] Supported account types: Verified correct selection

---

### ✅ API Permissions

**Microsoft Graph:**
- [ ] `User.Read` - Delegated (should be there by default)
- [ ] `email` - Delegated (optional but recommended)
- [ ] `profile` - Delegated (optional but recommended)
- [ ] `openid` - Delegated (usually automatic)

**Admin Consent:**
- [ ] Granted admin consent for all permissions (if you're admin)
- [ ] OR documented that users will need to consent

---

### ✅ Expose an API (For Backend)

- [ ] Set Application ID URI (e.g., `api://{CLIENT_ID}`)
- [ ] Added scope: `access_as_user`
- [ ] Configured scope consent settings:
  - Who can consent: **Admins and users**
  - Admin consent display name: Set
  - Admin consent description: Set
  - User consent display name: Set
  - User consent description: Set
  - State: **Enabled**

---

### ✅ Token Configuration (Optional)

**Optional Claims - ID Token:**
- [ ] `email`
- [ ] `family_name`
- [ ] `given_name`

**Optional Claims - Access Token:**
- [ ] `email`
- [ ] `family_name`
- [ ] `given_name`

---

### ✅ Branding (Optional)

- [ ] Added application logo
- [ ] Set publisher domain
- [ ] Added terms of service URL
- [ ] Added privacy statement URL

---

## 🔍 Verification Steps

### 1. Check Overview Page

Navigate to: **App registrations** → **Your App** → **Overview**

Verify you see:
```
Application (client) ID: [GUID]
Directory (tenant) ID: [GUID]
Application ID URI: api://[CLIENT_ID]
```

### 2. Test Authentication Flow

**Option A: Use JWT Debugger**

1. Get a token from your app
2. Go to https://jwt.ms
3. Paste the token
4. Verify claims include:
   - `aud` (audience): Your client ID
   - `iss` (issuer): `https://login.microsoftonline.com/{tenant}/v2.0`
   - `email`: User's email
   - `oid`: User's object ID

**Option B: Use Microsoft Graph Explorer**

1. Go to https://developer.microsoft.com/graph/graph-explorer
2. Sign in with your account
3. Try: `GET https://graph.microsoft.com/v1.0/me`
4. Should return your user profile

### 3. Check Redirect URIs

Navigate to: **Authentication** → **Platform configurations**

Verify you see:
```
Single-page application
├── http://localhost:5173
└── https://yourdomain.com (for production)
```

### 4. Check Client Secrets

Navigate to: **Certificates & secrets** → **Client secrets**

Verify:
- At least one active secret exists
- Expiration date is in the future
- You have the secret value stored securely

⚠️ **Warning**: If expired, create a new secret and update your backend `.env`

---

## 📸 Azure Portal Navigation Guide

### Finding Microsoft Entra ID

**Path 1: Search**
```
Azure Portal Home → Search bar → "Microsoft Entra ID" → Click first result
```

**Path 2: Menu**
```
Azure Portal Home → Menu (☰) → Microsoft Entra ID
```

### App Registrations

```
Microsoft Entra ID → Manage (sidebar) → App registrations
```

### Your Specific App

```
App registrations → All applications → Click your app name
```

### Common Settings Locations

| Setting | Location |
|---------|----------|
| Client ID, Tenant ID | **Overview** |
| Create client secret | **Certificates & secrets** |
| Redirect URIs | **Authentication** |
| API permissions | **API permissions** |
| Expose scopes | **Expose an API** |
| Optional claims | **Token configuration** |

---

## 🔐 Security Recommendations

### Client Secrets Management

- [ ] **Never commit secrets** to version control
- [ ] **Use Azure Key Vault** for production secrets
- [ ] **Rotate secrets** before expiration
- [ ] **Create alerts** for expiring secrets (90 days before)
- [ ] **Have multiple valid secrets** during rotation period

### Access Control

- [ ] Review who has access to this app registration
- [ ] Use **Azure RBAC** roles appropriately:
  - **Application Administrator**: Can manage all app registrations
  - **Cloud Application Administrator**: Can manage cloud apps
  - **Application Developer**: Can create app registrations
- [ ] Enable **Conditional Access** policies (if available)
- [ ] Configure **MFA** for all admin accounts

### Monitoring

- [ ] Enable **Sign-in logs** (Azure AD Premium required)
- [ ] Set up **alerts** for:
  - Failed sign-ins
  - Sign-ins from unusual locations
  - Consent grants
- [ ] Review **Audit logs** regularly
- [ ] Configure **Azure Monitor** integration

---

## 🚨 Common Configuration Mistakes

### ❌ Mistake 1: Wrong Platform Type

**Problem**: Selected "Web" instead of "Single-page application"

**Symptoms**: 
- Redirect errors
- Can't authenticate from frontend

**Fix**: Delete Web platform, add SPA platform

---

### ❌ Mistake 2: Missing Implicit Grant

**Problem**: Didn't check "Access tokens" and "ID tokens"

**Symptoms**:
- `error: invalid_request`
- `error_description: AADSTS900144`

**Fix**: Go to Authentication → Implicit grant → Check both boxes

---

### ❌ Mistake 3: Incorrect Redirect URI

**Problem**: Redirect URI doesn't exactly match

**Symptoms**:
- `error: redirect_uri_mismatch`
- `error_description: AADSTS50011`

**Fix**: 
- Must match EXACTLY (including http/https, port, trailing slash)
- Common mistakes:
  - `http://localhost:5173/` vs `http://localhost:5173`
  - `https://` vs `http://`
  - `www.domain.com` vs `domain.com`

---

### ❌ Mistake 4: Forgot to Copy Client Secret

**Problem**: Clicked away without copying secret value

**Symptoms**:
- Can't authenticate from backend
- `401 Unauthorized` errors

**Fix**: 
- Create a new client secret
- Old secret value is **NOT RETRIEVABLE**
- Update backend `.env` with new secret

---

### ❌ Mistake 5: Using Personal Account Type Only

**Problem**: Selected "Personal Microsoft accounts only"

**Symptoms**:
- Organizational accounts can't sign in
- `error: unauthorized_client`

**Fix**: 
- Can't change account type after creation
- Must create new app registration
- Select "Multi-tenant" or "Single tenant"

---

## 📖 Additional Azure Portal Features

### Application Insights Integration

```
Your App → Monitoring → Application Insights → Enable
```

Benefits:
- Track authentication failures
- Monitor token acquisition performance
- Detect unusual sign-in patterns

### Conditional Access Policies

```
Microsoft Entra ID → Security → Conditional Access
```

Use cases:
- Require MFA for sensitive operations
- Block sign-ins from specific countries
- Require compliant devices

### Enterprise Applications

```
Microsoft Entra ID → Enterprise applications → Your app
```

Here you can:
- Assign users and groups
- Configure SSO
- View sign-in logs
- Set up provisioning

---

## 🔄 Maintenance Schedule

### Weekly
- [ ] Check sign-in logs for anomalies

### Monthly
- [ ] Review API permissions
- [ ] Check user assignments

### Quarterly
- [ ] Audit access to app registration
- [ ] Review conditional access policies
- [ ] Update documentation

### Bi-Annually
- [ ] Rotate client secrets (before expiration)
- [ ] Review security recommendations
- [ ] Test disaster recovery procedures

---

## 📞 Support Resources

### Azure Portal Help

- **In-Portal Help**: Click **?** icon in top-right corner
- **Azure Support**: Create support ticket (requires support plan)
- **Community**: [Microsoft Q&A](https://learn.microsoft.com/answers/)

### Documentation

- [App Registration](https://learn.microsoft.com/azure/active-directory/develop/quickstart-register-app)
- [Authentication](https://learn.microsoft.com/azure/active-directory/develop/authentication-vs-authorization)
- [Permissions](https://learn.microsoft.com/azure/active-directory/develop/v2-permissions-and-consent)

### Troubleshooting

- [Error Codes](https://learn.microsoft.com/azure/active-directory/develop/reference-aadsts-error-codes)
- [Best Practices](https://learn.microsoft.com/azure/active-directory/develop/identity-platform-integration-checklist)

---

## ✨ Pro Tips

1. **Bookmark your app registration** in Azure Portal
2. **Use descriptive names** for secrets (include creation date)
3. **Set calendar reminders** for secret expiration
4. **Create a test app** for development/staging
5. **Document all configuration** in your team wiki
6. **Use Azure CLI** for automation: `az ad app`

---

**Last Updated**: January 5, 2026  
**Azure Portal Version**: Current as of January 2026  
**Verified**: Microsoft Entra ID (formerly Azure AD)
