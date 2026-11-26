# Git workflow

Use `.worktree-policy.yaml` for explicit Git/worktree operations and `.claude/workflows/sophon-workflow.md` for development routing. Main is protected; named topic branches use main as their base and normal delivery is by pull request. No automatic commit/push/merge/stash follows a content edit.

When commit or PR creation is requested, include only the intended changes, review the full delta including relevant new files, use a concise conventional commit title and describe the final behavior plus actual validation. Preserve unrelated dirty/untracked work. Do not assume a machine's attribution settings.

Routine changes need relevant minimal checks without a saved plan. Planned work follows one approval and its unchanged phases. Preserve partial work on escalation; never use reset/clean/stash merely to prepare a baseline. Apply the canonical correction/material rules and explicit destructive-operation authorization.
