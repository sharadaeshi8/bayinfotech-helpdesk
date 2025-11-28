---
id: kb-performance-issues
title: System Performance Troubleshooting
category: troubleshooting
subcategory: performance
severity_hint: MEDIUM
tier_hint: TIER_2
tags: [slow, lag, cpu, memory]
related_docs: [kb-system-monitoring]
---

# Problem Statement
System is running slowly or lagging.

# Resolution Steps
1. Check resource usage: `top` or `htop`.
2. Identify high-consuming processes.
3. Check for I/O wait (wa in top).
4. If a specific process is stuck, try `kill -15 [PID]`.
