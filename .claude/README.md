# Claude workflow for Sophon Realtime

Start a fresh Claude session in this repository with `claude --agent sophon-plan`; `.claude/settings.json` selects the same default. Existing sessions may retain already-loaded instructions. Read `.claude/workflows/sophon-workflow.md` for the canonical state/routing rules and `.claude/workflows/sophon-serving-profiles.md` for environment selection.

## Development

Routine work: inspect, edit, run the relevant minimal check, report. Consequential work: save the plan/check/current records, obtain one approval, execute unchanged phases continuously, and correct ordinary failures within scope. The planner alone owns records. Read-only calibration/review does not edit or execute validation. Keep product Python with `sophon-python-dev`, automation with `sophon-python-tooling`, shell helpers with `sophon-shell-tooling`, and remote operations with `sophon-server-operator`.

Tag, Flash and E2E plugins have separate environments. The native engine has thinker/engine environments. Live checks are additional when relevant. Choose commands from checked-in installers/package metadata and the affected tests; do not install every variant or treat a GPU check as mandatory for an offline helper.

Mario is an on-demand reference for future development tasks. The `mario-reference` skill defines bounded read-only source access; it does not request a product migration or runtime state analysis.

## Remote configuration

Copy `.claude/config/server-session.example.json` to a user-local path outside the repository, normally `%LOCALAPPDATA%/Sophon/server-session.json` on Windows. Fill the already supplied SSH alias, expected host/user/port, dedicated remote source directory, and separate Mario reference root. Do not commit actual values or credentials. Existing SSH keys/configuration remain managed by OpenSSH; the JSON does not contain private keys or passwords.

Set `SOPHON_SESSION_CONFIG` or pass `--config`. The helper verifies alias identity before connecting, retains strict host-key checking, and uses bounded noninteractive commands. The remote side needs an existing parent directory and Python 3.10+; it does not install Python. The local source must be the actual Git worktree top level, not a linked path or subdirectory. The remote source root must be a dedicated directory named `sophon-realtime`, separate from Mario. Both remote roots and their ancestors are checked for links and overlap. A missing leaf directory is created only during an authorized upload.

## Source synchronization

`/sync` routes a request to the server operator. With no action it previews first. Use one manifest for the reviewed snapshot; preview output must be a new file outside the checkout. These example paths are placeholders:

```text
python .claude/tools/sophon-source-sync.py preview --config SESSION_CONFIG --manifest NEW_MANIFEST
python .claude/tools/sophon-source-sync.py preview --config SESSION_CONFIG --manifest NEW_MANIFEST --include path/to/new.py --replace path/to/known-existing.py
python .claude/tools/sophon-source-sync.py upload --config SESSION_CONFIG --manifest MANIFEST
python .claude/tools/sophon-source-sync.py verify --config SESSION_CONFIG --manifest MANIFEST
```

Preview reads selected remote file identities but makes no remote writes. It selects tracked files plus exact new files named with `--include`. Review the manifest's file paths, hashes, modes, prior remote identities and explicit replacement list. Known conflicting replacements require a fresh preview with `--replace`; there is no --force. Source or remote drift invalidates upload. Every successful upload is followed by verification.

Always excluded at the repository root:

```text
.claude/
.worktree-policy.yaml
AGENTS.md
CLAUDE.md
```

The same filter applies even to explicit selections, and is checked again remotely. Git metadata, local plan/check records, environments, secrets, generated logs/caches, and model/checkpoint payloads are also excluded. Required checked-in audio fixtures and small supporting model assets are preserved unless a specific exclusion applies. Files larger than 32 MiB require separate handling rather than accidental source transfer.

Deleted local files are not deleted remotely. Unrelated and excluded remote paths are untouched. Each file is staged and checked before replacement; verified replacements release their recovery copies. A failed/interrupted transfer can leave partial updates or a reported recovery directory/lock. Inspect and reconcile those exact task-owned artifacts before retrying; never recursively clean the remote source root. Linux replacements use pinned no-follow directory handles. The lock coordinates this helper only: quiesce external editors/services that write selected files during transfer. This is per-file replacement, not an atomic deployment or an atomic compare-and-swap against arbitrary external writers. Source hashes and Git executable modes are checked again before success is reported.

Uploading source does not install packages, download weights, start/restart services, run inference or prove loaded-code activation. Those need their own task scope. Mario never participates in source synchronization.

## Local checks

```text
python -m unittest discover -s .claude/tools/tests -p "test_*.py" -v
python -m py_compile .claude/tools/sophon-source-sync.py
python .claude/tools/sophon-source-sync.py --help
bash -n .claude/hooks/check-format.sh
```

The source-sync tests use temporary directories and local/mocked transport, not live SSH. Platform-specific symlink/permission checks report skips when unavailable. `.claude/hooks/check-format.sh` performs syntax checks on changed/new Python and shell files (or exact supplied paths); it does not introduce a formatter or an automatic hook chain.

Git/worktree operations use `.worktree-policy.yaml`: main is protected, topic branches base on main, normal delivery uses a pull request, and automatic direct integration into main is disabled. Preserve untracked work. This workflow does not automatically commit, push or merge changes.
