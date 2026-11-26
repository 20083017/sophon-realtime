# Mario text runtime and isolated development integration

`live/sophon_live/mario_runtime.py` is a stdlib-only, transport-neutral **text**
runtime. Importing it does not import the gateway, Mario or models, start tasks,
or open connections. The gateway remains default OFF. Its explicit isolated-development adapter can
construct this runtime with the real Mario business library; there is no fake
production provider or implicit model/service startup.
Deterministic providers live only in the test files under `live/tests/`.

## Explicit Python injection

From the repository root, the import is `live.sophon_live.mario_runtime` (or
`sophon_live.mario_runtime` when `live/` is already on the caller's import path).
The caller supplies both async callables; the module supplies neither one.
This single-delegation example does not run on import or connect anything.

```python
from live.sophon_live.mario_runtime import (
    BusinessCallable, EventCallback, MarioRuntime,
)

async def one_synthetic_session(
    session_id: str,
    turn_id: str,
    event: dict[str, object],
    business: BusinessCallable,
    emit: EventCallback,
) -> None:
    runtime = MarioRuntime(session_id, business, emit)
    try:
        await runtime.handle(event, turn_id=turn_id)
    finally:
        await runtime.close()
```

Use one runtime per session on one asyncio event loop. Reuse it for that session's
later delegations; concurrent `handle` calls implement replacement, not a queue
of business responses. The caller owns and must await/cancel its `handle` tasks,
and must `await runtime.close()` on disconnect. Do not call lifecycle methods
from the runtime's own business/callback task; this raises a fixed `RuntimeError`
instead of deadlocking. Different runtimes share no registry or lifecycle state.

`business(request)` receives a frozen `MarioRequest` with `session_id`, `turn_id`,
`delegation_id`, monotonic `generation` (first accepted request is 1), and `task`.
Session ID comes from construction, turn ID from the Python argument, delegation
ID/task from the event. Generation is assigned locally, never a public field.
The business callable returns a **nonblank string**, not a Mario result object.
There is no authoritative native turn-commit/readiness signal in this interface.

Synthetic input and exact callback output (no added IDs/timestamps/receipts) are

```json
{"type":"session.delegation.created","offset_ms":0,"delegation":{"id":"item_test","type":"delegation","target":"client","task":"SYNTHETIC_TEST_ONLY"}}
```

```json
{"type":"session.commentary.append","delegation_id":"item_test","content":"SYNTHETIC_TEST_ONLY"}
```

Only consumed fields are validated. `offset_ms` and extra metadata are ignored,
not forwarded. IDs must be nonempty strings without whitespace or ASCII control
characters; task/result must be nonblank strings. Text is preserved, not coerced,
trimmed, normalized or parsed. No provider is called for malformed input.

## Errors and cancellation

- Invalid session ID: fixed `ValueError` at construction; noncallable injections
  or omitted required Python arguments: `TypeError`.
- Malformed event/turn/delegation/task or unusable business result: callback error
  with `invalid_value`; unsupported nonblank event type: `invalid_request_error`.
- Provider exception: exactly `{"type":"error","error":{"code":"server_error","message":"Business callable failed."}}`.
  Messages are fixed/bounded; exception/input contents are not echoed or logged.
- Callback failures propagate to the Python caller without retry, conversion to
  a provider error, or a second event: the callback may already have sent data.
  `CancelledError` is never converted to an error event.

A valid replacement invalidates the old frozen request/generation **before**
cancelling, and awaits its cleanup before starting another provider. A final
identity/generation/closed fence immediately precedes callback handoff; delayed
success/error, even after suppressed cancellation, cannot pass that fence.
Caller cancellation also invalidates then cancels/drains owned work before it
propagates. A superseded caller may get `CancelledError`, or return `None` if its
provider suppressed cancellation; neither outcome certifies delivery.

`close()` invalidates first, cancels/awaits owned work, releases callable/request/
task references and is idempotent. New handles then raise `RuntimeError`.
Cancellation during cleanup propagates after cleanup; cancellation while waiting
to acquire the lifecycle lock has not applied that operation. Callables must
cooperate with cancellation and finish cleanup: there is no forced termination
or hard timeout for arbitrarily uncooperative code. A timeout cancelling a caller
can therefore take longer than its deadline while cooperative cleanup finishes.

Rejected input does not replace valid active work. Its error callback is awaited
directly in the **caller** coroutine, not a new owned background task; the caller
must finish/cancel it even if the runtime closes after that error handoff.

## What this does not prove

A generated result is not callback handoff; handoff/completion is not transport
**sent**, and sent is not **played**. Once handed off, an event cannot be retracted
by this runtime. No fake receipts/history are produced. Existing gateway
`session.commentary.appended` is not a playback acknowledgment; an unknown
commentary delegation ID can currently acknowledge/no-op. See
[`sophon_live/gateway.py`](sophon_live/gateway.py) and [`README.md`](README.md).
Commentary is tool-result context which the model rephrases, **not exact speech**,
an exclusive output gate or native turn authority. These tests use callbacks,
not gateway dispatch, a live socket, audio or actual playback.

The standalone runtime still treats arbitrary JSON strings as opaque text; its
inert test provider does not apply actions or certify model results. Only the
explicit isolated adapter below adds real model transport, strict validation,
Mario prompt/state authority and validated internal script jumps. Neither path
initializes Skill Engine, Mario TTS, `/ws/mario`, BackOffice or robot/cloud tools.
No UID-priority or heard-history timing claims are made here.

## Strict completed-reply boundary

[`sophon_live/mario_reply.py`](sophon_live/mario_reply.py) adds the pure,
stdlib-only `parse_mario_reply` function. It does not change `MarioRuntime` or
construct a model client. The caller supplies completed content, its actual
`finish_reason`, allowed script IDs and the current script. API envelopes, SSE
chunks, reasoning prose, Markdown fences and recovered JSON fragments are not
accepted. Only `finish_reason="stop"` is supported; parseable `length` output is
still rejected. Never manufacture a completion reason to make validation pass.

This initial bounded contract requires exactly `response` (nonblank string)
and `actions` (zero or one item). It rejects duplicate keys at every depth,
nonfinite constants, extra fields, invalid Unicode and malformed/truncated JSON.
The sole action form is `{"skill":"script_jump","params":{"target_script":"..."}}`,
with its target in the caller-provided IDs. Unknown/external actions reject while
Skill Engine is excluded; they are not silently reported successful. Action-only
or multi-action replies are outside this version, not repaired or executed.

Results are frozen `MarioReply` / `ScriptJump` metadata. Each jump records
`source_script`, `target_script`, and `is_noop` for a same-script target. No state
changes, compression, dispatch or success receipt occurs, even when generated
response text claims a transition happened. Mario retains future state authority.
Errors are fixed `MarioReplyError` messages without raw payload or decoder details.
Text, sound tags, whitespace and Unicode bytes are preserved without normalization.

An inert synthetic callable can explicitly validate before returning text to the
unchanged runtime; it is not an installed provider or a real inference wrapper:

```python
from live.sophon_live.mario_reply import parse_mario_reply

async def synthetic_validated_business(request):
    reply = parse_mario_reply(
        '{"response":"SYNTHETIC_OK","actions":[]}',
        finish_reason="stop",
        allowed_scripts={"Script_1", "Script_4"},
        current_script="Script_1",
    )
    return reply.response
```

Only validated response text is returned here; real handling of action metadata
is performed only by the explicit isolated development integration below. A parser failure propagates to
the existing runtime's fixed provider-error envelope, never commentary success.
Validation does not prove semantic correctness, action application or playback.

## Protocol fixture boundaries

The new tests contain inert fixtures, not new transport implementations:

| Surface | Request/event shape | Audio distinction |
| --- | --- | --- |
| Native Tag/Flash Realtime | `session.update`, `input_audio_buffer.append` | Existing adapter sends base64 `pcm_f32le` at 16000 Hz |
| Live GPT gateway | `session.start`, `session.input_audio.append` | PCM16; 16000 Hz in these fixtures |
| Native HTTP | `POST /v1/chat/completions`, `modalities:["text","audio"]`, user `input_audio` plus the audio marker | Base64 WAV input; SSE audio chunks are WAV at 24000 Hz |

See [Tag API notes](../tag/README.md#api-notes), [Flash API](../flash/README.md#api),
[`adapters.py`](sophon_live/adapters.py), and the existing profile
[`client_example.py`](../tag/client_example.py) for the grounded shapes. The HTTP
client loads its profile's `config/system_prompt.json` and includes the text
marker `<|audio|>` in user content. It performs requests and
writes audio at module level, so do not import it or use `--help` as offline
validation. Tag documents stripped sound tags in HTTP text; Flash retains them.
The reply parser preserves whichever text it receives, rather than stripping tags.

Transport envelopes/SSE are rejected as Mario reply content. Fixtures distinguish
formats but do not prove either native backend, endpoint aliases, deployment or
full duplex. Native live tests still require an explicitly selected native base
URL/backend, scoped authentication/TLS handling and authorized audio input.
No private endpoint is derived from the Live URL, and no previous TLS exception
is made a default. No model, audio, Skill Engine or service request runs here.

## Offline checks

From the repository root, using the available local Python without extra packages

```sh
python -m unittest discover -s live/tests -p 'test_mario_runtime.py'
python -m unittest discover -s live/tests -p 'test_mario_reply.py'
python -m py_compile live/sophon_live/mario_runtime.py live/tests/test_mario_runtime.py
python -m py_compile live/sophon_live/mario_reply.py live/tests/test_mario_reply.py
```

The code uses Python >=3.10 syntax/APIs (current plugin installers select 3.12).
Local Windows Python 3.14 checks do not prove Python 3.12, Linux/GPU behavior,
model quality, integration, activation or latency. **G0 remains NOT PROVEN**;
the isolated integration below does not establish native audio or deployment.


## Isolated Mario development adapter (default OFF)

`mario_bridge.py` explicitly loads a regular `mario_business` package from the
external bound development root using an importlib package spec, rejects package
collisions, and never modifies `sys.path`. The isolated library reuses Mario's
prompt builders, two-script loader, decision/jump/follow-up loop, SessionState,
SessionManager and short-history Luigi summary policy. It requires a strict
validator, explicit assets/store/log paths and an owned model client. Imports
create no database, log directory, client or task. Only Script_1 and Script_4
are loadable; immutable templates are not rewritten to remove other references.
External skill routes are denied before registry lookup or lazy client imports.
Normal observe and long/global model compression are explicitly deferred; their
buffers are retained, not silently summarized by another unbudgeted model.

The server-only switch is `SOPHON_LIVE_MARIO=1`, with an absolute
`SOPHON_LIVE_MARIO_CONFIG` pointing to the existing **external** companion JSON.
Do not put endpoints, credentials or machine bindings in source. The adapter
checks its `development_integration` roots, ownership receipt, source manifest,
immutable asset hashes, TLS verification and unchanged shared model limits.
Missing/unsafe bindings or a missing real factory fail closed. Programmatic
in-memory callers explicitly open `MarioFactory`, inject its `DevBindings` and
factory into LiveSession arguments, and await session/factory close. Tests use
only HTTP transport/native engine/WebSocket resources as mocks, not business
logic. The five unchanged support modules are required for actual gateway imports.
This section documents wiring, **not authorization to run a listening gateway**.

A unique synthetic UID per LiveSession lives in one library SessionManager;
there is no production-user mapping or cold load of existing histories. One UID
is serialized. A complete reply and its **actual** finish_reason are validated
inside the reused loop before new input/history, jumps or summaries commit.
Each validated round increments the factual state revision. No-action and a
same-target jump settle immediately; a real jump runs a bounded follow-up.
All validated segments survive in order, joined by exactly `"\n\n"`, including
both jump-opening and follow-up text. History is **generated/business, not
heard, delivered or played back**. A later-round failure/cancellation retains
prior validated state; the library exposes its actual revision/segments and
failed/cancelled outcome rather than pretending a rollback or full success.

The completed-result client requests strict JSON schema, <=1536 output tokens,
a 30-second deadline and no automatic retry. A process-locked durable ledger
under the bound reports root reserves each of at most six shared requests
**before dispatch**; failed/reserved attempts still count after process reruns.
Internal jump/follow-up rounds use that same ledger. Per-test resettable fixture
budgets are allowed only with an actual HTTP MockTransport, never real traffic.

Live delegation event shapes stay unchanged. An internal async driver owns
Mario work without blocking audio. Competing client commentary/thinking is
rejected only for internally owned delegations. Generation and state-revision
fences apply at commit, callback and queued commentary consumption. Replacement,
barge-in, engine cancellation and disconnect invalidate before cancellation;
owned drivers, provider work, timers, persistence I/O and clients are drained or
closed. A cancellation-suppressing provider cannot commit stale work. Cleanup
waits for owned work rather than claiming it can forcibly terminate arbitrary
Python providers or retract native audio already released.

### Additional offline verification

Use the approved isolated Linux Python 3.12 environment with actual Live
httpx/numpy/aiohttp/websockets requirements, not a universal toolchain. Set
`MARIO_TEST_BINDINGS` to the external companion JSON **content** and
`MARIO_TEST_RUNTIME` to the bound owned fixture directory, without printing
private bindings. From the transferred Sophon source root run

```sh
python -m unittest live.tests.test_mario_integration
python -m unittest discover -s "$MARIO_LIBRARY_ROOT/tests" -p test_business_library.py
python -m py_compile live/sophon_live/gateway.py live/sophon_live/mario_bridge.py live/sophon_live/mario_runtime.py
```

The original stdlib parser/runtime commands above remain offline regressions.
A real-model verification must separately reserve the same durable budget and
use the actual library/bridge with an in-memory LiveSession and mocked native
engine; never run `main`, launchers, ASR, audio or a native engine to test it.
The six-request limit is not multiplied by the three-round decision limit.
G0/exclusive speech, semantic native turn readiness, audible history, deployment
activation, model quality and full-duplex performance remain unproven here.
