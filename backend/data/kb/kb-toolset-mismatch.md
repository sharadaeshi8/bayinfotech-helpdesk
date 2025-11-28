---
id: kb-toolset-mismatch
title: Incorrect Toolset Loaded
category: environment
subcategory: configuration
severity_hint: MEDIUM
tier_hint: TIER_2
tags: [tools, ide, vscode, missing]
related_docs: []
---

# Problem Statement
Required tools (VS Code, Terminal, specific CLIs) are missing or incorrect.

# Resolution Steps
1. Verify the lab requirements.
2. Check if the tool is installed but not in PATH.
3. Run `source /etc/profile` to reload environment variables.
4. If tools are genuinely missing, the container image may be outdated.
