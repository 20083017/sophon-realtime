# Sophon-Realtime-32B-Tag 在 DGX Spark 上的部署指南（国内网络版）

> **社区贡献，未经核心维护者验证。** 本指南及 `web/` 下的文件由社区用户 **Takshzoe** 整理并分享，我们仅做了目录整理。核心维护者没有 DGX Spark 硬件，无法复现。遇到问题请开 issue，并附上模型版本、`sophon-realtime` / vLLM 版本、`deploy_8000.yaml` 和相关日志。
>
> **当前状态（2026-11-21）**：贡献者报告服务可正常加载和对话，文本首 token 约 313 ms，说完后约 402 ms 开始回复，但**音频首包约 3.25 s 且有卡顿**。正在排查中：(1) TensorRT 是否真正生效（日志应出现 `Loaded flow-estimator TensorRT engine`）；(2) 与量化版本对比。在有结论前，请不要把这些数字当作 Spark 的性能结论。


> 基于模型卡片 v1.2.0 的官方教程改造，针对 DGX Spark（GB10 / aarch64 / 128 GB 统一内存 / CUDA 13）和国内网络环境。
> 整理时间：2026-11-19


## 1. 通用前置检查

以普通用户 SSH 登录 DGX Spark 后执行：

```bash
whoami                      # 确认不是 root
echo $HOME                  # 你的家目录，例如 /home/nvidia
uname -m                    # 必须输出 aarch64
python3 --version           # 理想是 3.12.x
nvidia-smi                  # 驱动 580.178.04 / CUDA 13.0 左右
nvcc --version              # 应为 13.0.x
free -h                     # 128 GB
df -h ~                     # 家目录所在分区建议至少留 120 GB 可用（权重 42 GB + 编译缓存）
```

如果 `python3` 不是 3.12：Ubuntu 24.04 一般自带 3.12，用 `python3.12 --version` 确认；确实没有，再让管理员执行一次 `sudo apt install -y python3.12-venv`（仅此一步需要 root）。

### 1.1 编译工具链（实测踩坑，务必先装）

vLLM 首次启动会触发 Triton JIT 编译，其中 Qwen3-VL 视觉塔的位置编码 kernel 会现场编译一个 C 扩展，**必须有 Python 开发头文件和编译器**，否则模型加载完（约 34 GiB、3–4 分钟）后直接崩在 KV cache 初始化阶段，报 `Python.h: 没有那个文件或目录`。DGX OS 默认缺这个头文件。

让管理员装一次（仅此一步需要 root）：

```bash
sudo apt update
sudo apt install -y python3.12-dev build-essential
# 验证
ls /usr/include/python3.12/Python.h
gcc --version | head -1
```

`python3.12-dev` 提供 `Python.h`，`build-essential` 提供 gcc/g++（日志里 gcc 虽能启动，但缺少头文件就会失败）。装完回到普通用户继续，不需要 root 跑服务。

---

## 2. 下载模型权重（ModelScope，42 GB）

### 2.1 直接在 Spark 上下载（推荐）

国内网络直连 ModelScope，速度通常比从别的机器拷贝更省事，还能断点续传（中断后重跑同一条命令即可）。

```bash
python3 -m pip --version || { echo "pip3 缺失，请管理员执行 sudo apt install -y python3-pip"; exit 1; }
pip3 install --user -i https://pypi.tuna.tsinghua.edu.cn/simple modelscope

mkdir -p ~/data/models
modelscope download \
  --model AdventistsAI/Sophon-Realtime-32B-Tag \
  --local_dir ~/data/models/Sophon-Realtime-32B-Tag
```

### 2.2 如果你已经在本地机器下载好了

把整个目录原样拷到自己的家目录，注意保持子目录结构（必须有 `thinker/`、`talker/`、`voices/`）：

```bash
scp -r /本地路径/Sophon-Realtime-32B-Tag <用户名>@<SPARK_IP>:~/data/models/
```

例：`<用户名>` 通常是 `nvidia`。拷完在 Spark 上确认属主是你自己：`ls -ld ~/data/models/Sophon-Realtime-32B-Tag`。

### 2.3 校验权重完整性

```bash
du -sh ~/data/models/Sophon-Realtime-32B-Tag     # 应约 42 GB
ls ~/data/models/Sophon-Realtime-32B-Tag/thinker/model-v15-*.safetensors | wc -l   # 应为 16
ls ~/data/models/Sophon-Realtime-32B-Tag/talker/flow.decoder.estimator.fp32.onnx
ls ~/data/models/Sophon-Realtime-32B-Tag/voices/chelsie_zh.wav
```

权重结构（已核实）：`thinker/` 是 FP8 量化的 Qwen3-VL-32B 思考器（16 个分片约 33 GB + 视觉塔 1.1 GB + 音频塔 0.39 GB），`talker/` 是 tag-tts（约 6.7 GB），`voices/` 是内置音色。

---

## 3. 路线 A：PyPI 安装（完全绕开 GitHub，推荐）

PyPI 上的 `sophon-realtime` 是纯 Python wheel（架构无关），自带部署配置和启动命令，不需要仓库源码。

### 3.1 建环境并安装

```bash
mkdir -p ~/sophon
python3 -m venv ~/sophon/venv
source ~/sophon/venv/bin/activate
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -U pip setuptools wheel

# 会连带安装 vllm==0.30.0 / vllm-omni==0.30.0 / duplexjev-vllm==0.3.0
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple "sophon-realtime==1.3.0"
```

如果 `python3 -m venv` 报 "ensurepip is not available"，说明系统缺 `python3.12-venv`，让管理员装一次即可（仅此一步需要 root），然后回到普通用户重跑本段。

说明：

- `vllm==0.30.0` 会从清华源拉到 `cp38-abi3-manylinux_2_28_aarch64` wheel（约 295 MB），兼容 Python 3.12。
- vLLM 0.30.0 的发布说明明确包含 **SM120/SM121 内核**（`B12X_ATTN` attention、GB10/DGX Spark 的 FP8 优化），所以 sm_121 是被支持的。
- `vllm-omni` 和 `duplexjev-vllm` 都是 `py3-none-any`，无架构问题。
- 依赖里的 torch 体积较大，耐心等。
- 虚拟环境和缓存都在自己家目录，不需要 root，也不会污染系统 Python。

### 3.2 安装 TensorRT（强烈建议，别跳过）

**为什么之前没装上**：`tensorrt-cu13-libs` 是个 stub 包，真正的动态库 `.so` 藏在 NVIDIA 的 PyPI（`pypi.nvidia.com`）里，清华源只有空的 stub。用 `--no-deps` 装会出现「pip 显示成功、`import tensorrt` 却失败」的假成功——启动日志里那句 `WARNING: TensorRT is not installed` 就是这么来的。

**正确装法**：让 pip 直接从 NVIDIA 中国镜像（国内可直连，`pypi.nvidia.com` 会自动跳转到 `pypi.nvidia.cn`）拉库。

```bash
source ~/sophon/venv/bin/activate

# 先把主包和 Python 绑定从清华源装上
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple \
  tensorrt-cu13==10.13.3.9 tensorrt-cu13-bindings==10.13.3.9

# 动态库 stub 必须从 NVIDIA 中国镜像装（清华源没有真的 .so）
pip install --extra-index-url https://pypi.nvidia.cn/ \
  tensorrt-cu13-libs==10.13.3.9

# 验证：能打印版本才算成功
python -c "import tensorrt; print('TensorRT', tensorrt.__version__)"
```

如果第二条命令拉不到 `.so`，可直接下载 wheel 本地安装（已确认该文件存在）：

```bash
wget "https://pypi.nvidia.cn/tensorrt-cu13-libs/tensorrt_cu13_libs-10.13.3.9-py2.py3-none-manylinux_2_35_aarch64.whl" \
  -O ~/tensorrt_libs.whl
pip install ~/tensorrt_libs.whl
python -c "import tensorrt; print('TensorRT', tensorrt.__version__)"
```

已核实：`tensorrt-cu13-bindings==10.13.3.9` 有 `cp312-none-manylinux_2_35_aarch64.whl`；动态库 wheel 是 `py2.py3-none-manylinux_2_35_aarch64.whl`，两者都匹配 DGX Spark 的 aarch64 + Python 3.12。

装好后重启服务，日志里出现 `Loaded flow-estimator TensorRT engine` 就说明生效了，音频首包会明显下降。如果反复失败，跳过也能跑（纯 PyTorch 路径，高并发慢约 3 倍），但不能再用 `--no-deps` 自欺欺人。

### 3.3 调整配置（重要）

CLI 支持 `--log-dir` 指定日志与运行时配置的存放位置。先生成一次配置再改：

```bash
mkdir -p ~/sophon/logs
sophon-realtime serve \
  --model ~/data/models/Sophon-Realtime-32B-Tag \
  --port 8000 --gpu 0 --log-dir ~/sophon/logs &
# 等配置文件出现后立刻 kill 掉这个进程，改完再正式启动，
ls ~/sophon/logs/deploy_8000.yaml
```

编辑 `~/sophon/logs/deploy_8000.yaml`，按 DGX Spark 调低资源占用：

```yaml
duplex_session:
  max_sessions: 4          # 原 32：Spark 上 2–4 路够用

stages:
  - stage_id: 0
    max_num_seqs: 8        # 原 32
    gpu_memory_utilization: 0.55   # 原 0.62
    max_model_len: 8192
  - stage_id: 1
    max_num_seqs: 8
    gpu_memory_utilization: 0.07   # 原 0.08
  - stage_id: 2
    max_num_seqs: 8
    max_num_batched_tokens: 8192   # 原 32768，降低峰值内存
    gpu_memory_utilization: 0.07   # 原 0.08
```

三个 stage 合计 `gpu_memory_utilization` 从 0.78 降到 0.69，约 88 GB，给系统和显示预留约 40 GB。**统一内存架构下系统和服务抢的是同一块内存**，这一步不能省。

### 3.4 启动服务

```bash
source ~/sophon/venv/bin/activate
cd ~/sophon
export FLASHINFER_WORKSPACE_BASE=$HOME/sophon/venv   # 固定编译缓存位置，避免反复重编译
mkdir -p ~/sophon/logs

sophon-realtime serve \
  --model ~/data/models/Sophon-Realtime-32B-Tag \
  --host 0.0.0.0 --port 8000 --gpu 0 \
  --log-dir ~/sophon/logs
```

首次启动会编译内核、建 TensorRT 引擎，20–40 分钟很正常。日志里出现 `Loaded flow-estimator TensorRT engine` 说明 TRT 生效；出现警告说走 PyTorch 则说明 TRT 没装上。



## 4 网页前端（打开网页连本地端口）

> 配套文件在本目录的 `web/` 下。下文命令假设已把它们拷到 Spark 的家目录：`cp web/sophon_web.py web/sophon_frontend.html web/start_sophon.sh ~/`。`前端使用说明.md` 即 `web/FRONTEND_CN.md`。

后端跑通后，用一个独立网页做全双工语音对话（**直接说话、可打断**）。配套文件：

- `sophon_frontend.html` —— **网页前端本体**，纯 HTML/CSS/JS，可单独打开/修改
- `sophon_web.py` —— 小服务，托管网页 + 把 WebSocket 反代到后端（默认读同目录的 HTML，监听 127.0.0.1:8443）
- `前端使用说明.md` —— 完整用法与排错

网页里「高级设置 → 后端地址」**留空即自动跟随当前域名**（端口转发场景最省事），也可手填 `127.0.0.1:8000` 或完整 `ws://IP:8000`。

### 推荐：NVIDIA Sync 直接填端口（当前环境）

NVIDIA Sync 已经管了 SSH 连接和端口转发，Tailscale 也默认运行，所以**不用再跑 `tailscale serve`**。

```bash
source ~/sophon/venv/bin/activate     # aiohttp 已随 vLLM 装好

# 终端 1：Spark 上启动网页服务（默认 127.0.0.1:8443）
python ~/sophon_web.py

# 终端 2：确认后端还活着（可选）
curl -s http://127.0.0.1:8443/ | head -c 80      # 返回 HTML 说明网页服务 OK
curl -s http://127.0.0.1:8000/health             # 后端健康检查
```

在 NVIDIA Sync 里把远端端口 `8443` 映射到笔记本本地端口 `8443`，浏览器打开 `http://localhost:8443` 即可通话，网页「后端地址」留空。

链路：

```
笔记本 http://localhost:8443 → NVIDIA Sync 端口转发 → Spark 127.0.0.1:8443 (sophon_web.py) → ws://127.0.0.1:8000 (后端)
```

要点：

- 浏览器把 `localhost` 视为安全上下文，`http://localhost:8443` 同样能拿麦克风权限，**不需要自签证书**。
- **别把 `8000` 填进 Sync**：8000 只有后端 WS/HTTP 接口，没有网页；要填的是 `sophon_web.py` 的 `8443`。
- 若 Sync 转发过来连不上，改用 `python ~/sophon_web.py --host 0.0.0.0`。

### 备选：Tailscale Serve（想用 `*.ts.net` 域名时）

```bash
tailscale serve --bg --https=443 http://127.0.0.1:8443
tailscale serve status                # 记下 https://<机器名>.<tailnet>.ts.net
```

Tailnet 需开启 MagicDNS + HTTPS Certificates（个人版默认开）。关闭映射：`tailscale serve --https=443 off`

不用以上两种时可自签 HTTPS：`python ~/sophon_web.py --self-signed --host 0.0.0.0`；纯本机调试用 `--host 127.0.0.1` 开 `http://localhost:8443`。

协议与官方一致：server VAD + barge-in + 24 kHz PCM，无第三方 CDN 依赖。详细步骤、链路验证和排错见 `前端使用说明.md`。

---

## 5. 命令速查（路线 A，普通用户）

```bash
# 环境（每次新开终端先做）
source ~/sophon/venv/bin/activate
cd ~/sophon
export FLASHINFER_WORKSPACE_BASE=$HOME/sophon/venv

# 下载权重（仅需一次）
modelscope download --model AdventistsAI/Sophon-Realtime-32B-Tag --local_dir ~/data/models/Sophon-Realtime-32B-Tag

# 启动服务（脚本会自动检查 venv 和模型目录，支持 --port/--daemon 等参数）
bash ~/start_sophon.sh
# 等价的手动命令：
# sophon-realtime serve --model ~/data/models/Sophon-Realtime-32B-Tag --host 0.0.0.0 --port 8000 --gpu 0 --log-dir ~/sophon/logs

# 健康检查
curl -s http://127.0.0.1:8000/health

# 看日志中的 TRT 状态
grep -a "TensorRT" ~/sophon/logs/*.log

# 网页前端（另开终端，后端仍需保持运行）
source ~/sophon/venv/bin/activate
python ~/sophon_web.py                                        # 127.0.0.1:8443
# NVIDIA Sync：把远端 8443 映射到笔记本本地 8443，浏览器开 http://localhost:8443
# 备选 Tailscale：tailscale serve --bg --https=443 http://127.0.0.1:8443
```

---

## 6. 参考来源

- 模型卡片：https://www.modelscope.cn/models/AdventistsAI/Sophon-Realtime-32B-Tag
- 官方仓库：https://github.com/adventists-ai/sophon-realtime/tree/main/tag
- vLLM 0.30.0 发布说明（含 SM121 / GB10 优化）：https://github.com/vllm-project/vllm/releases/tag/v0.30.0
- DGX Spark 软件版本：https://docs.nvidia.com/dgx/dgx-spark/release-notes.html
- DGX Spark 硬件规格：https://docs.nvidia.com/dgx/dgx-spark/hardware.html

**最后提醒**：Sophon-Realtime 官方只在 H100/H800/A100 80 GB 上验证过。DGX Spark 属于未验证平台，模型能加载、接口能通，但延迟和并发表现需要你自己实测。如果只是想体验全双工语音效果，模型卡片里提供的在线 API（注册送 3 小时）会更省事。
