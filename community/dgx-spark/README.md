# Community guide: Sophon-Realtime-32B-Tag on NVIDIA DGX Spark

> This experimental guide was written and shared by community member **Takshzoe**.
> The core maintainers do not have DGX Spark hardware and have not reproduced it.
> For issues, include the model revision, `sophon-realtime` and vLLM versions,
> your `deploy_8000.yaml` and the relevant logs.

The full guide is in Chinese: [README_CN.md](README_CN.md). It targets DGX Spark
(GB10, aarch64, 128 GB unified memory, CUDA 13) on mainland-China networks
(ModelScope weights, Tsinghua PyPI mirror, NVIDIA China mirror for TensorRT).

## What it covers

- System packages the first vLLM start needs (`python3.12-dev`, `build-essential`;
  without `Python.h` the Triton JIT build fails after the weights load).
- Installing `sophon-realtime` from PyPI in a user venv, no repository checkout.
- Installing TensorRT for CUDA 13 so the libraries are real (a stub-only install
  imports nothing and the server silently falls back to PyTorch).
- Lower memory settings for unified memory: `max_sessions: 4`, `max_num_seqs: 8`,
  stage memory utilization 0.55 / 0.07 / 0.07.
- A browser front end with a small WebSocket proxy (`web/`), reached through
  NVIDIA Sync port forwarding or Tailscale Serve.

## Status (2026-11-21)

The contributor reports that the server loads and holds conversations: text
first token about 313 ms, reply starting about 402 ms after the user stops.
First audio is about 3.25 s with stuttering. Whether TensorRT was active, and a
comparison with quantized builds, are still being checked. Do not read these
numbers as Spark's performance until that is resolved.

## Files

| File | Purpose |
| --- | --- |
| `README_CN.md` | Deployment guide (Chinese) |
| `web/start_sophon.sh` | Starts the backend with path checks; `--port`, `--daemon` |
| `web/sophon_web.py` | Serves the front end and proxies WebSocket to the backend (default 127.0.0.1:8443) |
| `web/sophon_frontend.html` | Standalone full-duplex voice page, no third-party CDN |
| `web/FRONTEND_CN.md` | Front-end usage and troubleshooting (Chinese) |

Thanks to Takshzoe for the write-up.
