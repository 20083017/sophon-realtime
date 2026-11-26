---
name: tdd-workflow
description: Use when a Python behavior change needs a focused regression test in the existing test framework.
---

# Focused regression testing

Inherit `.claude/workflows/sophon-workflow.md` and the selected profile. Write a test for an observable broken behavior, run it to establish the failure, make the smallest fix, and rerun affected checks. Keep mocks at external boundaries; include failure paths that the change affects.

Use existing unittest/async test conventions. Do not introduce pytest, a coverage percentage, unrelated test types or an approval gate solely for this skill. Documentation/configuration checks remain proportionate. Never weaken assertions or claim that unrun model/GPU checks passed. Return command, exit status and behavior proven.
