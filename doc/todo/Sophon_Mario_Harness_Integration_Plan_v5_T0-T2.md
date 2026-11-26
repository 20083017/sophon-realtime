# Sophon-Realtime × Mario/Luigi Harness — Implementation Plan v5 (T0–T2)

**Type:** CLI-ready, source-grounded, stage-gated architecture and development specification  
**Date:** 2026-11-24  
**Supersedes:** `Sophon_Mario_Harness_Integration_Plan_v4.md`; preserves the native model/evidence, session and safety design but changes active execution to **T0, T1 and T2**  
**Reader:** Claude Code / engineering CLI agent  
**Source basis:** user-uploaded `Mario.zip`, `Sophon-Realtime项目技术文档.html`, and current official Sophon `finetune/README.md`/`CHANGELOG.md` (source claims require revalidation against installed commits).

> **Execution instruction:** Start with the **T0-A read-only source audit**, then develop the minimal T0 runtime integration only if G0 is proven. Progress to T1 only after G1, and T2 only after G2 plus data/rights/GPU readiness. T2 may train a new **candidate reply LoRA**, but must not overwrite the original adapter or deploy to production without approval. **T3 RSI and T4 RL/MOPD are deferred.**

## Executive decision — active T0–T2 track

| Stage | What will change | What stays unchanged | Evidence for completion |
|---|---|---|---|
| **T0** | Minimal Sophon↔Mario bridge, speech arbiter, event correlation, exact-audio baseline | Mario scripts and state; Sophon turn model; weights | Source-based G0 + passing G1 replay/voice tests |
| **T1** | Feature-flagged Mario prompt/evidence & guarded voice policy, optional native Script_0 chat | Mario script authority; original models | Controlled matched A/B + G2 |
| **T2** | Mario-supervised speech/tool dataset and **Sophon Thinker Tag reply-LoRA candidate** | Mario executable Harness; audio encoder, talker, DuplexJev turn-taking | Data/rights/readiness; training logs; sealed evaluation + G3 |
| **T3 / T4** | **Not developed** (RSI / GRPO / MOPD / MoE research) | — | Backlog only |

**Hard constraints:** Minimal source changes, protected legacy entry points, one speech owner per turn, no fabricated audio/vision readouts, no NLU11/proprietary car-model/physical vehicle integration, and no automatic training/deployment. This plan describes intended work, **not evidence that the integration or training has been run**.

---

## 0. Product decision — active development T0–T2

We are building **Sophon-Native Mario Harness**, a realtime, scenario-aware customer-experience assistant.

- **Sophon-Realtime is the continuously active realtime interaction runtime**, not a terminal TTS microservice. Preserve its raw-audio listening, model-based turn-taking, paralinguistic perception, speculative drafting where safe, barge-in, backchannel/early-response recovery, speech realization and playback-aware conversation history.
- **Mario is the application Harness and business/scenario authority**, not a replacement speech model. Preserve its `Script_0`–`Script_10` system, global rules, prompt composition, LLM/tool planning loop, `script_jump`, `SessionState`, skills and guarded scenario transitions.
- **Luigi** is an asynchronous advisor and summarizer, not the synchronous owner of speech, scenario transitions or physical actions.
- **Our car-specialized models** will be registered as optional application tools in a **later, explicitly authorized phase**. Design one neutral adapter/contract now; do **not** load, integrate or retrain NLU11/Qwen 0.6B/4B or a vehicle executor during the T0 baseline. The initial objective is improved Mario scenarios through Sophon model-derived **interaction evidence** and natural speech, with a strict distinction between exposed events and hypothetical model outputs.

**One-sentence architecture:** Sophon listens and speaks continuously; Mario plans the business interaction and owns the state; a minimal bridge/arbiter safely joins them so that Sophon can **natively converse** on permitted turns and **naturally speak Mario-grounded content** on guided turns.

### What v5 retains and changes

**v5 decision:** T0 and T1 are no-training development stages; **T2 is now in development scope**, but its training run is conditional on T0/T1 gates, approved audio/trajectory data, reproducible model/adapters, license and compute readiness. T3 automated recursive self-improvement (RSI) and T4 GRPO/distillation research are **not in the current implementation scope**. LoRA never imports executable Harness logic or modifies Sophon's native turn-taking.

| Earlier plan | v5 T0–T2 decision |
|---|---|
| Sophon primarily receives Mario-final text via `say` | `say` remains the safety baseline, **not the sole output strategy**; explicitly test natural/grounded Sophon generation and native chit-chat |
| All scripts, including `Script_0`, remain Mario-generated during first pilot | Preserve that baseline; add a **later, gated** Sophon-native `Script_0` experimental lane with Mario re-entry guard and state continuity |
| Sophon audio events enrich Mario prompt | Define a **model-to-model evidence contract**: ASR text, event/turn data, played speech, optional typed audio decisions and optional delegation proposals, each with source/confidence/provenance |
| Model value seemed limited to speech I/O | Map the **ASR, DuplexJev perception, stage-0 Thinker, Tag/Flash/E2E speech models** explicitly to Mario inputs/outputs; distinguish built-in vs optional/external interfaces |
| One generic bridge | Preserve **Turn/Response Arbiter**, versioned event contracts, prompt boundary, speech policy and a bounded two-control-loop design |
| Specialized car models entirely out of design | Define a **future ModelToolAdapter** interface without implementing the models now |

### Non-negotiable scope

**Active now, in sequence:** **T0** source/protocol feasibility + minimal Sophon/Mario bridge and baseline; **T1** bounded Mario Prompt/tool policies + controlled native Sophon interaction experiments; **T2** dataset curation, continued Sophon Tag Thinker reply-LoRA with ms-swift, and matched shadow evaluation against frozen T1. The scope is development and evaluation, **not automatic production rollout**.

**Not in T0–T2:** NLU11 execution; proprietary 0.6B/4B car-specialist tools; physical vehicle-control DM/CAN; new multimodal encoders; modifying Sophon's DuplexJev turn model; new MoE experts; GRPO/MOPD; **T3 automated self-improvement/recursive retraining**; production model replacement; rewriting Mario's scripts/state machine; automatically enabling Luigi or visual ingestion; modifying `duplex.py`/vLLM-Omni unless an explicit, reviewed feasibility blocker requires it. Sophon's own ASR and Thinker remain in scope as parts of the Sophon runtime.

**Order and authority:** T0→T1→T2 is sequential. Verify actual repositories and the reply-ownership gate before source changes; use small isolated branches and reversible flags. A source-grounded implementation can proceed within the user's requested T0–T2 project scope after the corresponding gate passes. **T2 GPU jobs, model downloads and use of recordings require demonstrated authorization and resource/data readiness; otherwise stop at a reproducible dry run with precise blockers.**

**Default operational rule:** avoid unrelated modifications; preserve existing Git refs and uncommitted changes; only add small adapters, test fixtures and feature-flag hooks.

---

## 1. Source baseline and evidence hierarchy

### 1.1 Supplied local evidence

1. **`Sophon-Realtime项目技术文档.html`** — user-provided offline technical analysis, dated 2026-11-20. Relevant sections:
   - §3 architecture (Live gateway / vLLM-Omni / `plugin/sophon_realtime/duplex.py` / stage 0 / speech stages)
   - §§4–5 four-way turn decisions, speculative drafts, barge-in and played-history truncation
   - §§6–7 audio-first history, `merge & abort`, `BC_RESUME`, new turn recovery
   - §9 two realtime protocols and internal check channel
   - §11 Tag/Flash/E2E build/config/deployment differences
   - §12 training is **optional**, not required for runtime tool delegation
   - §§14–16 paralinguistics, native audio readout, reusable engineering principles.
2. **`Mario.zip`** — user-uploaded Mario source snapshot (source must be checked against CLI checkout).
3. **`Sophon_Mario_Integration_CLI_Plan.md`** — previous v1 integration plan; retain all T0/G0 response-control safety gates unless verified source contradicts them.

Treat the HTML's timings, thresholds, APIs, installed versions and benchmark scores as **reported properties of the snapshot**, not proof of the CLI machine's runtime behavior. Model-based turn confidence and acoustic features may exist internally without being surfaced by the public gateway.

### 1.2 Upstream validation references (check current commit, not assumed runtime)

- https://github.com/adventists-ai/sophon-realtime
- https://github.com/adventists-ai/sophon-realtime/blob/main/live/README.md
- https://github.com/adventists-ai/sophon-realtime/blob/main/CHANGELOG.md
- https://github.com/adventists-ai/sophon-realtime/blob/main/live/sophon_live/realtime.py
- https://github.com/adventists-ai/sophon-realtime/blob/main/live/sophon_live/gateway.py
- https://github.com/adventists-ai/duplexjev

**As of the source review on 2026-11-24**, the upstream changelog lists **v1.6.2 (2026-11-23)**: `say` long-output/first-turn fixes and preservation of actually spoken text for interrupted `say`. v1.6.1 refined queuing/interruptibility; v1.6.0 introduced `response.create` with `response.say` and repaired certain mid-call `session.update` behavior. **The CLI must identify the deployed source/plugin/gateway versions rather than assume any release has been installed.** The changelog says PyPI could differ from the repo/plugin version; record the full commit and installation provenance.

At the upstream source inspected on 2026-11-24, `live/sophon_live/realtime.py` handles `response.cancel` as `pass`. This is **not reliable engine-side cancellation**. The code also says a normal `response.create` without `say` is not itself proof the engine will be forced to answer independently of its own turn detection. Verify exact target source.

### 1.3 Mario CODE-OBSERVED snapshot anchors (verify against actual checkout)

| Existing code | Observed meaning | Integration consequence |
|---|---|---|
| `src/mario_session.py` `_dispatch` | `chat` / `audio` / wakeup / `stop` / `try_sit`; `payload.query` carries ASR **text**; some `action/expression` NLU bypasses Mario LLM | Do not substitute raw audio for this field or mutate legacy non-chat branches in T0 |
| `src/mario_session.py` `_handle_chat`, `_stream_and_commit` | Has its own task cancellation, per-session queue, TTS and Skill Engine audio forwarder; `delivered_text` tracks submitted/generated text | Avoid two speech owners; don't assume forwarded text was actually played |
| `src/observer.py` `run_mario_loop_streaming` | Streams JSON `response` characters **before** parsing final JSON `actions`; then may `script_jump`, call tools and rerun prompt (max 3 rounds) | **Do not feed early text directly into audible Sophon output** for baseline |
| `src/state/session_state.py` `SessionState` | `current_script` starts at `Script_1`, owns scenario history, summaries, and `global_round_count` | Mario remains sole scenario-state authority |
| `src/state/session_state.py` `jump_to_script` | Sets `current_script` and entry round; no special suspended/resume script state | Add resume metadata only when needed by validated test cases |
| `src/prompts.py` `build_mario_prompt` | Renders global rules, scripts overview, active script, compressed and recent histories, and JSON `response/actions` instruction | Keep baseline; append small *typed* realtime context under a flag |
| `src/observer.py` `script_jump` | The Mario LLM proposes jump in `actions`; code immediately calls `session.jump_to_script` and schedules compression | Add optional policy validation, not an unrelated replacement state machine |
| `src/mario_session.py` `_run_try_sit` | Authorized external event changes to `Script_6` directly | Preserve event-driven transition path |
| `script-system/Script_0.md`, `global_rules.md` | Chat script is business-aware, with “no unsolicited selling” and business reentry; `script_jump` requires empty `response` | Chat handoff must preserve business reentry and avoid double openings |
| `src/prompts.py` and `src/mario_session.py` | Luigi suggestion injection and per-turn observation submission partly commented | Do not silently enable Luigi as part of bridge wiring |

**Important:** Mario's `Script_0` is a business script, **not** synonymous with `SOPHON_MODE`. A Sophon-authored answer need not change `current_script`.

---

## 2. Target architecture and ownership

```text
                  CONTINUOUS, AUDIO-NATIVE INTERACTION
Customer microphone <---------------------------------> Sophon Realtime Engine
                         listening / turn-taking / prosody / draft / speech
                                     ^      |
                                     |      | typed turn/transcript/barge-in/speech events
                                     |      v
                          Sophon Application Gateway
                                     |
                           [NEW] Mario Bridge
                                     |
               [NEW] Turn Gate / Response Arbiter / Playback Ledger
                          |                      ^
                typed TurnContext                 | ResponsePlan
                          v                      |
         +---------------------------------------------+
         |               Mario Harness                 |
         | SessionState + Script Loader + Prompt       |
         | Mario planner + script_jump + skill engine  |
         | optional Luigi async observation           |
         +---------------------------------------------+
                          |                      ^
                     future model tool contract  |  tool result
                          v                      |
           [FUTURE] Car Knowledge/Feature Model(s)  --+

For business-owned replies:
Mario decides WHAT/WHY -> Response Arbiter decides HOW ->
   (A) Mario exact speech via Sophon `say`, OR
   (B) Mario-grounded facts/intent -> Sophon native natural formulation (gated).
For allowed small talk:
Sophon can decide WHAT/HOW and speak natively, while Mario retains script state,
observes the turn, and intercepts explicit business reentry BEFORE release.
```

### Ownership table

| Concern | Single authority | Other participant |
|---|---|---|
| Audio input/voice activity/turn-taking/backchannel detection | Sophon | Mario consumes typed events, does not duplicate VAD/turn scoring |
| Speech generation, voice, sound tags, barge-in and playback queue | Sophon | Mario selects speech policy, receives playback feedback |
| `current_script`, guide stage, scene plan, `script_jump` | Mario | Sophon receives a *small* scenario summary, not the full business state machine |
| Business facts, allowed tool plan, skill results | Mario / explicit skill executor | Sophon can verbalize approved results but cannot invent tool outcomes |
| Temporary natural chit-chat | Sophon, **only after turn gate approves** | Mario retains chat-scene/reentry guard |
| Background observation and summaries | Luigi (advisory) | Never commits script changes or speech directly |
| Future proprietary automotive knowledge/model | Explicit model-tool adapter under Mario | Sophon receives bounded grounded output |
| Persistent business memory | Mario `SessionState` | Sophon maintains its own *actual-audio/played-text* conversation history |

**Invariant:** One live Sophon audio session and one corresponding Mario business session per customer; never two independent active TTS/playback owners. Maintain mapping, not duplicate business state.

---

## 3. Exploit Sophon features *without* bypassing Mario

The user HTML identifies features that should be **preserved, reused and evaluated**. The bridge must not reimplement Sophon's realtime internals unnecessarily.

| Sophon capability | How to use in integrated design | Boundary / test |
|---|---|---|
| Native audio and paralinguistic context | Keep original audio inside Sophon thinker for prosody, hesitation, stress, emotional speaking style | Do **not** assume a public `emotion=...` or `P(finished)` event exists; only send grounded metadata Mario can actually obtain |
| Four-way DuplexJev turn decision (finished/incomplete/backchannel/wait) | Let Sophon decide when to release/conclude user turn | Do not impose Mario's text-only timer over it; public VAD `speech_stopped` is not necessarily the internal semantic end-of-turn |
| Speculative draft and generation invalidation | Keep Sophon's native draft for **Sophon-native** turns; use request generation fences for Mario asynchronous plans | **Never release speculative business guidance/skills** before Mario plan and response ownership are settled |
| Barge-in | Sophon stops/marks its speech; bridge cancels or invalidates stale *uncommitted* Mario replies | Barge-in never rolls back an already executed skill or committed script transition automatically |
| `merge & abort` (early reply) | Preserve Sophon recovery when it detects user continuation | Mario should not store the premature assistant draft as heard or count the continuation as two distinct business requests |
| `BC_RESUME` / backchannel | Sophon handles brief “嗯/对” while the assistant is talking | Do not start a new Mario script turn unless the application actually receives a new intentional request |
| Actual played-content history | Reconcile Mario's `delivered_text` with Sophon's observed spoken prefix, interruption and truncation | Keep generated/submitted/played/committed separate; if playback feedback is approximate, mark it as estimated |
| Expressive sound tags | Tag/Flash/E2E can naturally render supported sound labels | Test tone/naturalness on **noncritical** narration; avoid altering numbers, names or claims |
| Built-in `delegate` and tool calling | Use as a **convenience/proposal** for backend work and Sophon-native interactions | Model-initiated delegation is not a sufficiently reliable sole business router; explicit Scenario Guard required |
| `response.say` | Baseline exact narration/announcements and verified results | Verify v1.6.2 plugin/gateway, no competing response; default interruptible true unless script requires otherwise |
| Mid-session instructions/tools | Give Sophon current scene summary and permitted behavior **only if target API supports verified updates** | Never assume `session.update` on GPT-Live equals `/v1/realtime` semantics; verify endpoint/version |
| Tag / Flash / E2E | Prefer an initial Flash vs Tag benchmark: Flash for concurrent low-latency car showroom; Tag for voice expressiveness; E2E optional | User HTML performance numbers are reference only; measure target GPU and actual voice quality |

**Do not copy Sophon's full 8-turn/120-second audio window into Mario's text prompt.** They serve different representations and budgets. Let Sophon manage audio history; let Mario manage business facts/scene history.

---


### 3.1 Model inventory — Sophon is not just ASR + TTS

**Documented by the supplied Sophon HTML (§§2–4, 9, 14–16) and upstream README/Live README.** These are different runtime/model functions, not all independent callable endpoints. Before implementation compare exact checkpoint, build, gateway commit and model/adapter licensing in the real deployment.

| Component | Actual Sophon role | Evidence useful to Mario | Accessibility / do not assume |
|---|---|---|---|
| Live gateway **Qwen3-ASR-0.6B** (auxiliary, ~2 GB GPU per upstream Live README) | Turns speech segments into transcribed text | Original/final ASR transcript and language if actually emitted | Live API provides transcript deltas; **not** the team's separate trained 0.6B NLU11, which stays out of scope. Test whether transcript is available **before** autonomous answer/delegation; never infer an ASR confidence field without evidence |
| **DuplexJev audio-native decision mechanism** within Sophon stage 0 | Audio-informed *finished/incomplete/backchannel/wait* classification (four options) and turn gating | Semantic turn commitment and distinction between customer turn vs brief acknowledgment; optional decision probabilities or state labels | These are internal model decisions. **No default public event for `P(finished)` / `P(backchannel)` / emotion is guaranteed**. First consume verified turn/interruption events; only add an observable exporter or separate decision call after verification |
| **Sophon stage-0 Thinker**, 32B or 4B family | Listens to voice, understands utterances and speech manner, writes reply text with expressive tags, can propose delegation | Native small-talk, oral-language formulation for Mario-approved facts, optional bounded task/speech-act hypothesis | No guarantee that an unmodified GPT-Live delegation task is an original transcript or a reliable routing signal. Keep Thinker speech planning constrained by Mario's approved response policy. The 4B variant has weaker general reasoning than 32B in the supplied document |
| **Paralinguistic typed readout** (DuplexJev/Para-family capability) | May classify speaking style, emphasis, laughter, affect or prosodic signals directly from raw audio | **Optional** conversational cue: hesitation → wait; emphasis → decide whether to clarify; calmer/shorter style for interruptions | Requires appropriate model/checkpoint, questions, audio transport and **proven callable readout**. Not automatically a public Sophon event, not automatically included with every Sophon brain checkpoint; assess research-only/NC licenses for optional weights. Classifier scores require calibration |
| **Speech generation**: Tag / Flash / E2E stages | Render tagged reply into audio: Tag expressive; Flash faster/concurrent; E2E compact talker + decoder | Natural voice, pronunciation and intonation in Mario-led or Sophon-native response | **These are output models, not separate business/semantic classifiers**. Mario does not consume their latent audio vectors as text or call them to set a script |
| Playback / barge-in / `merge & abort` / `BC_RESUME` machinery | Session-control logic using model decisions and playback tracking | Interruption, resume eligibility, actual/estimated heard prefix for Mario context | Session-control metadata is not equivalent to customer intent; only pass observations with provenance. Do not treat `delivered_text` as played text |

**Key separation:** The ASR model is part of the Sophon Live gateway; the **DuplexJev perceptual readout** and **Thinker dialogue generation** are associated with stage 0; Tag/Flash/E2E convert replies into sound. They solve different tasks and should not be treated as interchangeable model tools. The Sophon model must remain audio-native; Mario does **not** need raw embedding vectors or a second audio encoder in this phase.

### 3.2 Model-output availability tiers — prevent fabricated Mario inputs

| Tier | Source and API meaning | Allowed use in Mario | Initial phase |
|---|---|---|---|
| **A: Observable events / text** | Verified transcript delta/final, interruption indication, response/transcript output, playback receipt if provided | First-class factual conversation context with exact or estimated markers | T0 discover and consume |
| **B: Derived runtime status** | Correlate actual turn events, timing and playback to infer `user_interrupted_assistant`, `answer_interrupted`, `awaiting_final_asr` | Control pacing and turn validity; do not claim a model's probability | T0, gated |
| **C: Optional audio-native typed decision** | A verified, separately exposed DuplexJev readout with documented label space, calibration and request cost | Soft, bounded Mario Prompt hint: `hesitation`, `backchannel`, `emphasis`, etc., where helpful | T1 optional A/B test, OFF by default |
| **D: Thinker-generated interpretation/delegation** | `session.delegation.created`, or purpose-built model output if supported | A **proposal** to Mario, never an authoritative user transcript/script jump | Later experiment, gated |
| **E: Raw hidden-state/audio embedding transfer** | Unexported internal tensor state | **Do not implement**. Requires architectural adapter/training and independent validation | Out of scope |

**Default behavior:** If an audio decision is absent, stale, late, incompatible or uncertain, omit it from Mario Prompt; **do not synthesize `emotion=happy` or `P(finished)=0.95` from transcript text**. The system must still function with ordinary ASR and the existing Mario Prompt.

### 3.3 Perception Evidence Bridge — proposed application contract

Sophon already processes the user's audio. The new **`SophonEvidenceAdapter`** should normalize only verified observables and optional bounded readout results into a typed evidence envelope. Keep model-produced *interpretations* separate from direct transcripts and business truth.

```json
{
  "session_id": "demo_001",
  "turn_id": "u_0042",
  "generation": 7,
  "transcript": {"text": "等一下，我还想问问这个座椅", "status": "final", "origin": "live_gateway_asr"},
  "turn_observation": {
    "type": "intentional_user_turn",
    "source": "verified_runtime_event",
    "semantic_turn_probs": null
  },
  "interruption": {"assistant_playback_interrupted": true, "source": "gateway_event"},
  "assistant_speech": {
    "heard_prefix": "接下来给您介绍座椅的舒适",
    "source": "playback_estimate",
    "exact": false
  },
  "audio_cues": {
    "availability": "not_exposed",
    "cues": []
  },
  "thinker_proposal": null,
  "mario_state_ref": {"current_script": "Script_6", "topic": "seat_comfort"}
}
```

**This JSON is our proposed adapter schema, not a published Sophon protocol.** Omit unavailable keys (or explicitly mark `not_exposed`). The `turn_observation.type` should only claim `intentional_user_turn` if such a semantic fact can actually be evidenced; a raw VAD start/stop is not sufficient. Track `observed_at`, `source_version` and request revision in production. Do not pass raw camera descriptions as spoken instructions. T0-A must map each populated key to the actual event/code path.

### 3.4 How this makes Mario *better* — three complementary loops

**Loop A: Speech interaction (always on).** Sophon's stage-0 model and duplex controller decide when to take the floor, when to hold/release a draft, and when to stop speaking. Mario is not called for every pause, hesitation or backchannel. This reduces spurious LLM calls and preserves fluidity.

**Loop B: Scenario planning (when there is a real user request).** Once a real final utterance is committed, `SophonEvidenceAdapter` supplies the verified transcript, what the user actually heard previously, and available interruption/turn metadata. Mario's existing `build_mario_prompt()` receives a bounded evidence block, while its original global rules, current script and output JSON structure remain authoritative. Mario generates `response/actions` and may propose `script_jump`.

**Loop C: Reply formulation (one owner, chosen per turn).** `MARIO_EXACT`: Sophon `say` realizes Mario's final text. `MARIO_GROUNDED_SOPHON`: Sophon Thinker writes natural speech *only* within Mario's approved facts and constraints. `SOPHON_NATIVE_CHAT`: Sophon Thinker handles allowed casual turns, while Mario retains Script_0 and re-entry guard. **No automatic second answer may escape during a Mario-owned turn.**

**Concrete example:** During `Script_6` narration, customer interrupts with “等一下，我还想问问这个座椅”. Sophon interrupts speech, retains a played-prefix estimate, and waits for semantic turn completion; Mario sees the final utterance plus `interrupted=true` and prior heard content. It answers the seat question without repeating the entire narration. Optional typed cue `hesitating` (if demonstrably available) can bias *pacing*, but cannot itself invoke `script_jump` or alter Mario state.

### 3.5 Audio-native typed decisions: only after a measurable need

The uploaded HTML reports a four-answer one-token/check mechanism (`max_tokens=1`, logits/logprobs over A–D) for turn-state; the standalone DuplexJev repo also describes typed question readouts for other audio features. A developer may test a **bounded separate `AudioDecisionAdapter`** if Mario's failures require information missing from text, but must show:

1. Which exact Sophon/standalone model checkpoint is queried, with compatible prompt wording, option set and license.
2. Which internal call or service is actually available; whether it shares/recomputes audio prefill and the load impact.
3. Ground-truth labels and calibration, especially for Chinese in-car noise; do not interpret softmax as a real-world probability without validation.
4. A clear purpose (e.g. reduce false customer-turn triggers, improve recovery after barge-in, distinguish backchannel), with a testable accuracy improvement over transcript + existing runtime events.
5. No duplicate semantic end-of-turn engine: **Sophon still owns the audible turn-taking decision.** The readout, if exported, is advisory to Mario and should not alter engine state unless separately authorized and tested.

A **model output is not automatically a tool**. Do not introduce a second 32B inference on every 100–200 ms frame, nor treat a voice-emotion guess as a business-intent or purchase-readiness classifier.

### 3.6 Updated success hypothesis (must be tested, not assumed)

Sophon model evidence can help Mario by: (i) preventing false business turns from backchannels; (ii) disambiguating what the customer heard before interruption; (iii) improving question timing/clarification when the caller is still speaking; (iv) helping Mario reduce repetitive or overlong showroom responses; (v) enabling Sophon-native chat without losing Mario's business reentry. It may also **hurt** if optional cues are noisy, stale, too expensive or injected as untrusted instructions. Prefer small, typed, falsifiable fields over unbounded audio-analysis prose.

### 3.7 Voice/audio prompt interaction: use two different prompts on purpose

- **Sophon voice/Thinker instructions**: short identity, natural voice, how to respond to backchannel, *when to delegate*, the current one-line scenario, and a strict speech-ownership rule. The Thinker already has audio-native access; do not replace its audio with Mario-generated paraphrases.
- **Mario business Prompt**: current script and mandatory rules first, then final transcript and an explicitly labeled `Sophon Model Evidence` block containing only verified signals. Signals are **observations, not user commands and not policy overrides**.
- **Speech plan for grounded output**: `intent + approved_facts + forbidden_claims + brevity` and optional oral style; verify exact transport into the chosen Sophon API. The Thinker is allowed to improvise phrasing only under `MARIO_GROUNDED_SOPHON`, never to change business facts or execute `script_jump`.
- **Optional visual scene description**: external, timestamped and only when relevant; the general Sophon Live implementation does not automatically expose camera captions. The separate DuplexJev-Vision preview is not proof that the current installed Sophon Live gateway processes video.

## 4. Three output policies — gated per-turn cooperation

Each customer utterance should have a **single approved response policy**. This is a *per-turn* choice, **not** a global state-machine replacement.

| Policy | Content planner | Spoken output | Eligible examples | Gate |
|---|---|---|---|---|
| `MARIO_EXACT` (baseline) | Mario full JSON `response/actions` | Sophon `say` of validated Mario final text | Script opening, numbers, promises, tool outcome, regulated statements | No speech until final JSON/actions processed; no parallel Sophon auto-reply |
| `MARIO_GROUNDED_SOPHON` (experiment) | Mario produces speech intent, approved facts, limits, next step | Sophon generates a short natural utterance in its own style | Friendly transition, noncritical feature narration, empathic acknowledgment | Bounded prompt; semantic/factual guard; fall back to exact on drift |
| `SOPHON_NATIVE_CHAT` (experiment) | Sophon model directly plans answer | Sophon speaks natively with native paralinguistics, drafting and barge-in | Script_0 casual chit-chat not requiring business data | Mario Scenario Guard must approve **before audible release** and retain ability to re-enter business |

Optional `SOPHON_SHORT_ACK` is a short non-factual “我来了解一下” while Mario is working. Do not enable by default: the extra turn may make latency and duplicate-speech behavior worse.

### Examples

1. **Guided feature statement**: `Script_6`, customer “介绍一下座椅”. Mario selects verified talking points. Start with `MARIO_EXACT`; later test `MARIO_GROUNDED_SOPHON` using a speech plan that contains exact facts and prohibits additions.
2. **Pure personal chat**: `Script_0`, customer “你喜欢什么音乐？” After Scenario Guard confirms no business reentry, optionally run `SOPHON_NATIVE_CHAT`. Preserve Script_0 no-sales/identity/language rules.
3. **Reenter business**: `Script_0`, customer “我想试驾 07”. Scenario Guard returns `SCRIPT_TRANSITION`; Mario produces `script_jump` with empty `response`, then target script opens exactly once. Sophon must not produce a competing independent answer.
4. **Short backchannel**: while narration continues, customer says “嗯”. Treat according to Sophon's proven backchannel behavior, not automatically as a complete new Mario user turn.
5. **Interruption**: customer says “等等，刚才说的那个座椅有什么区别？” during playback. Sophon stops its own audio; bridge records heard prefix; Mario gets *new* deliberate query with up-to-date history and script context.

**Hard requirement:** There must be one and only one customer-facing response owner at a time, with a tested handoff mechanism. A feature flag is insufficient if autonomous Sophon speech can race Mario output.

---

## 5. Session state and scenario transitions — minimal, not another agent framework

### 5.1 Keep Mario's existing `current_script`

Do not replace `Script_X` with `MARIO_MODE` / `SOPHON_MODE`. Add only minimal interaction metadata to Mario's existing session or associated bridge state:

```python
# Illustrative only; not copied from existing source.
@dataclass
class RealtimeScenarioBinding:
    sophon_session_id: str
    mario_session_id: str
    current_script: str          # read from Mario SessionState; do not maintain a second authoritative copy
    turn_id: str
    generation: int
    response_policy: str        # MARIO_EXACT | MARIO_GROUNDED_SOPHON | SOPHON_NATIVE_CHAT
    pending_response_id: str | None = None
    last_playback_receipt: dict | None = None
    suspended_script: str | None = None  # optional, only when supporting true pause/resume
```

`response_policy` may change each turn **without changing** Mario's `current_script`. Separate a *temporary conversational excursion* from an explicit request to leave a guide.

### 5.2 Transition semantics

- **Existing baseline:** Mario LLM proposes `script_jump` from current Prompt; `observer.py` calls `SessionState.jump_to_script`. External `try_sit` changes to `Script_6` separately. Preserve exact behavior in baseline mode.
- **Recommended hardening after baseline:** wrap `script_jump` with a minimal validator for known target, current script/allowed transition, current generation and duplicate jump. Do not rewrite original scripts or remove business rules in the bridge patch.
- **Sophon native chat:** Mario's Scenario Guard examines finalized transcript plus active script and relevant history; only eligible `SMALL_TALK` is handed off. `SHOWROOM_SERVICE` or `BUSINESS_REENTRY` is routed to Mario. Ambiguous -> Mario clarification, never spontaneous Sophon business answer.
- **Script_0 contract:** keep its existing “only answer, do not push sales, don't fabricate personal experiences, correct language, no duplicate introduction” rules as a *bounded behavioral summary* for Sophon. Do not paste all scripts into Sophon's audio prompt.
- **Resume semantics:** `suspended_script`/step is not currently native to Mario; add only after a case demonstrates true guided pause/resume needs it. A one-off off-topic question need not permanently terminate Script_6.

### 5.3 Proposed router returns a *plan*, not a magic mode switch

```json
{
  "turn_id": "u_0042",
  "generation": 7,
  "current_script": "Script_6",
  "decision": "MARIO_GUIDE",
  "response_policy": "MARIO_EXACT",
  "transition_proposal": null,
  "reason_code": "ACTIVE_GUIDE_QUESTION"
}
```

Example classifications: `MARIO_GUIDE`, `SOPHON_SMALL_TALK`, `SCRIPT_TRANSITION`, `MARIO_SERVICE`, `CLARIFY`. Treat `reason_code` as an application-internal audit field, not a claim of model confidence.

---

## 6. Typed input, speech plans and playback receipts

### 6.1 `TurnContext` — Sophon → Mario

The minimal example below complements the **model-derived `SophonEvidenceAdapter` contract in §3.3**. Expose only evidence returned by verified endpoints and mark inferred/estimated signals. Do not synthesize a paralinguistic label merely because the underlying model has that ability.

```json
{
  "session_id": "demo_001",
  "turn_id": "u_0042",
  "generation": 7,
  "source": "sophon_realtime",
  "audio_events": {
    "speech_started": true,
    "speech_stopped": true,
    "turn_committed": true,
    "was_barge_in": true
  },
  "asr": { "text": "刚才那个座椅再介绍一下", "final": true },
  "speech_history": {
    "assistant_played_prefix": "我们先了解一下座椅的舒适性",
    "estimated": true,
    "interrupted": true
  },
  "mario": { "current_script": "Script_6", "active_topic": "seat_comfort" },
  "perception": null
}
```

**This is an application contract, NOT a native Sophon API payload.** The bridge must map only actual supported events. If Sophon emits `speech_stopped` before ASR is finalized or its internal semantic turn resolution, wait for the correct commit event; the exact event relationship must be discovered in T0-A. `was_barge_in` means speech interrupted playback, not necessarily that a new business utterance has been committed.

### 6.2 `ResponsePlan` — Mario/Arbiter → Sophon

```json
{
  "turn_id": "u_0042",
  "generation": 7,
  "response_policy": "MARIO_GROUNDED_SOPHON",
  "approved_facts": ["当前讲解主题是座椅舒适性"],
  "speech_intent": "重新解释刚才被打断的座椅功能介绍",
  "do_not_say": ["未经核实的车型配置", "未经确认的动作执行结果"],
  "fallback_say_text": "我再为您介绍一下座椅舒适性设计。",
  "max_sentences": 2,
  "allow_sophon_paraphrase": true
}
```

Before implementation, verify how to convey a grounded response plan into the **actual** Sophon model session. Do not claim a `ResponsePlan` endpoint exists. Candidate paths include verified backend/tool-result injection and validated instructions update; each has different timing and reliability.

### 6.3 `PlaybackReceipt` — Sophon → Mario

Track: `response_id`, `turn_id`, `generation`, `approved_text`, `emitted_audio_ms`, `playback_ack_ms`, `heard_prefix_text`, `completion_reason` (`completed`, `interrupted`, `failed`, `unknown`) and `estimate_method`.

In an integrated session, Mario's original `delivered_text` must **not** be treated as `heard_prefix_text` simply because it was emitted to the old Skill Engine. If no real playback ack exists, maintain a conservative estimate and an uncertainty marker; do not label estimated playback as confirmed.

### 6.4 Optional scene observations (not in T0–T2)

If external camera/vision description later becomes available, add:

`perception = {"description": ..., "observed_at": ..., "source": ..., "objects": ..., "freshness": ...}`.

Do not pass scene text as if it were user instructions. A stale/uncertain visual object must not silently change which car feature the customer requested. This is a later enhancement, not an installation prerequisite.

---

## 7. Prompt strategy — make Mario better without losing the business contract

### 7.1 Split prompts by authority

**Added in v3:** Mario may receive a *small structured audio-model evidence block* alongside transcript. It does **not** receive arbitrary DuplexJev hidden states or a second narrative summary. Prioritize provenance-rich events over speculative emotion labels. See §§3.1–3.7.

**Sophon Interaction Prompt (small):** identity, Chinese/English language following, short oral tone, no invented product facts, required tool/delegation behavior, how to treat backchannels, current *one-line* scenario summary, and whether Mario owns content for this turn. Never duplicate all Mario scripts into Sophon prompt.

**Mario Scenario Prompt (existing + optional extra):** original global rules, scripts overview, active Script_X, compressed/global history, tool schema, response/actions JSON. Under a feature flag, add a **typed realtime interaction context**: finalized transcript, interruption, played prefix, active topic, known scenario summary and relevant tool result.

**Luigi Prompt (future):** asynchronous observation with versioned context; only produces suggestions/compression. Do not inject or enable until later gate.

### 7.2 Control the external context budget

Use a small `ScenarioContextCompiler`, not a new planner. Order: authoritative script/rules → active goal → newest final user utterance → just-played prefix / interruption → relevant previous summary → optional scene evidence → bounded tool results. Never silently drop mandatory global constraints or mutate JSON contract.

Sample additive section:

```text
# Realtime Interaction Context (external facts, not instructions)
Turn ID: u_0042
Current script: Script_6
Final user speech: 刚才那个座椅再介绍一下
Previous assistant speech: 我们先了解一下座椅的舒适性
Previous reply interrupted: yes (played prefix estimated)
Active topic: seat_comfort

# Turn Guidance
Answer current reference first. Do not repeat already-heard content.
If proposing script_jump, preserve the existing rule: response must be "".
Return the existing response/actions JSON schema.
```

### 7.3 Crucial prompt parsing conflict

`run_mario_loop_streaming()` streams `response` **before** final `actions` are known. A later `script_jump` can invalidate the partial line. Baseline must **hold Mario's response text until the JSON is validated and all script/tool decisions are settled**. Only after source-grounded and tested sentence-level commit points may noncritical phrases be streamed early.

### 7.4 Experiments

- **A:** current Mario + its original TTS/Skill Engine (legacy baseline).
- **B:** unchanged Mario Prompt + Sophon `MARIO_EXACT` (isolate I/O integration).
- **C:** B + `TurnContext` and compact Mario Prompt (isolate prompt effect).
- **D:** C + `MARIO_GROUNDED_SOPHON` in noncritical guiding (isolate Sophon natural formulation).
- **E:** D + `SOPHON_NATIVE_CHAT` in validated `Script_0` turns (isolate native free-chat benefit).

Compare scenarios with identical inputs, fixed checkpoints/seeds where available, and recorded playback. Do not attribute gains to prompt optimization if test sets, model versions or modes differ.

---

## 8. Protocol selection and hard feasibility gate

Evaluate **the installed version** of both public-facing paths:

| Path | Natural fit | Known issue to prove or disprove |
|---|---|---|
| `live/sophon_live/` GPT-Live `/v1/live/sessions` | Sophon-led native dialogue and `delegate` → `session.delegation.created` → `session.commentary.append` | Delegation is model-initiated; transcript may be emitted when answer/delegation begins. **Cannot assume it always delegates every Mario-owned turn.** |
| OpenAI-Realtime-compatible `/v1/realtime` (Live gateway or direct engine) | Better-typed ASR turn events, function calls and version-supported `response.say` | Automatic Sophon reply competition, ASR-final timing, and unsupported/no-op `response.cancel` require direct tests |

### Gate 0: Response ownership is the decisive blocker

**Additional model-evidence gate:** record which Sophon brain, speech-stage model, live ASR and optional DuplexJev readout are installed; trace which model outputs are surfaced to `gateway.py`/`realtime.py` as usable application events versus held privately inside stage 0. Do not promise a public paralinguistic endpoint without source/test evidence.

For a business-owned turn, show evidence that the architecture can:

1. Route the user utterance to Mario **without Sophon independently releasing an audible answer**.
2. Preserve Sophon's turn-taking, backchannel and barge-in functions during the wait.
3. Queue or cause exactly one Mario-approved spoken result, with a unique response ID.
4. Prevent stale provisional/generated replies from reaching the ear.
5. Maintain coherent Sophon and Mario histories when a response is interrupted.
6. Return to Sophon-native speech on a permitted small-talk turn **without restarting the audio session** (later experimental gate).

Do not silently invent an `auto_response=false` setting or claim `response.cancel` works. Determine whether a **gateway-layer release gate** suffices, and whether dropped/held text contaminates engine audio history. If no validated interception point exists, report the exact blocker and implement only a limited **Mario exact-speech** proof-of-concept if safe; **do not falsely claim full Sophon-native/Mario hybrid control**.

### Gate 0 verification matrix

- Voice in while previous voice out: barge-in audible stop and history truncation.
- Four turn types: complete utterance, unfinished sentence, short “嗯”, and thinking pause.
- Sophon direct natural chat does not create a Mario action or script jump.
- Model-initiated `delegate` is observed, including one example where the model chooses *not* to delegate.
- Business-owned `say`/tool result does not overlap Sophon automatic reply.
- Request cancellation/late backend results have generation fence and observed fail-closed behavior.
- `say` before the first user speech; long Chinese sentence; interruptible and non-interruptible cases (use consent-sensitive speech behavior intentionally).
- Missing ASR, outdated gateway version, audio engine disconnect, and mixed sessions are reported accurately.

---

## 9. Active development roadmap — T0 → T1 → T2

**Terminology:** `T0`/`T1`/`T2` are the **canonical development milestones** of v5, not three model versions that are all independently deployable. Each milestone contains small tasks with independent commits and receipts. The old v4 Phase 0–1 maps to **T0**, the old v4 Phase 2 and guarded part of Phase 3 map to **T1**, and the old v4 optional LoRA study maps to **T2**. Its Phase 4 extras and the proposed T3 RSI loop are **deferred**.

| Stage | Core objective | Training? | Exit gate | Rollback |
|---|---|---|---|---|
| **T0 — Integration baseline** | Verify Sophon I/O control, build minimal Mario Bridge, preserve existing scripts and exact speech | **No** | `G0/G1`: ownership feasibility + stable complete scenario replay | Switch bridge OFF → original Mario |
| **T1 — Prompt / tool optimization** | Use only verified Sophon interaction evidence, adjust prompt context and controlled response policies | **No** | `G2`: measured improvement and no unacceptable correctness regressions | Disable context/grounded/native policy → T0 |
| **T2 — Mario-guided SFT + LoRA** | Distill validated Mario tool/dialogue behavior into Sophon's **reply Thinker** adapter, then shadow-evaluate | **Yes, after readiness gate** | `G3`: successful adapter compatibility, objective evaluation vs frozen T1, no regressions | Unload candidate LoRA → T1 |
| **T3 — RSI / auto data improvement** | Failure mining and recurrent retraining | **Deferred** | No work in current scope | Not applicable |
| **T4 — GRPO/MOPD / model architecture research** | Advanced RL/distillation or MoE | **Deferred** | No work in current scope | Not applicable |

### 9.1 T0 — Source feasibility + minimal Mario/Sophon runtime (no training)

**T0-A: Read-only audit, required first.**

- Identify both repository roots, SHA/branch, dirty status, environment, actual Sophon engine/plugin/gateway/model versions and Mario input/output path. Never treat the ZIP or user HTML as proof of installed code.
- Trace exact turn/ASR events, `say`, delegation, automatic responses, cancellation semantics, barge-in, playback/actual-heard history; produce a public/internal/unavailable **Model Evidence Availability Matrix** with file:line references.
- Trace Mario `_dispatch`, `_handle_chat`, `run_mario_loop_streaming`, streamed `response/actions`, `script_jump`, `SessionState` and original TTS. Enumerate feasible hook points; identify potential dual-speaking and history-commit races.
- Validate **G0 hard feasibility:** A business-owned Mario reply can be spoken without a competing Sophon auto-reply, with safe interruption and no incorrect history commit. If unproven, stop before runtime integration; report the smallest controlled experiment.

**T0-B: Minimal reversible bridge (after G0 and source-change authorization).**

- Add narrow `SophonMarioBridge` (same repository or sidecar by actual topology); correlate Sophon sessions, Mario sessions and `turn_id`/`generation`. Keep Sophon as the only active audio speaker.
- Use final/committed transcription to invoke Mario's **existing text** chat path. Keep `Script_0...Script_10`, `global_rules`, `script_jump` and existing Mario Prompt unchanged for baseline.
- Buffer Mario's generated `response` until the complete `actions` JSON is validated; **do not speak partially streamed text that a later `script_jump` could invalidate**.
- Add `MARIO_EXACT` via demonstrated `say`/speech-bridge contract and a `ResponseArbiter/SpeechGate`; original Mario TTS is suppressed **only** in bridged sessions. Keep legacy untouched behind `sophon_mario_bridge_enabled=false`.
- Collect playback/interrupt receipts with exact-vs-estimated provenance. Generation fences discard stale response text and candidate plans; cannot undo already executed actions.

**T0 test set:** welcome `Script_1`; casual `Script_0`; `try_sit→Script_6`; `script_jump` with empty response; interruption; backchannel `嗯`; hesitation; two simultaneous sessions; stale output; original Mario fallback.

**G1 pass:** no duplicate or unapproved audible responses; no stale reply or cross-session leakage; correct script transitions; no claim of exact heard audio where only estimated; can disable integration with one flag; retain exact test receipts. For zero-tolerance invariants, **any violation fails the gate**.

### 9.2 T1 — Better Mario performance from Sophon evidence and prompts (no training)

**T1-A: Controlled context improvement.**

- Extend the existing prompt *additively*, under feature flag, with a bounded `SophonEvidence` / `TurnContext`: verified ASR, interruption, heard-prefix/provenance, active Mario script, relevant conversation summary. Keep global rules and the original `response/actions` schema authoritative.
- Enforce provenance: native stage-0 DuplexJev audio probabilities, emotion labels and image descriptions are **not** fields unless a source-grounded API emits them. `C2` optional typed readout is OFF by default.
- Implement a small `ScenarioContextCompiler`, not a new agent framework. Freeze the experiment dataset before comparing versions.

**T1-B: Response-policy experiments.**

- First compare `C0` (legacy transcript), `C1` (verified realtime events) and, only if supported, `C2` (verified audio-native readouts).
- Then independently compare `MARIO_EXACT` with `MARIO_GROUNDED_SOPHON` for noncritical narration (Mario-approved factual content; no unsupported new facts). Only if the response-ownership gate supports per-turn changes, test `SOPHON_NATIVE_CHAT` inside `Script_0` with a guarded business-reentry path.
- Keep `Script_0` as Mario business state; a temporary Sophon chat turn must not erase script history or an unfinished guided-tour step. Preserve the single audible response invariant.
- Record model-call count, token use, end-of-turn-to-first-audio P50/P95, prompt length, scenario success and native speech quality from recordings.

**G2 pass:** against frozen T0 replays, show a predeclared measurable quality gain in at least one primary metric (scenario selection, correct resumes, reduced repetition, user-rated naturalness) **without** critical regressions in scenario correctness, false jumps, tool validity, factual accuracy, double speech or P95 latency. Report negative/no-gain outcomes faithfully. Freeze the best T1 prompt, tool schema, and policy configuration as the **T2 baseline**.

### 9.3 T2 — Mario-trajectory SFT + Sophon Thinker reply-LoRA

**T2-A: Readiness and data governance (no training job yet).**

- Confirm the exact checked-out Sophon `finetune/README.md`, `sophon_swift` adapters, checkpoint and target deployment build, adapter licenses, GPU memory, permitted source audio and use rights. The documented reference is **Tag reply LoRA**; other builds require independent compatibility proof.
- Export **reviewed Mario interaction trajectories**, not raw scripts as “ground truth”: source turn, active script, tool proposals, validated `script_jump`, tool results, approved spoken reply and actual/estimated playback prefix. Include successful *no-tool/no-jump* cases and negative examples; exclude mistakes and sensitive/unconsented recordings.
- Convert to official-style ms-swift JSONL (`messages`, `<audio>`, `audios`, Qwen-style `tools` / `<tool_call>` / `role: tool`). Use audio-backed data for the target speech task. Partition by **full sessions and speakers**, retaining a sealed held-out split. Validate syntax, file mapping, script labels and tool-call serialization before training.
- Publish a provenance/dataset card, train/val/test manifests, sampling rules, consent summary and leakage audit. If usable aligned/authorized speech data are missing, **stop at dataset tooling and report the blocker**; do not claim a LoRA result.

**T2-B: Bounded SFT experiment (after T2-A readiness).**

- Continue the bundled **Tag reply LoRA** through the upstream ms-swift `--adapters tag_swift` path; freeze audio encoder/projector, do **not** merge weights, preserve the documented sound-tag system-prompt contract. Use tag-replay mixing as a tunable baseline (upstream suggests 20–30%) and a small, fixed initial experiment; do not blindly run expensive sweeps.
- Record exact base checkpoint SHA, tag adapter, training config/seed, source hashes, run IDs, training logs, resulting adapter hash. Export by `to-vllm` only if the current repository supports it. Never overwrite the original adapter.
- Perform upstream `tools/regress.py` **and** Mario-specific full-dialogue tool/scene evaluations: scenario/delegation precision/recall, reentry, valid arguments, no wrong `script_jump`, multi-turn continuity, speech labels, language and audio latency.

**T2-C: Shadow comparison and release decision.**

- Evaluate T0, frozen best T1, and T2 candidate on the **same held-out sessions**, pinned hardware/model, with tool actions mocked or blocked. Score whole trajectories and listening/interruption behavior, not just token outputs.
- Keep the Sophon turn-taking base model unchanged; if turn-taking worsens at runtime, treat it as a system regression, **not evidence that the documented reply LoRA directly trained DuplexJev**.
- Candidate LoRA is shadow/off by default. **G3 passes only** if it improves a predeclared Mario behavior metric vs T1 and meets all no-regression gates (including tag quality, business state and no unauthorized tools). An unsupported build, unsafe data, failing speech gate or no gains means retain T1 and produce the exact failed evidence.

**T2 deliverables:** checked data manifest and sanitization report; validated JSONL train/val/held-out; reproducible training configuration, adapter artifact metadata (or precise not-ready report), model-regression and scenario-regression receipts; promotion recommendation and single-flag rollback. No production rollout without separate approval.

### 9.4 Scope stop — what stays beyond T2

**T3 automated failure synthesis/recursive retraining, T4 GRPO/MOPD, extra teachers, new model experts, our proprietary NLU11 and vehicle-control actions are explicitly NOT implementation tasks in this document.** Keep a concise backlog entry only. Do not let a tool or agent opportunistically expand into them.

---

## 10. Minimal file-level change candidates (verify before editing)

| Candidate path | Minimal anticipated change | Not to touch yet |
|---|---|---|
| Sophon `live/sophon_live/gateway.py` and/or `realtime.py` | Add bridge event correlation / read-only tap, **verified model-evidence mapping**, and proven reply release arbitration where justified | Do not refactor VAD/turn-taking/ASR internals just to expose unavailable emotion or hidden states |
| Sophon `live/applications/mario/evidence_adapter.py` (NEW, illustrative) | Normalize real ASR/turn/playback events into typed, versioned `SophonEvidence`; optional readout OFF by default | Never invent `P(finished)`/emotion or import model internals into Mario |
| Sophon `live/applications/mario/bridge.py` (NEW, location illustrative) | User-turn/event translation, Mario session correlation, generation fence | Do not fork Sophon core engine |
| Sophon `live/applications/mario/speech_policy.py` (NEW) | Exact vs grounded vs native output routing, audit IDs, feature flags | Do not claim unverified native speech-release controls |
| Mario `src/mario_session.py` | Thin input/output adapter; opt-out original TTS/Skill Engine audio only for integrated path | Leave legacy `action/expression` and other routes intact |
| Mario `src/observer.py` | Preserve existing planner, JSON and script_jump; optional validated final-response capture | Do not replace three-round tool loop |
| Mario `src/prompts.py` | Optional typed context injected after mandatory rules; retain original prompt under flag | No prompt-template wholesale rewrite |
| Mario `src/state/session_state.py` | Only essential correlation/resume metadata; back-compatible serialization | No general memory migration |
| Mario `script-system/` | No T0 edits; any Script_0 policy adaptation is separate gated T1 experiment | Do not rewrite business rules while wiring I/O |
| `tests/` (new/extended) | Mock Sophon audio events, script transitions, guards, history, multi-session race tests | No expensive model downloads for offline unit tests |

**Minimum-diff rule:** If a change can be done as a new adapter plus a tiny guarded call-site, prefer it to copying Mario into Sophon's low-level plugin or replacing Mario's framework.

---

## 11. Traceability and test plan

### 11.1 Must-pass scenario cases

| ID | Interaction | Expected result |
|---|---|---|
| S01 | Welcome (`Script_1`) | One approved opening, Mario script intact |
| S02 | Customer tries seat (`try_sit`) | Existing direct transition to `Script_6`, one opening |
| S03 | User interrupts feature narration | Sophon audio stops; heard prefix reconciled; next Mario query based on current script |
| S04 | Customer says brief “嗯” over narration | Sophon backchannel path, **not** spurious Mario script jump |
| S05 | Customer has a thinking pause (“我想……”) | No premature script transition or leaked speculative business speech |
| S06 | Unrelated question in Script_6 | Existing baseline `script_jump Script_0` works; experimental handoff later |
| S07 | “我想试驾07” in Script_0 | One business reentry to appropriate script, zero independent Sophon reply |
| S08 | Script jump with empty `response` | New script says opening only once |
| S09 | Mario response JSON yields text then later `script_jump` | Early text held; no invalid audible leakage |
| S10 | Stale tool/ASR/playback event arrives | Generation fence rejects stale event; no duplicate effects |
| S11 | Two simultaneous sessions | Isolation of script state and audio |
| S12 | Missing ASR / engine / model / tool | Honest controlled fallback, no imaginary transcript/confirmation |
| S13 | Sophon native short chat | Natural prosody/backchannel and no sales push; this is gated T1 only |
| S14 | Repeated interruption and resume | Consistent Sophon audible transcript / Mario business history |
| S15 | Existing Mario legacy mode off/on | Original TTS/skills and scripts behave unchanged when bridge disabled |

### 11.2 Metrics separated by source

**Business/Mario:** script transition accuracy, false jumps, missed reentry, task/skill correctness, JSON validity, duplicate openings, memory continuity, prompt tokens/cost.

**Voice/Sophon:** end-of-user-turn→first-audio P50/P95, interruption→audible stop P50/P95, false turn-cutoff, backchannel false requests, naturalness/intonation human ratings, audible-vs-intended words, Tag/Flash device throughput.

**Integration:** unapproved spontaneous speech count (target **zero**), duplicate audible response count (**zero**), stale generation leak (**zero**), uncertain playback accounting frequency, session-crossing events (**zero**), tool answer drift, rollback reliability.

**Model-evidence ablations:** Compare **C0 transcript only**, **C1 transcript + validated turn/interruption/played-prefix**, **C2 C1 + verified calibrated DuplexJev audio readout** (only if the model path exists). Predefine improvement targets for false Mario turns, false `script_jump`, guide interruption recovery, repeat content, latency and token/model-call cost. A change cannot be attributed to audio intelligence unless it outperforms C1 on matched trials.

**Evaluation sets:** use consistent recorded Chinese showroom conversations, including Script_0 and Script_6, short acknowledgments, hesitation, interruptions, wrong/partial ASR and script reentry. Include negative and adversarial cases. Record exact model/checkpoint, hardware, protocol/build and task revision for every result; distinguish mock from physical audio tests.

---

## 12. Recovery, risk and rollback rules

1. **No fake cancellation:** `response.cancel` may be a no-op. Demonstrate actual input/speech cancellation, or label unsupported and fail safe.
2. **No accidental double-agent:** if Sophon can auto-answer while Mario is working, do not release the Mario output until the response arbitration is demonstrably reliable.
3. **No invented playback accuracy:** Sophon may estimate emitted/played text. Never store `generated_text == actually_heard_text` without observed support.
4. **No two history authorities for the same fact:** Mario history is business state and tool evidence; Sophon history is audio/played speech. Synchronize with correlation IDs and provenance.
5. **Do not alter the model to paper over business issues:** no premature DuplexJev retraining, SOPHON plugin rewrites, transcript-to-emotion inference or cross-model LoRA sharing.
6. **No over-assignment to delegation:** official live docs admit wrong/missed tool delegation; the Scenario Guard and Mario state remain authoritative for business paths.
7. **Protect upstream:** no automatic application merges, protected branch changes, remote host updates, or unrelated dependency work.
8. **Feature flags:** disable native-chat/grounded speech if any gate fails. Preserve known-good `MARIO_EXACT`, then original Mario only.
9. **Evidence:** no positive implementation or production-readiness claim without concrete tests and versioned logs.

---

## 13. Deliverables and reporting contract — T0–T2

### T0 results

1. Read-only repository + commit inventory; verified feature matrix (`ASR`, model turns, interruption, `say`, automatic reply, playback, cancel, delegation) with exact file/line references.
2. **G0 feasibility receipt**, including pass/fail conditions and actual model/runtime behavior. A failed G0 blocks T0-B, T1 and T2.
3. Minimal adapter architecture, file-level diff and feature flags; Mario session correlation and response arbitration design.
4. Runnable replay tests and measured **G1** results, preserving script/state, single-speaker and rollback invariants. Distinguish offline mocks from real audio.

### T1 results

1. Pinned T0 test cohort and three controlled prompt-evidence variants (`C0/C1/C2`, where C2 may be unsupported).
2. Bounded Prompt Context Compiler and policy toggles; exact old/new prompt diffs and noncritical grounded/native-chat experiments **only when verified safe**.
3. Results: scenario accuracy, jumps/reentry, latency P50/P95, duplication, tool and word factuality, turn interruption, prompt tokens and model-call counts.
4. **G2** pass/fail and frozen best T1 configuration for T2.

### T2 results

1. Source and permissions check: Sophon release, fine-tune script, base/Tag adapter IDs, licenses, dataset consent and compute readiness.
2. Dataset lineage: reviewed Mario teacher trajectories, train/validation/sealed-test session manifests, valid official-style audio/tool JSONL, held-out contamination report.
3. Training command/config/seed/adapter hash and export/serving readiness, **or an explicit no-training blocker**; keep existing original model/Tag adapter intact.
4. `tools/regress.py` + Mario-specific held-out evaluations, frozen T1 vs candidate T2, **G3** pass/fail and reversible deployment recommendation. Do not promote automatically.

### Every CLI check-in must report

```text
Stage: T0-A / T0-B / T1-A / T1-B / T2-A / T2-B / T2-C
Source commits / environment:
Evidence classification: CODE-CONFIRMED / DOCUMENTED / PROPOSED / BLOCKED
Files changed (or NO FILES CHANGED):
Tests run and receipts:
Gate result:
Risks / rollback flag:
Next bounded action inside T0–T2:
```

---

## 14. Copy-and-paste CLI execution prompt — develop T0–T2 only

Attach this Markdown and the Sophon HTML/Mario snapshot to the CLI. **Start at T0-A source audit. Continue only after each gate is proven. T2 model download/training has a separate readiness and authorization check.**

```text
Read Sophon_Mario_Harness_Integration_Plan_v5_T0-T2.md completely, plus our Sophon-Realtime technical HTML and Mario.zip source snapshot. Use current authoritative Git checkouts as the implementation source of truth. This assignment is to DEVELOP only T0 → T1 → T2 in that order, subject to the explicit gate and resource/permission constraints in the plan. Do not implement T3 RSI or T4 GRPO/MOPD.

Goal: Sophon-Realtime is the continuous audio-native full-duplex interaction runtime (native ASR, DuplexJev turn/backchannel decisions, stage-0 Thinker, speech models, barge-in, playback); Mario is the authoritative scenario planning and state Harness (Script_0...Script_10, prompts, script_jump, SessionState and skills). Do not treat Sophon as a TTS-only service, and do not try to import Mario's executable Harness into LoRA weights. Luigi stays advisory and disabled unless a separately validated requirement exists.

T0: Start with a read-only source/feasibility audit: identify exact checkout SHAs, installation paths and deployed Sophon engine/plugin/model versions. Trace automatic answers, reliable controlled say, response.cancel behavior, interruptions, ASR timing, heard-vs-generated text, Mario's streamed response/actions, and script_jump. Prove response ownership Gate G0 before modifying runtime source. If G0 fails, STOP with a minimal proof experiment. If it passes and the working branch is safe, implement a tiny, reversible bridge + speech arbiter using current Mario scripts and prompts unchanged, then run the fixed regression tests (G1). Never modify the original code baseline or production deployment without approval.

T1: On the working T0 baseline, add optional typed SophonEvidence/TurnContext to Mario prompts. Do controlled C0/C1 comparisons; C2 audio-native cues only if truly exposed, OFF otherwise. Test exact Mario speech vs approved grounded expressive Sophon response and, if safe, guarded Script_0 Sophon-native chat. Preserve Mario current_script and business reentry. Measure gains and all no-regression checks, then freeze the best T1 config (G2). If T1 fails, do not start T2.

T2: First audit availability/consent of real Mario audio trajectories, reviewed scenario labels, official Sophon finetune/README.md, adapter format and licenses, target Tag build, compatible GPU/compute, and whether the user has authorized the necessary downloads/jobs. Prepare validated session-split JSONL with Qwen tool calls, negative/no-jump cases and Tag replay. Use the official continued-Tag reply-LoRA ms-swift recipe only after this readiness check and validated authorization. Keep encoder/projector/talker and native turn-taking frozen. Never merge adapter weights. Run a bounded SFT job if genuinely ready; otherwise stop at reproducible dataset/training dry-run and report exact blockers. Compare T0/T1/T2 on identical sealed held-out sessions, tools in mock mode, upstream regression and Mario scenario metrics. G3 must pass before proposing candidate promotion; never deploy to production automatically.

Across all stages: minimum modifications, small reversible commits, protect existing Git worktrees/branches, no invented APIs, explicit model/event provenance, no double replies or stale output, correct script ownership and playback history. Do not integrate trained NLU11/car models, physical vehicle execution, vision ingestion, new DuplexJev decision training, new MoE experts, Luigi activation, GRPO/MOPD or RSI automation. Work entirely within T0–T2. Report code-confirmed file:line evidence, changes/tests, exact gate results, the next bounded step, and rollback. Never claim any model is trained or integration is complete without actual evidence.
```

**STOP:** Never turn a response-ownership failure into an unverified workaround; never begin T2 after a failing T1 or absent approved speech data. **SUCCESS:** Reversible T0 bridge, measured T1 improvement, independently evaluated T2 candidate (or a precise evidence-backed T2 blocker).

---

## 15. T2 training design — Mario-guided Sophon Thinker reply LoRA

> **Decision:** T2 is an active *gated* development milestone, not an automatic training or production instruction. Use **behavior distillation from Mario's verified trajectories into Sophon's reply-generating Thinker LoRA**; do **not** import `SessionState`, `script_jump` implementation, Skill Engine, Luigi or dynamic scripts into weights. Training begins only after T0/G0–G1, T1/G2, dataset/rights/compute readiness and explicit authority for material resource use. Candidate adapters remain shadow-only until G3.
>
> **Source boundary:** The user's `Sophon-Realtime项目技术文档.html` §§12.2–12.6 and 15 describes both runtime decision readouts and LoRA training. The official [Sophon fine-tuning README](https://github.com/adventists-ai/sophon-realtime/blob/main/finetune/README.md) trains the **reply Thinker LLM**. The separate [DuplexJev repository](https://github.com/adventists-ai/duplexjev) trains audio-native single-token decision models with a different recipe. These are related models but **different training targets**. Verify exact checked-out versions before attempting any command.

### 15.1 The key distinction: two neural learning targets, one executable Harness

| Layer / capability | Trainable in the documented Sophon ms-swift reply LoRA? | Owner after integration |
|---|---|---|
| Sophon Thinker: Mario-style greetings, guided conversation, persona, concise spoken responses | **Yes, candidate**; supervise speech responses with scenario context | Sophon Thinker, under Mario response policy |
| Sophon Thinker: select `mario_scenario_request` and provide typed arguments | **Yes, candidate**; supervised tool-use trajectories; must be empirically validated | Thinker **proposes**; Mario validates |
| Sophon Thinker: pick up after tool result, avoid redundant openings, distinguish temporary digression | **Partially**; teach conversational habits, not guaranteed business correctness | Thinker expression + Mario Scenario Guard |
| Sophon audio turn model: finished/incomplete/backchannel and speech-style readout | **No, not via reply LoRA**; turn questions go to the base model | Existing Sophon/DuplexJev runtime |
| Audio encoder / multimodal projector, speech talker / vocoder, timbre / delivery | **No in the documented deployable ms-swift path** | Existing Sophon inference stacks |
| Mario `SessionState`, `current_script`, `script_jump`, validation, history and external skills | **No**; requires executable code, persistence and side effects | Mario Harness — authoritative |
| Luigi summaries and asynchronous scenario suggestions | **No**; can optionally provide **training examples** after verified labeling | Luigi service / Mario state, not Thinker weight |
| Vehicle-specific specialist tools, trained NLU11, vision ingestion | **Not in this lane**; retain adapters only | Future separately approved Mario tools |

The original Mario LLM can be kept as the **complex business planner and fallback**. Training aims to reduce unnecessary full Mario LLM turns when Sophon can handle a known conversational pattern, **without changing who may commit transitions or execute tools**.

### 15.2 Runtime design — one Sophon Thinker, one Mario state authority

**The preferred inference contract is a proposal/approval loop, not `Sophon decides script_jump`:**

1. The Sophon stage-0 Thinker listens continuously, handles audio-native turn-taking, and generates natural speech or proposes an application tool call.
2. A minimal `ScenarioGuard` (or Mario Bridge arbiter) checks whether a business-related turn needs Mario, including **false-negative tool calls**, Script_0 business re-entry and ambiguous handoffs. Do **not** rely on the Thinker always calling a tool.
3. If Mario work is required, call **one narrow, typed tool** such as `mario_scenario_request`. The output carries a **proposal with correlation ID and current scenario context**, not an executable script transition.
4. Mario performs the actual script selection / `script_jump`, business planning and skill validation. It returns the approved scenario facts, `response_policy`, and any next-step constraints.
5. The Response Arbiter authorizes **exactly one** audible response plan, using `MARIO_EXACT`, `MARIO_GROUNDED_SOPHON`, or `SOPHON_NATIVE_CHAT` as specified in §4. Unapproved speculative Sophon output must not leak.
6. The Bridge reconciles emitted/played speech and Mario history using a generation fence; interruptions never authorize a stale tool result or a duplicate answer.

**Training does not eliminate Gate 0**. The integration must first demonstrate that autonomous output can be suppressed or gated safely. A LoRA that selects the right tool 99% of the time does not solve double replies, inaccurate playback history, or incorrect cancellation.

**Proposal schema (project-specific; not a published Sophon or Mario API):**

```json
{
  "tool": "mario_scenario_request",
  "arguments": {
    "turn_id": "u_0042",
    "session_generation": 8,
    "scenario_ref": "Script_6",
    "request_type": "feature_question",
    "topic_hint": "seat_comfort",
    "user_text": "介绍一下这个座椅"
  }
}
```

The receiving service must validate allowed `request_type` values, current state, maximum payload size, version/generation, speaker and transcript provenance. `topic_hint` and `scenario_ref` are **hints**; neither can change the canonical scenario. Do not let the model produce arbitrary executable skill names or perform side effects itself.

### 15.3 How to build correct Mario-supervised trajectories

**Train from verified behavior, not from static script text or unreviewed LLM outputs.** The canonical training unit is a complete, versioned customer interaction (including positive and negative transitions) whose final business outcome can be checked.

Capture **input, observed context, proposed tool, Mario approved/rejected decision, result, final spoken reply and interruption receipt**. A dataset example should distinguish the **original customer utterance** from Mario or Sophon's paraphrases, and distinguish **actually played** content from merely generated content.

Recommended subsets:

- **In-script guidance:** welcome (`Script_1`), needs clarification (`Script_2`), feature introduction (`Script_6`), transition to a test drive (`Script_7`) and follow-up.
- **Tool calling:** cases where `mario_scenario_request` is required, where it is **not** required, duplicate-tool rejection and appropriate clarification.
- **State continuity:** `Script_6` → temporary `Script_0` chat → business re-entry, preserving the previous guide step. Include cases where explicit leave means **not** resuming.
- **Speech behavior:** short, spoken Chinese text; proper names/numbers; preserve optional sound tags; no Markdown or chain-of-thought in the spoken response.
- **Interruption and recovery:** mid-speech barge-in, brief backchannel, unfinished utterance, invalid/stale tool result, missing transcript or ambiguous topic.
- **Edge and negative cases:** no unsupported feature claims; do not invent availability or speak confirmation before a tool result; refuse or clarify malformed and adversarial tool arguments.

**Data quality rules:** Review and label the final tool outcome and actual audible prefix; strip personally identifying recordings or use permitted, properly consented captures; freeze source script version and exact model checkpoint. Use held-out **sessions / speaker groups / scenario variants**, not random individual turns from the same conversation. Maintain a permanent regression suite before adding training data.

### 15.4 Example official-style supervised conversation (schematic)

The documented [ms-swift format](https://github.com/adventists-ai/sophon-realtime/blob/main/finetune/README.md) uses JSONL `messages`, ordered `audios`, Qwen-style `tools` and `<tool_call>...` with `role: tool` results. The following is **a schematic training example**: replace placeholders with your real recorded audio, exact tool schema and a validated Mario response. Confirm adapter import/validation with the upstream sample `finetune/examples/data_example.jsonl` before training.

```json
{
  "messages": [
    {"role": "system", "content": "你是展厅语音助手。业务场景必须由 Mario Harness 验证。需要时可以用声音标签表现笑声、咳嗽和重读。"},
    {"role": "user", "content": "<audio>"},
    {"role": "assistant", "content": "<tool_call>{\"name\":\"mario_scenario_request\",\"arguments\":{\"request_type\":\"feature_question\",\"topic_hint\":\"seat_comfort\"}}</tool_call>"},
    {"role": "tool", "name": "mario_scenario_request", "content": "{\"script\":\"Script_6\",\"approved\":true,\"facts\":[\"approved description of seat comfort\"]}"},
    {"role": "assistant", "content": "好的，我来为您介绍这款车的座椅舒适功能。"}
  ],
  "tools": [
    {"type": "function", "function": {"name": "mario_scenario_request", "description": "Request a validated showroom scenario action from Mario", "parameters": {"type": "object", "properties": {"request_type": {"type": "string"}, "topic_hint": {"type": "string"}}, "required": ["request_type"]}}}
  ],
  "audios": ["data/recording_0001.wav"]
}
```

Do not treat the `facts` placeholder as real verified vehicle knowledge. When implementing, verify that the actual training/evaluation runner accepts the exact assistant tool-call serialization and the tool-result `name` field. Synthetic examples without real audio are useful for policy design but **do not prove native spoken tool calling improves**.

### 15.5 Official training compatibility: what to preserve

Use the latest checked-out [Sophon fine-tuning README](https://github.com/adventists-ai/sophon-realtime/blob/main/finetune/README.md) as the execution source of truth. As documented in the 2026-11-24 source review:

- **Continue the bundled Tag reply LoRA** (`adapters/tag`) using `--adapters tag_swift` instead of creating a fresh independent LoRA. This preserves sound-tag writing behavior. Rank **16**, alpha **32** are defined by that adapter.
- Use the documented **ms-swift** path; the encoder, projector, talker and vocoder remain frozen. Turn-taking uses the base model without the reply LoRA. Do not claim this training improves DuplexJev endpointing or new visual perception.
- The data are **speech-grounded** (`<audio>` and corresponding audio files). The training prompt must preserve the official sound-tag instruction wording and the deployment prompt must agree with the training contract.
- For a task dataset with few expression labels, mix in enough approved **tag-replay data** (the upstream guide gives **20–30% as an example**) and use its `tools/regress.py` comparison to protect voice-tag behavior, language, malformed tags, response length and other baseline speech attributes.
- Export via `sophon_swift.adapters to-vllm`; deploy as **request-attached reply LoRA**, not a merged base weight. The upstream guide explicitly warns against `merge_lora` because the thinker/talker share a base representation.
- Review each downloaded checkpoint's license and dependency notices: Sophon v1 releases and some standalone DuplexJev-Para/Emotion models may carry **different commercial-use terms**. Do not assume a separately downloaded decision-model weight has Sophon's license.
- The reference guide's training / memory claims refer to its validated **H100 80GB** configuration. **Do not assume the same workflow is immediately supported for every 4B, quantized, hosted, E2E or Vision build.** Verify checkpoint, adapter load path, hardware, license and training compatibility by build.

**Reference training commands for T2-B only** (not for T0/T1; always use the checked-out upstream README and G3 gates):

```bash
# Read and confirm versions, adapters, existing data, weights and licenses FIRST.
# Then follow the exact finetune/README.md in the checked-out Sophon commit:
python -m sophon_swift.adapters to-swift Sophon-Realtime-v1/adapters/tag tag_swift
# ... swift sft --custom_register_path sophon_swift/swift_register.py \
#       --model Sophon-Realtime-v1 --adapters tag_swift --tuner_type lora \
#       --freeze_vit true --freeze_aligner true --dataset approved_mario_audio.jsonl ...
# ... to-vllm ...; compare original tag vs candidate with tools/regress.py.
```

### 15.6 Evaluation: prove a LoRA is better than a prompt/tool baseline

Before training, record a matched held-out baseline **T0**: original Sophon Thinker + current Mario Harness + current prompt/context and verified tool schema. Then compare:

| Variant | Description | What it isolates |
|---|---|---|
| **T0 — Runtime-only** | Original Sophon, Mario guard, scripts and existing prompt/tool definitions, **no LoRA** | Does integration alone solve the problem? |
| **T1 — Prompt/tool improvement** | T0 plus bounded scenario context/tool documentation | Can better prompts remove error without training? |
| **T2 — Mario behavior LoRA** | T1 with a newly trained **Sophon reply LoRA**, same Mario runtime | Incremental trained behavior gain |
| **Build portability (future research)** | 4B/Flash/E2E only after independent support and separate approval | **Not part of T0–T2** |

**Primary quality metrics:** scenario-request tool precision/recall, missed business re-entry, false `script_jump` proposals, script/resume success, hallucinated feature claims, tool-argument validity, duplicate tool calls, and explanation correctness. Evaluate the **full conversational trajectory**, not just an isolated tool-call token.

**Voice regression:** incorrect sound-tag syntax, tag density, wrong-language outputs, latency to first audible speech (P50/P95), interrupted reply recovery, audio coherence, backchannel quality, naturalness and extra inference cost. The upstream `tools/regress.py` does **not** replace your scenario-specific evaluation.

**Critical safety and continuity invariants:** no unauthorized script transition or side effect; no two spoken replies for the same turn; no false vehicle confirmation; no stale generation escaping; no invented scene/ASR evidence. The user-defined pass thresholds should be established before training; **do not invent a percentage improvement or claim training success without observed held-out results**.

### 15.7 T2 readiness, training and shadow gates

- **T2-A readiness:** G0/G1/G2 passed; exact repo/model/adapters/licensing identified; dataset consent and source provenance validated; speaker/session held-out split sealed; no original model overwrite; compatible hardware and resource authorization confirmed.
- **T2-B train:** Start with one bounded official-style continued-Tag SFT run only if T2-A passes. Pin seed and hashes. Test adapter export. Preserve original adapter and turn-taking model.
- **T2-C shadow/G3:** Compare original Sophon+Mario T0, frozen best T1 and candidate T2 using identical held-out conversations. Require improved predeclared Mario tool/scenario metric vs T1, **zero critical correctness/speech ownership regressions**, and acceptable sound-tag/language/latency deltas. Report per-case errors, not just aggregate rates.
- **Promotion is separate from experimentation.** A successful G3 permits a recommendation or optional limited test after approval; production deployment is never automatic.

### 15.8 T2 implementation discipline and safe stop conditions

In T2-A, confirm the current Sophon **reply LoRA** implementation (`finetune/`, `sophon_swift`, adapters, build-specific training/serving path) and precisely distinguish it from DuplexJev's separate turn-decision training. Identify a minimum Mario-facing tool schema, consented audio-backed trajectories and a session-split sealed evaluation cohort. Reproduce upstream data/schema checks and produce train/not-train evidence.

In T2-B, **only if readiness passes**, continue the bundled Tag adapter in a bounded ms-swift SFT experiment with pinned dataset/config/hardware; leave Mario's executable scripts/state untouched. In T2-C, evaluate both the full Mario trajectories and native audio/tag behavior in shadow mode. Any failed readiness condition prevents training; any failed G3 prevents candidate promotion. No RSI-driven automatic retraining or GRPO enters T2.

**End goal:** keep Sophon's real-time audio model; **optionally teach its reply Thinker Mario-style behavior**; retain Mario's script/state/tool Harness as executable truth; gain accuracy or lower latency only if comparison with the no-training baseline proves it.
