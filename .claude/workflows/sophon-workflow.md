---
name: sophon-workflow
description: Python development workflow for Sophon agents, validation, source synchronization and scoped remote work.
---

# Sophon development workflow

This is the canonical Claude workflow. Follow root `AGENTS.md`, explicit user scope, and applicable directory instructions. `CLAUDE.md`, agents, rules and skills reference this workflow; none adds a parallel approval lifecycle. Mario's runtime design is investigated only when a future development task needs it.

## Ownership and routing

| Task | Owner |
| --- | --- |
| Scope, decisions, records, acceptance | `sophon-plan` |
| Scoped architecture or compatibility question | `sophon-architecture-calibrator` (read-only) |
| Product Python, configuration and relevant tests | `sophon-python-dev` |
| Scoped semantic/async/configuration review | `sophon-code-review` (read-only) |
| SSH, source sync, authorized remote validation/operation | `sophon-server-operator` |
| Python diagnostics, reporting and automation | `sophon-python-tooling` |
| Bash and shell helpers | `sophon-shell-tooling` |
| Requested Git/worktree lifecycle | `worktree-manager` |

Owners are routes, not a mandatory chain. Execute directly when the current owner can finish the task. One writer per file scope; children do not delegate. Read-only roles may read/search/diff but do not edit, run tests, install packages or operate services. Read-only findings return to the planner; they do not approve work or change the plan state.

## Select the route

Small, understood, reversible changes use `inspect -> edit -> smallest relevant check -> report`. No saved plan or extra approval is required. Verify according to `AGENTS.md`: focused test, syntax check, or another minimal check that proves the changed behavior. Documentation corrections need only applicable content/reference checks. Do not require a blanket coverage percentage, full suite, remote run or delegated review for every change.

Consequential, cross-module or uncertain work, and an explicit request for a plan, use the planned route. Read relevant code, callers, configuration, types and tests before deciding. Use existing patterns; scope architectural analysis to the decision. Design depth: A = same contract/owner/lifetime; B = internal state/ownership/contract change; C = subsystem or public protocol change. Put B/C decisions, alternatives and acceptance in the same plan. Consult brainstorming or `grill-me` for unresolved material choices, not for facts inspectable in the repository.

## Planned records and authorization

Only `sophon-plan` writes `doc/plan/<id>.md`, `doc/check/<id>-CHECK.md` and `doc/check/CURRENT.md`. Resolve all paths inside the workspace; reject traversal and linked-path escape. The plan owns ID/version, scope/non-goals, design decisions, interfaces, profiles, resources, acceptance, phase owners and boundaries. The check owns approval evidence, overall state, phase/step, outcomes, actual commands/exit status, corrections, blocker evidence and next action. CURRENT is only a pointer. Do not create duplicate ledgers or treat an agent-written status as consent.

Planning permits bounded local reads and task-relevant read-only remote source/reference discovery through `sophon-server-session`, when required and within a user-selected root. It does not authorize edits, installs, tests, inference, service operations or uploads. Present the plan and wait for explicit approval of that version. Record the approval before implementation. Approval covers its unchanged phases and targeted corrections; no routine phase-by-phase confirmation.

| State | Entry and next action |
| --- | --- |
| `AWAITING_USER_CONFIRMATION` | Plan/version presented; wait for user review/approval. |
| `APPROVED` | Record actual approval and scope; start the approved phase. |
| `IN_PROGRESS` | Execute current phase, correct within scope, validate and advance. |
| `BLOCKED` | Confirm one material category below; record proof and await user direction. |
| `PAUSED` | User explicitly pauses; retain phase/step. |
| `DONE` | Required deliverables/checks and scoped cleanup complete; report limits. |
| `CANCELLED` | User cancels; stop and preserve records/work. |

Resume an unchanged blocked/paused plan only following user direction. Changed scope/acceptance requires a revised version and confirmation. Reconcile stale/missing records before resuming; never infer approval or replace another active plan silently. An unavailable required check remains pending and prevents DONE; an optional unrun check is disclosed, never reported as passed.

Direct work that becomes consequential stops further edits without reverting. Capture and attribute staged/unstaged/untracked changes, distinguish pre-existing or uncertain ownership, and include retention/correction of the partial work in the new plan. A captured baseline is not approval. Do not stash/reset/clean/stage merely to tidy it.

## Corrections and material boundaries

An ordinary failure remains IN_PROGRESS when correction stays within the current approved phase, files/resources, scope/acceptance and safety boundary, requires no new high-risk operation, and is targeted. Continue reasoned correction and affected checks without fixed retry counts. Keep technical timeouts/workload bounds. Never weaken assertions or acceptance to get a pass.

Only these material categories require BLOCKED and a user decision:
1. Scope or acceptance must change.
2. A safety boundary changes.
3. An unapproved file/resource must be modified.
4. A new high-risk operation is required.
5. A foundational architecture/infrastructure assumption is disproved.
6. Continuing could damage data or the environment.
7. The approved approach cannot reasonably meet acceptance within the correction boundaries.

A failure count, missing optional tool, review severity or child's early return is not alone a material category. Record category, direct evidence, consequence, smallest correction, owner and next action; stop affected pending work safely. Necessary cleanup of owned processes or already-running safety recovery may finish without starting another phase.

## Python profiles and evidence

Select the affected profile in `.claude/workflows/sophon-serving-profiles.md`; do not install all variants together or invent one universal Python environment. Windows is a control/development environment; Linux/GPU evidence comes from the selected remote environment. Read actual checked-in install/constraint files before selecting interpreter or dependency versions.

Distinguish source, environment, configuration on disk, and loaded runtime. Use `CODE-CONFIRMED`, `CHECK-CONFIRMED`, `ENV-CONFIRMED`, `RUNTIME-CONFIRMED`, `PARTIAL`, or `HYPOTHESIS` for material conclusions. Syntax/unit tests do not prove model quality, deployment activation, latency or full-duplex behavior. State exactly which profile/environment was exercised.

Use the smallest check matching acceptance. Python syntax checks must not import model modules or start services. Run focused offline tests before relevant integration checks; widen only for changed risk/acceptance. Record command, exit status and outcome. For planned validation retain one bounded authoritative log when useful for acceptance/failure diagnosis; report a short excerpt and its path rather than duplicating full output. Successful equivalent checks do not need repeating.

## Remote operation and source sync

Read `sophon-server-session` for remote work and `sophon-source-sync` for transfer. Connection settings are user-local JSON outside the checkout. Use the configured SSH alias, verified destination identity, dedicated source root and Mario reference root. Never fall back to another host/project on failure. Keep host-key checking, noninteractive authentication, no forwarding/multiplexing, explicit target and bounded commands.

The local checkout is the source for requested uploads. Preview, upload, verify, environment install, model download, service start/restart, inference and benchmarking are distinct actions. Perform only actions in the current request/approved phase; upload does not activate code. Remote source edits must be reconciled before replacement. Never mirror/delete the remote parent tree or operate on Mario as part of Sophon source sync.

Source sync always excludes repository-root `.claude/`, `.worktree-policy.yaml`, `AGENTS.md` and `CLAUDE.md`, even if explicitly selected. The helper applies the same filter to preview, payload and verification; preserve unrelated/excluded remote files. Git metadata, local planning records, secrets, environments, model weights, caches and generated outputs are not source-transfer payloads. Keep needed checked-in fixtures.

## Handoffs, data and completion

A direct handoff specifies bounded task, owner, files, profile, expected behavior and minimal check. A planned handoff adds plan ID/version, actual approval evidence, phase, resources, acceptance, correction boundaries and material stops. Include source/remote identities only when relevant and keep private connection values outside committed records. Use source paths/hashes rather than copying entire reference projects. Never equate developer skills with application/runtime skills.

Audio, transcripts, histories and logs are not automatically synthetic. Keep credentials and private data out of committed files and ordinary reports. Use authorized fixtures and bounded redacted evidence. Prefer existing logging and configuration mechanisms; avoid unrelated frameworks or product refactors.

Follow `.worktree-policy.yaml` for explicit Git/worktree operations. Do not turn Git readiness into a prerequisite for ordinary content edits. Preserve dirty/untracked work; no implicit commit, push, merge, stash or cleanup. Destructive Git, broad deletion, system-package/account/firewall/SSH/permission changes and unrelated process/container destruction require explicit authorization for the exact effects. Existing authorization remains valid for unchanged scope; never bypass platform permission rejection.

Temporary cleanup is limited to paths created and owned by the task. Verify resolved absolute paths and content identity before deleting exact files/empty task directories. Keep recovery artifacts until their approved retention condition is met. Report changed behavior/files, actual verification, remaining limits and cleanup outcomes. DONE requires required acceptance, not just a successful edit or source upload.
