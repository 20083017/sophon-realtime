Shell Scripting Rules

Applies to repository shell scripts, Claude helper scripts, build/deploywrappers, log collectors, and device operation scripts.

Defaults

Use #!/usr/bin/env bash for Bash scripts.

Use set -euo pipefail unless a legacy script cannot safely support it.

Quote variable expansions by default.

Prefer arrays for commands, especially ssh, scp, rsync, and path lists.

Keep scripts non-interactive unless they are explicit operator workflows.

Use environment variables or config files for host, user, key, deploy path,service, timeout, and log path.

Avoid eval, parsing ls, and broad || true.

Compatibility

Preserve existing arguments, environment variables, output paths, and exitcodes unless a breaking change is explicitly requested.

Validate required tools, variables, arguments, and paths before changing state.

Reject unknown arguments and fail with actionable error messages.

Do not assume the current working directory; resolve repository-relative pathsfrom the script location when needed.

Repeatable Execution

Scripts that modify state must be safe to run again with the same inputs.

A repeated run must not:

duplicate configuration, services, rules, symlinks, or background processes

append the same content repeatedly

fail only because an expected directory or file already exists

overwrite unrelated files

leave stale temporary files or collectors

Use appropriate safeguards such as:

mkdir -p

check-before-create, replace, or delete

mktemp -d with cleanup traps

temporary files followed by atomic replacement

bounded retries and timeouts

PID tracking

backups before modifying important files

--dry-run or explicit --force for risky operations

When full idempotency is not possible, detect the previous state and clearlydocument cleanup, rollback, or required confirmation.

Safety

Do not use unbounded loops, waits, retries, or tail -f; use timeout,duration limits, sample limits, or size limits.

Do not use destructive commands such as rm -rf unless the target is explicit,validated, and guarded against empty, root, or unresolved paths.

Do not silently weaken SSH host-key verification.

Separate remote upload, execution, verification, and cleanup.

Upload to a temporary remote path before replacing important files.

Do not reboot devices or restart services unless explicitly requested.

Stop only processes created by the current script.

Provide rollback instructions for risky device or deployment changes.

Logging

Preserve full logs in files and pass compact excerpts to agents.

Use `.claude/tools/compact-log.sh` for bounded summaries of authorized logs. Keep one authoritative log and report the actual exit status; never fetch runtime logs merely to validate a local helper.

Record relevant command arguments, timestamps, exit status, Git revision, anddevice context.

Clean up temporary local and remote collectors.

Validation

For every changed shell script:

bash -n path/to/script.sh

Run when available:

shellcheck path/to/script.sh

Use shfmt -w only when the repository already uses it or the user requests it.

Prefer dry runs, syntax checks, mocks, or isolated targets for deploy scripts.

Run safe smoke tests twice when feasible to verify repeat-run behavior.

Do not claim device validation or idempotency unless it was actually tested;otherwise report it as unverified.

Wire-Protocol Delimiters and Unicode

Define structural punctuation by role, codepoint, and encoded bytes rather than
terminal appearance. For an ASCII/UTF-8 contract, ; is U+003B byte 3B, : is
U+003A byte 3A, and = is U+003D byte 3D. Fullwidth ； is U+FF1B bytes EF BC 9B,
and fullwidth ： is U+FF1A bytes EF BC 9A; they are not equivalent delimiters.

Use protocol-specific constants or variables. Do not reuse or globally replace
a legacy fullwidth delimiter when another protocol requires ASCII.

Use printf rather than echo or echo -e when emitting protocol text. Represent
required TAB bytes explicitly with printf or a validated Bash ANSI-C quoted
value; do not confuse a TAB byte with the two characters backslash and t.

Do not normalize, transliterate, or silently substitute Unicode punctuation at
a wire boundary. Keep structural delimiter validation separate from
natural-language payload text.

When exact bytes matter, inspect bounded data under LC_ALL=C with od or an
equivalent byte-oriented tool. Tests must assert accepted ASCII bytes and reject
visually similar fullwidth structural punctuation and mixed assignment styles.
