# Performance Optimization

## Execution and Model Selection

Follow `.claude/workflows/sophon-workflow.md`: choose the smallest sufficient execution depth, read affected context, and reuse the existing owner. Avoid repeated discovery, routine hashes and unnecessary artifact output. Existing agent configuration controls model selection; the examples below are advisory, not permission to override settings or launch agents.

**Lightweight models**, when already configured for the owner:
- Lightweight agents with frequent invocation
- Pair programming and code generation
- Worker agents in multi-agent systems

**Implementation models**, when already configured for the owner:
- Main development work
- Orchestrating multi-agent workflows
- Complex coding tasks

**Reasoning models**, when already configured for the owner:
- Complex architectural decisions
- Maximum reasoning requirements
- Research and analysis tasks

## Context Window Management

Keep enough context for implementation and corrections. Near context limits, preserve compact handoff context and update existing planned records where applicable; do not create plan/check artifacts for independent direct work. Avoid starting these tasks without sufficient context:
- Large-scale refactoring
- Feature implementation spanning multiple files
- Debugging complex interactions

Lower context sensitivity tasks:
- Single-file edits
- Independent utility creation
- Documentation updates
- Simple bug fixes

## Planning and Design

Use the canonical saved-plan checkpoint when required; direct-eligible work has no mandatory plan. Do not add a separate Plan Mode, critique panel or agent chain as a procedural prerequisite. Resolve facts and ordinary engineering decisions from evidence; discuss unresolved material choices. Full grilling follows an explicit request, and required B/C design work remains intact.

Use critique or independent agents only for a concrete unresolved question or genuinely independent work. Do not repeat discovery or launch parallel agents merely because a generic playbook suggests it.

## Build Troubleshooting

Return direct failure evidence to the existing implementation/execution owner. Correct within the current approved boundaries and rerun the affected acceptance check. No extra resolver chain, full rerun or fixed correction/review count is required. Retain technical limits and stop only for a confirmed canonical Material blocker.
