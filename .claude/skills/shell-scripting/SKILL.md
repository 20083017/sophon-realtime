---
name: shell-scripting
description: Use when editing or reviewing Bash launch, SSH, diagnostic or automation scripts for a selected Sophon environment.
---

# Shell tooling

Follow `.claude/workflows/sophon-workflow.md` and `.claude/rules/shell-scripting.md`. Read the affected script and callers, preserve its CLI/environment contract, quote paths and keep operations bounded. Respect a user-specified script/validation boundary; do not expand a skill-only change into a remote script or infrastructure audit.

Use existing helpers rather than adding a wrapper without need. Keep upload, execution, activation and cleanup explicit; never weaken SSH verification or stop unrelated processes. Use `bash -n` and relevant offline smoke tests. Inspect additional connection/configuration facts only when required by the selected operation or an actual failure.

Report changed behavior, actual exit status and any untested remote effects. A local syntax check is not evidence that a remote launch or repeat-run operation works.
