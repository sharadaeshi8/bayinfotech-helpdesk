---
id: kb-container-init-failure
title: Container Initialization Errors
category: infrastructure
subcategory: containers
severity_hint: HIGH
tier_hint: TIER_3
tags: [container, docker, kubernetes, init-fail]
related_docs: []
---

# Problem Statement
Container fails to start with initialization error.

# Common Errors
- "CrashLoopBackOff"
- "Error: missing /opt/startup.sh"

# Resolution Steps
1. Check container logs: `kubectl logs [pod-name]`.
2. Verify image version matches the lab requirement.
3. Check if required volume mounts are present.
4. If "missing /opt/startup.sh", the image may be corrupted. Escalate to Platform Team.
