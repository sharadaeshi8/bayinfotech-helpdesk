---
id: kb-session-timeout
title: Session Timeout Configuration
category: authentication
subcategory: session-management
severity_hint: LOW
tier_hint: TIER_2
tags: [session, timeout, config]
related_docs: [kb-auth-loop]
---

# Problem Statement
Users are logged out too frequently or sessions persist too long.

# Resolution Steps
1. Go to System Settings -> Security -> Session Policies.
2. Adjust "Idle Session Timeout" (Standard: 30 mins).
3. Adjust "Absolute Session Timeout" (Standard: 12 hours).
4. Apply changes.
