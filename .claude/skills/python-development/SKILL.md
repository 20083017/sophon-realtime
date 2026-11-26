---
name: python-development
description: Use when implementing or reviewing Sophon Python product modules, configuration consumers, or async behavior.
---

# Python Development

Read `.claude/workflows/sophon-workflow.md`, `.claude/workflows/sophon-serving-profiles.md` and `.claude/rules/python-development.md`. Select the affected profile before choosing an interpreter or command. Product work belongs to `sophon-python-dev`; parsers/reporting/automation use `python-tooling`.

Inspect the affected caller/data/configuration contract and nearest tests. Keep changes minimal and verify the behavior with existing offline tests before any authorized service check. Respect cancellation/resource lifetime and input/audio contracts only where relevant; this skill does not define a new runtime state machine. Do not install all variants or import model-heavy modules as a syntax check.

Example: a Flash benchmark parser change uses its existing unittest suite in an environment with its test dependencies; it does not start a model server. Report selected environment, changed behavior and actual evidence. An absent GPU is not a successful runtime test.
