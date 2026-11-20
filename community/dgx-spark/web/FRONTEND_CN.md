# 智子实时语音 · 网页前端

一个独立的 HTML 网页，打开后连本地端口即可调用 Sophon-Realtime 全双工语音服务（**直接说话、边听边想、随时打断**）。协议与官方一致，无第三方 CDN 依赖。

## 文件

| 文件 | 作用 |
|---|---|
| `sophon_frontend.html` | **网页前端本体**。纯 HTML/CSS/JS，可单独打开、修改 |
| `sophon_web.py` | 小服务：托管网页 + 把 WebSocket 反代到后端。默认读上面那个 HTML |
| `start_sophon.sh` | 启动**后端**（加载权重，监听 8000）。前端跑之前必须先跑它 |

## 启动顺序（两个进程）

```bash
# 终端 1：后端，加载权重，监听 8000（首次约 10 分钟）
bash ~/start_sophon.sh
# 等到日志出现 "Application startup complete" 再起前端

# 终端 2：网页 + 反代，监听 8443
source ~/sophon/venv/bin/activate
python ~/sophon_web.py
```

`start_sophon.sh` 默认用 `~/data/models/Sophon-Realtime-32B-Tag`、`--host 0.0.0.0`、`--port 8000`、`--gpu 0`，会先检查 venv 和模型目录再启动。常用变体：

```bash
bash ~/start_sophon.sh --port 8001         # 换端口
bash ~/start_sophon.sh --daemon            # 后台运行，控制台日志写 ~/sophon/logs/console-<时间>.log
bash ~/start_sophon.sh --help              # 看全部参数
```

> 从 Windows 复制脚本到 Spark 后，若报 `^M` / `bad interpreter`，先跑 `sed -i 's/\r$//' ~/start_sophon.sh` 去掉 Windows 行尾。

## 最简用法：打开网页连本地端口

网页连接地址在「高级设置 → 后端地址」里配，三种方式任选：

1. **留空（默认）**：自动跟随当前网页的域名。配合 `sophon_web.py` + NVIDIA Sync / Tailscale 时用这个，最省事。
2. **填 `127.0.0.1:8000`**：网页和后端在同一台机器、且网页从 `http(s)` 打开时，直连后端。
3. **填完整 `ws://IP:8000` / `wss://域名`**：网页和后端在不同机器时。

> 麦克风权限要求浏览器处于**安全上下文**：`https://` 或 `localhost`。直接双击 `file://` 打开也能录音（视为安全上下文），但跨域连 `ws://127.0.0.1:8000` 时部分浏览器会拦，推荐走下面的 `sophon_web.py` + 端口转发。

## 推荐部署：NVIDIA Sync 直接填端口（你现在这套）

NVIDIA Sync 已经管了 SSH 连接和端口转发，Tailscale 也是默认运行的，所以**不用再跑 `tailscale serve`**。Spark 上只起网页服务，Sync 里填端口即可。

### 链路

```
笔记本浏览器  http://localhost:8443
    → NVIDIA Sync 端口转发（本地 8443 → Spark 8443）
    → DGX Spark  127.0.0.1:8443   (sophon_web.py：托管网页 + WS 反代)
    → ws://127.0.0.1:8000          (Sophon 后端)
```

### 步骤

把 `sophon_frontend.html` 和 `sophon_web.py` 放同一目录（比如家目录），然后：

```bash
source ~/sophon/venv/bin/activate     # aiohttp 已随 vLLM 装好

# 终端 1：Spark 上启动网页服务（默认监听 127.0.0.1:8443）
python ~/sophon_web.py

# 终端 2：确认后端还活着（可选）
curl -s http://127.0.0.1:8443/ | head -c 80      # 返回 HTML 说明网页服务 OK
curl -s http://127.0.0.1:8000/health             # 后端健康检查
```

在 **NVIDIA Sync** 里选中这台 DGX Spark 的连接，添加/编辑端口转发（custom app / port forwarding）：

- 远端端口（Spark）：`8443`
- 本地端口（笔记本）：`8443`

本地端口和远端端口可以不同，比如本地 `9443` → 远端 `8443`，那么浏览器就开 `http://localhost:9443`。

笔记本浏览器打开 `http://localhost:8443`：

1. 点「开始通话」，允许麦克风。
2. 状态变「正在聆听」后直接说话；它回答时你插话即可打断。
3. 音色默认 `vivian_zh`，可在下拉框改；高级设置可调 VAD、静音判定、后端地址。
4. 网页里「后端地址」**留空**即可——它会连 `ws://localhost:8443/v1/realtime`，由 Sync 转到 Spark 的 8443，再由 `sophon_web.py` 反代到后端 8000。

**为什么 `http://localhost` 也能录音**：浏览器把 `localhost` 视为安全上下文，所以 `http://localhost:8443` 和 `https://` 一样会给麦克风权限，不需要自签证书，也不弹警告。

### 注意

- **不要把 `8000` 填进 Sync**。8000 只有后端的 WS/HTTP 接口，没有网页；浏览器打开会是空白或 404。要填的是 `sophon_web.py` 的 `8443`，它同时提供网页和 WebSocket 反代。
- 如果 Sync 转发过来连不上（页面打不开），把网页服务改成监听所有地址再试：
  ```bash
  python ~/sophon_web.py --host 0.0.0.0
  ```

## 备选：Tailscale Serve（想用 `*.ts.net` 域名时）

如果你更想通过 Tailscale 域名 + 真实 HTTPS 访问（比如手机也用），才需要这一步。NVIDIA Sync 场景下可以跳过。

### 前提

- 后端 `sophon-realtime serve ... --port 8000` 在跑。
- Spark 与笔记本/手机在同一 Tailscale tailnet；tailnet 开了 MagicDNS + HTTPS Certificates（个人版默认开）。

### 步骤

```bash
source ~/sophon/venv/bin/activate

# 终端 1：启动网页服务（默认读同目录的 sophon_frontend.html，监听 127.0.0.1:8443）
python ~/sophon_web.py

# 终端 2：Tailscale 把本地端口映射出去（只需一次，后台常驻）
tailscale serve --bg --https=443 http://127.0.0.1:8443
tailscale serve status                # 记下 https://<机器名>.<tailnet>.ts.net
```

在已登录 Tailscale 的笔记本/手机打开 `https://...ts.net` 地址；网页「后端地址」留空，它会连 `wss://当前域名/v1/realtime`。

关闭映射：`tailscale serve --https=443 off`

## 不用 Sync 也不用 Tailscale 时

让 `sophon_web.py` 自己签 HTTPS：

```bash
python ~/sophon_web.py --self-signed --host 0.0.0.0
# 本机 https://localhost:8443；远程 https://<IP>:8443（需信任自签证书）
```

或纯本机调试（HTTP，仅 localhost 能录音）：

```bash
python ~/sophon_web.py --host 127.0.0.1
# 浏览器开 http://localhost:8443，后端地址留空即可
```

## 链路验证

```bash
curl -s http://127.0.0.1:8000/health                 # 1) 后端
curl -s http://127.0.0.1:8443/ | head -c 80           # 2) 网页服务（返回 HTML）
```

- NVIDIA Sync：确认端口转发状态为已连接，再在笔记本开 `http://localhost:8443`。
- Tailscale：`tailscale serve status` 看映射；再从 tailnet 内 `curl -s https://<机器名>.<tailnet>.ts.net/ | head -c 80`。

## 常见问题

| 现象 | 处理 |
|---|---|
| Sync 里填了端口但网页打不开 | 填 `8443` 不是 `8000`；确认 Spark 上 `sophon_web.py` 在跑；不行就 `--host 0.0.0.0` |
| 页面开了但麦克风报错 | 用 `http://localhost:<port>` 或 `https://` 打开；不要直接用 `file://` 再跨域连 WS |
| **`错误：Timeout waiting for session.update`** | 握手顺序问题。duplex 协议要求**客户端连接后主动发第一条 `session.update`** 打开会话，服务端才回 `session.created`。本网页已按此实现（onopen 立即发）；若仍报，确认用的是最新版 `sophon_frontend.html`，并看事件日志是否出现 `WebSocket 已连接` |
| 连上没反应 | 看「高级设置 → 事件日志」；确认后端 8000 在跑；检查后端地址填对了没 |
| `.ts.net` 打不开 / TLS 报错 | tailnet 开 HTTPS Certificates；首次签证书等几秒 |
| 首句音频等 20 秒+ | 声码器首次 JIT 编译，多说几句会快；装 TensorRT 后改善 |
| 改了网页没生效 | 确认改的是 `sophon_frontend.html`；`sophon_web.py` 默认读同目录这个文件 |

## 自定义

```bash
python ~/sophon_web.py --port 9000                         # 换端口（Sync / Tailscale 目标同步改）
python ~/sophon_web.py --backend ws://127.0.0.1:8000       # 后端地址
python ~/sophon_web.py --page ~/my_frontend.html           # 换网页文件
tailscale serve --bg --https=443 http://127.0.0.1:9000     # 仅 Tailscale 方案需要跟着改
```
