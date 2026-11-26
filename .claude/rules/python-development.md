---
paths:
  - "**/*.py"
---

# Python product development

Select the profile in `.claude/workflows/sophon-serving-profiles.md` and inherit canonical workflow routing. Read callers, inputs, configuration consumers and nearest tests. Preserve the supported interpreter and existing style; avoid unsolicited packaging or dependency changes.

Use clear typed boundaries where consistent with the module, explicit exception/fallback behavior, and one owner for mutable state/resources. Scope sessions, streams, GPU/model resources and asynchronous tasks to their real lifetime. Await cancellation/cleanup when the owning contract requires it; do not swallow cancellation or block the event loop with synchronous I/O. Use existing executors/queues, bounded timeouts and backpressure rather than adding a second scheduler. Review only behavior affected by the change.

Treat audio formats, rates, chunk ordering, IDs, config defaults and public events as explicit contracts. Inspect their actual consumers; do not infer a runtime state machine from the agent workflow or copy another project's internals by resemblance. Keep secrets/audio/history out of routine logs.

For logic changes, prefer focused regression tests with existing fixtures and test framework. Separate offline validation from model loading and live-service checks. Syntax checks do not establish runtime behavior. Do not weaken assertions, silently skip required checks or add tools solely to satisfy generic guidance.
