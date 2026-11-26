# Testing

Follow `.claude/workflows/sophon-workflow.md` and root `AGENTS.md`. Every change gets an appropriate minimal check; logic changes prefer a focused regression test. Select the actual profile and existing test framework. There is no universal coverage percentage or requirement to run all test types.

Use RED/GREEN for behavior changes where tests apply. Test real outcomes and boundary/failure cases, mock external resources rather than the logic being verified, and never remove assertions to force a pass. Run relevant existing checks; broaden only for demonstrated impact or acceptance.

Requested/approved validation is work to execute, not just commands to suggest. If unavailable, record the concrete limitation and mark it unrun. Required acceptance cannot be marked complete while unverified. Do not invoke GPU/model/live-service tests for an offline helper change or confuse syntax success with runtime proof.
