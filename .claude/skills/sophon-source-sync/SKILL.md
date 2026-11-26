---
name: sophon-source-sync
description: Use when previewing, uploading or verifying local Sophon source files against the configured remote source directory.
---

# Sophon Source Sync

Follow the canonical workflow and `sophon-server-session`. Use `.claude/tools/sophon-source-sync.py --help`; `/sync` routes here through the server operator. Store config and manifests outside the repository.

1. `preview` selects tracked files plus explicitly included new files, applies exclusions, records local hashes/modes and remote identities, and reports additions/unchanged/replacements/conflicts. No remote writes.
2. Review the concrete selected changes under the existing task authorization. A known replacement must be explicitly selected with `--replace` in preview. Unexpected remote conflicts require reconciliation, not --force.
3. `upload` consumes that manifest, rechecks source and remote identity, transfers selected files and verifies them. `verify` checks the manifest against the remote tree.

Always exclude repository-root `.claude/`, `.worktree-policy.yaml`, `AGENTS.md`, and `CLAUDE.md`, including explicit selections. The helper also filters private/local/generated/model content and preserves required checked-in fixtures. Never bypass it using a whole-directory scp/rsync/archive or delete remote files to mirror a checkout.

Use the dedicated Sophon target, separate from Mario. Source upload does not install dependencies, fetch models, run inference or start/restart services. Report partial transfer/failure and any retained recovery staging honestly. No live upload is needed to test the helper.
