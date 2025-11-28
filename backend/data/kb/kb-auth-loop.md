---
id: kb-auth-loop
title: Login Redirection Troubleshooting
category: authentication
subcategory: session-management
severity_hint: MEDIUM
tier_hint: TIER_2
tags: [login, redirect, session, cookies, saml]
related_docs: [kb-mfa-reset, kb-session-timeout]
---

# Problem Statement
Users experience continuous redirects to the login page even after successful authentication.

# Root Causes
1. Browser cache/cookie corruption
2. Session timeout misconfiguration (default: 30 minutes)
3. SAML token expiration issues
4. Conflicting browser extensions
5. Clock skew between client and server

# Resolution Steps

## Step 1: Clear Browser Data
1. Press Ctrl+Shift+Delete (Windows) or Cmd+Shift+Delete (Mac)
2. Select "Cookies and other site data" and "Cached images and files"
3. Click "Clear data"
4. Attempt login again

## Step 2: Check Session Configuration
1. Navigate to Admin Panel → System Settings → Session Management
2. Verify session timeout is set to 1800 seconds (30 minutes)
3. Check "Enable session persistence" is enabled
4. Save changes and restart the application service

## Step 3: Verify SAML Configuration
1. Check Identity Provider logs for successful assertion
2. Ensure the Assertion Consumer Service (ACS) URL matches the configuration
3. Verify the signing certificate has not expired

# When to Escalate
- Issue persists after all steps completed
- Multiple users reporting simultaneously (potential server issue)
- SAML configuration changes require admin privileges
- Session logs show authentication failures with error code 401-LOOP
