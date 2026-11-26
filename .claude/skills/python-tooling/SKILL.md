---
name: python-tooling
description: Use when writing, reviewing, or fixing Python scripts for diagnostics, parsing, metrics, reporting, automation, and repository helper tooling.
---

# Python Tooling Skill

Follow `.claude/rules/python-tooling.md`.

## Checklist

1. Identify inputs, outputs, side effects, and device/runtime boundaries.
2. Prefer standard-library implementations for small tools.
3. Use `argparse` for CLI behavior.
4. Avoid shell-string subprocess calls; prefer argument lists.
5. Add timeouts around subprocess and collection work.
6. Redact secrets and sensitive identifiers in summaries.
7. Validate with `python3 -m py_compile`.
8. Run focused tests or a safe smoke command when available.

## Output

Report changed scripts, validation commands, sample invocation, and any
unverified device/runtime behavior.

