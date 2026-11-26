# Sophon × Mario — T0-A embedded-business feasibility/design plan

| Field | Value |
| --- | --- |
| ID / version | `2026-11-24-sophon-mario-t0-a` / `v2` |
| State | `DONE` |
| Planner / records owner | `sophon-plan` in the primary planning context |
| Requested milestone | T0-A feasibility/design only; not runtime implementation or the complete T0–T2 proposal |
| Specification | `../todo/Sophon_Mario_Harness_Integration_Plan_v5_T0-T2.md`; prior full read retained, narrowed by actual interview decisions below |
| Canonical execution ledger | `../check/2026-11-24-sophon-mario-t0-a-CHECK.md` |
| Prior independent plan | `2026-11-24-claude-python-workflow-upgrade` / `v2`, already `DONE`; retained unchanged |

## 1. Authorization, interview decisions and objective

**v2 read-only A1–A3 is approved; actual user quote/scope and state transitions are recorded in CHECK. v1 was not approved.** Earlier requests to start according to v5 and supplied endpoints do not approve a generated plan. Actual interview decisions:

- **“Q1 A, Q2 A”** selects one business-conversation path, integration only, preserving Mario scripts, prompts, state and tool authority. No native-chat switching, T1 or T2 now.
- The user subsequently rejected using Mario WebSocket for the new path because Sophon supplies realtime transport. This supersedes Q3; it does **not** approve a particular source hook.
- **“Q4 A”** prefers in-process embedding **conditional on dependency, session and lifetime compatibility**. This is an architectural preference, not v2 approval or authority to modify/run services.

**Target:** Sophon client WS → direct async Mario business interface → Sophon speech. Preserve legacy Mario `/ws/mario` compatibility for existing consumers; introduce no second realtime transport or mandatory Mario WS bridge. The internal async generator is a candidate reuse seam, not a proven embeddable API.

Approval of **v2** would authorize only bounded read-only **embedded-Mario compatibility/source preflight**, feasibility/design analysis and these record updates, including necessary read-only SSH through existing validated session configuration. It would **not** authorize tests, product imports/execution, HTTP/WS/model requests, source edits, installs, downloads, uploads or service actions. Unchanged approved A1–A3 would proceed continuously without routine phase-by-phase approval.

Objective: reuse completed planning discovery, resolve only integration-critical dependency/session/resource/control questions, and deliver a G0 disposition plus a precise bounded experiment proposal if needed. **No runtime source implementation before the original G0.** Static preflight completion is not G0/runtime success or authority to enter T0-B.

**Non-goals:** replace Mario core with Sophon BackOffice; alter Mario scripts/prompts/state/tool semantics; copy the Mario repository into Sophon; blindly import `app.py` or add a global `sys.path` workaround; native-chat return/T1/T2; training/LoRA/data collection; development-harness changes; real tool/vehicle actions. No `duplex.py`/vLLM-Omni edits, Git lifecycle or cleanup.

## 2. Profiles, resources and completed planning evidence

- **Primary profile:** Live gateway (`live/sophon_live/`, `live/`). **Conditional backend:** exactly deployed Tag **or** Flash, selected by provenance. E2E/native engine are not selected; no universal environment or GPU requirement.
- Local checkout: `D:/project/sophon-realtime`, recorded HEAD `e187202824738290d76dde27adb748fe3c14da6e`, branch `refactor/python-workflow-upgrade`. Prior read-only status identified pre-existing untracked `.claude/`, `.worktree-policy.yaml`, `AGENTS.md`, `CLAUDE.md`, `doc/`. Preserve all; no product partial edits were made by this planning task.
- Tag/Flash metadata: plugin `1.6.2`, Python `>=3.10`, `duplexjev-vllm>=0.3.0`; normal installers select Python **3.12**, vLLM/vLLM-Omni **0.30.0**, duplexjev-vllm **0.3.0**. These are CODE-CONFIRMED source contracts, not installed/runtime versions. `live/start_live.sh:9-16` can stop/start a gateway; never execute it for discovery.
- Parent completed bounded read-only SSH planning discovery through the existing helper: configured alias identity, strict host-key checks, no forwarding/multiplexing and selected-root resolution checked. Configured remote Mario root exists and resolves to the user-selected path; Mario is a **subdirectory of an enclosing Git checkout**, at revision `e195c93f83330b192d18b36fcad4fd907b905809`. Selected source root need not equal Git toplevel. Worktree cleanliness/deployed alignment remain unverified. Keep private roots/endpoints outside records.
- Mario `src/requirements.txt`: `fastapi>=0.100.0`, `uvicorn[standard]>=0.23.0`, `httpx>=0.24.0`, `websockets>=11.0.0`. No hard version conflict is proven; broad bounds do **not** prove a compatible combined installation. Local tooling was Windows Python 3.14; the remote read-only reader was system Python 3.6. Neither proves a product environment.
- Missing old HTML/ZIP snapshots are not a reason to rediscover everything. Current selected source is authoritative; request snapshots only for a concrete discrepancy. Endpoint availability remains user-reported, not probed.

### Sophon CODE-CONFIRMED anchors — completed read-only planning discovery

| Finding | Source / implication |
| --- | --- |
| Internal automatic response enabled | `live/sophon_live/adapters.py:40-46` sets `extra_body.auto_response=True`; no proven public suppression control follows from this field. |
| Public cancellation is a no-op | `realtime.py:324-345`: `response.cancel` is `pass`; truncate acknowledges without an engine call; ordinary response creation does not independently force an answer absent pending tool output. |
| Exact-speech source route exists | `realtime.py:350-368` → `adapters.py:77-84` → selected plugin `bridge.py` `/say` → `duplex.py` queue. Not proof of exclusivity, audible completion or deployed support. |
| No proved pre-release business-turn gate | `realtime.py:650-674` forwards engine audio; `gateway.py:473-506` queues it. `gateway.py:441-469,477-484,512-525` starts ASR at output/delegation onset, possibly too late for business routing. Existing close/task handling is at `gateway.py:595ff`, not proof of a new gate. |
| VAD/transport are not semantic/heard evidence | `realtime.py:406-415,454-481` VAD/commit precedes async ASR; `gateway.py:535-579` uses send-clock/playback estimates, not proved playback ack. |
| Protocols and backend authority differ | GPT-Live rejects `session.update` (`gateway.py:263-268`); Realtime supports it (`realtime.py:218-268`). `backend.py` BackOffice is a separate model-tool loop with its own prompts, not Mario business authority. |
| Existing test/startup are resource-facing | `live/live_test.py:16-66` is live WS inference, not an offline test/auth contract. `gateway.py:607-619` initializes/warms ASR; `backend.py:20-38` selects a model service. No discovery imports/launches. |

### Mario CODE-CONFIRMED anchors — parent read-only source discovery

Paths below are relative to the configured Mario root; no product modules were imported/executed.

| Finding | Source / integration consequence |
| --- | --- |
| Legacy WS is input-only | `src/app.py:86-94,128-135` queues `user_id/session_id` input; outputs go to Skill Engine, not reply WS. Preserve compatibility, do not build the new reply path on this route. |
| Application is not an import-safe library | `src/app.py:10,23-32,58,62-72` mutates `sys.path`, configures global logging, creates a static directory, loads scripts and starts global LLM/Luigi/TTS/Skill Engine. Do not import the application as the embedding API. |
| Sessions/tasks are globally coupled | `src/mario_session.py:28-30,33-84` has global user/reverse registries and async lock; same uid/new session replaces tasks while sharing SessionState. Constructor starts a worker (`656-667`); close cancels/awaits owned tasks (`818-842`). Identity/loop/cleanup ownership needs explicit design. |
| Existing output/history are not heard evidence | `src/mario_session.py:860-1017` streams through its own TTS/Skill Engine and commits generated/partial text. No-TTS (`938-955`) accumulates text but exposes no WS output. Disabling TTS is not a business-response API. |
| Promising internal async seam, not proven API | `src/observer.py:36-49` defines `run_mario_loop_streaming(session,user_input,t0)`; `66-78` emits deltas before complete JSON/actions parsing. Buffer/suppress provisional output; do not call it final/heard. |
| State/tools/history precede playback | `src/observer.py:99-107` script-jump mutates state/submits compression; `158-174` yields skill events/result queue and awaits results; `223-243` commits intermediate assistant/tool history. A final-output hook alone does not solve history or tool/result ownership. |
| Core client deployment is unknown | `src/llm/llm_client.py:11-33,181-197` provides an OpenAI-compatible `httpx` async client with global init/get. Model/auth/path and relation to the supplied endpoint are unverified. Do not substitute stateless Sophon BackOffice. |
| Persistence/assets need isolated resources | `src/state/persistence.py:25-28,41-44,52-57,134` uses source-relative default DB, constructor initialization, directory/schema creation and module singleton. `src/state/session_state.py:319-321` lazily imports the store on state creation; `src/scripts/loader.py:24-31` roots assets relative to source. Never use production DB/histories for feasibility work. |

**Compatibility verdict — PARTIAL / conditional:** direct async reuse is promising, but import/dependency/session/lifetime compatibility and exclusive speech/heard-history control remain unproven; no hard dependency conflict is established. Parent source-identity/access checks are CHECK-CONFIRMED, code facts are CODE-CONFIRMED, deployed/runtime alignment and G0 are **NOT PROVEN**.

## 3. C-level decisions and remaining questions

The future integration changes subsystem ownership (**C**); v2 changes no product contract. User choices settle business-only routing, Mario authority and Sophon realtime transport. Do not reopen native mode or redundant WS bridges.

1. **Embedding boundary:** prefer in-process only if an import-safe business boundary reuses Mario orchestration without app bootstrap/global path mutation or replacing prompts/tools. The observer generator is a candidate, not a user-approved hook/API. If incompatible, return direct evidence and the smallest alternative decision; do not silently choose a sidecar/second transport.
2. **Dependency/resource/lifetime:** resolve Python 3.12/selected-profile constraints, initialization order, global clients/registries/lock, uid/session replacement, worker cancellation and isolated DB/asset paths. Do not install or instantiate to answer static questions.
3. **Business result/tool/history:** separate provisional deltas, settled JSON/actions, tool events/results, generated/intermediate history and heard speech. Specify needed request/result/cancel/commit semantics while retaining Mario authority. Output buffering alone does not prove correct history.
4. **Sophon control:** identify an evidenced pre-release business-input/exclusive-speech point preserving native listening/turn/backchannel/barge-in behavior and late-result isolation. ASR ordering and engine heard-history remain gaps; a final-output hook/proxy mute is not a solution by itself.

No native-chat return is required now. Original G0 speech/control/history acceptance is not weakened by static preflight.

## 4. Narrow read-only scope and ownership

**Single A1–A3 owner:** current primary planner/executor; `sophon-plan` alone writes plan/check/CURRENT. No children or duplicate discovery. Product/reference sources have **no implementation writer** in v2. Completed planning discovery is evidence, not approved execution phases.

| Scope | Only unresolved read-only questions |
| --- | --- |
| Identity/profile | Reconcile known revisions/root identity and missing nonsecret deployed Tag **or** Flash provenance. Do not require source-root/Git-root equality, a clean tree or repeat the completed route discovery. |
| Embedded Mario | Necessary bounded ranges/direct callers of `src/{app,mario_session,observer}.py`, `src/llm/llm_client.py`, `src/state/{persistence,session_state}.py`, `src/scripts/loader.py`, requirements/install metadata. Resolve import graph, globals, DB/assets, tasks and result/tool/history contract; follow only evidenced references. No full scripts/prompts sweep. |
| Sophon control | Necessary caller/config ranges in Live gateway/realtime/adapters/backend and selected installer/plugin contract. Only evidenced pre-release/say/history/cancel questions; no broad engine/site-packages audit, logs or model imports. |
| Future implementation boundary | A future implementation proposal must specify the **writable Mario working-copy root and exact file scope before any modification**. Current configured Mario root remains reference-only. No full repository copy into Sophon or presumed authority over another checkout. |

Necessary remote reads use `mario-reference`/`sophon-server-session`, validated configured identity, strict host-key checks, noninteractive auth, no forwarding/multiplexing, configured connect timeout and command timeout capped at 120 s. Resolve reads inside the selected root; no fallback/permission bypass/endpoint probes. Exclude secrets, private audio/histories and production DB contents.

## 5. Execution phases — approved v2 read-only A1–A3 completed

### A1 — Embedded compatibility/source preflight

**Owner:** same audit owner. **Inputs:** actual v2 approval, completed planning evidence, Live plus conditional Tag/Flash contracts. Reconcile only missing identity/provenance and unresolved import/dependency/resource/session/lifetime questions in §4. No imports, installs, tests or product execution.

**Acceptance A1:** compact compatibility disposition in the matching check: supported static facts, exact constraints/unknowns, isolated resource/lifecycle requirements and any concrete incompatibility. Broad dependency bounds do not establish installation success.

### A2 — Direct business-interface and control disposition

**Owner:** same audit owner; sources remain read-only. Specify proposed async request/result/tool/cancel/history boundary retaining Mario scripts/prompts/state/tool authority and legacy WS compatibility. Map only integration-critical evidence: turn readiness, provisional/settled result, skill result ownership, session/task isolation, exclusive Sophon speech and generated/sent/heard history. Cite anchors or precise gaps in this check, not another report.

**Acceptance A2:** supported candidate interface/control point or precise unresolved decision; explicit source disposition against original G0 H1–H5. Internal generator != proven embeddable API; suppressed output != correct history. No source implementation before G0.

### A3 — G0 disposition and precise bounded experiment proposal

**Owner:** same audit owner. Return conditional embedding verdict, G0 disposition and only the smallest necessary next experiment specification, or direct evidence that the approach cannot meet original G0. Specify actual protocol/control point, nonproduction identities, authorized ephemeral probe scope, isolated resources, fixtures, limits, observations, fail-closed stop/cleanup and remaining authorization. No experiment/probe run or written by v2.

**Acceptance A3:** narrow source-preflight/design package, concrete remaining questions and bounded experiment proposal. Required static evidence may complete T0-A preflight with **G0 NOT PROVEN**, never G0 itself. Missing required evidence stays pending or becomes a proven canonical material blocker. No T0-B/T1/T2/runtime success claim.

## 6. Original G0 hypotheses and bounded experiment basis

| ID | Hypothesis / decisive evidence |
| --- | --- |
| H1 | Verified business-turn input reaches Mario before autonomous Sophon audio release; requires demonstrated control, not prompt obedience. |
| H2 | Listening/native semantic turn/backchannel/barge-in behavior remains active while Mario work is pending; no replacement turn detector. |
| H3 | Exactly one approved result is spoken with attributable session/response/turn/generation IDs; queue acceptance alone is insufficient. No competing/stale audio. |
| H4 | Cancel/disconnect/late work fails closed; public ack/proxy mute/tool acceptance/truncation alone does not prove engine cancellation. |
| H5 | Interrupted/held/dropped speech creates no incorrect heard-history commits; generated/sent/estimated-played/client-acknowledged states stay distinct on both sides. |
| H6 — out of scope | Native-chat return/switching is excluded by Q1/Q2 and is not v2 acceptance. No T1/T2 work now. |

**Experiment proposal basis — NOT AUTHORIZED BY v2:** A3 must bind any proposal to the actual source-selected control/interface. No generic probes/invented hooks. If G0-critical control requires product edits, report that boundary rather than implementing before original G0. Separately authorized ephemeral clients/stubs do not permit runtime source/reference edits.

Reuse the existing small discriminator budget only if it answers the unresolved G0 question: dedicated nonproduction existing service, at most **four sessions × 60 s** (four minutes total), max two concurrent, 10 s connection/30 s response bounds, no automatic retries beyond budget. Approved short fixtures cover business completion, interruption/continuation, unfinished/backchannel and paired-session late-result isolation; controlled 1 s business-stub delay/fixed speech marker, no real Mario model/tool/vehicle actions. Confirm protocol/auth/source build and fixture rights before separately approved requests; never infer another endpoint. Any embedding-specific experiment proposal must name an import-safe seam and isolated DB/asset/client/task resources, never `app.py` bootstrap or production histories.

Observe ASR/pre-release order, approved-result-only speech, IDs, cancellation/late work and history provenance. Stop on unexpected speech/session crossing, identity/auth failure or safety uncertainty. Keep one bounded redacted event timeline, authorized audio only; close only owned sessions, no restart/install/upload. Transmission is not audibility: missing playback/history evidence leaves H3/H5 partial. This discriminator is **not full G0**; remaining original G0 cases remain required before T0-B implementation.

## 7. Acceptance, corrections and canonical handoff

Required acceptance is the narrow T0-A **embedded compatibility/source-preflight and design decision package**: A1–A3 dispositions, supported interface/control evidence or exact gaps, original G0 disposition, bounded experiment specification and no unauthorized side effects. Completed planning discovery is not approved phase execution. For records-only changes use content/reference/ID consistency review, not tests. Runtime/quality/latency/GPU remain unverified.

Use `.claude/workflows/sophon-workflow.md`, **Corrections and material boundaries**. Its six correction boundaries remain **current approved phase, files/resources, scope/acceptance, safety boundary, no new high-risk operation, targeted correction**. In-scope corrections continue without a retry quota; do not weaken acceptance.

The same seven material categories govern BLOCKED: (1) changed scope/acceptance; (2) changed safety boundary; (3) unapproved file/resource modification; (4) new high-risk operation; (5) disproved foundational architecture/infrastructure assumption; (6) possible data/environment damage; (7) approved approach cannot reasonably meet acceptance within correction boundaries. Record category, direct evidence, consequence, smallest correction, owner and next action; stop affected work safely. Missing required evidence can become category 7 after bounded approved access is exhausted, not from an agent label. Optional unrun experiments/tools alone do not block source preflight; agent labels are not consent.

Canonical handoff is this plan plus its check, not CURRENT alone. Include ID/version, **actual approval evidence**, phase/step, single owner, exact roots/files, Live plus selected backend profile, source identities, acceptance, timeouts, six correction boundaries, seven material stops and next action. Mario access uses `mario-reference`; no child delegation, second ledger or new gates.

## 8. Confirmation checkpoint and execution status

**Execution status: DONE — unchanged read-only v2 A1–A3 completed; actual approval, required acceptance checks, source findings and G0 NOT PROVEN disposition are recorded in CHECK. No implementation/testing/live authority follows.**

Historical checkpoint: v1/v2 were awaiting confirmation when presented. Actual v2 approval is now recorded in CHECK. Originally suggested wording (not the approval evidence): **“Approve `2026-11-24-sophon-mario-t0-a` v2 for read-only embedded-Mario compatibility/source preflight and the G0 decision/experiment proposal only; no tests, product imports/execution, source edits, endpoint requests or service actions.”**

Configured reference-root selection is already established; do not ask the user to repeat private roots/endpoints. Missing deployment/protocol/resource facts remain explicit. Actual approval is saved before A1; unchanged A1–A3 continue continuously. Runtime experiments/future implementation require their exact presented authorized scope, preserving original G0 and specifying a writable Mario working-copy scope before any modification.
