# 🚀 Mind :: 代理思维

![Mind](https://raw.githubusercontent.com/PlaxtonFlarion/SoftwareCenter/main/Assets/MindSource/app_readme.png)

**Mind 智能任务中枢**

**工具编排｜全链路可观测 · 可回放 · 可扩展**

**[Releases](https://github.com/PlaxtonFlarion/SoftwareCenter/releases) · [Assets](https://github.com/PlaxtonFlarion/SoftwareCenter/tree/main/Assets/Mind) · [Framix](https://github.com/PlaxtonFlarion/SoftwareCenter/tree/main/Assets/Framix) · [Memrix](https://github.com/PlaxtonFlarion/SoftwareCenter/tree/main/Assets/Memrix)**

---

**快速入口**

- [快速开始](#quick-start)
- [运行模式](#modes)
- [命令行参数](#cli-arguments)
- [文档索引](docs-index.md)

**专题入口**

- [订阅模式](agent-mode.md)
- [接口实战](#playbook-api)
- [模板能力](playbook.template.md)
- [安全工具](playbook.security.md)
- [设备与 UI 实战](playbook.device.md)
- [Monkey 扰动](playbook.monkey.md)
- [多媒体链路](#playbook-media)
- [背景与架构](#architecture)
- [构建发布](#build-release)

**按任务跳转**

- 设备 / UI 执行：从 [快速开始](#quick-start)、[运行模式](#modes) 和 [设备与 UI 实战](playbook.device.md) 入手
- 性能与稳定性：看 [性能工具接口层](#performance-tooling) 和 [性能实战](#playbook-performance)
- 接口协议验证：看 [接口实战](#playbook-api)
- 模板 helper / 签名前置：看 [模板能力](playbook.template.md)
- 安全签名 / JWT / AES / RSA：看 [安全工具](playbook.security.md)
- Monkey 稳定性扰动：看 [Monkey 扰动](playbook.monkey.md)
- 音视频与证据链：看 [多媒体链路](#playbook-media)
- 批跑 / 编排 / 回归：看 [命令行参数](#cli-arguments) 中的 `--code`
- 订阅任务下发 / 长链路监听：看 [订阅模式](agent-mode.md)
- 背景设计与实现：看 [背景与架构](#architecture)

**首次阅读建议**

- 只想先跑起来：先看 [快速开始](#quick-start) → [运行模式](#modes) → [命令行参数](#cli-arguments)
- 只想确认能力边界：看 [Top10 核心能力](#top10) 和 [运行模式](#modes)
- 已经知道要找什么：直接走 [文档索引](docs-index.md)
- 准备看协议、模板和安全链路：从 [接口实战](#playbook-api)、[模板能力](playbook.template.md)、[安全工具](playbook.security.md) 继续
- 准备看设备、多媒体和稳定性链路：从 [设备与 UI 实战](playbook.device.md)、[Monkey 扰动](playbook.monkey.md)、[多媒体链路](#playbook-media) 继续

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

- 打开后台管理中心，确认模型槽位和服务状态可见
- 选一个适合当前任务的入口：`chat / fast / plan`，或者订阅用的 `agent`
- 先发一条最小命令，再决定是否继续读设备、协议或多媒体专题

Mind 有两种运行方式：

- **命令行模式**：每条命令执行一次任务，适合脚本/CI
- **交互式模式**：进入循环交互，可在 chat/fast/plan 间随时切换，适合探索与调试

补充：

- **订阅模式**：`mind --agent`，本地注册会话并等待服务端下发任务，适合远端调度与长链路监听

### 打开管理中心

首次使用，建议先打开后台管理中心面板：

```bash
mind --hello
```

`--hello` 会拉起本地后台管理中心面板，统一管理：

- 配置主模型与副模型
- 查看本地运行日志
- 查看服务状态

主副模型槽位为：

- `primary`
- `secondary`

每个槽位当前包含：

- `api`：目前支持 `OpenAI`
- `type`：`Text` 或 `Multimodal`
- `route`：`Responses` 或 `chat_completions`
- `model`
- `apikey`
- `base_url`（可选）

填写建议：

- `api`：写 `OpenAI`
- `type`：按文本模型或多模态模型选择
- `route`：按当前接入方式选择 `Responses` 或 `chat_completions`
- `model`：填写对应平台支持的模型名
- `apikey`：填写该平台的访问密钥
- `base_url`：直连官方时可留空；走代理、中转或兼容服务时再填写

如果你是从 [Software Center](https://github.com/PlaxtonFlarion/SoftwareCenter) 进入，请优先阅读 Software 首页内置的 `README`：其中包含环境变量、后台管理中心与基础使用说明。

### 推荐终端与环境变量

- Windows：推荐使用 `Windows Terminal`
- macOS：推荐使用 `iTerm2` 或系统 `Terminal`
- Windows 与 macOS 都建议先把 `mind` 所在目录加入 `PATH`
- 不推荐默认配置系统代理或挂 VPN；只有明确需要兼容网关时，再单独配置 `base_url`

常见环境变量示例：

macOS：

```bash
# Mind 示例
echo 'export PATH="/Applications/Mind.app/Contents/MacOS:$PATH"' >> ~/.zshrc

source ~/.zshrc
```

Windows：

```powershell
# Mind 示例（默认安装目录）
[Environment]::SetEnvironmentVariable(
  "Path",
  [Environment]::GetEnvironmentVariable("Path", "User") + ";C:\Program Files\Mind",
  "User"
)

$env:Path += ";C:\Program Files\Mind"
```

### 最小上手

```
# chat：先确认能力边界和做法
mind --chat "请用工程视角概述当前系统的核心能力、边界与典型使用场景"

# fast：做一个短链路任务
mind --fast "对 path/to/video.mp4 进行关键帧抽取，并返回可用证据"

# plan：执行一条更稳定的动作链
mind --plan "打开系统设置，稳定等待 2 秒后返回桌面"

# agent：进入订阅，等待服务端推任务
mind --agent
```

如果你要跑批量任务或协议用例，直接看 [命令行参数](#cli-arguments) 里的 `--code`，以及后面的 [接口实战](#playbook-api)。

### 交互式运行
启动 REPL：
```
mind
```

进入 REPL 后，可随时切换执行模式：
```
/chat
概述当前系统的核心能力、约束边界与推荐用法

/fast
对 path/to/video.mp4 做关键帧抽取，并输出可回链证据

/plan
进入设置页，短暂停留后返回桌面
```

常用指令：

- /help：查看指令索引
- /chat：切换到对话模式
- /fast：切换到高速模式
- /plan：切换到编排模式
- /quit：退出

REPL 是交互入口；真正决定执行方式的是 chat/fast/plan 这些执行模式。  
如果你需要完整指令说明，继续看后面的 [交互模式](#interactive-mode)。

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
- `mind --hello`

**`--hello` 里至少应该先配什么？**

- `primary.api`
- `primary.model`
- `primary.apikey`

建议同时补全 `secondary` 槽位，用于备用模型或多模态模型。

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

**批跑与回归**

- **宏编排声明层**：用 `--code`、`cfg` 和步骤编排承载批跑与回归

如果你已经知道当前任务方向：

- 设备 / UI：优先看 `前台状态收敛 + 滚动到可见区域 + 元素诊断`
- 接口 / 协议：优先看 `接口验证`
- 性能 / 稳定性：优先看 `Memrix + Framix + Monkey`
- 多媒体 / 证据链：优先看 `媒体提取 + scrcpy 录屏`
- 批跑 / 回归：优先看 `宏编排声明层`

---

<a id="modes"></a>
## ⭐️ 运行模式
**Mind** 提供三种本地主动执行模式：`--chat`、`--fast`、`--plan`。  
除此之外，还有一条独立的订阅入口：`--agent`。  
它们的差异不在“模型强弱”，而在“任务形态”和“执行边界”。

补充判断：

- `chat / fast / plan`：本地主动发起一次任务
- `agent`：本地先进入订阅，再等待服务端下发任务
- `agent` 不属于 REPL 内部状态；协议细节见 [订阅模式](agent-mode.md)

### 先这样判断

- **先问自己还在不在探索阶段**：如果还在确认能力边界、做法和路径，先用 `chat`
- **再问是不是短链路任务**：如果更像接口、媒体、文本或文件处理，优先用 `fast`
- **最后问是不是需要稳步骤**：如果更看重巡检、固定流程、回归和证据整齐，再用 `plan`

### 模式边界对齐

| 模式 | 任务形态 | 更适合 | 不建议主打 |
|------|----------|--------|------------|
| `chat` | 边探索边推进 | 探索、问答、临时任务、混合型接口/设备操作 | 追求最稳定步骤形态 |
| `fast` | 短链路快速完成 | 接口请求、事件流采样、媒体处理、短路径任务 | 设备/UI 执行、重型性能链路、需要全域工具时 |
| `plan` | 先定步骤再稳定执行 | 巡检、固定流程、批处理、需要步骤可读和更强可复盘性时 | 开放式多轮探索、边聊边改策略 |

### 具体怎么理解

- **`chat`**：默认入口，边探索边推进；适合问答、诊断和混合型任务
- **`fast`**：短链路执行面；优先服务接口、媒体、文件这类明确目标任务
- **`plan`**：稳路径执行面；更适合巡检、固定流程、回归和需要可读步骤时

补充说明：

- `plan` 除了顺序执行步骤，还承载执行过程中的规则判断
- `--code` 里的 `global_rule / rule` 属于星图规则层，不等同于 `plan` 的执行期规则判断

常见误判：

- `fast` 不是“轻量版 chat”，而是专门为短链路收窄过的执行面
- `plan` 不是“所有能力都更强”，它强调的是步骤稳定和顺序执行
- 接口能力统一归在协议与校验能力里，不需要把它理解成单独的 `api` 分类

### 常用命令

- `mind --chat "..."`：默认入口；适合探索、问答、混合型任务
- `mind --fast "..."`：适合接口、媒体、文件类短链路
- `mind --plan "..."`：适合巡检、固定流程和回归；先规划再执行
- `mind --agent`：适合订阅监听、远端任务下发和恢复重连链路

---

<a id="cli-arguments"></a>
## ⭐️ 命令行参数
Mind 的参数分两类：**互斥参数** 与 **兼容参数**。

- **互斥参数（Mutually Exclusive）**：一条命令里只能选 **一个**；用于确定“主运行协议/主入口”。  
  典型：`--chat | --fast | --plan | --agent`，以及 `--hello | --upgrade` 这类“单一动作入口”。  
- **兼容参数（Composable / Compatible）**：一条命令里可以叠加 **多个**；用于增强“归档、观测、批跑策略”等运行属性。  
  典型：`--gravity`、`--reflection`、`--code` 等。

> 心智模型：**互斥参数选“你要跑什么主模式”**；**兼容参数加“你要怎么跑、怎么记、怎么查”**。

### 先记住怎么组合

- 先选一个主入口：`--hello`、`--upgrade`、`--chat`、`--fast`、`--plan`、`--agent`
- 再叠加运行属性：比如 `--gravity`、`--reflection`
- 需要批跑或回归时，再挂上 `--code <path...>`
- `--code` 不替代主模式，它只是把一批任务交给你选定的执行协议去跑

### 常用速查
如果你只想先跑起来，先记住这 6 个入口：

| 场景 | 入口 | 什么时候用 |
|------|------|------------|
| 自然语言探索 | `mind --chat "..."` | 先问能力边界、混合型临时任务 |
| 快速短链路任务 | `mind --fast "..."` | 接口、媒体、文件类短任务 |
| 结构化执行 | `mind --plan "..."` | 需要步骤稳定、证据整齐 |
| 订阅监听 | `mind --agent` | 等待服务端下发任务、维持长链路 |
| 进入交互模式 | `mind` | 想在 REPL 里切换 `chat / fast / plan` |
| 给本次运行归档 | `mind --chat "..." --gravity <tag>` | 按项目、批次、版本聚合产物 |
| 批量执行星图 | `mind --chat --code <path...>` | 批跑、回归、规则化星图执行 |

建议的阅读顺序：
- 只想上手：先看 `--chat / --fast / --plan`
- 需要订阅监听：再看 `--agent` 和 [订阅模式](agent-mode.md)
- 想留痕归档：再看 `--gravity`
- 想调试链路：再看 `--reflection`
- 想批跑和回归：最后看 `--code`

### 中枢协议（参数互斥）
`--hello`

用于拉起本地后台管理中心面板，并统一管理模型配置、日志与服务状态：
- `primary`：主槽位，主执行链路默认读取这里
- `secondary`：备用槽位，可用于备用模型或多模态模型
- 每个槽位包含：`api / type / route / model / apikey / base_url`
- 可查看本地运行日志
- 可查看 MCP 服务状态
- 命令：`mind --hello`

示例：
```
# 拉起后台管理中心面板
mind --hello
```

### 奇点协议（参数互斥）
`--upgrade`

用于更新本地 **MCP 服务/运行组件** 到最新版本形态（拉取 → 校验 → 覆盖 → 切换）。

- 适用于：需要同步更新底层 MCP 能力集时
- 不参与 chat/fast/plan 执行链路：它是一个“单一动作入口”（执行完即退出）
- 命令：`mind --upgrade`

示例：
```
# 更新 MCP 服务到最新版本
mind --upgrade
```

### 折跃协议（参数互斥）
`--agent`

用于启动订阅模式，本地会注册会话并建立长链路，持续等待服务端下发任务。

- 适用于：远端调度、本地常驻监听、需要断线恢复与重连的任务接收场景
- 不属于 REPL 的 `CHAT / FAST / PLAN` 状态：它是独立 CLI 入口
- 服务端链路核心是 `/agents/open`、`/agents/ws`、`/agents/resume`
- 协议时序、消息类型和排障细节，直接看 [订阅模式](agent-mode.md)

示例：
```
# 启动订阅，等待服务端推送任务
mind --agent
```

### 引力协议（参数兼容）
`--gravity <tag>`

为本次运行设置 **引力标签（gravity tag）**，用于确定日志/报告的 **落盘根目录命名空间**：
- 同一 `tag` 的多次运行会被聚合到同一命名空间（便于按项目/版本/场景归档）
- 适用于：回归批次、灰度组、特性分支、实验编号、设备分组等
- 命令：`mind --chat "..." --gravity <tag>`

示例：
```
# 将本次执行的日志/报告归档到同一 gravity 命名空间
mind --plan "打开设置，等待2秒，然后截图" --gravity TEST_202602

# 高速链路归档（同标签可聚合多轮接口 / 媒体 / 分析产物）
mind --fast "对 path/to/video.mp4 抽帧并返回证据" --gravity Perf_Baseline_v1
```

### 反射协议（参数兼容）
`--reflection`

开启 详细调试视角，输出运行轨迹与关键决策信息（用于定位“为什么这么做”）：
- 打印：关键分支选择、执行路径、路由与决策依据（更丰富的 trace / debug 视角）
- 适用于：PoC 调试、工具链问题定位、计划偏航分析、线上回归异常复盘
- 命令：`mind --plan "..." --reflection`

示例：
```
# 开启详细运行轨迹输出（建议与 plan 联用）
mind --plan "打开App，等待3秒，返回桌面" --reflection

# 高速模式下查看链路细节（用于异常定位）
mind --fast "对 /graphql 端点执行查询并校验响应结构" --gravity Perf_v3 --reflection
```

建议：--reflection 会增加输出量，默认关闭；仅在需要追踪决策与链路细节时开启。

### 星图协议（参数兼容）
`--code <path...>`

用于装载一个或多个批量执行星图，并按选定协议执行。
- 支持 `.md / .txt`
- 可与 `--chat / --fast / --plan` 组合：决定这批星图按哪种主模式执行
- 一次可装载多份星图：`--code a.md b.md c.md`

文件格式：
`--code` 采用“自然语言块”作为用例单元：每个用例是一段文本，按 `---` 分隔。
- **分隔符**：单独一行 `---`（去掉空白后等于 `---`）用于分隔用例块
- **元信息（可选）**：每个用例块顶部可写多行 `# key: value`
  - 常用：`# name: xxx`（用于 `cfg.pattern` 正则筛选）
  - 其它字段也允许：`# tag: xxx`、`# owner: xxx` 等（会被解析进 meta）
- **正文**：元信息之后的所有内容，作为该用例的自然语言目标（交给 chat/fast/plan 执行）
- **空行**：块首尾空行会被自动忽略；正文为空的块会被跳过

入口层只需要记住：
- `--code` 适合批跑、回归和规则化执行
- 正文优先写自然语言，不必在入口文档里展开底层结构
- 真正的字段、层级和规则写法，直接看 [星图协议](cli-code.md)

#### 示例：
```
# 指定用 chat 协议装载一份星图
mind --chat --code http.md

# 指定用 fast 协议执行接口 / 媒体类星图
mind --fast --code media.md concurrent.md

# 指定用 plan 协议执行编排型星图
mind --plan --code workflow.md

# 一次装载多份星图
mind --chat --code http.md sse.md ws.md graphql.md
```

#### 文件样例：
```
# name: open_home
打开 `com.example.app`。
等待 `3` 秒。
回到桌面。
---

# name: quick_shot
打开相机。
等待 `1` 秒。
截图。
---
```

#### 一行写法：
```
# name: open_home
打开 `com.example.app`，等待 `3` 秒，回到桌面。
---

# name: quick_shot
打开相机，等待 `1` 秒，截图。
---
```

### 深入：三层前后置 + 星图规则层
`--code <path...>`

高级批跑说明已拆到独立正文：[星图深入说明](cli-code-advanced.md)。

这里先记住 5 个点就够了：
- `cfg` 支持批次级、轮次级和任务级前后置
- 任务级前后置现在分成两层：`item_prefix / item_suffix` 负责每个任务块外层包裹，`global_prefix / global_suffix` 负责单条任务正文前后置
- `global_rule` 是整份星图的默认规则文本，`rule` 是单任务覆盖规则文本
- `prefix/suffix` 会覆盖 `global_prefix/global_suffix`
- `repeat / pattern / attempts / stop_on_fail` 分别控制跑几轮、跑哪些、单条失败后怎么补救、整包是否继续
- 这里的 `global_rule / rule` 属于星图规则层，不等同于 `plan` 执行面的规则判断
- 需要完整执行顺序、覆盖优先级、多文件装载心智和常见误写时，直接看独立文档

---

<a id="interactive-mode"></a>
## ⭐️ 交互模式
完整 REPL 说明已拆到独立正文：[交互模式](interactive-mode.md)。

README 这里只保留入口层信息。

### 核心要点
- 启动 `mind` 即进入循环交互模式
- REPL 内部只有 `CHAT / FAST / PLAN` 三种互斥状态
- 已实现的是模式切换、模型切换、凭证切换和普通目标执行
- 批量重复执行优先用 `--code` 配合 `cfg.repeat / loop`，不要依赖未实现的 `/again`

### 常用指令
- `/help`
- `/chat`
- `/fast`
- `/plan`
- `/model <name>`
- `/apikey <key>`
- `/quit`

### 输入约束
- REPL 当前支持单行和多行输入
- 需要多任务编排或长文本星图时，直接改走 `--code`

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

<a id="playbook-performance"></a>
## ⭐️ 性能实战
完整性能案例和星图样例已拆到独立正文：[性能实战](playbook.performance.md)。

README 这里只保留入口层信息。

### 核心要点
- Framix 负责视觉真值与阶段报告
- Memrix 负责资源指标、趋势和稳定性采样
- 性能回归优先用 `mind --plan --code ...`
- Monkey 和长稳扰动场景建议写进星图，不要堆在命令行里

### 能力速览
- **视觉真值**
  入口：Framix 帧分析与阶段报告
- **指标采样**
  入口：Memrix 内存 / 流畅度 / 趋势对比
- **稳定性扰动**
  入口：Monkey + logcat 异常留痕
- **典型跑法**
  命令：`mind --plan --code ...` 或 `mind --chat "..."`

### 常见场景
- `E2E / ASR / VAD / tokens/s`
- `Android 内存基线 / 内存泄漏 / 流畅度`
- `Android Monkey`

---

<a id="playbook-api"></a>
## ⭐️ 接口实战
完整协议约定、helper 迁移和样例说明已拆到独立正文：[接口实战](playbook.api.md)。

README 这里只保留入口层信息。

### 核心要点
- 接口能力统一归在协议与校验能力里
- 协议覆盖 `HTTP / SSE / WebSocket / GraphQL / TCP / UDP / SMTP / IMAP / FTP`
- 单请求、批量请求、提取和验收都有稳定字段边界，细节直接看接口专题页
- 安全场景重点看星图结构、模板变量和通过条件，不必在 README 里保留运行回放

### 协议速览
- **基础请求**
  覆盖：`HTTP / SSE / WebSocket / GraphQL / TCP / UDP / SMTP / IMAP / FTP`  
  命令：`mind --chat --code api_case.md`
- **批量请求**
  覆盖：`nexus_*_batch`  
  命令：`mind --chat --code api_batch.md`
- **预执行检查**
  覆盖：`nexus_render_*` / `nexus_validate_*`  
  命令：`mind --chat --code api_check.md --reflection`
- **结果能力**
  覆盖：`extract` / `asserts` / 媒体落盘 / `fail_fast`  
  命令：`mind --chat --code api_case.md --gravity API_REGRESSION`

### 批量星图最小骨架
``````
# name: batch_case_name
设置共享变量，例如 `base_url = {{ env.base_url }}`、`token = {{ env.token }}`。
依次请求同一站点下的多个接口，每一项只补自己的差异参数。
对每个接口分别检查状态码和关键业务字段。
最后按统一规则判断整批是否通过。
---
`````` 

需要字段级骨架、`env / items / concurrency / fail_fast` 的真实写法时，直接看 [星图协议](cli-code.md) 和 [接口实战](playbook.api.md)。

### 本地 Mock
- README 不再内嵌 mock 服务代码
- 本地 mock 只需要覆盖请求字段、返回结构和验收条件
- 协议字段边界对齐 `nexus_*_request` 和 `nexus_*_batch`

---
<a id="playbook-media"></a>
## ⭐️ 多媒体链路
完整媒体命令、组合链路和星图任务已拆到独立正文：[多媒体链路](playbook.media.md)。

README 这里只保留入口层信息。

### 核心要点
- `fast` 模式适合媒体短链路任务
- 能力覆盖抽帧、裁剪、转码、拼接、换容器、音轨处理和播放验证
- 推荐顺序是 `probe -> trim / extract -> convert / replace -> play`
- 长视频优先先裁剪，再抽帧或转码
- 需要完整证据链或多步星图时，直接看独立文档

### 能力速览
- **抽帧取证**
  入口：`snapshot / frames / keyframes / scene`
- **视频处理**
  入口：`trim / scale / convert / concat / remux / mute`
- **音频处理**
  入口：`extract_audio / replace_audio / convert_audio / play`
- **组合链路**
  入口：多步串联的媒体预处理与证据链任务

### 常用命令
- `mind --fast "从 /path/to/demo.mp4 的第 3.5 秒抽取一张截图，并返回证据"`
- `mind --fast "把 /path/to/demo.mp4 从第 12 秒裁到第 25 秒，并输出 mp4 片段"`
- `mind --fast "从 /path/to/demo.mp4 提取关键帧，最多返回 8 张，并输出结果证据"`
- `mind --fast "从 /path/to/demo.mp4 提取音轨为 mp3，并返回输出文件"`

---

<a id="architecture"></a>
## ⭐️ 背景与架构
完整背景、云端架构和推理集群说明已拆到独立正文：[背景与架构](architecture.md)。

README 这里只保留最小摘要，避免首页继续变成架构白皮书。

### 核心要点
- 运行骨架是 `Mind + Helix` 的控制面 / 执行面分层
- 执行闭环核心是 `tool_call -> tool_result`
- 能力主要分成设备与 UI、协议与校验、基础能力、多媒体处理几类
- 接口能力归在协议与校验这一类
- 云端负责增强与治理，不接管端侧确定性执行

### 最小架构图
```text
Mind (CLI)
  ↓
Helix (MCP)
  ↓
设备与 UI / 协议与校验 / 基础能力 / 多媒体处理
```

### 阅读建议
- 只关心怎么用：README 前半部分就够了
- 需要看执行骨架、能力边界、云端增强和推理集群，再看独立文档

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
2. 本地自测：覆盖 `chat/fast/plan` 与 REPL 关键路径
3. 更新文档：新增/变更能力需同步 README；工具说明与维护约定看 [维护者指南](maintainer-guide.md)
4. 提交 PR：描述动机、设计、影响范围与回滚策略

> 建议：为新工具补齐 1 个最小示例任务（自然语言输入）+ 1 个产物截图/报告说明，方便业务侧快速验证。

---

## ⭐️ 特别鸣谢
......

---
