# Sophon × Mario offline foundation

- ID / version: `2026-11-24-sophon-mario-offline-foundation` / `v1`
- State: `DONE` / F1–F3; required OFFLINE acceptance complete from implementation-owner receipts and parent acceptance review. **G0 NOT PROVEN**; no integration/activation claim.
- Records owner: `sophon-plan`; sole product module/tests/usage-doc owner: `sophon-python-dev`.
- Canonical handoff: this plan + [CHECK](../check/2026-11-24-sophon-mario-offline-foundation-CHECK.md); [CURRENT](../check/CURRENT.md) is only a pointer.

## Decisions and bounded deliverable

Q1 A/Q2 A: one Mario business-conversation path, integration only; preserve Mario scripts, prompts, state and tool authority. No native-chat switching/T1/T2.
Q4 A: prefer in-process direct async; no second `/ws/mario` connection. Existing Mario compatibility is untouched.
“I think maybe you can start develop according to current protocol and we'll test later.” selects development-first/live-later; latest **Q5 B** defers ALL real inference wiring.
Deliver the first real **offline code foundation**, with a deterministic test-only provider; it does not implement or replace Mario reasoning or a real Mario wrapper.
Skip optional generic OpenAI-compatible BackOffice and all model API probes. No Mario application import, reference copy/change or remote discovery.

## Exact write scope and profile

All product paths below are NEW, owned by this task only; no existing product/service behavior changes.
- `live/sophon_live/mario_runtime.py`: stdlib-only transport-neutral async interface, owned local session/task lifecycle and synthetic event mapping.
- `live/tests/test_mario_runtime.py`: stdlib `unittest` / `IsolatedAsyncioTestCase`, deterministic fake provider and callback fixtures only here.
- `live/MARIO_OFFLINE.md`: brief explicit Python-injection usage, contracts and honest limits.
Planner alone updates this plan, its CHECK and CURRENT; preserve completed `2026-11-24-sophon-mario-t0-a` v2 and older upgrade records unchanged.
Preserve pre-existing untracked `.claude/`, `.worktree-policy.yaml`, `AGENTS.md`, `CLAUDE.md`, `doc/` and all unrelated work; no Git lifecycle/cleanup.
Selected profile: [Live gateway](../../.claude/workflows/sophon-serving-profiles.md), offline helper surface only; no Tag/Flash/native backend exercised or installed.
Actual interpreter reported by implementation owner: `C:/Users/TINNOVE/AppData/Local/Python/pythoncore-3.14-64/python.exe`, Python 3.14.7 / Windows. Python 3.10 grammar checked; >=3.10/current installers' 3.12 remain targets, not tested runtimes. No Linux/GPU run.
No new dependencies, packaging changes or universal toolchain; this is product Python, not diagnostic tooling.

## B design: one local owner, current wire contract

B decision: one explicitly constructed runtime per session owns one active task, generation counter and closed state; serialize same-session lifecycle transitions. No global registry, provider framework, factory, config knobs or inference backend.
Prefer one injected async business callable plus async event callback over an in-process Mario import or WS/API adapter; those real integrations remain deferred. No C/public-protocol change.
An internal typed request carries validated session/turn/delegation IDs, generation and task text; business callable returns text. Generation is monotonic and never added to public events; no history/audio input is required.
Session and turn IDs arrive by explicit Python injection; the adapter consumes a synthetic existing `session.delegation.created` event, not a claimed authoritative native turn-readiness signal.
On replacement (including a new turn), invalidate old generation BEFORE cancellation, cancel and await the owned task before launching its replacement. Fence results/errors against session/turn/generation/delegation and closed state immediately before callback handoff.
Disconnect/close invalidates first, cancels/awaits owned work and releases references; repeated close is harmless. Different sessions never cancel or mutate one another.
The callable contract requires cancellation-cooperative cleanup; a delayed/suppressed-cancel result must still be fenced. Await owned cleanup, do not swallow caller cancellation; tests bound waits with deterministic barriers/timeouts, not timing guesses.
Cancellation proves only owned local task lifecycle; it cannot reverse already handed-off events, Mario tool effects or remote work.

Current shapes grounded in `live/sophon_live/gateway.py:179-180,250-259,513-525`:
- Input: `{"type":"session.delegation.created","offset_ms":0,"delegation":{"id":"item_test","type":"delegation","target":"client","task":"SYNTHETIC_TEST_ONLY"}}`.
- Output: `{"type":"session.commentary.append","delegation_id":"item_test","content":"SYNTHETIC_TEST_ONLY"}`; optional existing `event_id` only, no new wire fields.
- Error envelope: `{"type":"error","error":{"code":"invalid_value","message":"..."}}`; use existing `invalid_request_error` for unsupported events, `invalid_value` for malformed input, `server_error` for provider failure; bounded sanitized messages, no exception payload echo.
Validate identifiers, event type/nested shape and usable text before starting work; malformed input never invokes provider. This is local adapter validation, NOT a changed gateway validator: unknown commentary delegation IDs currently acknowledge/no-op.
Mapping acceptance uses synthetic event/callback input only, never gateway dispatch or a live socket. Commentary is tool-result context/model-rephrased speech, not exact-say or an exclusive speech gate.
Keep generated result, callback handoff, transport-sent and played states distinct: only the first two are locally knowable. Do not emit/fake playback receipts; existing `session.commentary.appended` is not played acknowledgment.
No fake backend CLI/env switch, automatic gateway construction, import-time task creation, service hookup or production fallback. No edits to `gateway.py`, startup or existing services.

## Continuous phases after actual v1 approval

| Phase | Sole implementation owner | Work / exit evidence |
| --- | --- | --- |
| F1 | `sophon-python-dev` | **DONE**: minimal interface/contract tests; intentional RED, 28 tests / 46 `NotImplementedError` errors, exit 1. |
| F2 | `sophon-python-dev` | **DONE**: owned lifecycle, fencing and exact current event/error mapping; final focused suite GREEN, 35 tests, exit 0. |
| F3 | `sophon-python-dev` | **DONE**: usage/limits, syntax/import/AST/doc checks and parent acceptance review complete; attributed commands/outcomes/limits in CHECK. |

One approval covers unchanged F1–F3 continuously, with targeted corrections; no routine reconfirmation or mandatory reviewer panel.
Handoff includes this ID/v1, actual approval quote, phase, exact files, Live/offline resources, acceptance below and canonical correction/material rules. Planner records state/evidence; role/child labels alone do not change state.

## Required offline acceptance

1. Deterministic success maps the originating delegation to the exact current commentary shape; provider failure produces the existing sanitized error envelope, no commentary success.
2. Missing/invalid session, turn or delegation identifiers, malformed/unsupported events and unusable task/result text reject clearly; no provider work for bad input, no invented public fields/events.
3. Same-session new turn invalidates, cancels and AWAITS old task cleanup before replacement starts; caller cancellation propagates; stale success/error (including delayed cancellation result) never reaches callback.
4. Disconnect during pending work cancels/awaits owned task; repeated cleanup is idempotent, no leaked owned tasks/callbacks. Two concurrent sessions remain isolated.
5. Assert exact event keys/values and distinguish local handoff from sent/played; fixtures are obvious inert synthetic text, no business scripts/tools or robot/cloud/system operations.
6. No raw history/audio/task-content logging or exception-content leakage; no logging/data framework. Review module/import surface for stdlib-only/offline behavior and usage doc for explicit injection and limits.

Required checks completed from repository root with the actual interpreter above; commands/outcomes are attributed in CHECK:
- `python -m unittest discover -s live/tests -p "test_mario_runtime.py"`
- `python -m py_compile live/sophon_live/mario_runtime.py live/tests/test_mario_runtime.py`
- Focused semantic/content/reference/privacy review of the three deliverables and canonical records. No full-suite/GPU/live tests; unavailable REQUIRED checks remain pending, not DONE.

## Boundaries, deferred work and approval

Apply the [canonical workflow](../../.claude/workflows/sophon-workflow.md#corrections-and-material-boundaries)'s existing six correction boundaries and seven material categories by reference; add no extra gates. Material changes require evidence, planner reconciliation and user decision; preserve partial edits/ownership on escalation.
No network/live tests, config/credential/auth/CA changes, installs/downloads/GPU, upload/activation, service/robot/system operations or Git commit. No writable Mario scope is authorized.
Real Mario wrapper/reasoning wiring, gateway dispatch integration, speech ownership, native turn readiness, heard-history reconciliation and engine cancellation are NOT implemented or claimed; future integration needs separate scope/approval.
**G0 NOT PROVEN; integration acceptance unchanged.** Development-first allows this detached offline foundation before G0, not runtime integration/activation without G0. Live validation is explicitly deferred/unverified and is NOT required for offline DONE.
**Actual user approval (2026-11-24):** **"Approve offline-foundation v1."** Approves presented v1, unchanged offline F1–F3 only; recorded before product execution. Prior v2 read-only approval remains separate.
**Scope clarification within approved v1 (no version/scope change):** No Skill Engine initialization/connection/dispatch/acks; no real inference/OpenAI BackOffice, `/ws/mario` or Mario TTS; no remote source changes/activation; no real `script_jump`/tool execution. Docs/`script_jump` inform synthetic fixtures and usage only, not a new parsing/execution interface. The approved callable returns text; no actual Mario wrapper or action engine. Raw-model JSON parsing/settled-result validation remains future-wrapper work; unfinished JSON stays uninterpreted text, fixture `script_jump` stays inert.

## Offline completion — 2026-11-24

F1–F3 DONE under unchanged recorded v1 approval. Only the three authorized new product paths were created by `sophon-python-dev`; existing services unchanged per parent receipt. Required acceptance is CHECK-CONFIRMED for the detached offline helper only; receipts, ordinary corrections and parent review are in CHECK. Final records-only ID/state/reference/privacy reconciliation passed; no product checks rerun by records owner. Next real integration is separately scoped/approved and must satisfy G0; **G0 NOT PROVEN**.
