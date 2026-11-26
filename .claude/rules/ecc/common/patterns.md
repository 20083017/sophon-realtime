# Common implementation patterns

Follow `.claude/workflows/sophon-workflow.md` and the affected module's existing contracts. Reuse local patterns and dependencies before introducing a new abstraction, wrapper or external skeleton. A generic design example does not override the selected Python profile or public protocol.

Keep one owner/source of truth for state, explicit inputs/outputs and failure behavior, and resource lifetime tied to the actual caller. Introduce a shared boundary only when the requested behavior requires it. Discuss consequential adaptation through the existing planner; do not automatically clone a framework or launch a panel of agents.

Select only the tests and review depth needed for the changed behavior. Do not impose unrelated frontend hooks, repository layers or API envelopes on existing Python modules.
