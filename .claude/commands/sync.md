---
description: Preview, upload or verify selected Sophon source with mandatory local-workflow exclusions
argument-hint: "[preview|upload|verify] [selection or manifest context]"
disable-model-invocation: true
---

Run in the primary planner context. Route through `.claude/workflows/sophon-workflow.md`, `sophon-server-operator`,
and the `sophon-source-sync` skill. Use the configured dedicated source target.
An unspecified action starts with a non-mutating preview. An explicit upload
request authorizes ordinary transfer of the reviewed in-scope manifest; do not
invent another routine approval when current task/plan authorization covers it.

Optional user instructions:

$ARGUMENTS

Always exclude repository-root `.claude/`, `.worktree-policy.yaml`, `AGENTS.md`
and `CLAUDE.md`, even when explicitly selected. Use the source-sync helper for
preview, transfer and verification; never whole-tree copy or mirror/delete.
Reconcile unexpected remote differences. Upload does not install dependencies,
download models, start/restart services or modify Mario. This command does not
approve a newly generated consequential plan or execute embedded shell.
