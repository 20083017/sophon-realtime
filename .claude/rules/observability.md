# Python observability

Apply only to logging/timing changes under the canonical workflow. Reuse the module's logger, context and metric owners. Use monotonic elapsed time, explicit units and bounded labels; distinguish queueing, computation, network delivery and client playback where the affected code measures them.

Correlate events using the actual scoped identity contract. Avoid duplicate terminal events/timers and account for exceptions, cancellation and disconnect cleanup. Do not equate a first chunk with completed work. Keep debug detail useful and bounded; logs are not automatically synthetic. Exclude credentials, raw private audio and unnecessary transcript/history payloads from routine output.

Verify the affected success/failure behavior using existing tests or bounded authorized traces. Source inspection establishes instrumentation intent, not measured latency or live activation. Do not introduce an unrelated logging, tracing, redaction or metrics framework.
