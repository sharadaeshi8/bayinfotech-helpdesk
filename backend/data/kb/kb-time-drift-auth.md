---
id: kb-time-drift-auth
title: Clock Skew Causing Auth Failures
category: authentication
subcategory: troubleshooting
severity_hint: MEDIUM
tier_hint: TIER_2
tags: [time, clock, ntp, auth-failure]
related_docs: [kb-auth-loop]
---

# Problem Statement
Authentication fails due to time difference between client/server and Identity Provider.

# Resolution Steps
1. Check client machine time against a standard time source (e.g., time.gov).
2. If using a VM, ensure NTP is configured and running: `sudo systemctl status ntp`.
3. Force sync time: `sudo ntpdate pool.ntp.org`.
4. Retry authentication.
