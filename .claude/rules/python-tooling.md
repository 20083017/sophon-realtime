# Python Tooling Rules

Applies to Python diagnostic tools, parsers, metrics collectors, report
generators, maintenance scripts, and Claude helper tools.

## Defaults

- Use Python 3 and `#!/usr/bin/env python3` for executable scripts.
- Prefer the standard library for small repository tools.
- Use `argparse` for command-line interfaces.
- Keep tool behavior explicit: input paths, output paths, timeout values, and device targets should be arguments or environment variables.
- Return clear exit codes and concise error messages.
- Avoid hardcoded local machine paths and device identifiers.

## Safety

- Use `subprocess.run([...], check=...)` with argument lists, not shell strings, unless shell behavior is explicitly required.
- Add timeouts for subprocesses, SSH-driven commands, and long-running collectors.
- Keep generated logs and reports in predictable output directories.
- Do not let Python tooling silently change product runtime behavior.

## Validation

- Run `python3 -m py_compile <script>` for every changed Python file.
- Run focused unit tests when present.
- Run a safe smoke test with `--help`, sample input, or dry-run mode when available.
- Device-facing Python tools require the same validation and log-compaction discipline as shell device scripts.

## Wire-Protocol Delimiters and Unicode

- Define structural punctuation by role, codepoint, and encoded bytes instead of
  glyph appearance. For an ASCII/UTF-8 contract, `;` is U+003B/`3B`, `:` is
  U+003A/`3A`, and `=` is U+003D/`3D`; fullwidth `；` is U+FF1B/`EF BC 9B`
  and fullwidth `：` is U+FF1A/`EF BC 9A`.
- Keep protocol-specific constants separate. Do not reuse legacy fullwidth
  delimiters for an ASCII protocol or infer a protocol from punctuation found
  in payload content.
- Do not use `unicodedata.normalize(..., "NFKC")`, transliteration, or implicit
  punctuation substitution at a wire boundary unless a versioned protocol
  explicitly requires it. Such normalization changes fullwidth punctuation
  into different structural bytes.
- Distinguish structural fields from natural-language payload text and validate
  delimiters only at the documented boundary.
- Parser and serializer tests must assert both codepoints and encoded bytes,
  include visually similar negative cases, and verify that mixed assignment
  styles are rejected rather than normalized.
