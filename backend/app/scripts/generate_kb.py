import os
import shutil

KB_DIR = "data/kb"

# Ensure directory exists
if os.path.exists(KB_DIR):
    shutil.rmtree(KB_DIR)
os.makedirs(KB_DIR)

kb_files = [
    # --- NEW ARTICLES (v2/Policy) ---
    {
        "filename": "00-platform-overview.md",
        "content": """---
id: kb-platform-overview
title: Platform Overview – CyberLab Help Desk
version: 1.0
last_updated: 2024-06-01
tags: [overview, platform, roles, architecture]
---

# Platform Overview – CyberLab Help Desk

CyberLab Help Desk supports users of the CyberLab Training Platform, which provides
browser-based access to:

- Virtual lab environments (VMs and containers)
- Pre-configured ranges (networked lab topologies)
- Training modules and assessments

## User Roles

The following roles are relevant for help desk routing and permissions:

- **Trainee** – primary learner, runs labs and exercises.
- **Instructor** – manages classes, assigns labs, monitors progress.
- **Operator** – manages day-to-day operations of lab environments.
- **Support Engineer** – handles escalated technical incidents.
- **Admin** – manages configuration, integrations, and user lifecycle.

Role information should be used for:

- Tailoring explanations (Trainee vs. Support Engineer)
- Determining whether system-level instructions are allowed
- Escalation routing (e.g., complex issues go to Support Engineers)

## Environment Types

CyberLab includes the following environment types:

- **Personal Lab VM** – one VM per trainee.
- **Shared Exercise Range** – multi-VM, multi-user environment.
- **Container-based Labs** – fast, ephemeral labs running as containers.

Each environment type has different recovery and escalation procedures (see
`kb-virtual-lab-recovery` and `kb-container-runtime-troubleshooting`).

## Help Desk Responsibilities

The AI Help Desk is responsible for:

- Answering common questions using the approved Knowledge Base (KB) only.
- Guiding users through safe, documented troubleshooting steps.
- Determining whether an issue can be resolved at self-service Tier 0 or requires escalation.
- Enforcing safety controls and blocking unsafe requests.

The Help Desk must **never**:

- Invent policies, procedures, commands, or URLs that are not in the KB.
- Provide host-level or infrastructure-level access instructions.
- Modify or override the tiering and escalation rules described in `kb-tiering-escalation`.
"""
    },
    {
        "filename": "01-access-and-authentication-v2.1.md",
        "content": """---
id: kb-access-authentication
title: Access and Authentication Troubleshooting
version: 2.1
last_updated: 2024-04-10
tags: [authentication, sso, login, access]
---

# Access and Authentication Troubleshooting (v2.1)

This document describes how to troubleshoot authentication and login issues
for the CyberLab platform.

> **Note:** This document supersedes earlier authentication guidance in
> `kb-auth-policy-2023`. For MFA-related policies, use `kb-auth-policy-2024`.

## Common Symptoms

1. **Login Redirection Loop**
   - User logs in, sees "Authentication successful", then is redirected back
     to the login page repeatedly.

2. **Session Expired Immediately**
   - User logs in successfully but is logged out after a few seconds.

3. **Time Drift Authentication Failures**
   - User reports that their lab VM clock is behind and cannot complete certain
     authentication workflows (e.g., token validation).

---

## 1. Login Redirection Loop

**Symptom:**
User reports: "I keep getting redirected to the login page even after logging in."

### 1.1 Required Clarifying Questions

Before suggesting steps, ask:

1. Which **browser** are you using?
2. Are you accessing CyberLab from within a lab VM or your local machine?
3. Approximately what **time** did the issue start?

### 1.2 Self-Service Steps (Tier 0/Tier 1)

1. Instruct the user to:
   - Close all CyberLab tabs.
   - Clear browser **cookies and site data** for `*.cyberlab.local`.
   - Close and reopen the browser.
   - Navigate to the CyberLab login page and try again.

2. If the user is accessing from inside a lab VM, ensure:
   - The VM browser is not using stale cached SSO sessions.

### 1.3 Escalation Criteria

Escalate to Tier 2 (Support Engineer) if:

- The user has performed all steps in 1.2 **twice** and the issue persists.
- Multiple users report the same behavior within a short time window.

When escalating, capture:

- Browser type and version.
- Network location (lab VM vs local).
- Approximate start time.
- Any error messages or codes observed.

---

## 2. Session Expired Immediately

If the user is logged out within seconds:

1. Verify with user:
   - Whether they are using private/incognito mode.
   - Whether any browser extensions are blocking cookies.

2. If session still expires:
   - Escalate to Tier 2 with captured session details.

---

## 3. Time Drift Authentication Failures

**Symptom:**
User reports: "My lab VM clock is behind and authentication keeps failing."

### 3.1 Policy

Trainees and Instructors are **not allowed** to modify time synchronization
or system clocks inside lab VMs.

Only Operators and Support Engineers may perform time-related remediation.

### 3.2 AI Help Desk Behavior

- If user is a **Trainee** or **Instructor**:
  - Do **not** provide commands or procedures to adjust system time.
  - Inform the user that time synchronization is a platform-level function.
  - Escalate to Tier 2 (Support Engineer) with:
    - VM name or ID.
    - Reported time skew (approximate).
- If user is an **Operator** or **Support Engineer**:
  - You may reference the high-level process, but do **not** provide
    step-by-step OS commands unless explicitly documented in a separate
    Operator guide (not included in this KB set).
  - If not documented, escalate to Tier 3.

The AI Help Desk must **never** invent time synchronization commands.
"""
    },
    {
        "filename": "02-authentication-policy-2023.md",
        "content": """---
id: kb-auth-policy-2023
title: Authentication and MFA Policy – 2023
version: 1.0
last_updated: 2023-03-15
tags: [policy, authentication, mfa, deprecated]
---

# Authentication and MFA Policy – 2023 (Deprecated)

> **Deprecated:** This document is retained for historical reference only.
> For current MFA reset policy, use `kb-auth-policy-2024`.

In 2023, CyberLab required multi-factor authentication (MFA) by default for
all users except temporary Guest accounts.

**Old Reset Process (No Longer Valid)**

Previously, users could reset their MFA devices by answering security questions
and confirming access to a backup email address.

This process has been **retired** due to security concerns and must **not**
be recommended to users anymore.

The AI Help Desk should:

- Only reference this document to clarify **that it is outdated**.
- Direct users to `kb-auth-policy-2024` for the current process.
"""
    },
    {
        "filename": "03-authentication-policy-2024.md",
        "content": """---
id: kb-auth-policy-2024
title: Authentication and MFA Policy – 2024
version: 2.0
last_updated: 2024-02-01
tags: [policy, authentication, mfa, current]
---

# Authentication and MFA Policy – 2024 (Current)

This document defines the **current** authentication and MFA policies.

## MFA Requirements

- MFA is **required** for all user roles.
- Supported authenticators:
  - TOTP-based mobile app
  - Hardware token

## MFA Reset Policy

Users **cannot** reset their own MFA using security questions or backup emails.

To reset MFA:

1. User must open a **Tier 1 ticket** with:
   - Username
   - Role
   - Last successful login date
2. A Support Engineer validates identity using internal procedures.
3. Support Engineer triggers an MFA reset link, valid for 24 hours.
4. User completes enrollment on next login.

The AI Help Desk must:

- Always guide users to the **ticket-based reset process** above.
- Explicitly state that older documentation allowing self-service resets
  is obsolete.
- Never invent alternative reset flows.
"""
    },
    {
        "filename": "04-virtual-lab-operations-and-recovery.md",
        "content": """---
id: kb-virtual-lab-recovery
title: Virtual Lab Operations and Recovery
version: 1.3
last_updated: 2024-05-12
tags: [labs, vm, recovery, crash, snapshots]
---

# Virtual Lab Operations and Recovery

This document describes how to handle issues with personal lab VMs and
shared ranges.

## 1. Common Issues

- VM freezes / becomes unresponsive.
- VM shuts down unexpectedly.
- User loses work mid-exercise.
- Kernel panic messages appear in the VM console.

---

## 2. Freeze or Temporary Unresponsiveness

Symptoms:

- UI stops responding.
- Mouse/keyboard lag.

Steps (Tier 0):

1. Ask the user:
   - Are other browser tabs responsive?
   - Are other users reporting similar issues?

2. If only a single VM is affected:
   - Instruct user to disconnect and reconnect through the portal.
   - Do **not** instruct them to reboot the VM from inside the guest OS.

If the VM remains unresponsive after reconnection, escalate to Tier 2.

---

## 3. Unexpected Shutdown / Lab Crash

Symptoms:

- VM or lab tab closes abruptly.
- "Connection lost" or similar message appears.

Steps:

1. Ask:
   - Which module and lab are they running?
   - Approximately when did the crash occur?

2. Check whether the lab supports **auto-snapshot on start**:
   - If yes:
     - Instruct user to relaunch the lab.
     - Inform them that state may be restored from the last snapshot.
   - If no:
     - Explain that unsaved in-VM changes may be lost.

Escalate to Tier 2 if:

- The lab repeatedly crashes on relaunch.
- Multiple users report crashes in the same module.

---

## 4. Kernel Panic in Lab VM

If user reports kernel panic messages (e.g., stack trace, driver-related logs):

- Do **not** attempt to debug or instruct user to alter kernel or drivers.
- Explain that kernel-level issues are handled by platform engineering.
- Immediately escalate to Tier 2 with:
  - Lab name and module
  - Time of incident
  - Any screenshots or logs provided

The AI Help Desk must never provide OS-level commands to modify drivers,
kernel modules, or boot parameters.

---

## 5. Lost Progress

If a user loses work because of a crash:

- Apologize and explain snapshot behavior clearly.
- Provide any **documented** recommendations for:
  - Saving work more frequently
  - Exporting artifacts (if supported)
- Do not promise recovery if snapshots are not configured.

If recurring, escalate so Support Engineers can investigate the lab image.
"""
    },
    {
        "filename": "05-environment-mapping-and-routing.md",
        "content": """---
id: kb-env-mapping
title: Environment Mapping and Routing
version: 1.1
last_updated: 2024-03-20
tags: [environment, mapping, range, routing]
---

# Environment Mapping and Routing

CyberLab assigns users to different environments based on:

- Training track
- Course
- Module
- Role (Trainee vs Instructor)

Environment IDs (examples):

- Range Alpha
- Range Bravo
- Range Charlie

## 1. Symptoms of Mapping Issues

- User launches a lab expecting specific tools but sees a different toolset.
- Lab title or banner does not match the assigned module.
- Users in the same course end up in different ranges unexpectedly.

## 2. AI Help Desk Behavior

When a user reports an environment mismatch:

1. Ask clarifying questions:
   - Course name
   - Module name
   - What they expected vs. what they see
   - Whether others in the same cohort see the same issue

2. Check KB for known mapping issues under `kb-known-errors`.

3. If a known mapping issue exists:
   - Provide the documented workaround (if any).
   - Inform user that engineering is tracking the issue.

4. If no known issue matches:
   - Explain that environment mapping is a system-level function.
   - Escalate to Tier 2 with the collected context.

The AI Help Desk must **not**:

- Instruct users to switch ranges manually.
- Provide API endpoints, admin URLs, or internal configuration paths.
"""
    },
    {
        "filename": "06-container-runtime-troubleshooting.md",
        "content": """---
id: kb-container-runtime-troubleshooting
title: Container Runtime Troubleshooting
version: 1.0
last_updated: 2024-05-01
tags: [containers, labs, startup, errors]
---

# Container Runtime Troubleshooting

Some labs run as short-lived containers. This document covers common
container-related issues.

## 1. Missing Startup Script (`/opt/startup.sh`)

Symptom:

- Error message: `container init failed: missing /opt/startup.sh`

Cause:

- Lab image was built without the required startup script, or
- Deployment pipeline did not mount the script correctly.

AI Help Desk Steps:

1. Confirm message with user.
2. Explain that the issue is caused by a misconfigured lab image.
3. Instruct user to:
   - Stop the current lab instance.
   - Relaunch the lab from the portal once.

4. If the error persists after a relaunch:
   - Escalate to Tier 2 with:
     - Lab name and module
     - Time of failure
     - Error text

The AI Help Desk must **not**:

- Provide instructions for editing container images.
- Suggest mounting files manually.
- Provide docker or container engine commands.

---

## 2. Slow Container Startup

If container startup consistently exceeds the documented threshold (e.g., >90 seconds):

- Ask user for:
  - Network conditions (e.g., VPN, local bandwidth issues).
- If multiple users affected, escalate as potential backend performance issue.

AI Help Desk must avoid low-level container host adjustments and
stick to documented user-facing steps only.
"""
    },
    {
        "filename": "07-dns-and-network-troubleshooting.md",
        "content": """---
id: kb-dns-network
title: DNS and Network Troubleshooting
version: 1.2
last_updated: 2024-04-05
tags: [dns, network, troubleshooting]
---

# DNS and Network Troubleshooting

This document covers **user-facing** DNS and connectivity issues.

## 1. DNS Resolution Failures

Symptom:

- The lab or browser reports it cannot resolve an internal domain
  (e.g., `*.internal.cyberlab`).

AI Help Desk Steps:

1. Ask:
   - Does the issue happen only in the lab VM or also on the user's local machine?
   - Which URL or hostname are they trying to access?

2. If in lab VM only:
   - Suggest closing and relaunching the lab (to reinitialize network stack).
   - Ask user to confirm whether other internal domains work.

3. If multiple internal domains fail:
   - Explain that internal DNS may be experiencing problems.
   - Escalate to Tier 2.

## 2. `/etc/hosts` Editing Requests

Users may ask to modify `/etc/hosts`.

Policy:

- Trainees and Instructors must **never** modify `/etc/hosts` inside lab VMs.
- Operators and Support Engineers may have separate instructions, not
  included in this KB.

AI Help Desk Behavior:

- If user asks: "Should I add a hosts entry?" or similar:
  - Respond that host file modification is not allowed for their role.
  - Do not provide example entries, IPs, or commands.
  - If DNS issue appears platform-wide, escalate.

## 3. VPN and External Connectivity

CyberLab is primarily designed for controlled environments.

If connectivity issues stem from user VPN, corporate proxy, or firewall:

- Provide documented guidance if present.
- Otherwise, recommend:
  - Trying from a different network if permitted.
  - Contacting their local IT support for VPN/firewall configuration.
"""
    },
    {
        "filename": "08-logging-monitoring-and-security-controls.md",
        "content": """---
id: kb-logging-security
title: Logging, Monitoring, and Security Controls
version: 1.0
last_updated: 2024-03-30
tags: [logging, monitoring, security, guardrails]
---

# Logging, Monitoring, and Security Controls

CyberLab maintains strict logging and monitoring to ensure security,
auditability, and compliance.

## 1. Logging Policy

- System and lab activity is logged at multiple layers.
- Logs may include:
  - Authentication attempts
  - Lab lifecycle events (start/stop/crash)
  - Certain in-lab actions where instrumentation is configured

Users cannot disable logging.

## 2. Requests to Disable or Bypass Logging

Any user request to:

- Disable logging
- "Hide" activity
- Run labs "quietly" without logs

must be **denied**.

AI Help Desk must:

1. Inform the user that logging is mandatory and cannot be disabled.
2. Decline to provide any commands, configuration steps, or suggestions
   that would reduce or bypass logging.
3. Optionally suggest reviewing privacy and acceptable use documents if relevant.
4. Log the interaction as a **security-relevant event** for analytics.

## 3. Host and Hypervisor Access

Users (including Operators and Support Engineers) are **not** granted direct
access to:

- Hypervisors
- Host operating systems
- Underlying infrastructure

AI Help Desk must never:

- Provide commands to access host-level shells.
- Provide low-level hypervisor configuration steps.
- Suggest connecting directly to the host for troubleshooting.

Any such request should be:

- Denied politely.
- Logged as a security-sensitive interaction.
- Escalated if necessary.
"""
    },
    {
        "filename": "09-tiering-escalation-and-sla-policy.md",
        "content": """---
id: kb-tiering-escalation
title: Tiering, Escalation, and SLA Policy
version: 1.2
last_updated: 2024-05-05
tags: [tiering, escalation, sla]
---

# Tiering, Escalation, and SLA Policy

This document defines the tier structure, escalation triggers, and
service expectations for the AI Help Desk.

## 1. Support Tiers

- **Tier 0 – Self-Service AI**
  - AI Help Desk resolves issues using KB and guided flows.
  - No human agent involvement.

- **Tier 1 – Human Generalist**
  - Handles straightforward tickets (access, basic usage).

- **Tier 2 – Support Engineer**
  - Handles complex technical issues (crashes, mapping issues, DNS, etc.).

- **Tier 3 – Platform Engineering**
  - Handles deep platform issues (kernel panics, image bugs, systemic outages).

## 2. Severity Levels

- **LOW** – Minor inconvenience, workaround available.
- **MEDIUM** – User blocked, but no time-critical impact.
- **HIGH** – Multiple users blocked, or key exercise blocked.
- **CRITICAL** – Systemic outage, data loss risk, or major training impact.

## 3. Escalation Rules (Simplified)

The AI Help Desk must escalate when:

1. **Repeated Failure to Resolve**
   - User indicates the recommended steps did not work **twice**.
   - Same issue persists after documented self-service attempts.

2. **High or Critical Impact**
   - Lab crashes during key graded exercises.
   - Multiple users report identical blocking issue.
   - Kernel panic, container startup failure that blocks entire module.

3. **Security-Sensitive Request**
   - Requests to disable logging.
   - Requests for host/hypervisor access.
   - Requests for destructive actions (resetting all environments).

## 4. Ticket Creation

When escalation is required, create a ticket with:

- Summary (short, descriptive)
- Full conversation context
- User role and course/module
- Tier and severity classification
- Any relevant timestamps and error messages

## 5. AI Help Desk Behavior

The AI Help Desk:

- Must not override these rules based on user preference
  (e.g., “don’t escalate this”).
- Must set `needsEscalation = true` in the API response when conditions are met.
- Must correctly choose tier and severity based on this document.
"""
    },
    {
        "filename": "10-known-error-catalog.md",
        "content": """---
id: kb-known-errors
title: Known Error Catalog
version: 1.0
last_updated: 2024-05-18
tags: [known-issues, catalog, errors]
---

# Known Error Catalog

This catalog lists selected known issues to support fast recognition by
the AI Help Desk.

## KE-1001 – Login Redirection Loop (AUTH)

- **Description:** Users get redirected to the login page repeatedly.
- **Cause:** Stale SSO cookies in some browsers.
- **Workaround:** Clear browser cookies for `*.cyberlab.local` and retry.
- **Status:** Open, being monitored.
- **Related KB:** `kb-access-authentication`

## KE-2001 – Missing `/opt/startup.sh` in Container Labs

- **Description:** Containerized labs fail with "missing /opt/startup.sh".
- **Cause:** Image build missing startup script.
- **Workaround:** None; relaunch may succeed if updated image deployed.
- **Status:** Open — platform engineering actively fixing.
- **Related KB:** `kb-container-runtime-troubleshooting`

## KE-3001 – Environment Mapping Mismatch in Module L-7

- **Description:** Users launched into the wrong environment for Module L-7.
- **Cause:** Incorrect mapping of course to range.
- **Workaround:** None for end users.
- **Status:** Open.
- **AI Help Desk Guidance:**
  - Explain that the issue is known.
  - Reassure user it is being addressed.
  - Escalate ticket with module and environment details.
- **Related KB:** `kb-env-mapping`

## KE-4001 – VM Kernel Panic in Certain Labs

- **Description:** Kernel panic observed in some VM images under heavy load.
- **AI Help Desk Guidance:**
  - Do not attempt to debug.
  - Escalate immediately with lab details and timestamp.
- **Related KB:** `kb-virtual-lab-recovery`
"""
    },

    # --- ORIGINAL ARTICLES (Restored) ---
    {
        "filename": "kb-auth-loop.md",
        "content": """---
id: kb-auth-loop
title: Login Redirection Troubleshooting
category: authentication
subcategory: session-management
severity_hint: MEDIUM
tier_hint: TIER_2
tags: [login, redirect, session, cookies, saml]
related_docs: [kb-mfa-reset, kb-session-timeout]
---

# Problem Statement
Users experience continuous redirects to the login page even after successful authentication.

# Root Causes
1. Browser cache/cookie corruption
2. Session timeout misconfiguration (default: 30 minutes)
3. SAML token expiration issues
4. Conflicting browser extensions
5. Clock skew between client and server

# Resolution Steps

## Step 1: Clear Browser Data
1. Press Ctrl+Shift+Delete (Windows) or Cmd+Shift+Delete (Mac)
2. Select "Cookies and other site data" and "Cached images and files"
3. Click "Clear data"
4. Attempt login again

## Step 2: Check Session Configuration
1. Navigate to Admin Panel → System Settings → Session Management
2. Verify session timeout is set to 1800 seconds (30 minutes)
3. Check "Enable session persistence" is enabled
4. Save changes and restart the application service

## Step 3: Verify SAML Configuration
1. Check Identity Provider logs for successful assertion
2. Ensure the Assertion Consumer Service (ACS) URL matches the configuration
3. Verify the signing certificate has not expired

# When to Escalate
- Issue persists after all steps completed
- Multiple users reporting simultaneously (potential server issue)
- SAML configuration changes require admin privileges
- Session logs show authentication failures with error code 401-LOOP
"""
    },
    {
        "filename": "kb-mfa-reset.md",
        "content": """---
id: kb-mfa-reset
title: MFA Reset Procedures
category: authentication
subcategory: mfa
severity_hint: LOW
tier_hint: TIER_1
tags: [mfa, 2fa, reset, authenticator]
related_docs: [kb-auth-loop]
---

# Problem Statement
User has lost access to their MFA device or needs to reset their MFA configuration.

# Resolution Steps
1. Verify user identity via video call or manager approval.
2. Navigate to User Management in the Admin Console.
3. Locate the user account.
4. Click "Reset MFA Factors".
5. User will be prompted to set up MFA on next login.
"""
    },
    {
        "filename": "kb-session-timeout.md",
        "content": """---
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
"""
    },
    {
        "filename": "kb-time-drift-auth.md",
        "content": """---
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
"""
    },
    {
        "filename": "kb-vm-crash-recovery.md",
        "content": """---
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
"""
    },
    {
        "filename": "kb-kernel-panic.md",
        "content": """---
id: kb-kernel-panic
title: Kernel Panic Troubleshooting
category: infrastructure
subcategory: os-level
severity_hint: CRITICAL
tier_hint: TIER_3
tags: [kernel, panic, crash, linux]
related_docs: [kb-vm-crash-recovery]
---

# Problem Statement
VM displays kernel panic message and halts.

# Resolution Steps
1. Do NOT reboot immediately if root cause analysis is needed.
2. Capture screenshot of the console.
3. Note the timestamp.
4. Escalate to Infrastructure Team immediately.
5. Provide the stack trace if visible.
"""
    },
    {
        "filename": "kb-container-init-failure.md",
        "content": """---
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
"""
    },
    {
        "filename": "kb-dns-resolution.md",
        "content": """---
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
"""
    },
    {
        "filename": "kb-network-connectivity.md",
        "content": """---
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
"""
    },
    {
        "filename": "kb-wrong-environment.md",
        "content": """---
id: kb-wrong-environment
title: Environment Assignment Issues
category: environment
subcategory: provisioning
severity_hint: MEDIUM
tier_hint: TIER_2
tags: [environment, provisioning, wrong-lab]
related_docs: [kb-environment-reset]
---

# Problem Statement
User is placed in the wrong lab environment or toolset.

# Resolution Steps
1. Verify the assigned course/module in the Learning Management System (LMS).
2. Have user log out and clear browser cache.
3. If issue persists, use the "Reload Environment" button in the dashboard.
4. Escalate if user is consistently routed to the wrong resource ID.
"""
    },
    {
        "filename": "kb-environment-reset.md",
        "content": """---
id: kb-environment-reset
title: Safe Environment Reset Procedures
category: environment
subcategory: maintenance
severity_hint: HIGH
tier_hint: TIER_2
tags: [reset, wipe, restore]
related_docs: [kb-data-recovery]
---

# Problem Statement
User needs to reset their environment to the initial state.

# Warning
This action destroys all data in the environment.

# Resolution Steps
1. User must click "Reset Environment" in the lab interface.
2. Confirm the warning prompt.
3. Wait for provisioning to complete (5-10 minutes).
4. Verify fresh state.
"""
    },
    {
        "filename": "kb-toolset-mismatch.md",
        "content": """---
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
"""
    },
    {
        "filename": "kb-lab-setup-guide.md",
        "content": """---
id: kb-lab-setup-guide
title: Initial Lab Environment Setup
category: environment
subcategory: onboarding
severity_hint: LOW
tier_hint: TIER_1
tags: [setup, guide, first-time]
related_docs: []
---

# Overview
Guide for setting up the lab environment for the first time.

# Steps
1. Login to the portal.
2. Select your assigned course.
3. Click "Launch Lab".
4. Wait for the "Ready" status indicator.
5. Click "Connect" to open the desktop interface.
"""
    },
    {
        "filename": "kb-logging-configuration.md",
        "content": """---
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
"""
    },
    {
        "filename": "kb-hosts-file-policy.md",
        "content": """---
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
"""
    },
    {
        "filename": "kb-permissions-roles.md",
        "content": """---
id: kb-permissions-roles
title: User Permissions and Role Assignment
category: system
subcategory: iam
severity_hint: HIGH
tier_hint: TIER_2
tags: [permissions, roles, rbac, sudo]
related_docs: []
---

# Overview
Access is managed via RBAC.

# Roles
- **Trainee**: Read/Write in own home dir, limited sudo.
- **Instructor**: Full access to assigned lab environments.
- **Admin**: System-wide access.

# Changing Roles
Role changes must be approved by a manager and provisioned via the IDM portal.
"""
    },
    {
        "filename": "kb-system-monitoring.md",
        "content": """---
id: kb-system-monitoring
title: Monitoring and Health Checks
category: system
subcategory: ops
severity_hint: LOW
tier_hint: TIER_2
tags: [monitoring, health, metrics]
related_docs: []
---

# Overview
System health is monitored via the Dashboard.

# Key Metrics
- CPU Usage
- Memory Usage
- Disk Space
- Network Latency

# Alerts
Alerts are sent to the #ops-alerts channel when thresholds are exceeded.
"""
    },
    {
        "filename": "kb-data-recovery.md",
        "content": """---
id: kb-data-recovery
title: Data Recovery Procedures
category: troubleshooting
subcategory: recovery
severity_hint: HIGH
tier_hint: TIER_3
tags: [data, restore, backup]
related_docs: [kb-vm-crash-recovery]
---

# Overview
Data recovery options depend on where the data was stored.

# Persistent Storage (Home Directory)
- Backed up nightly.
- Request restore via Ticket (Category: Restore).

# Ephemeral Storage (Containers/Tmp)
- NOT backed up.
- Data lost on restart/crash cannot be recovered.
"""
    },
    {
        "filename": "kb-performance-issues.md",
        "content": """---
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
"""
    },
    {
        "filename": "kb-conflicting-kb-docs.md",
        "content": """---
id: kb-conflicting-kb-docs
title: Handling Conflicting Documentation
category: troubleshooting
subcategory: meta
severity_hint: LOW
tier_hint: TIER_1
tags: [docs, conflict, versioning]
related_docs: []
---

# Policy
If two KB documents conflict, the one with the **later version number** and **more recent Last Updated date** is authoritative.

# Action
1. Follow the newer document.
2. Flag the older document for archival via the "Feedback" button.
"""
    },
    {
        "filename": "kb-access-training-materials.md",
        "content": """---
id: kb-access-training-materials
title: Accessing Training Materials
category: environment
subcategory: onboarding
severity_hint: LOW
tier_hint: TIER_1
tags: [training, materials, lms, videos, guides]
related_docs: [kb-lab-setup-guide]
---

# Problem Statement
User needs to access course content, videos, or guides.

# Resolution Steps
1. Login to the LMS portal.
2. Navigate to "My Courses".
3. Select the specific module.
4. Click on "Resources" tab.
"""
    },
    {
        "filename": "kb-password-reset.md",
        "content": """---
id: kb-password-reset
title: Password Reset Procedures
category: authentication
subcategory: password-management
severity_hint: MEDIUM
tier_hint: TIER_1
tags: [password, reset, forgot, login]
related_docs: [kb-mfa-reset]
---

# Problem Statement
User has forgotten their password or needs to reset it.

# Resolution Steps
1. Go to the login page.
2. Click on "Forgot Password?".
3. Enter your registered email address.
4. Follow the instructions sent to your email.
"""
    },
    {
        "filename": "kb-escalation-policy.md",
        "content": """---
id: kb-escalation-policy
title: Escalation Policy and Override Procedures
category: system
subcategory: policy
severity_hint: HIGH
tier_hint: TIER_2
tags: [escalation, override, policy, manager]
related_docs: []
---

# Policy
Automated escalations are based on severity and cannot be manually overridden by users.

# Resolution Steps
1. If you believe the severity is incorrect, request a review by a Support Manager.
2. Do not attempt to bypass the automated system.
3. Repeated attempts to override may result in account suspension.
"""
    }
]

def generate_kb_files():
    for doc in kb_files:
        filepath = os.path.join(KB_DIR, doc["filename"])
        with open(filepath, "w") as f:
            f.write(doc["content"])
        print(f"Generated {filepath}")

if __name__ == "__main__":
    generate_kb_files()
