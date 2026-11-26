# Sophon × Mario protocol validation — CHECK

| Field | Value |
| --- | --- |
| ID / version | `2026-11-25-sophon-mario-protocol-validation` / `v1` |
| Plan | [Canonical plan](../plan/2026-11-25-sophon-mario-protocol-validation.md) |
| State | `DONE` (offline only) |
| Actual approval | User, 2026-11-25, exact: **“Approve protocol-validation v1.”**; unchanged v1 scope and continuous phases 2–3, recorded before implementation; generated records/agent messages are not consent |
| Approval transition | `AWAITING_USER_CONFIRMATION` → `APPROVED` → `IN_PROGRESS` → `DONE`; actual approval preserved; no product work performed by records owner |
| Records owner | `sophon-plan`, sole writer of plan/CHECK/CURRENT |
| Product owner | Primary executor routed as `sophon-python-dev`, not another child; sole writer of exact three product files in plan |
| Phase / step | 1 planning DONE; 2 implementation DONE; 3 verification DONE; unchanged v1 required local acceptance complete |
| Material blocker | None; approved unchanged offline scope |
| Runtime | **G0 NOT PROVEN**; Q5 B real inference wiring DEFERRED |

## Authority and preserved baseline

- Pre-approval planning direction: native Tag/Flash WS and HTTP audio endpoints matter; use READMEs/project docs and “continue to develop our plan using the test.” Planning direction, not implementation/integration approval.
- One business path/in-process preference/no `/ws/mario`, SkillEngine, MarioTTS or real script/tool effects remain selected.
- [Offline-foundation v1 CHECK](2026-11-24-sophon-mario-offline-foundation-CHECK.md) remains DONE unchanged: historical owner-reported 35 tests + py_compile exit 0, Python 3.14.7 / Windows; current 35-test nonregression rerun below, not 3.12/Linux proof. Existing text callable/module/tests frozen here.
- [Preflight v2 CHECK](2026-11-24-sophon-mario-t0-a-CHECK.md) and [older upgrade CHECK](2026-11-24-claude-python-workflow-upgrade-CHECK.md) remain DONE unchanged, including plans/logs. CURRENT previously named completed work only; no active plan displaced.
- Parent baseline: user independently STAGED `.claude/`, root policies/instructions and `常用命令.txt` before the first code edit; not executor staging. Command notes unread; user-staged/unrelated dirty work preserved. Live paths already unstaged/untracked from prior foundation. No Git add/commit/reset/stash/cleanup; normal pycache ignored. Planner changes only this plan/CHECK/CURRENT; older records/logs unchanged.

## Attributed prior diagnostics — parent receipts, NOT rerun

- Separately authorized model-only HTTP diagnostics, Qwen3.6-27B-FP8: three synthetic plain-prompt cases curl exit 0 / finish_reason stop, strict JSON FAIL (prose/reasoning/embedded examples). Recovered fragments are not authoritative final replies.
- Three strict `response_format.type=json_schema` cases PASS: baseline SYNTHETIC_OK/actions[], Script_4 script_jump, explain jump but stay Script_1/actions[]. Schema allowed [] OR one jump, not forced action; no Mario code/state/tools ran.
- Constrained requests were single samples (~0.5–1 s), not voice/model-quality evidence. No private endpoints, paths or raw traces copied here.
- Separately authorized Live WSS: HTTP101; session.start→session.started active; close→session.closed closed, matching ID/reason close_requested, WS1000. PCM16/16000, voice/client-delegation/store=false metadata echo; no client audio/delegation results/Mario calls.
- Explicit one-off TLS verification exception: TLS1.3 encrypted but certificate identity NOT verified. No blanket deployment/inference integration consent or reusable TLS exception follows.

## Approved implementation — parent/primary-executor receipts

- Sole product writer: primary executor routed as `sophon-python-dev`; NEW `live/sophon_live/mario_reply.py`, NEW `live/tests/test_mario_reply.py`, brief extension ONLY of `live/MARIO_OFFLINE.md`. Existing `mario_runtime.py` and prior runtime tests untouched; no new dependencies or environment changes.
- Pure stdlib `parse_mario_reply(content, finish_reason, allowed_scripts, current_script)` returns frozen `MarioReply`/`ScriptJump` tuple metadata. Requires stop, nonblank response, exact keys and at most one script_jump; validates caller IDs/context and target. Same-current target is_noop; no action execution.
- Rejects duplicate keys, nonfinite constants, malformed/truncated/markdown/prose/recovered JSON, extra content/fields, wrong types, invalid Unicode and unknown targets/external skills. Response bytes/tags preserved; fixed errors, no payload-bearing decoder/Unicode exception chaining. Documented bounded subset rejects action-only/multi-action replies.
- No API/SSE unwrapping, network/model/script engine/SkillEngine/gateway activation or actual audio. Parser success is validation, not execution, transport interoperability or playback.

## Required local acceptance — actual parent commands/outcomes

Environment: repo root, Windows Python **3.14.7**, executable `%LOCALAPPDATA%/Python/pythoncore-3.14-64/python.exe`. CHECK-CONFIRMED via supplied primary-executor receipts; all final commands/checks below exit **0**, not checks performed or repeated by this records writer.

| Actual command / focused check | Final outcome |
| --- | --- |
| `python -m unittest discover -s live/tests -p test_mario_reply.py` | 33 PASS, 0.334 s; required synthetic prompt/schema shapes, strict JSON/action/context/Unicode/privacy acceptance complete |
| `python -m unittest discover -s live/tests -p test_mario_runtime.py` | 35 PASS, 7.327 s; unchanged tests/contract; benign async-debug slow-task message, no failure |
| `python -m py_compile live/sophon_live/mario_reply.py live/tests/test_mario_reply.py` | PASS, both changed Python files |
| `python -W error::SyntaxWarning -m py_compile live/sophon_live/mario_reply.py live/tests/test_mario_reply.py` | PASS, SyntaxWarning treated as error |
| `python -I` isolated inline AST/import/doc acceptance | PASS: both files Python 3.10 grammar; stdlib-only imports; silent/task-free isolated import + explicit parse smoke; doc relative links, Python blocks, Markdown table, protocol matrix and private-endpoint absence |
| Focused semantic/privacy review by primary executor | PASS: native Realtime vs Live PCM/events and HTTP WAV/SSE accurate; Tag strips vs Flash keeps tags; bounded subset documented; no actual transport-interoperability claim |
| Corrected `git diff --no-index --check` whitespace helper | All three product files PASS; strict checker exit 0; underlying exit 0 or 1 only with no stdout whitespace diagnostics; stderr permits only exact known autocrlf LF→CRLF warning |

Authoritative final logs/summary are external: `%LOCALAPPDATA%/Sophon/reports/protocol-validation-02a46136/`, `check-1.log`, `check-2.log`, `check-3.log`, `summary.json`. Supplied paths NOT read/copied here. No actual Python 3.10/3.12 run, Linux/GPU/model/live-service/audio or transport interoperability proof.

## Ordinary within-scope corrections — no waived acceptance

- RED interface stub: reply discovery exit 1, 31 tests, 1 failure/129 intentional NotImplementedErrors. First GREEN 31 PASS. Oversized-integer decoder regression then 32 tests/1 error, exit 1 (4300-digit conversion ValueError not yet sanitized); targeted catch fix → 32 PASS.
- Unicode test insertion embedded an unpaired surrogate: UnicodeEncodeError after truncating TASK-OWNED NEW test file. Runner detected 0 tests, exit 5 — NOT a pass. Full original tests/all assertions restored plus context regression using `chr(0xD800)`; final 33. No pre-existing file loss or weakened assertions.
- Whitespace helper initially assumed exit 0; new-file differences may exit 1. Corrected status/diagnostic classification above, not source/test assertions; final strict checker exit 0.
- Ordinary targeted corrections within the existing six boundaries, not material blockers or waived acceptance. RED excerpts/tool outputs/temp evidence retained; no code/data cleanup/reset.

## Records reconciliation and completion

- Saved exact approval/version/owners unchanged. Phases 1 planning, 2 implementation and 3 verification DONE; all unchanged v1 required local acceptance complete. Parent receipts supply outcomes, not consent.
- Historical planning records checks passed exit 0 after shell parsing exit 2 before edits. This reconciliation had three long-heredoc shell parsing failures exit 2, before edits in each failed call; shorter commands updated plan/CURRENT and a dedicated file write completed CHECK. No product access or acceptance change.
- Records-only ID/version/state/approval/owner/canonical-link/containment/privacy consistency check PASS, exit 0; exactly these three existing records written. No product reads/imports/edits/tests, network, children or older-record changes by this writer.
- **DONE is offline only; G0 NOT PROVEN.** Q5 B real inference wiring DEFERRED, SkillEngine off, text contract unchanged. Speech ownership/native readiness/heard history/cancellation/deployment/model quality/integration activation remain unverified.
- No pending v1 local acceptance. Actual native audio/real integration requires separate scope and selected native endpoint/deployed Tag OR Flash/auth/TLS/audio fixtures. Endpoint unknown is not an offline blocker. Earlier user-directed external synthetic 3.63 s Chinese WAV NOT used here. Prior one-connection TLS exception is neither default nor future authorization; no network this phase.
- Canonical handoff remains plan + CHECK; CURRENT pointer-only. Preserve older completed records/logs and unrelated staged/unstaged/untracked work. No new permission request, panel or child. Future work follows the [existing correction/material rules](../../.claude/workflows/sophon-workflow.md#corrections-and-material-boundaries).
