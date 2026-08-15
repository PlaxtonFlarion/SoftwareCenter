# 🚀 Mind :: 代理思维

![Mind](https://raw.githubusercontent.com/PlaxtonFlarion/SoftwareCenter/main/Assets/MindSource/app_readme.png)

**Mind 智能任务中枢**

**工具编排｜全链路可观测 · 可回放 · 可扩展**

**[Releases](https://github.com/PlaxtonFlarion/SoftwareCenter/releases) · [Assets](https://github.com/PlaxtonFlarion/SoftwareCenter/tree/main/Assets/Mind) · [Framix](https://github.com/PlaxtonFlarion/SoftwareCenter/tree/main/Assets/Framix) · [Memrix](https://github.com/PlaxtonFlarion/SoftwareCenter/tree/main/Assets/Memrix)**

---

**阅读导航**

- 第一次进入项目：先看 [快速开始](#quick-start) → [执行入口](#execution) → [命令行参数](#cli-arguments)
- 只想确认能力边界：看 [Top10 核心能力](#top10) 和 [执行入口](#execution)
- 已经知道要找什么：直接走 [正文目录](docs/README.md)

**专题跳转**

- 协议、模板和安全：看 [接口实战](#playbook-api)、[模板能力](docs/playbook.template.md)、[安全工具](docs/playbook.security.md)
- 外接工具协作：看 [外接 MCP 配置](#外接-mcp-配置单格式)
- 生命周期脚本：看 [Hooks 配置](docs/hooks.md)
- 设备、多媒体和稳定性：看 [设备与 UI 实战](docs/playbook.device.md)、[Monkey 扰动](docs/playbook.monkey.md)、[多媒体链路](#playbook-media)、[性能实战](#playbook-performance)、[云端压测与任务收束](#playbook-load)
- 订阅链路：看 [订阅模式](docs/agent-mode.md)
- 背景设计与实现：看 [背景与架构](#architecture) 和 [构建发布](#build-release)

---

## 🏆 项目简介

**Mind** 是面向工程交付的命令行代理执行框架：把一句话意图拆成可执行步骤，并编排调用 **MCP 工具** 完成设备控制、数据采集、媒体处理和脚本编排等任务。

它的重点不是“能不能回答”，而是“能不能落地”：链路可观测、结果可复现、过程可沉淀。

- **可组合**：Prompt / Resource / Tool 统一调度，工具即积木  
- **可复现**：同样输入得到同样流程与结果（可追踪、可回放）  
- **可扩展**：新增能力只需注册工具，无需改核心逻辑  

**项目代号**：Mind ｜ **中文名称**：代理思维 ｜ **产品定位**：智能代理执行框架

---

<a id="quick-start"></a>
## ⭐️ 快速开始

如果你是第一次进入项目，先把下面三件事跑通：

- 先确认 `mind --help` 可用
- 先用 `exec` 发一条最小命令，确认 native tools / 外接 MCP 链路可用
- 需要 Helix 工具时，启动命令加 `--helix`，或进入 REPL 后使用 `/helix-link`

### 确认命令入口

首次使用，建议先确认 CLI 参数能正常显示：

```bash
mind --help
```

默认执行链路可使用 native tools 和已启用的外接 MCP。需要 Helix 工具时，在进入交互界面时接入服务：

```bash
mind --helix
```

进入 REPL 后可以继续使用：

- `/helix-link`：检查并启动 Helix 服务，将 MCP 接入当前会话
- `/helix-mode`：在已连接 Helix 的会话中选择 `app / api` 工具过滤器
- `/helix-unlink`：从当前会话移除 Helix MCP，不停止本地 Helix 服务
- `/helix-home`：在已连接 Helix 的会话中打开首页
- `/helix-stop`：停止本地 Helix 服务

`/helix-mode` 和 `/helix-home` 发现 runtime asset 缺失时只执行下载；下载完成后需要重新打开应用，再通过 `--helix` 或 `/helix-link` 接入。

如果你是从 [Software Center](https://github.com/PlaxtonFlarion/SoftwareCenter) 进入，请优先阅读 Software 首页内置的 `README`：其中包含环境变量、后台管理中心与基础使用说明。

### 推荐终端与环境变量

- Windows：推荐使用 `Windows Terminal`
- macOS：推荐使用 `iTerm2`；系统 `Terminal` 可以使用，但不显示窗口进度状态
- 其他终端默认不显示窗口进度状态
- Windows 与 macOS 都建议先把默认 `Mind/MindEngine` 目录加入 `PATH`
- 不推荐默认配置系统代理或挂 VPN；只有明确需要兼容网关时，再单独配置 `base_url`

常见环境变量示例：

macOS：

```bash
# Mind 示例（默认 Mind/MindEngine 目录）
echo 'export PATH="/Applications/Mind/MindEngine:$PATH"' >> ~/.zshrc

source ~/.zshrc
```

Windows：

```powershell
# Mind 示例（默认 Mind\MindEngine 目录）
[Environment]::SetEnvironmentVariable(
  "Path",
  [Environment]::GetEnvironmentVariable("Path", "User") + ";C:\Program Files\Mind\MindEngine",
  "User"
)

$env:Path += ";C:\Program Files\Mind\MindEngine"
```

### 最小上手

```
# 先跑一条最小命令
mind exec "请用工程视角概述当前系统的核心能力、边界与典型使用场景"

# 需要持续交互时进入 REPL
mind

# 需要外接工具协作时直接使用 exec
mind exec "打开 DBHub，查询 users 表并返回结果摘要"

# 需要等待远端任务时用 agent listen
mind agent listen
```

如果你要处理协议或批量请求，直接看后面的 [接口实战](#playbook-api)。

### 常见问题解答

**已经联网，但一直 timeout？**

- 这类问题优先归到网络链路问题，先关闭 VPN、本地代理和系统代理
- 某些 VPN 或代理会中断 CLI 长连接、SSE 或流式响应，表现为一直 `timeout`
- 先在直连网络下验证；只有明确需要兼容网关时，再单独配置 `base_url`

**出现 SSL 证书错误？**

- 这通常是本地证书链被改写，常见原因是抓包工具、HTTPS 代理或证书注入。
- 先关闭抓包/代理并恢复系统证书信任，再重试；它和 `timeout` 不是同一类问题。

**配置、环境变量和服务状态应该去哪里看？**

- [Software Center](https://github.com/PlaxtonFlarion/SoftwareCenter) 内置 `README`
- 当前仓库的 [快速开始](#quick-start)
- 模型和密钥配置改为维护本地 `config.toml`

**`config.toml` 里至少应该先配什么？**

- `primary.provider`
- `primary.model`
- `primary.apikey`

没有主槽位这三项时，主执行链路无法正常调用模型。

---

<a id="top10"></a>
## ⭐️ Top10 核心能力

如果你只想快速建立心智模型，可以把核心能力先拆成四组来看：

**设备执行与页面收束**

- **前台状态收敛**：确认应用拉起、焦点命中和前台稳定状态
- **滚动到可见区域**：把目标控件推进到可见区域
- **元素诊断与修复**：处理定位漂移、属性变化和轻度页面变形
- **scrcpy 录屏**：为单设备或多设备保留执行录屏证据

**接口、媒体与证据链**

- **接口验证**：覆盖 HTTP、SSE、WS、GraphQL 等协议
- **媒体提取**：抽关键帧、场景帧和视频片段

**性能与稳定性**

- **Memrix 链路**：做内存、流畅度与稳定性采样
- **Framix 链路**：做帧级分析、阶段诊断和视觉证据沉淀
- **稳定性扰动**：结合 Monkey 与日志留痕做异常探测

**执行与订阅**

- **主动执行与订阅**：用 `exec` 或交互会话发起任务，用 `agent listen` 接收服务端下发任务

---

<a id="execution"></a>
## ⭐️ 执行入口
**Mind** 使用一条统一的主动执行链路：单次任务使用 `mind exec`，持续交互使用 `mind`。
远程任务订阅使用独立入口 `mind agent listen`，不改变主动执行链路的状态。

工具范围由本地 runtime、已启用的外接 MCP 和会话是否接入 Helix 决定。CLI 可用 `-H, --helix [app|api]` 在启动时接入 Helix；只写 `-H` 或 `--helix` 时默认选择 `app`，不传时不连接。交互会话可用 `/helix-link` 接入、用 `/helix-mode` 选择过滤器，或用 `/helix-unlink` 移除连接。外接服务配置见 [外接 MCP 配置](#外接-mcp-配置单格式)，订阅协议见 [订阅模式](docs/agent-mode.md)。

---

<a id="cli-arguments"></a>
## ⭐️ 命令行参数
Mind 使用子命令区分运行入口，再通过命令选项调整输出、模型和工具权限。

- **子命令**：`exec`、`resume`、`agent listen`、`upgrade helix`、`doctor`、`mcp`、`mcp-server`、`completion`
- **常用选项**：`--sandbox`、`--ask-for-approval`、`-H/--helix`、`--json`、`--image`、`--model`
- **默认入口**：不带子命令的 `mind` 进入交互模式

> 心智模型：**先选要执行的命令，再为该命令添加运行选项。**

### 先记住怎么组合

- 单次任务使用 `mind exec [PROMPT]`
- `mind exec` 也可以简写为 `mind e`
- 图片使用 `-i/--image`，模型使用 `-m/--model`；两者都可以放在根命令或 `exec`/`resume` 子命令
- prompt 可以与管道输入组合，例如 `git diff | mind exec "审查这些改动"`
- 远端任务订阅使用 `mind agent listen`
- Helix 运行组件升级使用 `mind upgrade helix`
- 本地环境诊断使用 `mind doctor`
- 向 MCP host 暴露 Mind agent 使用 `mind mcp-server`

完整的选项位置、图片合并、模型覆盖、stdin、会话恢复、MCP 管理与补全命令见[命令行使用参考](docs/cli-usage.md)。

### 常用速查
如果你只想先跑起来，先记住这些入口：

| 场景 | 入口 | 什么时候用 |
|------|------|------------|
| 单次主动任务 | `mind exec "..."` | 探索、接口、媒体、编码或外接工具协作 |
| 订阅监听 | `mind agent listen` | 等待服务端下发任务、维持长链路 |
| 进入交互模式 | `mind` | 在同一会话内连续处理多个目标 |
| 启用 Helix MCP | `mind exec "..." --helix` | 本次运行需要 Helix MCP 工具 |
| 调整工具准入 | `mind exec "..." -s workspace-write -a on-request` | 本次运行允许工作区写入，越界前请求审批 |
| 环境诊断 | `mind doctor` | 只读检查配置、MCP、Helix 和本地 coding 工具 |
| MCP 服务 | `mind mcp-server` | 通过 stdio 向 Codex 等 MCP host 暴露 `mind_exec` |

外接工具可以通过命令行 `mind exec "..."` 或交互会话使用，服务定义见 [外接 MCP 配置](#外接-mcp-配置单格式)。

### Helix 接入选项
`-H, --helix [app|api]`

用于在本次运行前接入本地 Helix 服务，并把 Helix MCP 工具挂入工具运行时：
- 不传 `--helix`：使用 native tools 和已连接的外部 MCP tools
- 只传 `--helix`：接入 Helix 并默认选择 `app` 工具过滤器
- 传入 `--helix api`：接入 Helix 并选择 `api` 工具过滤器
- 可用于交互入口、`mind resume`、`mind exec` 和 `mind agent listen`
- 接入前先检查 Helix runtime asset；缺失时在交互终端确认下载，再启动或复用本地 Helix MCP
- 交互模式可通过 `mind --helix` 启动时接入，也可进入后使用 `/helix-link`

示例：
```
# 本次请求启用 Helix MCP
mind exec "查询外部服务并结合 Helix 工具返回结果" --helix

# 进入 REPL 并接入 Helix
mind --helix

# 进入 REPL 并使用 API 自动化工具
mind --helix api
```

### Helix 升级命令
`mind upgrade helix`

用于更新本地 **MCP 服务/运行组件** 到最新版本形态（拉取 → 校验 → 覆盖 → 切换）。

- 适用于：需要同步更新底层 MCP 能力集时
- 不参与模型执行链路：它是一个“单一动作入口”（执行完即退出）
- 命令：`mind upgrade helix`

示例：
```
# 更新 MCP 服务到最新版本
mind upgrade helix
```

### 环境诊断命令
`mind doctor`

只读检查当前平台、源码或打包入口布局、Python、Mind 用户目录、主配置、外部 MCP 配置、Helix 运行组件，以及 `rg`、`jq`、`ast-grep`。诊断不会创建配置文件、启动服务或访问网络。

```bash
# 适合终端阅读
mind doctor

# 适合 CI 或脚本消费
mind doctor --json
```

没有失败项时返回 `0`；配置无法解析、平台不受支持等失败项返回 `1`。缺少尚未启用的可选组件只报告 warning，不会让诊断失败。

### MCP Server 命令
`mind mcp-server`

以 stdio 启动长驻 Mind MCP 服务，对外提供结构化工具 `mind_exec`。工具支持请求取消、默认 900 秒超时，以及通过返回的 `session_id` 在原工作目录续接会话。服务会复用 Mind native tools 和 `~/.mind/config.toml` 中已启用的外部 MCP，但不会自动启动 Helix。

```bash
# 打包安装后的 Codex 配置
codex mcp add mind -- mind mcp-server

# 源码模式
codex mcp add mind -- python D:\PycharmProjects\ProxyMind\mind.py mcp-server

# 检查 Codex 中的注册结果
codex mcp get mind --json
```

`codex mcp add` 中的 `--` 用于结束 Codex 自身的选项解析；`mind mcp-server` 是它随后启动的 stdio 子进程命令。不要在 Mind 自己的 `[mcp_servers]` 中注册 `mind mcp-server`，否则会递归启动自身。

完整工具参数、通用 MCP 配置和生命周期说明见 [Mind MCP Server](docs/mcp-server.md)。

### 外接工具与编码协作
`mind exec "..."`

统一执行链路可使用外接 MCP 工具、native tools 和原生 coding 工具；需要 Helix MCP 时显式叠加 `--helix`。

- 适用于：数据库、浏览器、外部服务、第三方 MCP 工具和编码任务协作
- 适合把 Playwright、外部知识库和原生 coding 能力接进本轮任务
- 需要 Helix MCP 工具时：`mind exec "..." --helix`
- 命令：`mind exec "..."`

#### 外接 MCP 配置单格式

配置写入 `~/.mind/config.toml`，并参与用户、Profile、可信项目和 CLI 覆盖的统一解析：

本地能力开关在启动时读取，修改后需要重新启动进程：

```toml
[features]
js_repl = true
subagents = true

[agents]
max_concurrent_threads_per_session = 4
max_depth = 1
default_fork_turns = 5
max_fork_context_chars = 40000
```

- `features.js_repl` 同时控制 `js_repl` 和 `js_repl_reset`
- `features.subagents` 同时控制子 Agent runtime 和 Agent 协作工具
- `[agents]` 只配置子 Agent 的并发、深度和上下文参数
- 能力开关不改变 `sandbox_mode` 或 `approval_policy`

外接 MCP 使用独立的服务配置：

```toml
[mcp_servers.playwright]
command = "npx"
args = ["-y", "@playwright/mcp@latest"]
allow = ["browser_*"]
deny = ["browser_evaluate", "browser_file_upload"]
```

Playwright MCP 如果已作为远程服务运行，也使用同一层级：

```toml
[mcp_servers.playwright]
url = "http://127.0.0.1:8931/mcp"
allow = ["browser_*"]
deny = ["browser_evaluate", "browser_file_upload"]
```

说明：

- `[mcp_servers.<name>]` 下的 `<name>` 是外接服务名
- 配置 `command` 表示 stdio 服务，配置 `url` 表示远程服务
- 同一个服务不能同时配置 `command` 和 `url`

支持字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| `url` | `string` | 必填。外接 MCP 服务地址。 |
| `enabled` | `boolean` | 可选。是否启用，默认 `true`。 |
| `required` | `boolean` | 可选。启动失败时是否终止应用启动，默认 `false`。 |
| `command` | `string` | `stdio` 必填。外接服务启动命令。 |
| `args` | `array` | 可选。`stdio` 启动参数。 |
| `env` | `table` | 可选。`stdio` 环境变量映射。 |
| `cwd` | `string` | 可选。`stdio` 工作目录。 |
| `bearer_token_env_var` | `string` | 可选。远程服务 Bearer Token 所在的环境变量。 |
| `http_headers` | `table` | 可选。远程服务固定请求头。 |
| `env_http_headers` | `table` | 可选。请求头到环境变量名的映射。 |
| `startup_timeout_sec` | `number` | 可选。单个服务启动超时秒数，默认 `10`。 |
| `tool_timeout_sec` | `number` | 可选。工具请求超时秒数，默认 `60`。 |
| `allow` | `array` | 可选。允许暴露的工具名或 glob 模式。 |
| `deny` | `array` | 可选。拒绝暴露的工具名或 glob 模式。 |

补充约定：

- 存在 `command` 时按 `stdio` 处理，存在 `url` 时按远程服务处理
- `url` 以 `/sse` 结尾时会连接 SSE 端点，其余 URL 使用 Streamable HTTP
- `enabled: false` 会跳过该服务
- `allow` 和 `deny` 按服务返回的原始工具名进行大小写敏感 glob 匹配，支持 `*` 和 `?`
- 未配置 `allow` 时不启用白名单；显式配置空数组时不暴露任何工具
- `deny` 最后执行并优先于 `allow`；`/mcp force` 不会绕过筛选规则
- 未识别字段会导致配置校验失败

例如，让 Playwright 只开放常规浏览器操作，并拒绝脚本执行和文件上传：

```toml
[mcp_servers.playwright]
command = "npx"
args = ["-y", "@playwright/mcp@latest"]
allow = ["browser_*"]
deny = ["browser_evaluate", "browser_file_upload"]
```

外接服务由本地配置接入。外接服务需提前可访问；`startup_timeout_sec` 用于启动、初始化和工具发现，`tool_timeout_sec` 用于后续工具请求等待。

示例：
```
# 使用 Playwright MCP 打开页面并读取内容
mind exec "打开 https://example.com，读取页面结构并总结主要内容"
```

### 订阅命令
`mind agent listen`

用于启动订阅模式，本地会注册会话并建立长链路，持续等待服务端下发任务。

- 适用于：远端调度、本地常驻监听、需要断线恢复与重连的任务接收场景
- 它是独立 CLI 入口，不改变交互会话状态
- 服务端链路核心是 `/agents/open`、`/agents/ws`、`/agents/resume`
- 协议时序、消息类型和排障细节，直接看 [订阅模式](docs/agent-mode.md)

示例：
```
# 启动订阅，等待服务端推送任务
mind agent listen
```

### JSON 输出选项
`--json`

以 JSONL 事件流输出运行过程，供程序、Agent、CI 和其他界面消费：
- 每行是一个完整 JSON 对象，并随事件产生立即写出
- 支持 `exec` 直接请求
- stdout 只写 JSONL；面向人的非结构化信息不混入事件流
- 直接执行无论是否使用 `--json` 都不询问、不等待，遇到需要人工确认的工具调用会直接拒绝
- `--json` 只改变输出格式；沙箱和审批策略仍由各自选项决定
- 完整成功返回退出码 `0`，失败或流提前结束返回 `1`，用户中断返回 `130`

示例：
```
mind exec "检查并修复测试" --json
mind exec "分析接口响应" --json
```

### 沙箱与审批选项
`--sandbox read-only|workspace-write|danger-full-access`

`--ask-for-approval untrusted|on-request|never`

沙箱决定工具能够触达的资源边界，审批策略决定何时询问用户。两个维度独立配置，且可以写在子命令之前或之后：
- 交互模式默认使用 `workspace-write + on-request`（`Auto`）
- 非交互运行默认使用 `read-only + never`，不会等待人工输入
- 完整访问需要显式组合 `danger-full-access + never`
- 交互模式可通过 `/permissions` 在 `Read Only`、`Auto`、`Full Access` 三个预设间切换

示例：
```
mind exec "检查项目并修复问题"
mind exec "连接外部工具并完成修改" -s workspace-write -a on-request
```

---

<a id="interactive-mode"></a>
## ⭐️ 交互模式
完整 REPL 说明已拆到独立正文：[交互模式](docs/interactive-mode.md)。

README 这里只保留入口层信息。

### 核心要点
- 启动 `mind` 即进入循环交互模式
- 已实现会话恢复、权限切换、工具状态查看和 Helix 服务控制

### 常用指令
- `/new`
- `/resume`
- `/permissions`
- `/model <model-id>`
- `/effort`
- `/preferences`
- `/compact`
- `/tools`
- `/diff`
- `/copy`
- `/ps`
- `/mcp`
- `/helix-link`
- `/helix-mode`
- `/helix-unlink`
- `/helix-home`
- `/helix-stop`
- `/shutdown`
- `/quit`

### 输入约束
- REPL 当前支持单行和多行输入
- 复杂任务建议拆成目标明确的多轮请求，避免在单次输入中混合无关目标

---

<a id="performance-tooling"></a>
## ⭐️ 自研性能工具接口层
**Mind** 的性能体系不是“跑一堆指标然后祈祷”，而是把 **采集 → 对齐 → 归因 → 回归** 做成工程闭环。  
这一层的定位是：**把端侧真实世界的性能信号，变成可对比、可复盘、可运营的标准产物**。

它不是附属功能，而是 Mind 的“第二条生命线”：  
端侧执行负责“把事做成”，性能接口层负责“把事做稳、做快、做得可证明”。

### [Framix · 画帧秀](https://github.com/PlaxtonFlarion/SoftwareCenter/tree/main/Assets/Framix)
**Framix** 专注 **视觉驱动的端到端耗时**：用画面真值对齐链路时序，把“体感卡不卡”翻译成可量化的时间线。
- **视觉 E2E 真值**：基于关键帧/状态变化定义起止点，避免埋点缺失或口径漂移  
- **端侧链路采集**：贴近设备真实表现，覆盖渲染、动效、加载、遮罩、跳转等肉眼可见路径  
- **时序对齐引擎**：把视频帧、事件、日志、工具调用时间戳对齐成同一条时间轴  
- **关键路径评估**：输出关键阶段耗时、瓶颈段落、稳定性抖动与对比结论  
- **结果可回放**：每个结论都能回到对应帧与证据（“为什么慢”可定位，不是猜）

> Framix 的爆点：把“感觉慢”变成“证据链上的慢”，把 E2E 性能从玄学拉回工程。

### [Memrix · 记忆星核](https://github.com/PlaxtonFlarion/SoftwareCenter/tree/main/Assets/Memrix)
**Memrix** 专注 **Android 性能数据采集与稳定性量化**：把资源变化从“某次偶现”升级为“可回归的趋势结论”。
- **多指标覆盖**：内存、流畅度、IO 等关键指标统一采集与落盘  
- **长稳压友好**：支持高频采样与长时间运行，适配性能采样与稳定性回归场景  
- **趋势化分析**：不仅看单点数值，更看斜率、抖动、回收效率、长期漂移与异常簇  
- **证据链产物**：指标曲线、阶段统计、异常片段与上下文（cid/sid、场景、设备、版本）一并沉淀  
- **回归可对比**：同一场景多轮对比，输出“变好/变坏”与影响范围，而不是一堆孤立数字

> Memrix 的爆点：把“看监控”升级为“做回归”——让性能问题可复现、可量化、可追踪。

### 组合拳：视觉真值 × 指标宇宙
这层接口最强的地方在于：**Framix 给出“用户看到的真相”，Memrix 给出“系统内部的原因”**，两者合在一起就是性能工程的黄金闭环：
- Framix 定位 **哪一段慢**（E2E 时间线真值）
- Memrix 解释 **为什么慢**（资源/趋势/稳定性信号）
- Mind 把两者绑定到同一 `cid/sid` 证据链，形成 **可回放、可审计、可回归** 的性能交付件

> 结论：这不是两个工具接口，这是一个“性能事实系统”：  
> 用视觉锚定真值，用指标解释原因，用回归保证不再复发。

---

<a id="playbook-load"></a>
## ⭐️ 云端压测与任务收束
完整边界、典型跑法和结果收束说明已拆到独立正文：[云端压测与任务收束](docs/playbook.load.md)。

- 云端压测适合分布式 worker、异步任务管理和统一收束
- 本地脚本使用工作区自己的命令行和脚本工具，不走 Helix MCP
- 文档聚焦任务边界、通过条件和结果形态，不展开内部实现名词
- 需要协议字段、提取和断言细节时，继续看 [接口实战](docs/playbook.api.md)

---

<a id="playbook-performance"></a>
## ⭐️ 性能实战
完整性能案例已拆到独立正文：[性能实战](docs/playbook.performance.md)。

- Framix 负责视觉真值与阶段报告
- Memrix 负责资源指标、趋势和稳定性采样
- 性能回归应固定输入、环境与验收条件，保留可比较的结果产物
- Monkey 和长稳扰动场景建议保存为可复用脚本，不要堆在命令行里

---

<a id="playbook-api"></a>
## ⭐️ 接口实战
完整协议约定、模板迁移和样例说明已拆到独立正文：[接口实战](docs/playbook.api.md)。

- 接口能力统一归在协议与校验能力里
- 协议覆盖 `HTTP / SSE / WebSocket / GraphQL / TCP / UDP / SMTP / IMAP / FTP`
- 单请求、批量请求、提取和验收都有稳定字段边界，细节直接看接口专题页
- 安全场景重点看模板变量和通过条件，不必在 README 里保留运行回放
- 需要字段级骨架、`env / items / concurrency / fail_fast` 的真实写法时，直接看 [接口实战](docs/playbook.api.md)

---
<a id="playbook-media"></a>
## ⭐️ 多媒体链路
完整媒体命令和组合链路已拆到独立正文：[多媒体链路](docs/playbook.media.md)。

- Helix `app` 工具过滤器覆盖媒体与应用自动化链路
- 能力覆盖抽帧、裁剪、转码、拼接、换容器、音轨处理和播放验证
- 推荐顺序是 `probe -> trim / extract -> convert / replace -> play`
- 长视频优先先裁剪，再抽帧或转码
- 需要完整证据链或多步处理时，直接看独立文档

---

<a id="architecture"></a>
## ⭐️ 背景与架构
完整背景、云端架构和推理集群说明已拆到独立正文：[背景与架构](docs/architecture.md)。

- 运行骨架是 `Mind + Helix` 的控制面 / 执行面分层
- 执行闭环核心是 `tool_call -> tool_result`
- 能力主要分成设备与 UI、协议与校验、基础能力、多媒体处理几类
- 接口能力归在协议与校验这一类
- 云端负责增强与治理，不接管端侧确定性执行

---

<a id="build-release"></a>
## ⭐️ 构建发布

![LOGO](https://raw.githubusercontent.com/PlaxtonFlarion/SoftwareCenter/main/Assets/MindSource/app_compile.png)

支持 **macOS** 与 **Windows** 平台安装包发布

**发布地址：** [https://github.com/PlaxtonFlarion/SoftwareCenter/releases](https://github.com/PlaxtonFlarion/SoftwareCenter/releases)

---

## ⭐️ 合作支持
如需技术合作、定制能力或企业级部署支持，请通过邮箱联系作者。

作者邮箱：`AceKeppel@outlook.com`

---

## ⭐️ 许可说明
当前仓库包含 `GPL-3.0` 授权文本（见 `LICENSE.md`）。  
如发布产物或常量中存在其他授权声明，请以 `LICENSE.md` 为准。

---

## ⭐️ 贡献指南
我们欢迎对 Mind 生态的任何形式贡献：新增能力、修复缺陷、补充文档、优化可观测性与工程稳定性。

### 贡献范围
- **新工具 / 新能力**：按域注册，补齐文档与示例
- **稳定性与可靠性**：超时/回收/错误边界/重试策略/证据链完备性
- **可观测性**：日志结构化、链路标识（cid/sid）、指标与报告落盘规范
- **文档与示例**：README、最佳实践、业务接入模板、常见问题（FAQ）

### 开发约定
- **执行优先**：任何能力必须可落地、可复现，避免“只看起来能用”
- **证据链优先**：新增能力必须产出可追踪证据（日志/媒体/指标/计划）
- **域隔离优先**：工具必须归属明确的 domain/class，不把能力写成“万能函数”
- **保持稳定性**：任何改动必须保持 CLI 行为兼容

### 提交流程
1. Fork & 新建分支：`feat/<name>` 或 `fix/<name>`
2. 本地自测：覆盖 `exec`、订阅与 REPL 关键路径
3. 更新文档：新增/变更能力需同步 README；工具说明与维护约定看 [维护者指南](docs/maintainer-guide.md)
4. 提交 PR：描述动机、设计、影响范围与回滚策略

> 建议：为新工具补齐 1 个最小示例任务（自然语言输入）+ 1 个产物截图/报告说明，方便业务侧快速验证。

---

## ⭐️ 特别鸣谢
......

---
