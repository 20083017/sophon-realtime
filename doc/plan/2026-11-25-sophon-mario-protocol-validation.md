# Sophon × Mario protocol validation

- ID / version: `2026-11-25-sophon-mario-protocol-validation` / `v1`
- State: `DONE` (offline only); actual v1 approval preserved in CHECK; phases 1–3 complete. Product outcomes are supplied parent/primary-executor receipts, not rerun by the records owner.
- Canonical handoff: this plan + [CHECK](../check/2026-11-25-sophon-mario-protocol-validation-CHECK.md); [CURRENT](../check/CURRENT.md) is pointer-only.
- Intent: continue planning from separately authorized diagnostics, not reinterpret them as integration approval.

## Decisions, baseline and ownership

One business path; prefer in-process; no `/ws/mario` hop, SkillEngine or MarioTTS; no real script/tool effects. **Q5 B: real inference wiring DEFERRED.**
Preserve [offline-foundation v1](2026-11-24-sophon-mario-offline-foundation.md) DONE and its text-callable contract; no edits to `mario_runtime.py` or its existing tests under this version.
Preserve [preflight v2](2026-11-24-sophon-mario-t0-a.md), [older upgrade](2026-11-24-claude-python-workflow-upgrade.md), their CHECK/logs and unrelated dirty/untracked work unchanged; command notes remain unread.

| Sole writer | Exact file scope |
| --- | --- |
| `sophon-plan` (this planner) | This existing plan, matching CHECK, existing `doc/check/CURRENT.md` only |
| Primary executor routed as `sophon-python-dev` (not another child) | NEW `live/sophon_live/mario_reply.py`, NEW `live/tests/test_mario_reply.py`; brief extension ONLY of existing `live/MARIO_OFFLINE.md` |

Profile: [Live gateway](../../.claude/workflows/sophon-serving-profiles.md), detached offline product Python, not tooling; Tag/Flash are documentation/fixture references, not exercised backends.
Stdlib + existing unittest conventions; no dependencies. Preserve >=3.10 compatibility/current 3.12 target (`tag/plugin/pyproject.toml:9`, `tag/install.sh:13-14`); no interpreter/install change.
Final required acceptance: Python 3.14.7 / Windows, 33 reply tests + 35 unchanged runtime tests; actual commands/parent receipts in CHECK. Python 3.10 grammar checked, not an actual 3.10/3.12 run; no Linux/GPU proof.

## B design: strict internal completed-reply boundary

Choose a standalone pure parser over changing the text runtime or adding a model client/script engine. Internal contract change (B); public APIs/protocols unchanged (not C).
Input: complete JSON content string plus explicit completion `finish_reason`, caller-provided allowed script IDs and current script ID; no inferred state/loaders/network/stream assembly.
Require `finish_reason == "stop"`; reject missing/other reasons including `length`, even if content parses. Unfinished output is never authoritative.
Require exactly `response` (nonblank string) and `actions` (list, zero or one item); preserve response text verbatim, including sound tags/Unicode.
Strict JSON: reject duplicate keys at every level, nonfinite constants, extra fields, wrong types, trailing content, malformed/truncated input, reasoning prose, markdown and recovered fragments.
No regex salvage, normalization or coercion; surrounding JSON whitespace is permitted. Never extract decisions from reasoning or response prose.
Only supported action: exact `{"skill":"script_jump","params":{"target_script":"Script_4"}}`; exact keys/types, target in caller-provided allowed IDs; validate caller context too.
Return immutable typed response/action metadata. Same-current-script target is explicitly no-op; no action is reported applied/executed. Unknown/external skills reject explicitly while SkillEngine is off.
Errors use fixed bounded messages, never raw payload/exception echo. Keep response separate from actions; only validated response may feed the unchanged async text callable in an explicit synthetic offline example.
No second script engine, LLM client/backend framework, hidden transition or fake playback/history receipt. Parser success is validation, not execution or speech.

## README-grounded fixtures and documentation

Use [Tag API notes](../../tag/README.md#api-notes), [Flash API](../../flash/README.md#api) and existing project contracts; never run/import/help either `client_example.py` (startup requests/writes).
Both native backends document WS `/v1/realtime` and POST `/v1/chat/completions` audio-in to text+audio-out; documentation is not deployed availability.
Native WS: `session.update`, continuous `input_audio_buffer.append`; Tag documents `extra_body.auto_response=true` and language. Existing adapter uses base64 `pcm_f32le`, 16000 Hz; not Live PCM.
Live GPT: `session.start`, PCM16/16000, `session.input_audio.append` and delegation/commentary events. Gateway Realtime wrapping establishes neither endpoint aliases nor backend selection.
HTTP: profile `config/system_prompt.json`, `modalities:["text","audio"]`, text `<|audio|>` + base64 WAV `input_audio`; SSE `data` with outer modality / `choices.delta.content`; audio WAV/24000 Hz.
Tag text strips tags; Flash keeps them. Assert fixture/doc distinction, never globally normalize response text. HTTP streaming success is not duplex/playback proof.
Keep a few inert synthetic fixtures in the new test file/brief doc extension, not a protocol framework or transport client; separate transport fixtures from Mario reply JSON.
Preserve existing offline usage/limits. Example returns only validated response text; inert actions cannot replace injected session/turn/delegation identity.

## Continuous phases after actual v1 approval

| Phase | Owner | Work / acceptance |
| --- | --- | --- |
| 1 | `sophon-plan` | DONE — planning complete; actual v1 user approval recorded before implementation |
| 2 | `sophon-python-dev` (primary executor) | DONE — focused RED → GREEN parser/tests, synthetic protocol fixtures and brief doc extension within exact three-file scope |
| 3 | Same `sophon-python-dev` | DONE — required local acceptance, targeted corrections and semantic/privacy/doc review; actual parent receipts reconciled in CHECK |

Approval covers unchanged phases 2–3 continuously and targeted corrections; no mandatory panels, extra lifecycle or routine reconfirmation. Planner alone maintains records; roles/statuses never supply approval.

## Required local acceptance (completed after approval; receipts in CHECK)

1. Three synthetic plain-prompt smoke shapes with prose/reasoning/embedded JSON reject; three schema-shaped cases accept: baseline `SYNTHETIC_OK`/actions[], allowed Script_4 jump, explain jump but remain Script_1/actions[]. Never infer actions from prose.
2. Cover strict JSON/schema failures, incomplete/length output, unknown target/skill, multiple actions, invalid caller context, same-target no-op, immutable metadata, preserved text/tag/Unicode bytes and sanitized errors. Exercise real parser logic, not mocks of it; synthetic fixtures only, no private traces.
3. Small protocol fixtures/docs agree with README/caller contracts above: native vs Live event/PCM distinctions, HTTP audio/text/SSE, Tag vs Flash tag handling; focused semantic/reference review, not live-protocol or G0 proof.
4. New focused tests GREEN; prior **35 runtime tests** remain GREEN without changing their file/contract. Confirm silent/offline stdlib import surface, no model/client startup effects.
5. Required commands from repository root with the selected available interpreter: `python -m unittest discover -s live/tests -p "test_mario_reply.py"`; `python -m unittest discover -s live/tests -p "test_mario_runtime.py"`; `python -m py_compile live/sophon_live/mario_reply.py live/tests/test_mario_reply.py`.
Record actual interpreter, exit status/counts/outcomes; required checks cannot be silently skipped. No full-suite/all-profile/GPU/model/voice benchmark required for this offline increment.

## Evidence limits, future branch and boundaries

Prior diagnostic receipts are attributed in CHECK, not new checks or consent. Schema-constrained success motivates validation; JSON recovered from reasoning is never authoritative final output.
**G0 NOT PROVEN**; speech ownership, native turn readiness, heard history, engine cancellation, deployment/model quality and integration activation remain unverified/deferred; offline DONE does not change that.
Future native tests need separately selected native base URL + deployed Tag OR Flash + auth/TLS scope + approved audio fixtures. Missing future resources do not block this offline increment; none requested now.
Prior one-connection TLS verification exception is not a future default/authorization. No Mario/fullv5/remoteconfig re-audit, HF reads or remote/environment inventory.
No implementation/tests/network during planning. Even after approval this scope excludes runtime wiring, real actions, new WS/HTTP clients/tool scripts, uploads, installs/downloads, services/GPU, credential/TLS/config changes and Git lifecycle.
Use the [existing six correction boundaries and seven material categories](../../.claude/workflows/sophon-workflow.md#corrections-and-material-boundaries) by reference; no extra approval chain. Material changes stop affected work with evidence and planner/user reconciliation; preserve partial edits/ownership.
**Next:** no pending v1 local acceptance. Actual native audio or real integration needs separate bounded scope/approval; native endpoint unknown is not an offline blocker. Earlier user-directed synthetic 3.63 s Chinese WAV was external and NOT used here. Q5 B deferred, SkillEngine off, G0 NOT PROVEN. This reconciliation changes only plan/CHECK/CURRENT; no product reads/imports/edits/tests, network or children.
