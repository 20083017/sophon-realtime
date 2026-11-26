# Sophon × Mario offline foundation — CHECK

| Field | Value |
| --- | --- |
| ID / version | `2026-11-24-sophon-mario-offline-foundation` / `v1` |
| State | `DONE` — OFFLINE scope only |
| Plan | [Canonical plan](../plan/2026-11-24-sophon-mario-offline-foundation.md) |
| Records owner | `sophon-plan` (sole writer of plan/CHECK/CURRENT) |
| Product owner | `sophon-python-dev` (sole writer of new module/tests/usage doc) |
| Actual v1 execution approval | Actual latest user message, 2026-11-24: **"Approve offline-foundation v1."**; presented v1 offline F1–F3 only |
| Phase / step | F1 DONE / F2 DONE / F3 DONE; required offline acceptance complete |
| Material blocker | None for completed offline scope; G0 NOT PROVEN for future integration |
| Runtime status | **G0 NOT PROVEN**; real Mario/gateway integration/live validation deferred/unverified |

## Authority and preserved baseline

- Actual design decisions supplied by user: Q1 A/Q2 A one Mario path, Q4 A prefer in-process/no second `/ws/mario`, development-first/live-later, latest “Q5 B” defer all real inference wiring; skip generic OpenAI BackOffice/model API probes.
- User direction “I think maybe you can start develop according to current protocol and we'll test later.” determines ordering, NOT approval of this newly generated implementation plan/version.
- Completed [T0-A CHECK](2026-11-24-sophon-mario-t0-a-CHECK.md) remains v2 DONE unchanged; its actual approval “Approve v2 for the read-only compatibility preflight and G0 decision/experiment proposal.” authorizes no new code/imports/tests.
- Older [workflow-upgrade CHECK](2026-11-24-claude-python-workflow-upgrade-CHECK.md) and prior plan/check/logs remain unchanged. Prior CURRENT named only completed work; no active plan was displaced.
- Pre-existing untracked `.claude/`, `.worktree-policy.yaml`, `AGENTS.md`, `CLAUDE.md`, `doc/` and unrelated work preserved. No product partial edits existed at planning baseline; records owner writes only plan/CHECK/CURRENT. Product creations attributed below.

## Completed F1–F3 — implementation-owner receipts (not rerun by records owner)

- Sole `sophon-python-dev` CREATED exactly `live/sophon_live/mario_runtime.py`, `live/tests/test_mario_runtime.py`, `live/MARIO_OFFLINE.md`. Live gateway profile, stdlib-only explicit injection; existing services unchanged, no activation.
- F1 DONE: intentional RED, 28 tests / 46 `NotImplementedError` errors, exit 1. F2/F3 DONE: final GREEN, usage/limits and required checks under unchanged approval/version/scope.
- Actual interpreter: `C:/Users/TINNOVE/AppData/Local/Python/pythoncore-3.14-64/python.exe`, Python 3.14.7 / Windows. Python 3.10 grammar checked; no 3.10/3.12 runtime, Linux/GPU validation claimed.
- From repository root: `python -m unittest discover -s D:/project/sophon-realtime/live/tests -p 'test_mario_runtime.py'` — exit 0, **35 tests passed, 7.195 s**.
- `python -m py_compile D:/project/sophon-realtime/live/sophon_live/mario_runtime.py D:/project/sophon-realtime/live/tests/test_mario_runtime.py` — exit 0; additional compilation with `-W error::SyntaxWarning` — exit 0.
- Isolated `python -I` import/AST/doc checks — exit 0: silent/task-free import, stdlib imports, Python 3.10 grammar and doc links. All product checks above are developer-reported, not records-owner executions.
- Delivered frozen `MarioRequest`, per-session `MarioRuntime`, typed async text callable/callback, exact GPT-Live event/error dicts, validation/sanitized failures, generation fencing, invalidate-before-cancel/await-before-replace, cancellation propagation/cooperative cleanup and idempotent close; no global registry/CLI/env/gateway activation.
- Tests cover exact shapes, invalid/missing IDs/events/results, Unicode preservation/frozen identity, same/reused-ID fences, awaited cancellation/replacement, delayed stale success/error, repeated caller cancel, disconnect/close, two sessions, provider/callback failures, privacy and handoff non-retraction. Completed-shape fixture extracts response only; unfinished JSON stays text; metadata cannot override injected identity; fixture `script_jump` inert.
- Ordinary developer corrections: regex SyntaxWarnings fixed before final checks; supplemental doc checker replaced over-literal line-wrapped phrase matching with whitespace-aware matching, then passed without weakening the required assertion. No material change/retry gate.
- Limits: callback handoff is not transport send/playback; local errors/cleanup cannot reverse remote effects. Providers/callbacks require cooperative cleanup; no safe forced termination of arbitrary uncooperative code. Raw-model JSON parsing/settled-result validation remains future-wrapper work.
- **G0 NOT PROVEN**. Real Mario model/wrapper/gateway wiring, speech ownership/native turn readiness/heard-history/engine cancellation unimplemented/unverified. No Skill Engine, Mario TTS, `/ws/mario`, model/API/network, deps/install/GPU/upload/service/commit or real tool action. Future integration separately scoped/approved with G0.

## Historical planning/approval evidence (pre-implementation snapshots)

- Prior planning owner reported bounded workflow/status/final-findings reads and three gateway excerpts grounding contracts; no source audit, credentials, remote discovery, delegation, product execution/imports/tests at that step. Final records owner did not repeat source discovery.
- Record containment/new-path checks: shell exit 0 before writing. First long shell write failed parsing (exit 2); follow-up metadata check (exit 0) confirmed both new records absent. Dedicated file writes used instead; no product partial edits or temporary artifacts.
- Initial planning snapshot before approval/execution: post-write records-only content/link/ID/privacy check: **PASS, shell exit 0** (inline wc/grep/iconv/realpath/link-existence assertions): PLAN 80 lines <=100, CHECK 41 lines <=65; canonical links, ID/v1/pending state, UTF-8 and bounded secret-pattern scan passed. Planned product paths remain absent. Manual scope/privacy review passed; no product tests/imports or runtime proof.
- Apply [canonical workflow](../../.claude/workflows/sophon-workflow.md#corrections-and-material-boundaries): six correction boundaries/seven material categories; no extra gates, generated approval or role-label state transitions.
- Historical handoff, now completed: F1 assigned to sole `sophon-python-dev`; unchanged F1–F3 executed continuously under recorded approval, with planner-only canonical updates.
- Approval/state evidence (2026-11-24): actual latest user message **"Approve offline-foundation v1."** recorded; entered `APPROVED`, then `IN_PROGRESS` / F1 for sole-owner handoff before any product execution.
- Clarification within existing v1, not scope/version revision: No Skill Engine initialization/connection/dispatch/acks; no real inference/OpenAI BackOffice, `/ws/mario` or Mario TTS; no remote source changes/activation; no real `script_jump`/tool execution. Docs/`script_jump` inform synthetic fixtures and usage only, not a new parsing/execution interface. The approved callable returns text; no actual Mario wrapper or action engine.
- Records-only correction: initial approval-update shell command failed parsing (exit 2) before execution; corrected with targeted literal record edits. No product edits/imports/tests, children, network or discovery in this handoff.

## Parent acceptance and final records reconciliation — 2026-11-24

- Parent-reported acceptance review read full runtime/usage and targeted test lifecycle/fixture portions: no must-fix findings. Required offline acceptance is CHECK-CONFIRMED, not live-integration proof.
- Parent-reported `git diff --no-index --check /dev/null <each of the three product paths>`: no whitespace errors, aggregate exit 0; only autocrlf LF-to-CRLF warnings. Parent status confirmed new product scope only those paths (`live/tests/` contains the test); existing product/service files and unrelated/untracked work, including unread `常用命令.txt`, unchanged. Records owner did not rerun Git/source checks.
- Records owner read only these three records and canonical workflow. Final ID/v1/actual-approval/state/canonical-reference/privacy review PASS: manual review of all three intended record changes plus in-memory assertions in records-only commands, exit 0. References checked lexically, not by reading external targets. Only these existing records changed; no product edits/imports/tests, children, network or other files inspected.
- Ordinary records corrections: two long reconciliation commands failed shell parsing (exit 2 before execution); shorter targeted commands succeeded. No product partial edits or new retry gate.
- Final state: **DONE, F1/F2/F3 DONE — OFFLINE ONLY; G0 NOT PROVEN**. Required reported acceptance passed; no full suite or new product test run needed/performed. Prior completed preflight/upgrade records untouched. Next: real integration separately scoped/approved; G0 and live acceptance outstanding.
