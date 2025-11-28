---
id: kb-network-connectivity
title: Network Connectivity Issues
category: infrastructure
subcategory: networking
severity_hint: MEDIUM
tier_hint: TIER_2
tags: [network, ping, connection]
related_docs: [kb-dns-resolution]
---

# Problem Statement
Loss of network connectivity to/from VM.

# Resolution Steps
1. Check interface status: `ip link show`.
2. Verify IP address assignment: `ip addr show`.
3. Ping gateway.
4. Check firewall rules: `sudo iptables -L`.
