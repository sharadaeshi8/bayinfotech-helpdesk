---
id: kb-vm-crash-recovery
title: VM Crash Recovery Procedures
category: infrastructure
subcategory: vm-management
severity_hint: HIGH
tier_hint: TIER_3
tags: [vm, crash, recovery, snapshot]
related_docs: [kb-data-recovery]
---

# Problem Statement
Virtual Machine has crashed or is unresponsive.

# Resolution Steps
1. Check VM status in the Lab Dashboard.
2. If "Running" but unresponsive, try "Soft Reboot".
3. If "Soft Reboot" fails, use "Hard Reset" (Warning: Potential data loss).
4. If VM fails to boot, restore from last nightly snapshot.

# Data Recovery
Note: Data not saved to persistent volumes may be lost during a crash. See KB-DATA-RECOVERY.
