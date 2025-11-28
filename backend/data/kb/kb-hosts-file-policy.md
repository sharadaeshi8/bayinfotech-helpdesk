---
id: kb-hosts-file-policy
title: Network Configuration Policy
category: system
subcategory: policy
severity_hint: MEDIUM
tier_hint: TIER_2
tags: [hosts, dns, policy]
related_docs: [kb-dns-resolution]
---

# Policy
Manual editing of `/etc/hosts` is prohibited as it creates technical debt and bypasses central DNS management.

# Approved Method
Use the central DNS server for all hostname resolutions. If a custom record is needed, submit a request to the Network Team.
