---
id: kb-dns-resolution
title: DNS Resolution Troubleshooting
category: infrastructure
subcategory: networking
severity_hint: MEDIUM
tier_hint: TIER_2
tags: [dns, network, resolution]
related_docs: [kb-network-connectivity]
---

# Problem Statement
Cannot resolve internal or external hostnames.

# Resolution Steps
1. Verify DNS settings in `/etc/resolv.conf`. Should point to internal DNS (10.x.x.x).
2. Test resolution: `nslookup internal-service`.
3. Flush DNS cache: `sudo systemd-resolve --flush-caches`.
4. Do NOT manually edit `/etc/hosts` as a permanent fix.
