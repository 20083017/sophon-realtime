# Code style

Follow `.claude/workflows/sophon-workflow.md`, root `AGENTS.md`, and the affected module's conventions. Python product rules are in `.claude/rules/python-development.md`; diagnostic scripts use `.claude/rules/python-tooling.md`; shell helpers use `.claude/rules/shell-scripting.md`.

Use the selected profile's interpreter and dependency contracts. Keep changes focused, public behavior explicit, and new dependencies justified. Existing formatting takes precedence over introducing another formatter. Apply configuration and observability rules only when those boundaries change. No generic rule adds a coverage percentage, full-suite requirement, approval lifecycle or unrelated refactor.
