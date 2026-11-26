---
name: sophon-server-session
description: Use when a task needs SSH access, selected remote validation or operations, or a configured remote source/reference read.
---

# Sophon Server Session

Read `.claude/workflows/sophon-workflow.md`. Resolve `SOPHON_SESSION_CONFIG` or an explicit config path to user-local JSON outside the checkout; `.claude/config/server-session.example.json` documents its fields. Do not embed actual connection values in repository files or print credentials. Reuse supplied settings rather than asking again.

Check configured alias resolution against expected host/user/port before connection. Use noninteractive SSH, strict host-key checking, disabled agent/X11 forwarding and multiplexing, and bounded connection/command timeouts. Do not bypass authentication or host-key failures or switch targets silently.

Read-only planning access is limited to the task's selected source/reference roots and source/config/test evidence; reject linked-path escapes. An unrelated service/log/GPU inspection is not source discovery. Remote mutation requires current task/approved-phase scope and exact resources.

For source transfer use `sophon-source-sync`. For later authorized Linux validation, select the existing profile's interpreter and scripts, check actual effects, bound workload/output and clean up owned processes only. Upload, install, download, activation and model requests remain distinct. Missing Python/GPU/environment is reported with the smallest next action; it never authorizes installation implicitly.
