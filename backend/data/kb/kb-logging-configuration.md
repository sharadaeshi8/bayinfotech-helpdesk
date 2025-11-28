---
id: kb-logging-configuration
title: Proper Logging Setup
category: system
subcategory: compliance
severity_hint: MEDIUM
tier_hint: TIER_2
tags: [logging, audit, compliance]
related_docs: []
---

# Policy
System logging MUST be enabled for security auditing. Disabling logging is a policy violation.

# Configuration
1. Logs are stored in `/var/log/`.
2. To configure log rotation, edit `/etc/logrotate.conf`.
3. To filter logs for debugging, use `grep` or `journalctl` filters, do not stop the service.
