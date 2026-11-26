---
name: sophon-verification-loop
description: Use when choosing, executing or reviewing validation evidence for a scoped Sophon change.
---

# Sophon Verification Loop

Read the canonical `.claude/workflows/sophon-workflow.md`. Choose the smallest check that proves the requested behavior in the selected profile. For routine changes perform an appropriate minimal check; for planned changes follow approved acceptance. Do not add another approval gate or blanket coverage threshold.

Keep source, syntax/unit, environment and runtime evidence distinct. Record command, exit status, relevant result and any unrun required check. Avoid service/model startup from imports or arbitrary --help calls. On a failure, investigate the concrete cause, correct within the current phase and rerun the affected check. Never weaken assertions. Read-only reviewers return findings to the owner rather than running tests or editing.

Example: a syntax check passes but a required Linux/GPU smoke is unavailable: report syntax PASS, runtime unrun and acceptance pending. Required gaps prevent DONE; optional limits are disclosed. Only canonical material boundaries require BLOCKED, not a fixed retry count.
