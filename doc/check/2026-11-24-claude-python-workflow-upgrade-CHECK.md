# Claude Python Workflow Upgrade Check Record

| Field | Value |
| --- | --- |
| Plan | `../plan/2026-11-24-claude-python-workflow-upgrade.md` |
| Plan ID | `2026-11-24-claude-python-workflow-upgrade` |
| Version | `v2` |
| State | `DONE` |
| Approval evidence | User approved v2: "approve, and start upgrade the workflow agents for me." |
| Phase / step | Complete; delivery and scoped cleanup verified |
| Completed implementation phases | 1, 2, 3, 4, 5 |
| Owner | Primary executor / planner |
| Next action | Start fresh Claude with normal login/trust; remote validation/upload remains a separate task |
| Updated | `2026-11-24T16:25:50+08:00` |
| Material blocker | None |
| Correction attempts | One integrated review fix pass; targeted regression evidence below |

## Discovery evidence

- Local HEAD: `e187202824738290d76dde27adb748fe3c14da6e`; current branch: `main`.
- Before planning artifacts, Git reported untracked `.claude/`, `.worktree-policy.yaml`, `AGENTS.md`, and `CLAUDE.md`; no tracked diff was reported. These are pre-existing content, not edits from this task.
- Existing default agent, rules, workflow, sync command, and remote helpers are WTP184-oriented. Python's current specialist is tooling-only. Worktree policy refers to master/develop although only main is present locally.
- User selected Claude-only support and shared rules with separate serving profiles. User explicitly excluded Mario runtime investigation/migration from this upgrade.
- Mandatory source-upload exclusions: `.claude/`, `.worktree-policy.yaml`, `AGENTS.md`, `CLAUDE.md`.
- Revision v2 records the user's request to remove the migration backup after successful upgrade verification and delivery. The cleanup is limited to recorded task-created backup paths. This was recorded before approval; the temporary backup was subsequently created under Phase 1 and removed after delivery as recorded below.
- Prior bounded read-only discovery established remote reference access; no server changes or uploads occurred. Mario runtime findings are not part of this plan's implementation inputs.

## Validation

Before implementation, planning artifact readback and a read-only Python consistency check passed (exit 0): three records have matching IDs/version/state, valid plan/check links, five implementation phases, all mandatory sync exclusions, and no embedded IP addresses. Git status shows only the original untracked harness entries plus the new `doc/` planning artifacts; no tracked diff was reported.

At that planning checkpoint no implementation tests had run. Subsequent offline test results are recorded below. No package installation, service operation, product inference or source upload has been performed.

## Phase outcomes

| Phase | Status | Evidence |
| --- | --- | --- |
| 1 Baseline and repository policy | Complete | 77-file archive verified; approved branch created; main-based policy preserves protected delivery |
| 2 Workflow and agents | Complete | Seven sophon roles plus worktree manager; canonical states/profiles/routing updated |
| 3 Rules and skills | Complete | Python rules and five reference skills; legacy files retired; generic contradictions reconciled |
| 4 Source synchronization | Complete | RED 20 expected failures before implementation; expanded offline suite: 27 tests, 24 passed, 3 platform skips |
| 5 Integrated review | Complete | Review regressions fixed; 35 passed / 3 platform skips; scope verified; delivered and backup removed |

Unverified items: live Claude discovery/routing and permission enforcement, Linux-only filesystem behavior, profile/GPU environments, and actual server synchronization. Offline helper evidence is recorded below.

## Execution decisions

- Approval applies to v2 and its scoped post-delivery cleanup.
- Ruling: use this check record as the execution ledger and the approved same-checkout branch; the approved plan supersedes generic additional worktree, commit, and parallel ledger requirements. This preserves the existing untracked harness.
- Phase interfaces: canonical workflow defines routing consumed by rules/skills; source-sync skills and CLI share configuration, manifest, and exclusion contracts; review consumes all phase evidence.

## Temporary baseline

- Backup: `%LOCALAPPDATA%/SophonWorkflowMigration/2026-11-24-v2/baseline.zip`
- SHA-256: `4504be18364858aba5cb3f1273776cacb2a2a2b42b84761ec5cc0cd3854e134b`
- Manifest: same directory, `baseline-manifest.json`; 77 files verified against the archive.
- Exact cleanup set: archive, manifest, and their empty task-owned directory after successful delivery.
- Baseline captured: `2026-11-24T15:48:00+08:00`. No other backup paths are authorized.

- Phase 1: managed-agent direct integration disabled because its target is now protected main; ordinary PR delivery remains available. No protection was relaxed.

## Behavioral baseline

A fresh read-only agent exercised the original harness before migration: Tag product ownership was undefined, sync meant binary artifacts and prohibited workstation source, native-engine validation had no profile, and Mario had no configured reference route. Small Python helper validation already worked and is retained. The response is source-based simulation, not a live Claude/runtime result. New skills are scoped reference guides to these known gaps; no generic pressure-policy framework is introduced.

- Phase 2/3: created Python roles/profiles and five focused reference skills; retired 36 baseline-verified legacy files from active discovery. Generic personal/handoff/docs skills retained. The temporary archive retains retired content until delivery.

## Validation progress

- RED: `python -m unittest discover -s .claude/tools/tests -p test_source_sync.py -q` failed as expected with 20 missing-implementation assertions; `source-sync-validation.log`.
- GREEN: expanded suite exited 0; 27 tests, 3 skips (Windows lacks symlink privilege and POSIX mode semantics); Windows junction protection passed. Full log: `source-sync-expanded.log`.
- Syntax helper checked four affected Python/shell files; helper CLI --help succeeded.
- Actual Claude CLI 2.1.309 was invoked with Read-only tools and no MCP servers; exited 1 before inference because it is not logged in. Live Claude behavior remains unverified; no credentials were changed. `claude-behavior-validation.log`.
- Structural check found pre-existing missing shell-skill frontmatter and unrelated global-hook/security-reviewer assumptions; corrected within the approved generic-rule scope.

## Integrated review and corrections

Fresh review required corrections for repository-root exclusion bypass, remote reference separation, name-based Linux writes, source executable-mode/final drift, nested planner delegation, generic parallel-panel instructions, and false syntax-check success. All are being addressed in one focused pass; no product or server scope was added.

- RED: 38 tests produced 11 failing regression assertions and 3 platform skips, `review-regressions-red.log` (exit 1).
- Root fix: validate the unresolved source path, reject links/junctions and require the Git worktree top level before any SSH object is created.
- Remote fix: validate both source/reference identities and overlap; Linux operations pin no-follow ancestor/parent directory handles. A source-configured double-slash anchor is rejected.
- Ruling: helper lock coordinates helper invocations; external writers must be quiesced. Per-file replacement cannot promise atomic compare-and-swap against arbitrary processes. Documented this operating boundary rather than claiming stronger guarantees.
- Source fix: compare current hashes and authoritative Git executable modes before upload and again after remote verification.
- Routing/rule fix: /sync stays in the primary planner context; no child planner chain or automatic skeleton/parallel panel.
- Syntax fix: propagate Git discovery errors, reject missing explicit files, and report empty discovery as no checks.
- Reviewer declined live Claude/SSH/product/GPU/Mario/POSIX/cleanup proof: these are evidence limits, not claims of success; offline fixtures and later cleanup verification cover only their stated scope.
- The live Claude fixture also reported that the workspace is untrusted and ignored 58 permission allow entries. No trust/authentication setting was changed. Native Claude behavior and effective permissions remain unverified until the user signs in and trusts this workspace interactively.
- User-local server-session configuration was created outside the repository using the supplied values; schema and `ssh -G` alias identity checks passed locally without a server connection. File: `%LOCALAPPDATA%/Sophon/server-session.json`.

## Delivery evidence

- Final offline suite: `python -m unittest discover -s .claude/tools/tests -p "test_*.py" -v` exited 0; **38 tests, 35 passed, 3 skipped**. Skips: symlink creation privilege for two tests and POSIX executable-mode test on Windows. Windows junction checks passed. Full log: `source-sync-final.log`.
- The review regressions went from 11 failures to PASS; the final run includes those corrections. No unaddressed required review findings remain. Linux no-follow directory-handle operations are implemented and syntax-checked, but not executed on this Windows host; they still need Linux validation before relying on live upload behavior.
- Final structural check: YAML/JSON, 8 agent names, skill and path references, main-based policy, Python AST, original ask/deny permissions, unchanged personal skills and AGENTS.md passed. `harness-structure-final.log`.
- Syntax helper checked five changed Python/shell files; `git diff --check` passed. Tracked product source has no diff. No product tests/GPU/service operations or server uploads were run.
- Ready-to-use documentation: `.claude/README.md`; canonical workflow: `.claude/workflows/sophon-workflow.md`; source-sync helper: `.claude/tools/sophon-source-sync.py`.
- Native Claude integration remains unverified: CLI authentication is absent and project permissions were ignored because the workspace is untrusted. Start an interactive Claude session and complete sign-in/trust normally; no authentication or trust setting was bypassed.
- Branch remains `refactor/python-workflow-upgrade`, with the requested changes uncommitted. The approved plan supersedes generic finish-branch menus and automatic commits.
- Report and changed files are delivered in the workspace. The agreed migration-backup cleanup is recorded below.

## Delivered scope inventory

- added: `.claude/agents/sophon-architecture-calibrator.md`, `.claude/agents/sophon-code-review.md`, `.claude/agents/sophon-plan.md`, `.claude/agents/sophon-python-dev.md`, `.claude/agents/sophon-python-tooling.md`, `.claude/agents/sophon-server-operator.md`, `.claude/agents/sophon-shell-tooling.md`, `.claude/config/server-session.example.json`, `.claude/rules/python-development.md`, `.claude/skills/mario-reference/SKILL.md`, `.claude/skills/python-development/SKILL.md`, `.claude/skills/sophon-server-session/SKILL.md`, `.claude/skills/sophon-source-sync/SKILL.md`, `.claude/skills/sophon-verification-loop/SKILL.md`, `.claude/tools/sophon-source-sync.py`, `.claude/tools/tests/test_check_format.py`, `.claude/tools/tests/test_source_sync.py`, `.claude/workflows/sophon-serving-profiles.md`, `.claude/workflows/sophon-workflow.md`
- modified: `.claude/README.md`, `.claude/agents/worktree-manager.md`, `.claude/commands/sync.md`, `.claude/hooks/check-format.sh`, `.claude/rules/code-style.md`, `.claude/rules/configuration-modification.md`, `.claude/rules/ecc/common/agents.md`, `.claude/rules/ecc/common/coding-style.md`, `.claude/rules/ecc/common/git-workflow.md`, `.claude/rules/ecc/common/hooks.md`, `.claude/rules/ecc/common/patterns.md`, `.claude/rules/ecc/common/performance.md`, `.claude/rules/ecc/common/security.md`, `.claude/rules/ecc/common/testing.md`, `.claude/rules/observability.md`, `.claude/rules/shell-scripting.md`, `.claude/settings.json`, `.claude/skills/shell-scripting/SKILL.md`, `.claude/skills/tdd-workflow/SKILL.md`, `.claude/tools/compact-log.sh`, `.worktree-policy.yaml`, `CLAUDE.md`
- retired: `.claude/agents/wtp184-architecture-calibrator.md`, `.claude/agents/wtp184-code-review.md`, `.claude/agents/wtp184-dialogue-dev.md`, `.claude/agents/wtp184-plan.md`, `.claude/agents/wtp184-python-tooling.md`, `.claude/agents/wtp184-server-operator.md`, `.claude/agents/wtp184-shell-tooling.md`, `.claude/config/test-hosts.env.example`, `.claude/rules/cpp-observability.md`, `.claude/rules/ecc/cpp/coding-style.md`, `.claude/rules/ecc/cpp/hooks.md`, `.claude/rules/ecc/cpp/patterns.md`, `.claude/rules/ecc/cpp/security.md`, `.claude/rules/ecc/cpp/testing.md`, `.claude/skills/cpp-coding-standards/SKILL.md`, `.claude/skills/kibana-online-log-retrieval/SKILL.md`, `.claude/skills/kibana-online-log-retrieval/references/OPERATIONS.md`, `.claude/skills/kibana-online-log-retrieval/scripts/audit_empty_history_response.py`, `.claude/skills/kibana-online-log-retrieval/scripts/replay_history_pair_to_dev.py`, `.claude/skills/wtp184-bazel-linux/SKILL.md`, `.claude/skills/wtp184-core-debug/SKILL.md`, `.claude/skills/wtp184-docker-log-inspection/SKILL.md`, `.claude/skills/wtp184-local-gdb/SKILL.md`, `.claude/skills/wtp184-redis-context/SKILL.md`, `.claude/skills/wtp184-redis-context/references/OPERATIONS.md`, `.claude/skills/wtp184-redis-context/scripts/redis_context.py`, `.claude/skills/wtp184-server-session/SKILL.md`, `.claude/skills/wtp184-server-session/migrate-dev-environment-copy-only.sh`, `.claude/skills/wtp184-stress-test/SKILL.md`, `.claude/skills/wtp184-verification-loop/SKILL.md`, `.claude/skills/wtp184-worktree-cleanup/SKILL.md`, `.claude/tools/wtp184-core.sh`, `.claude/tools/wtp184-deploy-ssh-contract.sh`, `.claude/tools/wtp184-docker-log.sh`, `.claude/tools/wtp184-server.sh`, `.claude/workflows/wtp184-workflow.md`
- unchanged: `.claude/rules/python-tooling.md`, `.claude/skills/docs-review/SKILL.md`, `.claude/skills/docs-review/references/docs-antipatterns.md`, `.claude/skills/docs-review/references/docs-principles.md`, `.claude/skills/docs-review/references/docs-strategy.md`, `.claude/skills/docs-review/references/storybook-style.md`, `.claude/skills/grill-me/SKILL.md`, `.claude/skills/grilling/SKILL.md`, `.claude/skills/handoff/SKILL.md`, `.claude/skills/i-have-adhd/SKILL.md`, `.claude/skills/python-tooling/SKILL.md`, `.claude/tmp/__pycache__/build_android_v3_adhd.cpython-314.pyc`, `.claude/tmp/__pycache__/build_android_v3_essentials.cpython-314.pyc`, `.claude/tmp/__pycache__/export_current_adhd_markdown.cpython-314.pyc`, `.claude/tmp/__pycache__/qr-v4-postimage-cmp.cpython-314.pyc`, `.claude/tmp/__pycache__/qr-v4-remote-apply.cpython-314.pyc`, `.claude/tmp/__pycache__/render_82b7ff0_html.cpython-314.pyc`, `.claude/tmp/__pycache__/render_android_v3_zh.cpython-314.pyc`, `AGENTS.md`

## Completed cleanup

- `2026-11-24T16:25:50+08:00`: verified the recorded archive SHA-256 and exact original Windows-newline manifest, then removed only `baseline.zip`, `baseline-manifest.json`, and their empty task-owned directory. All three paths are absent.
- Removed 3 task-generated Python cache files and their empty cache directories. Original unrelated caches, user-local server config, product files and shared backup parent remain untouched.
- The first cleanup guard stopped before deletion because its reconstructed manifest used LF rather than the original Windows CRLF; exact original bytes and archive contents were subsequently verified before cleanup.
- Temporary baseline recovery is no longer available, as requested. Delivered source, plan/check records and validation logs remain.
