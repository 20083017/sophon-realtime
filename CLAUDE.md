# Sophon Realtime development

This repository is a Python full-duplex voice-model project. Follow root `AGENTS.md` and `.claude/workflows/sophon-workflow.md`; `sophon-plan` is the default Claude routing agent. Small understood changes use direct execution with a relevant minimal check. Consequential work uses one approved plan and its existing plan/check/current records; continue unchanged approved phases without repeated confirmation.

Select the affected environment from `.claude/workflows/sophon-serving-profiles.md`: Tag, Flash, E2E plugin, native engine, or Live gateway scope. Read actual package/install/constraint files before choosing interpreter or dependency versions. Keep product development separate from diagnostic tooling. Use existing code style and focused tests; do not install a universal toolchain or run a GPU/model service for an offline helper change.

Local source is authoritative for requested source uploads. Remote connection and root paths live in user-local JSON outside the repository. Use `sophon-server-session` and `sophon-source-sync`; upload always excludes repository-root `.claude/`, `.worktree-policy.yaml`, `AGENTS.md`, and `CLAUDE.md`. Source upload does not install, download models, start services or prove activation.

Mario is a separate reference repository. Use `mario-reference` only when a development task needs it; workflow maintenance does not request Mario runtime analysis or migration. Preserve private audio, histories, credentials and unrelated changes. Do not commit connection values or infer that logs are synthetic.

Use `.worktree-policy.yaml` for explicit Git/worktree work. `main` is protected. No automatic commit, push, merge, stash or cleanup follows an edit. Keep architecture/review roles read-only and give each implementation scope one owner. Report actual checks and remaining limits; never report an unrun check as passed.
