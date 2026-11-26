#!/usr/bin/env bash
# Syntax-only checks; use a formatter separately when the selected profile configures one.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
explicit=0
if (($#)); then
  explicit=1
  files=("$@")
else
  list_tmp="$(mktemp -t sophon-syntax.XXXXXX)"
  trap 'rm -f -- "$list_tmp"' EXIT
  git ls-files -mo --exclude-standard -z -- '*.py' '*.sh' > "$list_tmp"
  git diff --cached --name-only -z -- '*.py' '*.sh' >> "$list_tmp"
  sort -zu "$list_tmp" -o "$list_tmp"
  mapfile -d '' -t files < "$list_tmp"
fi
PYTHON="${SOPHON_PYTHON:-python3}"
checked=0
for file in "${files[@]}"; do
  if [[ ! -f "$file" ]]; then
    if ((explicit)); then echo "Requested file missing or not regular: $file" >&2; exit 2; fi
    continue
  fi
  case "$file" in
    *.py)
      command -v "$PYTHON" >/dev/null || { echo "Python unavailable: $PYTHON" >&2; exit 2; }
      "$PYTHON" - "$file" <<'PY'
import ast, pathlib, sys, tokenize
path = pathlib.Path(sys.argv[1])
with tokenize.open(path) as source:
    ast.parse(source.read(), filename=str(path))
PY
      checked=$((checked + 1)) ;;
    *.sh) bash -n "$file"; checked=$((checked + 1)) ;;
  esac
done
if ((checked == 0)); then
  echo "No Python/shell files selected; no syntax checks ran."
else
  printf 'Syntax checks passed for %s Python/shell files. No formatter was invoked.\n' "$checked"
fi
