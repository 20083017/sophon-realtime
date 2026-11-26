# Configuration and resource changes

Inherit `.claude/workflows/sophon-workflow.md` and select the affected profile. Resolve the requested file and references relative to the actual loader's root. Keep source templates, transferred disk files, environment overrides and the running process's loaded configuration distinct.

Inspect schema, defaults, load order, path handling and activation behavior before editing. Change only requested keys/records; preserve comments/encoding/order where relevant and do not normalize whole files. Confirm dependent values and preserve unrelated resources. Strict JSON does not allow comments.

Use focused parser/consumer checks. A disk edit or source upload is not runtime activation; do not restart services or make model requests unless the task authorizes them. Keep machine-specific connection settings outside the checkout. Record changed behavior, affected consumers, actual checks and any activation uncertainty. Use the canonical correction boundaries rather than adding a separate approval process.
