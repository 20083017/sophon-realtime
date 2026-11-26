# Sophon serving profiles

Read the selected source files before choosing commands or versions. This is a routing map, not a new dependency lock. Do not merge environments across variants.

| Profile | Product roots | Environment and startup source | Validation selection |
| --- | --- | --- | --- |
| Tag | `tag/plugin/sophon_realtime/`, `tag/config/` | `tag/install.sh`, `tag/start.sh`, `tag/plugin/pyproject.toml`; install script selects Python 3.12 in `tag/.venv` | Syntax and affected offline tests first; `tag/client_example.py` requires a running chosen server |
| Flash | `flash/plugin/sophon_realtime/`, `flash/config/` | `flash/install.sh`, `flash/start.sh`, `flash/plugin/pyproject.toml`; separate `flash/.venv` | Benchmark helper changes: `python -m unittest discover -s flash/tests -p "test_*.py"`; its test dependencies must exist. Client smoke is remote/runtime evidence |
| E2E plugin | `e2e/plugin/sophon_realtime/`, `e2e/config/` | `e2e/install.sh`, `e2e/start.sh`, `e2e/plugin/pyproject.toml`; separate `e2e/.venv` | Affected syntax/unit checks; `e2e/client_example.py` is a server-dependent smoke |
| Native engine | `sophon_expressive/`, `scripts/` | `scripts/install.sh`, `scripts/start.sh`, `requirements-engine.txt`, `scripts/constraints-thinker.txt`, `scripts/constraints-engine.txt` | Respect `.venv-thinker` and `.venv-engine`; gateway/inference checks require selected services and GPU resources |
| Live gateway | `live/sophon_live/`, `live/` | `live/start_live.sh`, `live/README.md`; uses a selected Tag/Flash backend | `live/live_test.py` sends requests to a running service; never classify it as an offline unit test |

Root Python packaging metadata is not a universal environment definition. Plugin package metadata allows Python >=3.10 while current plugin installers select 3.12; native installation selects `PYTHON`/the available interpreter. Preserve these distinctions and re-read the selected files when they change.

Use `python -m py_compile <changed.py>` in the selected interpreter for syntax without importing the application. A local Windows syntax result is not Linux/GPU runtime evidence. Only run an existing formatter/type checker when the affected project config establishes it; do not add a toolchain merely to satisfy a generic checklist.

Shell modifications use `bash -n <changed.sh>` and available relevant checks. GPU selection, ports, model directories, environment creation/download and service actions require the task's explicit scope. Never run install/start scripts as discovery or use `--help` on an application module without first checking import/startup side effects.

`mac/`, `finetune/` and community deployments retain their own documented environments and are selected only by tasks touching them. They are not default regression targets for Linux serving changes. Profile absence of offline tests is an evidence gap to address with a focused test where behavior changes, not permission to claim validation.
