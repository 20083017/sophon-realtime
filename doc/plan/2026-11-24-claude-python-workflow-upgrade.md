# Claude Python Workflow Upgrade Implementation Plan

> For agentic workers: execute this approved plan task by task using `superpowers:executing-plans`. Checkbox steps track completion. Use the repository's canonical workflow and one planning record; do not start another approval lifecycle.

**Plan ID:** `2026-11-24-claude-python-workflow-upgrade`  
**Version:** `v2`  
**Status:** `DONE`  
**Goal:** Upgrade the existing Claude development harness from WTP184 C++ workflows to Python workflows for Sophon, including safe local-to-remote source synchronization.  
**Architecture:** Retain the current planner, bounded specialist roles, approval states, and plan/check/current records. Replace project-specific assumptions with shared Python rules, explicit serving profiles, and environment-configured remote operations.  
**Tech stack:** Claude Markdown agents/rules/skills, JSON settings, YAML worktree policy, Python standard-library tooling, existing Bash launch scripts, OpenSSH.  
**Spec:** The accepted scope and design decisions below, incorporating the user's decisions and source-sync exclusions.  
**Execution:** Primary executor implements the upgrade; delegation is optional when explicitly authorized or required by an applicable skill. Specialist role definitions do not require spawning every role for every task.

## Accepted scope and boundaries

- Target Claude only. Keep `AGENTS.md` as the existing repository constraints; do not add a Codex harness.
- Upgrade development agents, workflow transitions, rules, skills, commands, associated helpers, and repository-specific worktree policy.
- Use shared Python rules with separate Tag, Flash, E2E plugin, and native-engine serving profiles. Live is an additional gateway scope when a task touches it.
- Mario is a reference repository for future development tasks. This upgrade defines how to locate and read it on demand; it does not inspect, translate, redesign, or migrate Mario's runtime state, protocols, skills, or integration behavior.
- Product Python modules, model configurations, serving scripts, dependency versions, and product behavior are outside this upgrade's edit scope.
- Actual source upload, environment installation, model downloads, service operations, inference, and product/GPU validation are outside this upgrade's execution scope. The sync implementation is verified locally with fixtures and mocked transport.
- User-provided host, account, remote parent, and Mario reference values belong in user-local configuration outside the repository. Tracked examples contain empty fields and explain how to configure them.
- The proposed remote Sophon destination is a dedicated `sophon-realtime` child of the supplied remote parent. Mario remains outside the sync target. Exact remote values are validated when a later task requests remote work.
- The mandatory upload exclusions are repository-root `.claude/`, `.worktree-policy.yaml`, `AGENTS.md`, and `CLAUDE.md`. The same filter applies to previews, manifests, transfer payloads, and post-transfer verification.
- Preserve the currently untracked harness files and unrelated user changes. No automatic commit, merge, push, stash, reset, or broad cleanup is included.
- Keep the migration backup through implementation and verification, then remove it after successful delivery as requested by the user. This covers only backup copies created and recorded by this upgrade; no additional routine confirmation is required for that cleanup.

## Global constraints

- Make the smallest complete harness change and reuse existing generic skills and shell patterns.
- Add no package dependency solely for the workflow upgrade. Prefer standard-library Python for sync tooling and its tests.
- Preserve authentication, authorization, host-key verification, secret handling, timeout limits, and scoped process ownership.
- Resolve contradictory copied instructions in favor of the root `AGENTS.md` and current user decisions. Small changes use proportionate validation rather than the legacy blanket exemption from all checks.
- Only the planner updates active plan/check/current records. Review and architecture roles return evidence without editing product files or granting approval.
- Keep workflow status, execution phase, and validation evidence distinct. Never infer runtime success from syntax checks or source upload.
- Keep private endpoints and machine paths out of checked-in examples and planning records.

## Design decisions

### Approach

Use an in-place, project-specific migration of the existing Claude harness. A new general-purpose, multi-language harness would add an unnecessary abstraction layer. Keep the generic planning and ownership model, replace the obsolete WTP184-specific content, and preserve a recoverable baseline outside active discovery paths.

Architecture impact is B: this changes the development workflow's project contracts and remote tooling, without changing product architecture. The source of truth is `.claude/workflows/sophon-workflow.md`; agents and skills reference it rather than repeating approval rules.

### Agent ownership

| Current role | Proposed role | Scope |
| --- | --- | --- |
| `wtp184-plan` | `sophon-plan` | Routing, scope, acceptance, approval evidence, plan/check/current records |
| `wtp184-architecture-calibrator` | `sophon-architecture-calibrator` | Read-only answers to a scoped architecture question during development |
| `wtp184-dialogue-dev` | `sophon-python-dev` | Python product implementation and focused tests |
| `wtp184-code-review` | `sophon-code-review` | Scoped Python correctness, compatibility, async behavior, and evidence review |
| `wtp184-server-operator` | `sophon-server-operator` | Authorized SSH, source synchronization, remote validation and operations |
| `wtp184-python-tooling` | `sophon-python-tooling` | Diagnostic, reporting, and automation scripts |
| `wtp184-shell-tooling` | `sophon-shell-tooling` | Shell helpers and existing Linux script maintenance |
| `worktree-manager` | Keep name | Git/worktree policy for this repository |

One implementation owner per file scope. Do not turn these roles into a mandatory agent chain. Python product development and diagnostic tooling remain distinct responsibilities.

### Workflow states and handoffs

Retain `AWAITING_USER_CONFIRMATION -> APPROVED -> IN_PROGRESS -> DONE`.

| Event | Required behavior |
| --- | --- |
| Explicit approval of the displayed plan/version | Record approval, then enter the approved phase |
| Ordinary in-scope failure | Remain `IN_PROGRESS`; correct and rerun the affected check |
| Confirmed material scope/safety/feasibility boundary | Record evidence and enter `BLOCKED` |
| Explicit user pause | Enter `PAUSED`, retaining phase and step |
| User resumes unchanged scope | Continue recorded phase with valid evidence preserved |
| Scope or acceptance changes | Revise version and return to confirmation |
| User cancels | Enter `CANCELLED`; preserve work and records |
| Required deliverables and checks complete | Enter `DONE`; disclose any limitations |

Keep the existing seven material blocker categories and bounded correction policy. An unavailable optional check is reported as unverified; an unmet required check prevents completion. A failure count or review severity alone is not a state transition.

Routine tasks use `inspect -> edit -> relevant minimal check -> report`. Planned tasks use `inspect -> plan/review -> implement -> local validation -> review`, adding source sync and remote validation only when the approved task requires them. Upload, install, download, start/restart, inference, and benchmarking are separate actions.

Handoffs contain task/plan ID and version where applicable, authorized scope, owner, current phase, selected profile, file boundaries, expected behavior, relevant environment, acceptance checks, source snapshot, and actual evidence. Planned handoffs also include recorded approval and material stop conditions. Direct tasks do not fabricate approval records.

### Python rules and serving profiles

Create one `python-development` skill and shared Python product rules covering existing style, explicit error handling, resource lifetime, safe subprocesses, asynchronous task ownership, cancellation, bounded work, and focused tests. Apply concurrency checks only to the changed path. Do not prescribe a new product state machine or architecture.

Keep useful `python-tooling`, `shell-scripting`, `handoff`, `docs-review`, and `grill-me` content. Adapt only conflicting project references or validation wording in reused generic rules/skills. Retire active C++/Bazel and old WTP184 deployment, core-debug, Redis, and log-retrieval instructions whose contracts do not apply here.

Store profile guidance in `.claude/workflows/sophon-serving-profiles.md`:

| Profile | Source of existing environment/commands | Guidance |
| --- | --- | --- |
| Tag | `tag/install.sh`, `tag/start.sh`, `tag/plugin/pyproject.toml` | Separate plugin environment; use its declared interpreter and dependencies |
| Flash | `flash/install.sh`, `flash/start.sh`, `flash/plugin/pyproject.toml` | Separate plugin environment; nearest tests include `flash/tests/` |
| E2E plugin | `e2e/install.sh`, `e2e/start.sh`, `e2e/plugin/pyproject.toml` | Separate plugin environment and E2E dependencies |
| Native engine | `scripts/install.sh`, `scripts/start.sh`, requirement/constraint files | Preserve separate thinker and engine environments |
| Live gateway | `live/start_live.sh`, `live/README.md`, `live/live_test.py` | Additional gateway checks only when relevant; distinguish live-service tests from offline tests |

Profiles describe what to inspect and which commands apply; they do not install environments, select a default GPU, unify dependency versions, or claim all variants are tested. Do not introduce Ruff, mypy, pytest, or other tooling unless a later task independently justifies it.

### Remote and source sync contract

Create `.claude/tools/sophon-source-sync.py` with `preview`, `upload`, and `verify` subcommands. Commands receive `--config` pointing to user-local JSON outside the checkout. The configuration uses `ssh_alias`, `remote_source_root`, and `mario_reference_root`; examples leave values empty. Verify the resolved SSH destination and remote path against the configured scope when connecting. Keep strict host-key checking, noninteractive authentication, no agent forwarding, and bounded connect/command timeouts.

The sync helper uses Python's standard library and installed OpenSSH tools, with argument-list local subprocess calls. Remote command arguments must be safely quoted; never concatenate unchecked shell fragments. A preview is non-mutating. Upload is a separate explicit action; it never installs packages, launches services, or invokes the old binary pipeline.

Source selection starts from tracked files plus explicitly selected untracked additions. Record a manifest of normalized relative path, size, SHA-256, and required file-mode information. Apply mandatory exclusions after selection so explicit input cannot override them. Also exclude Git metadata, local plan/check records, environments, caches, generated logs, and model/checkpoint artifacts. Classify ambiguous large or generated additions before inclusion; do not use a blanket audio-file exclusion that removes required checked-in fixtures.

Reject traversal, symlink/junction escapes, and targets outside the dedicated Sophon destination. A preview identifies additions, replacements, and remote divergence. Before replacement, confirm that the source still matches the manifest and the remote file still matches its previewed identity. An unexpected existing-file conflict must not be silently overwritten. Transfer only selected files through bounded task-owned staging, verify hashes and relevant modes, and report partial failures accurately. Never apply a directory-wide delete/mirror operation; excluded paths and unrelated remote files remain untouched. Preserve recovery copies for replaced files within the task's bounded staging until verification succeeds.

The `mario-reference` skill documents scoped read-only reference access through the configured location, when requested by a future development task. No Mario source copy, runtime analysis, or migration task is part of this plan.

## Review focus

1. Explicitly selected excluded files, Windows path case/separators, and an excluded directory's descendants never enter the transfer manifest.
2. Source changes after preview, remote conflicts, hash mismatch, interrupted transfer, or failed SSH return failure without claiming successful synchronization.
3. Traversal and linked-path escapes cannot reach Mario or other remote/local resources outside the selected source/destination.
4. Reused generic rules, nested C++ rules, agent skill lists, command front matter, and permissions cannot retain conflicting active WTP184 behavior.
5. Missing GPU/environment, CLI availability, or required validation evidence never becomes a fabricated PASS or DONE.

## Implementation phases

### Phase 1: Preserve the harness and establish repository policy

**Owner:** primary executor, with worktree-manager guidance.  
**Files:** `.worktree-policy.yaml`, `.claude/agents/worktree-manager.md`; user-local baseline archive outside the checkout.  
**Consumes:** existing untracked harness and current `main` revision.  
**Produces:** recoverable baseline, working branch, coherent main-based local policy.

- [x] Preserve an exact baseline of `.claude/`, `.worktree-policy.yaml`, `AGENTS.md`, and `CLAUDE.md` outside the checkout; record archive location and checksum in the check record without credentials. Record every migration-created backup path for exact cleanup after delivery.
- [x] Create `refactor/python-workflow-upgrade` from current `main` in the same checkout, preserving untracked content. Approval of this plan authorizes that one-time base selection over the copied policy's obsolete master/develop requirements; it does not permit direct commits to protected branches.
- [x] Update branch/base/delivery and cleanup-target references consistently for this repository. Protect `main`; preserve destructive-operation and payload-preservation restrictions. Do not create master/develop solely to satisfy old assumptions.
- [x] Verify current branch, preserved content, and the policy's internally consistent branch references. Do not commit or merge.

### Phase 2: Migrate the canonical workflow and agents

**Owner:** primary executor.  
**Files:** `CLAUDE.md`, `.claude/README.md`, `.claude/settings.json`, `.claude/workflows/wtp184-workflow.md` -> `sophon-workflow.md`, `.claude/workflows/sophon-serving-profiles.md`, `.claude/agents/wtp184-*.md` -> the mapped `sophon-*.md` roles.  
**Consumes:** accepted states, roles, boundaries, and serving profiles.  
**Produces:** one active Python workflow and resolvable role references.

- [x] Replace WTP184 identity, C++ pipeline, compiler/build defaults, synthetic-data assumptions, and old remote-source authority with the accepted Python scope and environment-based contract.
- [x] Preserve workflow states, plan/check/current paths, single-writer ownership, correction rules, and evidence distinctions. Resolve the small-change validation conflict with `AGENTS.md`.
- [x] Apply the role mapping and profile guidance; update the default agent, command/agent references, and attached skills. Keep existing compatible model preferences rather than changing model policy opportunistically.
- [x] Update relevant settings references without weakening permission protections or adding blanket command permissions. Hook changes are limited to the existing format helper's obsolete C++ behavior; do not introduce a new mandatory hook chain.
- [x] Check JSON parsing, Markdown/front-matter structure, referenced paths, agent names, and state/approval wording. Retired files must not remain active through nested discovery or indirect references.

### Phase 3: Migrate rules and reusable skills

**Owner:** primary executor.  
**Files:** `.claude/rules/code-style.md`, `configuration-modification.md`, `observability.md`, new `python-development.md`; applicable reused generic rules/skills; new skills `python-development`, `sophon-verification-loop`, `sophon-server-session`, `sophon-source-sync`, and `mario-reference`; `.claude/hooks/check-format.sh`.  
**Consumes:** canonical workflow from Phase 2.  
**Produces:** focused Python guidance and no conflicting active C++ workflow.

- [x] Implement shared rules and skills by referencing the canonical workflow rather than duplicating its state machine.
- [x] Adapt configuration and observability rules to Python/profile contracts; remove copied C++ loader examples and assumptions that all audio/history/logs are synthetic.
- [x] Retain useful generic tooling, documentation, handoff, and interview skills. Reconcile only directly conflicting ECC/TDD/generic instructions.
- [x] Retire `cpp-observability.md`, `ecc/cpp/`, `cpp-coding-standards`, and old WTP184-specific skills/tools after baseline preservation. Keep retired content in the temporary migration backup outside active discovery until delivery; do not leave a second discoverable legacy harness. Keep unrelated personal skills unchanged.
- [x] Make the format helper applicable to configured Python/shell checks, reporting unavailable tooling honestly. Do not install a new formatter or reformat product code.
- [x] Verify active references and audit representative Python edit, review, remote-operation, and Mario-reference routing against the documented scope.

### Phase 4: Implement and test source synchronization

**Owner:** primary executor acting in the Python-tooling/server roles.  
**Files:** `.claude/tools/sophon-source-sync.py`, `.claude/tools/tests/test_source_sync.py`, `.claude/config/server-session.example.json`, `.claude/commands/sync.md`, corresponding skills from Phase 3. Retire the obsolete mower `test-hosts.env.example` after preservation.  
**Consumes:** source-sync contract and mandatory exclusions.  
**Produces:** preview/upload/verify CLI with one manifest/filter implementation and offline validation evidence.

- [x] Add failing standard-library `unittest` cases for mandatory exclusions, `.claude` descendants, explicit-inclusion bypass, path normalization, linked/traversal escapes, and preservation of required runtime fixtures.
- [x] Add mocked transport cases for source/remote drift, existing-file conflict, interrupted copy, verification mismatch, SSH failure, executable-mode preservation, and absence of implicit install/start/delete operations.
- [x] Implement the minimal CLI and transfer logic that satisfies those cases. Preview and upload must use the same normalized manifest and filter functions.
- [x] Update `/sync` to route source synchronization through `sophon-plan` and the server operator; remove WTP184 LATEST/binary-pipeline semantics. Requests inherit existing authorization and do not create repeated routine approval prompts.
- [x] Run `python -m unittest discover -s .claude/tools/tests -p "test_source_sync.py" -v`, syntax validation of changed Python helpers, and `python .claude/tools/sophon-source-sync.py --help`. Test local preview fixtures. Do not upload to the server during this upgrade.

### Phase 5: Review the integrated harness and deliver

**Owner:** primary executor; read-only review if authorized/required.  
**Files:** changed harness, planning records, and the recorded migration-created backup paths only.  
**Consumes:** completed phase evidence.  
**Produces:** reviewable upgrade, exact change list, validation results, remaining limits, and usage instructions.

- [x] Check all active references, settings syntax, worktree policy, applicable shell syntax, and stale WTP184/C++ directives. Legacy mentions are allowed only in explicit migration/history context, never active defaults.
- [x] Evaluate representative task scenarios: small Python edit; consequential planned task; ordinary failure; material blocker; pause/resume; each profile selection; sync exclusions; Mario reference request; missing environment. Keep simulated actions local and prevent live server/model invocation.
- [x] If a suitable Claude session is available, validate discovery and routing in a bounded local session using fixture tasks. Otherwise report live Claude behavior as unverified; do not treat static document checks as behavioral proof.
- [x] Run `git diff --check` and inspect tracked plus untracked harness changes against the preserved baseline, because the imported harness began untracked. Verify product files and `AGENTS.md` are unchanged.
- [x] Update usage documentation and the check record with actual commands/results and any unavailable verification. Make the completed changes and validation report available for review without automatic commit/push/upload.
- [x] After required verification passes and the completed upgrade is delivered, remove only the recorded migration-created backup archive/copies. Resolve and verify their absolute paths and task ownership immediately before deletion; do not delete a shared backup directory, unrelated backups, or files whose identity has changed. Verify removal and record the result. If the upgrade fails, pauses, or is cancelled before successful delivery, retain the backup for recovery.
- [x] Mark DONE only when required acceptance and the requested backup cleanup are complete; report any cleanup failure without claiming it succeeded.

## Acceptance and correction boundaries

The upgrade is accepted when the Claude entry point resolves the new roles; one canonical workflow governs approvals and transitions; all serving profiles have coherent guidance; active C++/old-host contracts are retired; source-sync tests prove all four mandatory exclusions and failure handling; worktree policy fits `main`; and the final report identifies actual checks and any live-session limitations.

Within a phase, correct only the named harness/tooling scope and rerun affected checks. Product changes, Mario implementation, actual remote upload or runtime work, additional dependencies, wider permissions, destructive recovery, and changed acceptance are scope changes. Preserve partial work and return the smallest proposed adjustment for review rather than expanding silently.

Before successful delivery, recovery uses the preserved baseline and exact changed paths. Restore only migration-owned content after confirming no newer edits would be overwritten. After delivery, remove the temporary backup under Phase 5 and retain its checksum and cleanup outcome as records; the backup is no longer a recovery option. No broad reset, clean, or deletion is authorized.

## Review checkpoint

Version v2 was explicitly approved by the user. Local implementation and required offline verification are delivered; the check record records evidence and verified post-delivery backup cleanup. Actual source upload, native Claude behavior and Linux/product runtime validation remain separate from this delivered offline upgrade.
