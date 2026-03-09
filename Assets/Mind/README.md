# 🚀 Mind :: 代理思维

![Mind](https://raw.githubusercontent.com/PlaxtonFlarion/SoftwareCenter/main/Assets/MindSource/app_readme.png)

**Mind 智能任务中枢**

**工具编排｜全链路可观测 · 可回放 · 可扩展**

**[Releases](https://github.com/PlaxtonFlarion/SoftwareCenter/releases) · [Assets](https://github.com/PlaxtonFlarion/SoftwareCenter/tree/main/Assets/Mind) · [Framix](https://github.com/PlaxtonFlarion/SoftwareCenter/tree/main/Assets/Framix) · [Memrix](https://github.com/PlaxtonFlarion/SoftwareCenter/tree/main/Assets/Memrix)**

---

- **[快速开始](#-快速开始-quick-start)**
- **[命令行参数](#-命令行参数-cli-arguments)**
- **[自研性能工具接口层](#-自研性能工具接口层-in-house-performance-tooling)**
  - **[Framix - 画帧秀](#framix--画帧秀--framix-interface-)**
  - **[Memrix - 记忆星核](#memrix--记忆星核--memrix-interface-)**
- **[性能实战教学](#-性能实战教学-performance-playbook)**
  - **[E2E 耗时、ASR 首字上屏、VAD 尾字上屏、流式 tokens/s](#e2e-耗时asr-首字上屏vad-尾字上屏流式-tokenss)**
  - **[Android 内存基线](#android-内存基线)**
  - **[Android 内存泄漏](#android-内存泄漏)**
  - **[Android 流畅度](#android-流畅度)**
  - **[Android Monkey](#android-monkey)**
- **[接口实战教学](#-接口实战教学-api-playbook)**
  - **[Http](#http-接口实战)**
  - **[SSE](#sse-接口实战)**
  - **[WS](#websocket-接口实战)**
  - **[GraphQL](#graphql-接口实战)**
- **[构建发布](#-构建发布-build--release)**

---

## 🏆 项目简介 (Project Overview)

**Mind** 把「一句话意图」拆成可执行步骤，并自动编排调用 **MCP 工具**：  
完成设备控制、数据采集、媒体处理、脚本编排等任务。

它既像一个可扩展的 **CLI Agent**，又像一个可插拔的 **自动化执行引擎**：  
轻量启动、链路可观测、结果可复现、过程可沉淀。

- **可组合**：Prompt / Resource / Tool 统一调度，工具即积木  
- **可复现**：同样输入得到同样流程与结果（可追踪、可回放）  
- **可扩展**：新增能力只需注册工具，无需改核心逻辑  

**项目代号**：Mind ｜ **中文名称**：代理思维 ｜ **产品定位**：智能代理执行框架

---

## ⭐️ 设计原则 (Design Principles)
传统自动化脚本与 RPA 在多工具协作、动态上下文与长期任务上存在断层，执行链路难以复用与回放。  
- **执行优先**：以工具调用为核心链路，确保任务可落地、可回放。  
- **约束优先**：`chat/fast` 模式遵循 `tool_call → tool_result` 闭环协议，`plan` 模式为单向链路执行。  
- **本地优先**：关键决策与执行留在端侧，降低时延与不确定性。  
- **工程优先**：授权、配置、可观测与回收机制齐备。  

与传统自动化对比：
- **传统层面**：脚本/流程固定、可复用性弱，跨系统编排成本高，遇到变化容易失效。  
- **智能代理**：以工具协议与编排为核心，支持动态路由与上下文管理，并保留可回放、可追踪的执行证据链。  

---

## ⭐️ 架构总览 (Architecture Overview)

Mind 面向工程交付，采用 **命令行作为唯一控制入口**，强调“可执行、可观测、可回放”。  
整体以 **控制面 / 执行面双进程分层** 为骨架，并通过 **MCP 工具协议**把能力按域组织为可插拔积木，形成稳定的 `tool_call → tool_result` 执行闭环。

### 1) 分层与职责

- **控制面（Mind）**：指令解析、会话编排、模型调度、任务路由、模式分流（chat/fast/plan）与结果聚合。  
- **执行面（Helix）**：工具注册与发现、调用生命周期管理、域隔离（automator/bench/common/media）、运行态监测与证据链落盘。  

> 结果：控制面只做“指挥与编排”，执行面只做“确定性落地”。崩溃/超时可隔离回收，链路更可控。

运行架构：
```
┌────────────┐
│  Mind      │
│  (CLI)     │
└─────┬──────┘
      │ 内部调用
      ▼
┌────────────┐
│  Helix     │
│  (MCP)     │
└─────┬──────┘
      │
      ▼
Tools: automator / bench / common / media
```

### 2) 三条执行通道
同一套工具能力，通过三条通道实现“探索—固化—回归”的闭环：
- **CHAT（探索通道）**：多轮交互 + 动态工具触发（适合探索与协作）
- **FAST（性能通道）**：性能采样/压测/长稳专用链路（适合指标与稳定性）
- **PLAN（确定通道）**：输出可复现的步骤链 → 顺序执行（适合回归/巡检/批处理）

### 3) 工具域与能力边界
能力按工具域注册与组合（工具即积木，域即边界）：
- `automator`：应用与系统控制、UI 操作链（启动/切换/按键、定位/点击/输入/滚动等）
- `bench`：性能与稳定性（指标采样、资源监控、长稳探测、端到端耗时）
- `common`：环境与基础能力（运行信息、文件与资源调度、通用工具）
- `media`：媒体能力（截图、录屏、音视频处理、帧级流水线/FFmpeg）

域隔离带来的工程收益：
- **能力可插拔**：新增能力只需注册工具，不改核心链路
- **风险可控制**：高危/高频工具与关键链路隔离，故障可局部熔断
- **交付可复制**：域能力可作为“标准件”跨项目复用

典型场景：
- 自动化巡检
- 设备操作
- 媒体处理流水线

### 4) 执行闭环与证据链
执行闭环：
```
模型流式生成意图
   ↓
Tool Call 触发执行动作
   ↓
Mind 任务中枢完成全局调度
   ↓
Arguments 增强链完成参数补强、纠偏与约束注入
   ↓
Helix 执行底座完成真实环境落地
   ↓
Enhancer 对执行结果进行结构化增强与证据封装
   ↓
多模态管线接管文件、视频、音频、图像等异构输入
   ↓
推理集群完成表征、检索、重排与视觉分析
   ↓
Tool Result 作为高质量证据回流模型上下文
   ↓
模型基于最新状态继续生成、决策与闭环推进
```

证据链体系（执行即留痕，结果可审计）：
- **链路标识**：cid/sid 贯穿一次会话/一次任务
- **证据落盘**：日志 + 媒体 + 指标 + 计划（plan）
- **可回放**：同输入/同计划可复现；PLAN 支持循环复现（/again）
- **可审计**：每一次 tool_call / tool_result 都可追踪、可复盘

### 5) 协议与传输
- **协议**：MCP 工具协议
- **传输**：streamable-http
- **鉴权**：Bearer Token

### 6) 云端增强与基础设施
- **核心**：端侧确定性执行 + 云端智能增强 —— 云端只增强“认知与策略”，不接管“确定性执行”。
- **增强**：检索/RAG、多模型路由、策略下发、知识与模板管理
- **治理**：配额与租户隔离、灰度/金丝雀、可观测与告警

---

## ⭐️ 云端架构 (Cloud Architecture)
Mind 的核心路线是：**端侧确定性执行 + 云端智能增强**。  
云端层只负责“让系统更聪明”（认知/策略/治理），**不接管确定性执行**，从而把不确定性关在门外，把可交付性留在链路里。

### 1) 云端职责边界
云端负责：
- **增强层**：检索/RAG、知识与模板管理、多模型路由、策略下发、自愈与回退策略
- **治理层**：租户隔离、配额与限流、鉴权与审计、灰度/金丝雀、版本管理
- **观测层**：全链路 Metrics/Tracing/Logs、告警与异常归因、回归追踪

云端不负责：
- 不直接操控端侧设备与执行工具（执行仍由 Helix 承担）
- 不把关键执行路径托管到不确定的远端调用（保证链路可控与可复现）

### 2) 参考组件栈
| 分类                 | 组件                        |
|--------------------|---------------------------|
| 网关 (Gateway)       | Cloudflare                |
| 缓存 (Cache)         | Redis                     |
| 存储 (Storage)       | Supabase Postgres + R2    |
| 检索 (Retrieval)     | Embedding / Rerank / 向量索引 |
| 推理 (Inference)     | GPU 容器化推理集群               |
| 观测 (Observability) | Metrics / Tracing / Logs  |
| 保障 (Reliability)   | 灰度发布 / 金丝雀路由              |

> 说明：该栈用于支撑 “增强链路 + 治理能力 + 可观测体系”，执行闭环仍以端侧 Helix 为主。

### 3) 云端分层
#### 执行层 (Helix)
**Helix** 在云端/本地均可作为 **MCP 工具宿主与执行闭环**：
- MCP 工具服务与执行闭环
- 健康检查与运行态监测
- 低延迟本地调用通道
- 证据链落盘与产物归档（日志/媒体/指标/计划）

默认接口（示例）：
- MCP：`/helix/mcp`
- Health：`/healthz`
- Ready：`/ready`
- Idle：`/idle`

生命周期（示例约定）：
- Helix 为独立子进程/服务，由 Mind 拉起或编排部署
- 空闲超过阈值（如 30 分钟）触发关闭与资源回收
- 请求/工具调用刷新 idle 计时，关闭时完成会话清理与产物落盘

#### 云端控制层 (AppServerX)
**AppServerX** 是云端的“增强与治理中枢”：
- **控制与编排**：模型/工具元数据中心，远程配置与策略下发
- **检索与增强**：多路召回、Rerank、RAG 与向量检索协同
- **安全与网关**：WAF、零信任访问控制、API 速率限制、审计与追踪
- **缓存与队列**：Redis、消息队列、延迟任务调度
- **数据层**：Postgres、对象存储、冷热数据分层
- **观测体系**：Metrics / Tracing / Logs 统一可观测与告警
- **模型基础设施**：模型注册、版本路由、灰度/金丝雀发布
- **GPU 推理**：统一推理入口、弹性扩缩容、多模型并行与版本切换
- **测试中台**：自动化流程验证、性能基准回归与稳定性测试

### 4) 云端增强闭环
**AppServerX** 将推理能力与测试中台打通，形成统一的编排、执行与回归闭环：
```
请求入口
  ↓
统一鉴权与网关
  ↓
路由与排队（模型/策略/队列）
  ↓
GPU 推理容器集群（多模型并行）
  ↓
结果聚合与策略回填
  ↓
指标采集 / 报告生成 / 回归追踪
  ↓
告警与异常归因（可观测体系）
```

### 5) 设计目标
- **可控性**：策略与增强可演进，但不破坏端侧确定性执行
- **可观测**：端云同链路追踪（与 `cid/sid` 对齐），可审计可复盘
- **可治理**：租户隔离、配额、灰度发布、回滚机制完善
- **可扩展**：模型与检索组件可插拔，推理集群弹性扩缩容

---

## ⭐️ 推理集群 (Inference Fabric)

Mind 的云端增强能力由 **推理集群**承载：构建面向“低延迟在线推理 + 批处理回归”的统一推理底座。  
目标不是“跑模型”，而是提供一套可治理、可观测、可演进的 **Inference Fabric**：让多模型协同像微服务一样可控、可回滚、可压测。

如果说 Mind 的端侧执行层负责“把事做成”，那么推理集群负责“把事做对、做稳、做快”：  
**把 GPU 从算力资源升级为可编排能力池**，把推理从一次调用升级为一套可运营的工程系统。

### 1) 设计定位：多模型协同的推理底座
集群承担两类核心任务：
- **在线推理（Online Serving）**：高并发、低抖动、稳定 P99，面向业务请求与 Agent 增强链路  
- **离线批处理（Batch & Regression）**：大规模回归、基线对比、数据回灌、模型验证与持续评估  

统一目标：交付 **可控智能** 与 **确定性增强** —— “聪明”可以升级，“确定性”不能丢。

> 推理集群的价值不在“能推理”，而在“可控地推理”：可观测、可灰度、可回滚、可压测、可对比。

### 2) 模型矩阵：检索 × 重排 × 视觉理解 
集群内置一套“检索-重排-视觉”的标准协同栈，覆盖 Agent 的关键决策与多模态理解。

#### Cross Encoder（重排核心）
- 用于候选集 **精排/重排**：在多路召回之后提供高精度相关性判定  
- 典型用途：工具选择精排、RAG 片段重排、多候选计划收敛  

> Cross Encoder 是增强链的“裁判”：负责把“可能正确”收敛为“最优正确”。

#### BGE（通用向量表征）
- 多语种/多任务向量嵌入，用于：语义召回、意图↔模板匹配、工具/知识索引  
- 与 Cross Encoder 形成经典组合：**BGE 负责召回，Cross Encoder 负责收敛**。  

#### 视觉双栈：灰度 CNN × 彩色 CNN (Vision Dual Stack)

> 注意：这里的“灰度/彩色”指 **输入图像模态**（灰度图/彩色图），不是发布策略。

- **灰度 CNN（Gray CNN）**：面向灰度输入的视觉判别器  
  - 强项：结构/边缘/形状一致性、对色彩扰动不敏感  
  - 典型用途：界面状态确认（加载/卡顿/遮罩）、版式一致性、对比度敏感异常检测、OCR 前置质量判别  

- **彩色 CNN（Hued CNN）**：面向彩色输入的视觉判别器  
  - 强项：色彩语义、主题/皮肤变化、色块/提示条/高亮状态识别  
  - 典型用途：状态条/提示色识别（成功/失败/警告）、主题切换一致性、颜色驱动的 UI 状态机判别  

> 两者是互补的“视觉传感器”：灰度负责**结构真值**，彩色负责**语义颜色**。

#### YOLO（目标检测）
- 面向 UI 元素/目标区域检测：定位按钮、弹窗、图标、提示条等  
- 与自动化链路联动：为 `automator` 提供可视锚点，提高复杂场景鲁棒性  

### 3) 统一推理流水线：一条链路，多段决策
推理集群不只是“挂几张模型卡”，而是把推理做成 **可编排的流水线**：每一段都有输入/输出、有指标、有回退。

典型增强链：
1. **BGE 语义召回**：召回候选工具/知识片段/计划模板  
2. **Cross Encoder 精排**：收敛到最优候选（工具/片段/计划）  
3. **视觉模型（灰度 CNN / 彩色 CNN / YOLO）**：关键帧状态确认与目标定位  
4. **策略层**：按任务类型/场景模板选择视觉栈与阈值（并定义回退路径）  
5. **返回增强结果**：为 Mind 端侧执行链提供“更稳的决策输入”，但不夺权于端侧执行  

Mind 保持原则：**云端增强负责“更聪明”，端侧执行负责“更确定”。**  
推理集群只做“增益”，不做“夺权”。

### 4) 可观测性：把推理变成可审计工程
推理集群的“爆点”在于：它让推理像工程系统一样 **可度量、可定位、可回归**。
- **链路标识**：与 Mind 的 `cid/sid` 对齐，实现端云同链路追踪  
- **关键指标**：
  - 延迟：P50 / P95 / P99（按模型、按流水线阶段、按租户/场景分桶）
  - 质量：重排增益、召回命中、检测稳定性、状态判别一致性（按模板/场景分桶）
  - 稳定性：超时率、失败率、回退率、抖动（按任务类型/设备/版本分组）

> 推理集群不是“调用 AI”，而是“交付可控智能”：能压测、能对比、能回滚、能复盘。

### 5) 工程化能力：灰度 / 回滚 / 压测 / 回归
推理集群把“模型上线”变成可运营流程：
- **灰度发布**：按租户/场景/流量比例逐步放量，观测指标守门  
- **快速回滚**：版本/权重/策略一键回退，确保异常不扩散  
- **压测基准**：在线 P99 与离线吞吐都有基线；每次升级必须跑过基准门槛  
- **回归体系**：批处理回归自动产出对比报告，定位“变好/变坏”的具体阶段  

### 6) GPU 选型：工程稳定与吞吐密度的黄金平衡
GPU 定位于“稳定在线推理”的甜点区间：
- 适合承载 **多模型并行**（召回/重排/分类/检测）与混合负载  
- 在成本、吞吐、部署密度之间取得工程级平衡  
- 对应 Mind 的目标：把增强能力做成长期可运营的基础设施，而不是一次性实验  

> 结论：推理集群是一台“智能的工厂流水线”，不是一张“会算的显卡”。

### 7) 策略大脑：路由、编排与自愈
推理集群真正“炸裂”的地方，是它不仅推理，还会 **管推理**：  
把模型、检索、重排、视觉、阈值与回退全部纳入同一套策略体系，形成可演进的“策略大脑”。
- **动态路由**：按任务类型/场景模板/租户等级/预算门槛，选择最合适的模型组合与流水线  
- **分段熔断**：某一段质量或延迟异常，自动降级跳段（如跳过视觉、降低重排强度、收敛候选数量）  
- **自愈回退**：失败不扩散，优先回退到“可交付的确定性路径”（宁可保守，也不翻车）  
- **策略审计**：每一次路由选择都有证据与理由，支持复盘与持续迭代  

> 推理集群不是“模型集合”，而是“策略驱动的推理操作系统”：让聪明变得可控，让升级变得可回滚。

### 8) 工程资产化：把智能变成可复用的积木

推理集群的最终形态，是把“智能”做成可复用、可组合、可迁移的工程资产：

- **模板化增强链**：常见任务沉淀为模板（检索→重排→视觉→阈值→回退），一键复用到不同业务  
- **场景分桶运营**：按场景/设备/版本建立质量画像与基线，做到“哪里变差一眼看穿”  
- **数据闭环飞轮**：在线日志与离线回归互相喂养，持续提升召回、重排与视觉稳定性  
- **成本可控**：按租户/任务分级计费与预算，做到“该省省、该猛猛”——花钱花在增益最大处  

> 这就是 Inference Fabric：把推理从一次 API 调用升级为可运营的“智能供给体系”。  
> 把“聪明”变成资产，把“增强”变成确定性增益，把“升级”变成工程常态。

---

## ⭐️ 快速开始 (Quick Start)

Mind 有两种运行方式：

- **命令行模式**：每条命令执行一次任务，适合脚本/CI
- **交互式模式**：进入循环交互，可在 chat/fast/plan 间随时切换，适合探索与调试

### 1) 命令行运行 (One-shot)
```
# 对话
mind --chat "你好，介绍一下系统能力"

# 性能
mind --fast "开始录屏，打开App，等待3秒，返回桌面，结束录屏，执行2次，分析阶段帧并生成报告"

# 编排
mind --plan "打开设置，等待 2 秒，然后截图看看有什么"

# HTTP 接口
mind --chat --file http.md

# SSE 事件流采样
mind --chat --file sse.md

# WebSocket 连接与收发
mind --chat --file ws.md
```

### 2) 交互式运行 (REPL)
启动 REPL：
```
mind
```

在 REPL 里切换模式并执行目标：
```
/chat
你好，介绍一下系统能力

/fast
开始录屏，打开App，等待3秒，返回桌面，结束录屏，执行2次，分析阶段帧并生成报告

/plan
打开设置，等待 2 秒，然后截图
```

常用指令：

- /help：查看指令索引
- /chat：切换到对话模式
- /fast：切换到性能模式
- /plan：切换到编排模式
- /quit：退出

REPL 是“持续读取输入”的交互壳；真正的执行语义由 chat/fast/plan 三种模式决定。

---

## ⭐️ 命令行运行 (CLI Modes)

Mind 提供三种互斥运行模式：

| 模式       | 说明   |
|----------|------|
| `--chat` | 对话模式 |
| `--fast` | 性能模式 |
| `--plan` | 编排模式 |

### 对话模式（chat）

```
mind --chat "你好，介绍一下系统能力"
```

定位：流式对话驱动模式。

特征：

- token-by-token 流式输出
- 多轮上下文保持
- 动态工具触发

### 性能模式（fast）

```
mind --fast "开始录屏，打开App，等待3秒，返回桌面，结束录屏，执行5次"
```

定位：纯性能执行模式。

特征：

- 不调用 automator 域能力
- 仅使用自研性能工具体系
- 偏向高吞吐与低延迟执行路径

性能模式包含：

- 自研性能工具接口层
- 指标采样
- 资源监控
- 压测链路
- 稳定性探测

适用于：

- 性能压测
- 长时间运行测试
- 资源消耗对比
- 指标基准评估

### 编排模式（plan）

```
mind --plan "打开App，等待3秒，返回桌面"
```

定位：确定性自动化编排模式。

特征：

- 输出结构化行动序列
- 强工具链路组织
- 可复现执行路径
- 强调步骤拆解与顺序控制
- 单向执行链路

执行抽象：

```
意图识别
   ↓
任务拆解
   ↓
生成有序工具计划
   ↓
顺序执行
```

适用于：

- 自动化巡检
- 批量流程执行
- 设备操作链路
- 可复现工作流

---

## ⭐️ 交互式运行 (Interactive Mode)

除了 `mind --chat | --fast | --plan` 的一次性命令模式外，Mind 还支持 **循环交互模式**（REPL）。  
该模式下会持续读取用户输入，并在 **CHAT / FAST / PLAN** 三种互斥状态之间切换执行。

### 启动与提示

`mind` 进入循环后，终端会显示当前模式与正在使用的 `<model>`：

- 顶部 banner 会随模式变化：Chat / Fast / Plan
- 每轮输入提示：`ready 输入目标或 /help`

> `mind_loop()` 会为一次会话生成 `cid/sid` 并贯穿本轮交互，用于链路追踪与调用元数据。

### 指令索引

在任意模式下输入 `/help` 可查看指令索引：

- `/help, /h`：指令索引（用法/示例/约定）
- `/license, /lic`：授权许可（License/特性）
- `/subscription, /sub`：订阅信息（授权状态/到期）
- `/quit, /q, quit, exit`：安全退出（断开会话）
- `/model <name>`：引擎切换（选择推理内核）
- `/apikey <key>`：凭证更新（替换访问密钥 / Token）
- `/again N <goal>`：复现回放（目标 × N 次）**仅在 PLAN 模式生效**
- `/chat`：切换到对话模式（CHAT）
- `/fast`：切换到性能模式（FAST）
- `/plan`：切换到编排模式（PLAN）

### 三种互斥运行状态（交互态）

循环模式内部有一个状态机：`CHAT` / `FAST` / `PLAN`，同一时刻只会处于其中一个状态。

| 状态   | 说明           | 选择指令    |
|------|--------------|---------|
| CHAT | 对话驱动（流式，多轮）  | `/chat` |
| FAST | 性能执行（性能路径）   | `/fast` |
| PLAN | 编排执行（确定性步骤链） | `/plan` |

切换时会输出类似：

- `Exchange → Chat`
- `Exchange → Fast`
- `Exchange → Plan`

### `/again` 循环复现（仅 PLAN）

`/again` 只在 **PLAN** 状态下生效，用于把一个目标重复执行 N 次（用于复现、回放、稳定性验证）：

```
/plan
/again 5 打开App，等待3秒，返回桌面
```

行为语义：

- 仅当 **tag == PLAN** 且命中 `/again N <goal>` 时生效
- 实际发送给执行器的 message 会被改写为：`<goal>，循环 N 次`
- 如果不在 PLAN 状态输入 `/again ...`，会被当作普通文本目标处理（不会进入循环语义）

### `/model` 引擎切换（带候选提示）
/model gpt-4o-mini

当输入无效或缺失时，会打印候选列表（示例）：

- `llama-3.3-70b-versatile`
- `openai/gpt-oss-120b`
- `gpt-4o-mini`
- `deepseek-chat`

并输出形如：`model invalid: /model <...>` 的错误提示。

> 切换成功后，本轮循环后续调用均使用新的 `model`。

### `/apikey` 凭证更新（带格式提示）
当输入无效或缺失时，会打印可接受的格式提示（示例）：

- `sk-...   (API Key)`
- `gsk_...  (API Key)`
- `ds-...   (API Key)`
- `<token>  (Pure token)`

并输出形如：`apikey invalid: /apikey <...>` 的错误提示。

> 切换成功后，本轮循环后续调用均使用新的 `apikey`。

### `/license` 与 `/subscription`

- `/license`（或 `/lic`）：展示授权许可信息页（License/特性）
- `/subscription`（或 `/sub`）：读取本地 License 文件并执行校验流程（授权状态 / 到期信息）

> `/subscription` 会调用本地授权验证（例如 `authorize.verify_license(<lic_file>)`），适合快速确认当前机器的授权是否有效。

### 退出

任意时刻输入以下任一指令即可安全退出循环：
```
/quit
/q
quit
exit
```

---

## ⭐️ 输入约束 (Input Constraint: Single Line Only)

Mind 当前在以下所有入口都以 **单行提交** 作为基本输入单位：

- `--chat`（对话模式）
- `--fast`（性能模式）
- `--plan`（编排模式）
- 循环交互模式（REPL / mind）

### 约束说明

- **多行输入（含粘贴多行）目前不支持**：终端会将多行拆分为多次提交，导致输入的 **边界 / 顺序 / 归属** 无法保证。
- 因此，Mind 不保证多行文本在 `chat / fast / plan / mind` 中作为一个“原子输入”被处理。

---

## ⭐️ 命令行参数 (CLI Arguments)
Mind 的参数分两类：**互斥参数** 与 **兼容参数**。

- **互斥参数（Mutually Exclusive）**：一条命令里只能选 **一个**；用于确定“主运行协议/主入口”。  
  典型：`--chat | --fast | --plan`，以及 `--pref | --upgrade` 这类“单一动作入口”。  
- **兼容参数（Composable / Compatible）**：一条命令里可以叠加 **多个**；用于增强“归档、观测、批跑策略”等运行属性。  
  典型：`--gravity`、`--reflection`、`--file`、`--repeat`、`--pattern` 等。

> 心智模型：**互斥参数选“你要跑什么主模式”**；**兼容参数加“你要怎么跑、怎么记、怎么查”**。

### `--pref`：基线协议（参数互斥）
用于打开/定位本地配置文件（偏好设置），以便持久化默认参数：
- `api`：默认模型 API 提供方（如 OpenAI / Groq）
- `model`：默认推理引擎 / 模型名
- `apikey`：默认访问密钥 / Token
- `base_url`：自定义 API Base URL（可选；为空则使用官方默认）

示例：
```
# 打开配置文件（首次自动生成）
mind --pref
```

### `--upgrade`：奇点协议（参数互斥）
用于更新本地 **MCP 服务/运行组件** 到最新版本形态（拉取 → 校验 → 覆盖 → 切换）。

- 适用于：需要同步更新底层 MCP 能力集时
- 不参与 chat/fast/plan 执行链路：它是一个“单一动作入口”（执行完即退出）

示例：
```
# 更新 MCP 服务到最新版本
mind --upgrade
```

### `--gravity <tag>`：引力协议（参数兼容）
为本次运行设置 **引力标签（gravity tag）**，用于确定日志/报告的 **落盘根目录命名空间**：
- 同一 `tag` 的多次运行会被聚合到同一命名空间（便于按项目/版本/场景归档）
- 适用于：回归批次、灰度组、特性分支、实验编号、设备分组等

示例：
```
# 将本次执行的日志/报告归档到同一 gravity 命名空间
mind --plan "打开设置，等待2秒，然后截图" --gravity TEST_202602

# 性能批次归档（同标签可聚合多轮压测产物）
mind --fast "开始录屏...结束录屏，执行5次" --gravity Perfermance_Baseline_v1
```

### `--reflection`：反射协议（参数兼容）
开启 详细调试视角，输出运行轨迹与关键决策信息（用于定位“为什么这么做”）：
- 打印：关键分支选择、执行路径、路由与决策依据（更丰富的 trace / debug 视角）
- 适用于：PoC 调试、工具链问题定位、计划偏航分析、线上回归异常复盘

示例：
```
# 开启详细运行轨迹输出（建议与 plan 联用）
mind --plan "打开App，等待3秒，返回桌面" --reflection

# 性能模式下查看采样/链路细节（用于异常定位）
mind --fast "开始录屏...结束录屏，执行5次" --gravity Perf_v3 --reflection
```

建议：--reflection 会增加输出量，默认关闭；仅在需要追踪决策与链路细节时开启。

### `--file <path>`：卷宗协议（参数兼容）
从文件中读取多条自然语言用例，并按选定协议批量执行：
- 支持 `.md/.txt`
- 可与 `--chat/--fast/--plan` 组合：指定批跑使用的主序协议
- 若仅传 `--file` 未指定协议，默认按 `--plan` 批跑

文件格式：
`--file` 采用“自然语言块”作为用例单元：每个用例是一段文本，按 `---` 分隔。

- **分隔符**：单独一行 `---`（去掉空白后等于 `---`）用于分隔用例块
- **元信息（可选）**：每个用例块顶部可写多行 `# key: value`
  - 常用：`# name: xxx`（用于 `--pattern` 正则筛选）
  - 其它字段也允许：`# tag: xxx`、`# owner: xxx` 等（会被解析进 meta）
- **正文**：元信息之后的所有内容，作为该用例的自然语言目标（交给 chat/fast/plan 执行）
- **空行**：块首尾空行会被自动忽略；正文为空的块会被跳过

示例：
```
指定用 chat 协议批跑
mind --chat --file pack.md

指定用 fast 协议批跑（可叠加 gravity / reflection）
mind --fast --file pack.md --gravity Perf_v1 --reflection

指定用 plan 协议批跑
mind --plan --file pack.md
```

文件样例：
```
# name: open_home
打开抖音
等待 3 秒
回到桌面
---

# name: quick_shot
打开相机
等待 1 秒
截图看看有什么
---
```

一行写法：
```
# name: open_home
打开抖音，等待 3 秒，回到桌面
---

# name: quick_shot
打开相机，等待 1 秒，截图看看有什么
---
```

进阶：三层前后置

格式约定：
- 顶部可包含一个 ` ```cfg ` 配置块：必须以 ` ```cfg` 开始，并以独立一行 ` ``` ` 结束
- cfg 多行字段推荐两种写法：
  - `key: |`（缩进块，适合中等长度）
  - `key: <<<` ... `>>>`（超长文本，适合规则说明）
- 用例仍用 `---` 分隔；每个用例块顶部支持 meta：`# key: value`
  - 支持多行 meta：`# key:` 后跟多行 `# ...`
  - 常用：`# name:` / `# prefix:` / `# suffix:` / `# rule_suffix:`

前后置层级：
- loop_prefix / loop_suffix：整个批跑的前置/后置（仅执行一次）
- round_prefix / round_suffix：每一轮的前置/后置（每轮执行一次）
- global_prefix / global_suffix：每条的默认前置/后置（每条执行一次）
- prefix / suffix：单条的前置/后置（存在则覆盖对应 global_*）

规则后置（增强版后置，可选）：
- global_rule_suffix：全局默认的“规则后置”（写在 cfg 块中；自由文本，用于证据/断言/打分等增强规则）
- rule_suffix：单条的“规则后置”（写在用例 meta 中；存在则覆盖 global_rule_suffix）

``````
```cfg
loop_prefix: |
  [LP] 批跑开始前：环境准备（一次）
loop_suffix: |
  [LS] 批跑结束后：环境清理（一次）

round_prefix: |
  [RP] 每轮开始：统一初始化（每轮一次）
round_suffix: |
  [RS] 每轮结束：统一收尾（每轮一次）

global_prefix: |
  [GP] 每条前置：通用准备（每条一次）
global_suffix: |
  [GS] 每条后置：通用收尾（每条一次）
  
 global_rule_suffix: <<<
【证据/断言/评分（自由文本）】
- 这里随便写规则：截图策略、UI断言描述、评分说明等
- 执行层暂时不需要解析结构，也可以直接作为“增强后置说明”附加给模型
>>>
```

# name: case_001
# prefix:
# [P1] 仅本条前置：覆盖 global_prefix
# suffix:
# [S1] 仅本条后置：覆盖 global_suffix
# rule_suffix: <<< 
# 这里写本条的“规则后置”（覆盖 global_rule_suffix）
# >>>
这里是正文（自然语言目标）。
---

# name: case_002
这里是正文（未写 prefix/suffix/rule_suffix，将使用 global_prefix/global_suffix/global_rule_suffix）。
---
``````

超长文本示例：
``````
```cfg
global_prefix: <<<
【占位符/填充字段规则（示例）】
>>>

global_suffix: <<<
【占位符/填充字段规则（示例）】
>>>

global_rule_suffix: <<<
【占位符/填充字段规则（示例）】
>>>
```
``````

超长文件样例：
``````
```cfg
global_prefix: <<<
base_url = http://127.0.0.1:18080
time_out = 10
concurrency = 2
>>>
```

# name: http
请求 /http 来验证解析与 ok 判定。

payload = {
    "kind": "json"
}

# rule_suffix: <<<
# PASS 条件：
# - ok == true
# - type == "http"
# - detail.response.status == 200
# - detail.response.body_json 不为空（能解析 JSON）
# - detail.response.body_json.ok == true
# >>>
---

# name: sse
从 /sse 拉取前 5 条事件，并验证 event/id/data 字段齐全（coalesce=true 以覆盖粘包场景）。

payload = {
    "max_events": 5, 
    "interval_ms": 20, 
    "coalesce": true
}

# rule_suffix: <<<
# PASS 条件：
# - step.type == "sse"
# - step.ok == true
# - step.detail.status == 200
# - step.detail.events 为数组，长度 == 5
# - events[i] 结构：
#  - 有 event 字段（字符串；hello/message/done 之一）
#  - 有 id 字段（字符串/数字皆可，最终应可 stringify）
#  - 有 data 字段（字符串；可被 json.loads 成对象更佳，但不强制）
# - 若 coalesce=true：仍应能稳定拿到 5 条（说明 buffer split 正常）
# >>>
---

# name: ws
连接 ws://127.0.0.1:18080/ws，依次发送 ping 与 close，收集最多 10 条消息并做断言。

payload = {
    "sends": ["ping", "close"]
}

# rule_suffix: <<<
# PASS 条件：
# - step.type == "ws"
# - step.ok == true
# - step.detail.messages 为数组，至少包含：
#   - "hello"（服务端 accept 后的首条）
#   - "echo:ping"（发送 ping 后的回声）
#   - "closing"（发送 close 后的关闭前提示；可有可无）
# - 若返回里有 error 字段：
#   - 在 ok==true 时 error 应为 null/None/空
# >>>
---
``````

### --repeat <N>：回声协议（参数兼容）

重复执行整份 --file 中的用例列表 N 次：
- 默认 1
- 适用于：稳定性回归、偶现问题复现、压力/长稳批跑

示例：
```
# 将 pack.md 全量重复执行 3 次
mind --plan --file pack.md --repeat 3
```

### --pattern <REGEX>：棱镜协议（参数兼容）

通过正则表达式筛选要执行的条目（匹配块内的 `name` 字段）：

- 未指定时默认执行全部
- 仅对 `--file` 批量执行生效
- 建议在每个块头写 `# name: xxx`，便于筛选与复用

示例：
```
# 只跑 name 命中 open 的条目
mind --plan --file pack.md --pattern "open"

# 跑 name 命中 open 或 shot 的条目
mind --plan --file pack.md --pattern "open|shot"
```

---

## ⭐️ 自研性能工具接口层 (In-house Performance Tooling)
**Mind** 的性能体系不是“跑一堆指标然后祈祷”，而是把 **采集 → 对齐 → 归因 → 回归** 做成工程闭环。  
这一层的定位是：**把端侧真实世界的性能信号，变成可对比、可复盘、可运营的标准产物**。

它不是附属功能，而是 Mind 的“第二条生命线”：  
端侧执行负责“把事做成”，性能接口层负责“把事做稳、做快、做得可证明”。

### [Framix · 画帧秀 (Framix Interface)](https://github.com/PlaxtonFlarion/SoftwareCenter/tree/main/Assets/Framix)
**Framix** 专注 **视觉驱动的端到端耗时**：用画面真值对齐链路时序，把“体感卡不卡”翻译成可量化的时间线。
- **视觉 E2E 真值**：基于关键帧/状态变化定义起止点，避免埋点缺失或口径漂移  
- **端侧链路采集**：贴近设备真实表现，覆盖渲染、动效、加载、遮罩、跳转等肉眼可见路径  
- **时序对齐引擎**：把视频帧、事件、日志、工具调用时间戳对齐成同一条时间轴  
- **关键路径评估**：输出关键阶段耗时、瓶颈段落、稳定性抖动与对比结论  
- **结果可回放**：每个结论都能回到对应帧与证据（“为什么慢”可定位，不是猜）

> Framix 的爆点：把“感觉慢”变成“证据链上的慢”，把 E2E 性能从玄学拉回工程。

### [Memrix · 记忆星核 (Memrix Interface)](https://github.com/PlaxtonFlarion/SoftwareCenter/tree/main/Assets/Memrix)
**Memrix** 专注 **Android 性能数据采集与稳定性量化**：把资源变化从“某次偶现”升级为“可回归的趋势结论”。
- **多指标覆盖**：内存、流畅度、IO 等关键指标统一采集与落盘  
- **长稳压友好**：支持高频采样与长时间运行，适配性能模式的吞吐路径  
- **趋势化分析**：不仅看单点数值，更看斜率、抖动、回收效率、长期漂移与异常簇  
- **证据链产物**：指标曲线、阶段统计、异常片段与上下文（cid/sid、场景、设备、版本）一并沉淀  
- **回归可对比**：同一场景多轮对比，输出“变好/变坏”与影响范围，而不是一堆孤立数字

> Memrix 的爆点：把“看监控”升级为“做回归”——让性能问题可复现、可量化、可追踪。

### 组合拳：视觉真值 × 指标宇宙 (Framix × Memrix)
这层接口最强的地方在于：**Framix 给出“用户看到的真相”，Memrix 给出“系统内部的原因”**，两者合在一起就是性能工程的黄金闭环：
- Framix 定位 **哪一段慢**（E2E 时间线真值）
- Memrix 解释 **为什么慢**（资源/趋势/稳定性信号）
- Mind 把两者绑定到同一 `cid/sid` 证据链，形成 **可回放、可审计、可回归** 的性能交付件

> 结论：这不是两个工具接口，这是一个“性能事实系统”：  
> 用视觉锚定真值，用指标解释原因，用回归保证不再复发。

---

## ⭐️ 性能实战教学 (Performance Playbook)

### E2E 耗时、ASR 首字上屏、VAD 尾字上屏、流式 tokens/s
``````
```cfg
loop_suffix: |
  生成视频帧阶段报告
  
round_suffix: |
  Framix 分析视频帧
>>>
```

# name: performance-001
  开始录屏，打开APP首页，等待输入框出现，点击输入框，输入"你好"，点击发送，等待回复完成，结束录屏，执行3次
---
``````

运行命令
```
mind --plan --file example.md
```

### Android 内存基线
``````
```cfg
loop_suffix: |
  生成分层内存测试报告

round_prefix: |
  开始采集内存
  
round_suffix: |
  结束采集内存
>>>
```

# name: performance-001
  打开APP首页，等待输入框出现，点击输入框，输入"你好"，点击发送
---
``````

运行命令
```
mind --plan --repeat 3 --file example.md
```

### Android 内存泄漏
``````
```cfg
loop_suffix: |
  生成内存测试报告

round_prefix: |
  开始采集内存
  
round_suffix: |
  结束采集内存
>>>
```

# name: performance-001
  打开APP首页，等待输入框出现，点击输入框，输入"你好"，点击发送，执行10次
---
``````

运行命令
```
mind --plan --file example.md
```

### Android 流畅度
``````
```cfg
loop_suffix: |
  生成流畅度测试报告

round_prefix: |
  开始采集流畅度
  
round_suffix: |
  结束采集流畅度
>>>
```

# name: performance-001
  打开APP首页，等待输入框出现，点击输入框，输入"你好"，点击发送，执行5次
---
``````

运行命令
```
mind --plan --file example.md
```

### Android Monkey
运行命令 - example - 01
```
mind --chat "对 com.example.app 做一次 Monkey 随机事件注入测试，固定 seed 为 42，事件间隔 150 毫秒，触摸事件占 65%，滑动事件占 20%，导航事件占 10%，总事件数 10000。测试前先清理 logcat，测试过程中持续采集日志，并按异常关键词降噪保留关键 tail，最后输出执行结果和日志证据。""
```

运行命令 - example - 02
```
mind --chat "Run a Monkey random event injection test on com.example.app with seed 42, throttle 150 ms, 65% touch events, 20% motion events, 10% navigation events, and 10000 total events. Clear logcat before the test, keep a live logcat capture during execution, filter noise by exception-related keywords, and return the execution result with key log evidence at the end."
```

运行命令 - example - 03
```
mind --chat "com.example.app に対して Monkey ランダムイベント注入テストを実行してください。seed は 42、イベント間隔は 150ms、touch 65%、motion 20%、nav 10%、総イベント数は 10000 です。実行前に logcat をクリアし、実行中は logcat を継続取得して、異常系キーワードでノイズを抑えた重要な tail を残し、最後に実行結果とログ証跡を返してください。"
```

---

## ⭐️ 接口实战教学 (API Playbook)

### Http 接口实战
Mock 接口
```python
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse

app = FastAPI(title="HTTP Mock")


@app.post("/http-upload")
async def mock_http_upload(
    note: str = Form(""),
    file: UploadFile = File(...)
) -> JSONResponse:
    # 只验证“收到文件”，不做实际处理
    content = await file.read()

    return JSONResponse(
        {
            "ok": True,
            "type": "http",
            "data": {
                "note": note,
                "file": {
                    "filename": file.filename,
                    "content_type": file.content_type,
                    "size": len(content)
                }
            }
        },
        status_code=200
    )


if __name__ == "__main__":
    pass
```

启动
```
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

运行命令
```
mind --chat --file http.md
```

Http 文件上传 + 提取 + 断言
``````
# name: http_upload
请求 /http-upload 来验证 HTTP 文件上传、提取与断言。

payload = {
    "method": "POST",
    "url": "http://127.0.0.1:8000/http-upload",
    "form": {
        "note": "upload-check"
    },
    "files": [
        {
            "field": "file",
            "filename": "demo.txt",
            "content_type": "text/plain",
            "text": "hello nexus upload"
        }
    ],
    "extract": {
        "note": "response.body_json.data.note",
        "filename": "response.body_json.data.file.filename",
        "mime": "response.body_json.data.file.content_type",
        "size": "response.body_json.data.file.size"
    },
    "asserts": [
        {"path": "response.status", "op": "eq", "value": 200},
        {"path": "response.body_json.ok", "op": "eq", "value": True},
        {"path": "response.body_json.type", "op": "eq", "value": "http"},
        {"path": "response.body_json.data.note", "op": "eq", "value": "upload-check"},
        {"path": "response.body_json.data.file.filename", "op": "eq", "value": "demo.txt"},
        {"path": "response.body_json.data.file.content_type", "op": "eq", "value": "text/plain"},
        {"path": "response.body_json.data.file.size", "op": "gt", "value": 0}
    ]
}

# rule_suffix: <<<
# PASS 条件：
# - ok == true
# - type == "http"
# - detail.response.status == 200
# - detail.response.body_json.ok == true
# - detail.response.body_json.type == "http"
# - detail.response.body_json.data.note == "upload-check"
# - detail.response.body_json.data.file.filename == "demo.txt"
# - detail.response.body_json.data.file.content_type == "text/plain"
# - detail.response.body_json.data.file.size > 0
# - detail.extract.note == "upload-check"
# - detail.extract.filename == "demo.txt"
# - detail.extract.mime == "text/plain"
# - detail.extract.size > 0
# >>>
---
``````

运行结果
``````
Mind :: 2026-03-10 01:18:48.787 | DEBUG    | Chat Streaming
我将使用 nexus_http 工具来执行这个 HTTP 文件上传请求，并进行提取与断言验证。
nexus_http {'payload': {'method': 'POST', 'url': 'http://127.0.0.1:8000/http-upload', 'form': {'note': 'upload-check'}, 'files': [{'field': 'file', 'filename': 'demo.txt', 'content_type': 'text/plain', 'text': 'hello nexus upload'}], 'extract': {'note': 'response.body_json.data.note', 'filename': 'response.body_json.data.file.filename', 'mime': 'response.body_json.data.file.content_type', 'size': 'response.body_json.data.file.size'}, 'asserts': [{'path': 'response.status', 'op': 'eq', 'value': 200}, {'path': 'response.body_json.ok', 'op': 'eq', 'value': True}, {'path': 'response.body_json.type', 'op': 'eq', 'value': 'http'}, {'path': 'response.body_json.data.note', 'op': 'eq', 'value': 'upload-check'}, {'path': 'response.body_json.data.file.filename', 'op': 'eq', 'value': 'demo.txt'}, {'path': 'response.body_json.data.file.content_type', 'op': 'eq', 'value': 'text/plain'}, {'path': 'response.body_json.data.file.size', 'op': 'gt', 'value': 0}]}}

tool=nexus_http total=1 ok=1 fail=0 elapsed_ms=72
agent_id=nexus ok=True kind=http total=1 mission_id=nexus_1773076744990

nexus_http ok=True
## HTTP 文件上传验证结果

✅ **所有验证条件全部通过**，HTTP 文件上传功能正常工作。

### 执行摘要
- **工具**: nexus_http
- **总请求数**: 1
- **成功**: 1
- **失败**: 0
- **耗时**: 72ms

### 验证结果详情

#### 1. 响应状态验证 ✅
- `response.status == 200` ✅ (实际: 200)

#### 2. 响应体结构验证 ✅
- `response.body_json.ok == true` ✅ (实际: true)
- `response.body_json.type == "http"` ✅ (实际: "http")

#### 3. 表单数据验证 ✅
- `response.body_json.data.note == "upload-check"` ✅ (实际: "upload-check")

#### 4. 文件上传验证 ✅
- `response.body_json.data.file.filename == "demo.txt"` ✅ (实际: "demo.txt")
- `response.body_json.data.file.content_type == "text/plain"` ✅ (实际: "text/plain")
- `response.body_json.data.file.size > 0` ✅ (实际: 18)

#### 5. 字段提取验证 ✅
- `detail.extract.note == "upload-check"` ✅ (实际: "upload-check")
- `detail.extract.filename == "demo.txt"` ✅ (实际: "demo.txt")
- `detail.extract.mime == "text/plain"` ✅ (实际: "text/plain")
- `detail.extract.size > 0` ✅ (实际: 18)

### 断言统计
- **总断言数**: 7
- **通过断言**: 7
- **失败断言**: 0
- **断言通过率**: 100%

### 服务器响应详情
```json
{
  "ok": true,
  "type": "http",
  "data": {
    "note": "upload-check",
    "file": {
      "filename": "demo.txt",
      "content_type": "text/plain",
      "size": 18
    }
  }
}
```

### 结论
HTTP 文件上传功能完全符合预期，所有验证条件均满足：
1. ✅ 文件上传成功（demo.txt，18字节）
2. ✅ 表单字段正确传递（note: upload-check）
3. ✅ 响应状态码正确（200）
4. ✅ 响应结构完整（ok, type, data）
5. ✅ 字段提取功能正常
6. ✅ 断言验证全部通过

**验证通过** - HTTP 文件上传接口工作正常，支持 multipart/form-data 格式的文件上传与表单数据混合提交。
Mind :: 2026-03-10 01:19:32.440 | DEBUG    | Chat done ...
``````

### SSE 接口实战
Mock 接口
```python
import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse

app = FastAPI(title="SSE Mock")


def sse_pack(*, event: str | None = None, data: str = "", id_: str | None = None) -> str:
    lines: list[str] = []
    if event is not None:
        lines.append(f"event: {event}")
    if id_ is not None:
        lines.append(f"id: {id_}")
    for line in str(data).splitlines() or [""]:
        lines.append(f"data: {line}")
    return "\n".join(lines) + "\n\n"


@app.get("/sse")
async def mock_sse(request: Request) -> StreamingResponse:
    mode = str(request.query_params.get("mode") or "hello")

    async def gen():
        if mode == "hello":
            yield sse_pack(event="ready", data="hello_ack", id_="1")
            await asyncio.sleep(0.02)
            yield sse_pack(event="message", data="stream_ready", id_="2")
            await asyncio.sleep(0.02)
            yield sse_pack(event="done", data="bye", id_="3")
            return

        if mode == "error":
            yield sse_pack(event="error", data="mock failure", id_="1")
            await asyncio.sleep(0.02)
            yield sse_pack(event="done", data="closed", id_="2")
            return

        if mode == "json":
            yield sse_pack(event="message", data='{"code":0,"msg":"ok"}', id_="1")
            await asyncio.sleep(0.02)
            yield sse_pack(event="done", data='{"finished":true}', id_="2")
            return

        yield sse_pack(event="unknown", data=f"mode={mode}", id_="1")

    return StreamingResponse(gen(), media_type="text/event-stream")


if __name__ == "__main__":
    pass
```

启动
```
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

运行命令
```
mind --chat --file sse.md
```

SSE 正常流提取与断言
``````
# name: sse
请求 /sse 来验证 SSE 提取与 ok 判定。

payload = {
    "url": "http://127.0.0.1:8000/sse",
    "params": {
        "mode": "hello"
    },
    "max_events": 2,
    "extract": {
        "ev0": "events.0.event",
        "msg0": "events.0.data",
        "msg1": "events.1.data"
    },
    "asserts": [
        {"path": "status", "op": "eq", "value": 200},
        {"path": "events.0.event", "op": "eq", "value": "ready"},
        {"path": "events.0.data", "op": "eq", "value": "hello_ack"},
        {"path": "events.1.data", "op": "eq", "value": "stream_ready"},
        {"path": "events", "op": "not_empty"}
    ]
}

# rule_suffix: <<<
# PASS 条件：
# - ok == true
# - type == "sse"
# - detail.status == 200
# - detail.events 不为空
# - detail.events.0.event == "ready"
# - detail.events.0.data == "hello_ack"
# - detail.events.1.data == "stream_ready"
# - detail.extract.ev0 == "ready"
# - detail.extract.msg0 == "hello_ack"
# - detail.extract.msg1 == "stream_ready"
# >>>
---
``````

SSE 错误事件流
``````
# name: sse_error
请求 /sse 来验证 SSE 错误事件提取。

payload = {
    "url": "http://127.0.0.1:8000/sse",
    "params": {
        "mode": "error"
    },
    "max_events": 2,
    "extract": {
        "err_event": "events.0.event",
        "err_msg": "events.0.data"
    },
    "asserts": [
        {"path": "status", "op": "eq", "value": 200},
        {"path": "events.0.event", "op": "eq", "value": "error"},
        {"path": "events.0.data", "op": "contains", "value": "mock"},
        {"path": "events", "op": "not_empty"}
    ]
}

# rule_suffix: <<<
# PASS 条件：
# - ok == true
# - type == "sse"
# - detail.status == 200
# - detail.events.0.event == "error"
# - detail.events.0.data 包含 "mock"
# - detail.extract.err_event == "error"
# - detail.extract.err_msg 包含 "mock"
# >>>
---
``````

SSE JSON 字符串事件
``````
# name: sse_json
请求 /sse 来验证 SSE JSON 字符串事件提取。

payload = {
    "url": "http://127.0.0.1:8000/sse",
    "params": {
        "mode": "json"
    },
    "max_events": 2,
    "extract": {
        "raw0": "events.0.data",
        "raw1": "events.1.data"
    },
    "asserts": [
        {"path": "status", "op": "eq", "value": 200},
        {"path": "events.0.data", "op": "contains", "value": "\"code\":0"},
        {"path": "events.1.data", "op": "contains", "value": "\"finished\":true"}
    ]
}

# rule_suffix: <<<
# PASS 条件：
# - ok == true
# - type == "sse"
# - detail.status == 200
# - detail.events.0.data 包含 "\"code\":0"
# - detail.events.1.data 包含 "\"finished\":true"
# - detail.extract.raw0 包含 "\"code\":0"
# - detail.extract.raw1 包含 "\"finished\":true"
# >>>
---
``````

运行结果
``````
Mind :: 2026-03-10 01:07:03.254 | DEBUG    | Chat Streaming
我将使用 nexus_sse 工具来验证 SSE 提取与 ok 判定。根据您提供的 payload 配置，我将执行 SSE 请求并验证提取和断言。
nexus_sse {'payload': {'url': 'http://127.0.0.1:8000/sse', 'params': {'mode': 'hello'}, 'max_events': 2, 'extract': {'ev0': 'events.0.event', 'msg0': 'events.0.data', 'msg1': 'events.1.data'}, 'asserts': [{'path': 'status', 'op': 'eq', 'value': 200}, {'path': 'events.0.event', 'op': 'eq', 'value': 'ready'}, {'path': 'events.0.data', 'op': 'eq', 'value': 'hello_ack'}, {'path': 'events.1.data', 'op': 'eq', 'value': 'stream_ready'}, {'path': 'events', 'op': 'not_empty'}]}}

tool=nexus_sse total=1 ok=1 fail=0 elapsed_ms=82
agent_id=nexus ok=True kind=sse total=1 mission_id=nexus_1773076036050

nexus_sse ok=True
## SSE 验证结果

**✅ 所有验证条件 PASS**

根据工具输出，所有规则条件均已满足：

### 基础条件验证：
1. **ok == true** ✅ - `data.ok: true`
2. **type == "sse"** ✅ - `kind: sse`
3. **detail.status == 200** ✅ - `detail.status: 200`

### 事件数据验证：
4. **detail.events 不为空** ✅ - 包含 2 个事件
5. **detail.events.0.event == "ready"** ✅ - 实际值: `"ready"`
6. **detail.events.0.data == "hello_ack"** ✅ - 实际值: `"hello_ack"`
7. **detail.events.1.data == "stream_ready"** ✅ - 实际值: `"stream_ready"`

### 提取字段验证：
8. **detail.extract.ev0 == "ready"** ✅ - 实际值: `"ready"`
9. **detail.extract.msg0 == "hello_ack"** ✅ - 实际值: `"hello_ack"`
10. **detail.extract.msg1 == "stream_ready"** ✅ - 实际值: `"stream_ready"`

### 断言结果：
- 所有 5 个断言全部通过 (5/5)
- 断言摘要：`assert_summary: {"total": 5, "pass": 5, "fail": 0}`
- 断言状态：`assert_ok: true`

### 执行详情：
- **耗时**: 82ms
- **事件数量**: 2 个 (达到 max_events 限制)
- **事件内容**:
  1. `{"event": "ready", "id": "1", "data": "hello_ack"}`
  2. `{"event": "message", "id": "2", "data": "stream_ready"}`

**结论**: SSE 提取与 ok 判定验证成功，所有规则条件均满足。
Mind :: 2026-03-10 01:07:38.722 | DEBUG    | Chat done ...
Mind :: 2026-03-10 01:07:40.323 | INFO     | ▶️  [2/3] sse_error
Mind :: 2026-03-10 01:07:42.472 | DEBUG    | Chat Streaming
我将使用 nexus_sse 工具来验证 SSE 错误事件提取。根据您提供的 payload 配置，我将执行 SSE 请求并验证错误事件的提取和断言。
nexus_sse {'payload': {'url': 'http://127.0.0.1:8000/sse', 'params': {'mode': 'error'}, 'max_events': 2, 'extract': {'err_event': 'events.0.event', 'err_msg': 'events.0.data'}, 'asserts': [{'path': 'status', 'op': 'eq', 'value': 200}, {'path': 'events.0.event', 'op': 'eq', 'value': 'error'}, {'path': 'events.0.data', 'op': 'contains', 'value': 'mock'}, {'path': 'events', 'op': 'not_empty'}]}}

tool=nexus_sse total=1 ok=1 fail=0 elapsed_ms=92
agent_id=nexus ok=True kind=sse total=1 mission_id=nexus_1773076073572

nexus_sse ok=True
## SSE 错误事件验证结果

**✅ 所有验证条件 PASS**

根据工具输出，所有规则条件均已满足：

### 基础条件验证：
1. **ok == true** ✅ - `data.ok: true`
2. **type == "sse"** ✅ - `kind: sse`
3. **detail.status == 200** ✅ - `detail.status: 200`

### 错误事件数据验证：
4. **detail.events.0.event == "error"** ✅ - 实际值: `"error"`
5. **detail.events.0.data 包含 "mock"** ✅ - 实际值: `"mock failure"` (包含 "mock")

### 提取字段验证：
6. **detail.extract.err_event == "error"** ✅ - 实际值: `"error"`
7. **detail.extract.err_msg 包含 "mock"** ✅ - 实际值: `"mock failure"` (包含 "mock")

### 断言结果：
- 所有 4 个断言全部通过 (4/4)
- 断言摘要：`assert_summary: {"total": 4, "pass": 4, "fail": 0}`
- 断言状态：`assert_ok: true`

### 执行详情：
- **耗时**: 92ms
- **事件数量**: 2 个 (达到 max_events 限制)
- **事件内容**:
  1. `{"event": "error", "id": "1", "data": "mock failure"}` ✅
  2. `{"event": "done", "id": "2", "data": "closed"}`

### 特别验证：
- **contains 断言验证**: `"mock failure"` 包含 `"mock"` ✅
- **提取字段验证**: `err_msg: "mock failure"` 包含 `"mock"` ✅

**结论**: SSE 错误事件提取验证成功，所有规则条件均满足。服务器正确返回了错误事件，并且提取和断言功能正常工作。
Mind :: 2026-03-10 01:08:15.312 | DEBUG    | Chat done ...
Mind :: 2026-03-10 01:08:18.404 | INFO     | ▶️  [3/3] sse_json
Mind :: 2026-03-10 01:08:21.382 | DEBUG    | Chat Streaming
我将使用 nexus_sse 工具来验证 SSE JSON 字符串事件提取。根据您提供的 payload 配置，我将执行 SSE 请求并验证 JSON 字符串事件的提取和断言。
nexus_sse {'payload': {'url': 'http://127.0.0.1:8000/sse', 'params': {'mode': 'json'}, 'max_events': 2, 'extract': {'raw0': 'events.0.data', 'raw1': 'events.1.data'}, 'asserts': [{'path': 'status', 'op': 'eq', 'value': 200}, {'path': 'events.0.data', 'op': 'contains', 'value': '"code":0'}, {'path': 'events.1.data', 'op': 'contains', 'value': '"finished":true'}]}}

tool=nexus_sse total=1 ok=1 fail=0 elapsed_ms=75
agent_id=nexus ok=True kind=sse total=1 mission_id=nexus_1773076111110

nexus_sse ok=True
## SSE JSON 字符串事件验证结果

**✅ 所有验证条件 PASS**

根据工具输出，所有规则条件均已满足：

### 基础条件验证：
1. **ok == true** ✅ - `data.ok: true`
2. **type == "sse"** ✅ - `kind: sse`
3. **detail.status == 200** ✅ - `detail.status: 200`

### JSON 字符串数据验证：
4. **detail.events.0.data 包含 "\"code\":0"** ✅ - 实际值: `"{\"code\":0,\"msg\":\"ok\"}"` (包含 `"code\":0`)
5. **detail.events.1.data 包含 "\"finished\":true"** ✅ - 实际值: `"{\"finished\":true}"` (包含 `"finished\":true`)

### 提取字段验证：
6. **detail.extract.raw0 包含 "\"code\":0"** ✅ - 实际值: `"{\"code\":0,\"msg\":\"ok\"}"` (包含 `"code\":0`)
7. **detail.extract.raw1 包含 "\"finished\":true"** ✅ - 实际值: `"{\"finished\":true}"` (包含 `"finished\":true`)

### 断言结果：
- 所有 3 个断言全部通过 (3/3)
- 断言摘要：`assert_summary: {"total": 3, "pass": 3, "fail": 0}`
- 断言状态：`assert_ok: true`

### 执行详情：
- **耗时**: 75ms
- **事件数量**: 2 个 (达到 max_events 限制)
- **事件内容**:
  1. `{"event": "message", "id": "1", "data": "{\"code\":0,\"msg\":\"ok\"}"}` ✅
  2. `{"event": "done", "id": "2", "data": "{\"finished\":true}"}` ✅

### JSON 字符串详细验证：
- **第一个事件**: `"{\"code\":0,\"msg\":\"ok\"}"`
  - 包含 `"code\":0` ✅
  - 完整 JSON 结构: `{"code":0,"msg":"ok"}`
  
- **第二个事件**: `"{\"finished\":true}"`
  - 包含 `"finished\":true` ✅
  - 完整 JSON 结构: `{"finished":true}`

### 特别验证：
- **contains 断言验证**: 正确识别 JSON 字符串中的键值对 ✅
- **转义字符处理**: 双引号在 JSON 字符串中正确转义 ✅
- **提取字段验证**: 提取的原始字符串包含预期的 JSON 片段 ✅

**结论**: SSE JSON 字符串事件提取验证成功，所有规则条件均满足。服务器正确返回了 JSON 格式的字符串事件，并且提取和断言功能正常工作，能够正确处理包含转义字符的 JSON 字符串。
Mind :: 2026-03-10 01:09:01.331 | DEBUG    | Chat done ...
``````

### Websocket 接口实战
Mock 接口
```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI(title="WS Mock")


@app.websocket("/ws")
async def mock_ws(ws: WebSocket) -> None:
    await ws.accept()

    try:
        first = await ws.receive_text()

        if first == "hello":
            await ws.send_text("hello_ack")
            await ws.send_text("stream_ready")
            await ws.close()
            return None

        if first == "force_error":
            await ws.send_text("error: mock failure")
            await ws.close()
            return None

        if first.startswith("echo:"):
            await ws.send_text(first)
            await ws.send_text("done")
            await ws.close()
            return None

        await ws.send_text(f"unknown:{first}")
        await ws.close()

    except WebSocketDisconnect:
        return None


if __name__ == "__main__":
    pass
```

启动
```
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

运行命令
```
mind --chat --file ws.md
```

Websocket 正常消息提取与断言
``````
# name: ws
请求 /ws 来验证 WebSocket 提取与 ok 判定。

payload = {
    "url": "ws://127.0.0.1:8000/ws",
    "sends": ["hello"],
    "max_messages": 3,
    "extract": {
        "msg0": "messages.0",
        "msg1": "messages.1"
    },
    "asserts": [
        {"path": "messages.0", "op": "eq", "value": "hello_ack"},
        {"path": "messages.1", "op": "eq", "value": "stream_ready"},
        {"path": "messages", "op": "not_empty"}
    ]
}

# rule_suffix: <<<
# PASS 条件：
# - ok == true
# - type == "ws"
# - detail.messages 不为空
# - detail.messages.0 == "hello_ack"
# - detail.messages.1 == "stream_ready"
# - detail.extract.msg0 == "hello_ack"
# - detail.extract.msg1 == "stream_ready"
# >>>
---
``````

Websocket 错误消息场景
``````
# name: ws_error
请求 /ws 来验证 WebSocket 错误消息提取。

payload = {
    "url": "ws://127.0.0.1:8000/ws",
    "sends": ["force_error"],
    "max_messages": 2,
    "extract": {
        "err0": "messages.0"
    },
    "asserts": [
        {"path": "messages.0", "op": "contains", "value": "error:"},
        {"path": "messages", "op": "not_empty"}
    ]
}

# rule_suffix: <<<
# PASS 条件：
# - ok == true
# - type == "ws"
# - detail.messages 不为空
# - detail.messages.0 包含 "error:"
# - detail.extract.err0 包含 "error:"
# >>>
---
``````

Websocket echo 场景
``````
# name: ws_echo
请求 /ws 来验证 WebSocket echo 提取与断言。

payload = {
    "url": "ws://127.0.0.1:8000/ws",
    "sends": ["echo:ping"],
    "max_messages": 2,
    "extract": {
        "echoed": "messages.0",
        "done": "messages.1"
    },
    "asserts": [
        {"path": "messages.0", "op": "eq", "value": "echo:ping"},
        {"path": "messages.1", "op": "eq", "value": "done"}
    ]
}

# rule_suffix: <<<
# PASS 条件：
# - ok == true
# - type == "ws"
# - detail.messages.0 == "echo:ping"
# - detail.messages.1 == "done"
# - detail.extract.echoed == "echo:ping"
# - detail.extract.done == "done"
# >>>
---
``````

运行结果
``````
Mind :: 2026-03-10 00:50:07.767 | DEBUG    | Chat Streaming
我将使用 nexus_ws 工具来验证 WebSocket 连接和提取功能。根据你的 payload 配置，我将发送 WebSocket 请求并验证断言。
nexus_ws {'payload': {'url': 'ws://127.0.0.1:8000/ws', 'sends': ['hello'], 'max_messages': 3, 'extract': {'msg0': 'messages.0', 'msg1': 'messages.1'}, 'asserts': [{'path': 'messages.0', 'op': 'eq', 'value': 'hello_ack'}, {'path': 'messages.1', 'op': 'eq', 'value': 'stream_ready'}, {'path': 'messages', 'op': 'not_empty'}]}, 'concurrency': 1}

tool=nexus_ws total=1 ok=1 fail=0 elapsed_ms=19
agent_id=nexus ok=True kind=ws total=1 mission_id=nexus_1773075020132

nexus_ws ok=True
## WebSocket 验证结果

✅ **所有验证条件 PASS**：

### 1. 基础状态验证
- **ok == true** ✓ - 整体执行成功
- **type == "ws"** ✓ - 工具类型为 WebSocket (kind=ws)

### 2. 消息内容验证
- **detail.messages 不为空** ✓ - 收到 2 条消息：["hello_ack", "stream_ready"]
- **detail.messages.0 == "hello_ack"** ✓ - 第一条消息匹配
- **detail.messages.1 == "stream_ready"** ✓ - 第二条消息匹配

### 3. 提取字段验证
- **detail.extract.msg0 == "hello_ack"** ✓ - 提取的第一个消息正确
- **detail.extract.msg1 == "stream_ready"** ✓ - 提取的第二个消息正确

### 4. 断言结果验证
所有 3 个断言全部通过：
1. `messages.0 == "hello_ack"` ✓
2. `messages.1 == "stream_ready"` ✓  
3. `messages not_empty` ✓

### 执行详情
- **连接地址**: ws://127.0.0.1:8000/ws
- **发送消息**: ["hello"]
- **接收消息**: ["hello_ack", "stream_ready"]
- **耗时**: 19ms
- **断言统计**: 3/3 通过

WebSocket 连接、消息收发、字段提取和断言验证全部成功完成。
Mind :: 2026-03-10 00:50:40.586 | DEBUG    | Chat done ...
Mind :: 2026-03-10 00:50:41.555 | INFO     | ▶️  [2/3] ws_error
Mind :: 2026-03-10 00:50:44.269 | DEBUG    | Chat Streaming
我将使用 nexus_ws 工具来验证 WebSocket 错误消息提取功能。根据你的 payload 配置，我将发送 "force_error" 消息并验证错误响应。
nexus_ws {'payload': {'url': 'ws://127.0.0.1:8000/ws', 'sends': ['force_error'], 'max_messages': 2, 'extract': {'err0': 'messages.0'}, 'asserts': [{'path': 'messages.0', 'op': 'contains', 'value': 'error:'}, {'path': 'messages', 'op': 'not_empty'}]}, 'concurrency': 1}

tool=nexus_ws total=1 ok=1 fail=0 elapsed_ms=6
agent_id=nexus ok=True kind=ws total=1 mission_id=nexus_1773075055051

nexus_ws ok=True
## WebSocket 错误消息验证结果

✅ **所有验证条件 PASS**：

### 1. 基础状态验证
- **ok == true** ✓ - 整体执行成功
- **type == "ws"** ✓ - 工具类型为 WebSocket (kind=ws)

### 2. 消息内容验证
- **detail.messages 不为空** ✓ - 收到 1 条消息：["error: mock failure"]
- **detail.messages.0 包含 "error:"** ✓ - 第一条消息包含 "error:" 字符串

### 3. 提取字段验证
- **detail.extract.err0 包含 "error:"** ✓ - 提取的错误消息为 "error: mock failure"，包含 "error:"

### 4. 断言结果验证
所有 2 个断言全部通过：
1. `messages.0 contains "error:"` ✓ - 实际消息 "error: mock failure" 包含 "error:"
2. `messages not_empty` ✓

### 执行详情
- **连接地址**: ws://127.0.0.1:8000/ws
- **发送消息**: ["force_error"]
- **接收消息**: ["error: mock failure"]
- **耗时**: 6ms
- **断言统计**: 2/2 通过

WebSocket 错误消息的提取和验证全部成功完成。服务器正确响应了 "force_error" 请求，返回了预期的错误消息格式。
Mind :: 2026-03-10 00:51:13.109 | DEBUG    | Chat done ...
Mind :: 2026-03-10 00:51:15.691 | INFO     | ▶️  [3/3] ws_echo
Mind :: 2026-03-10 00:51:18.574 | DEBUG    | Chat Streaming
我将使用 nexus_ws 工具来验证 WebSocket echo 功能。根据你的 payload 配置，我将发送 "echo:ping" 消息并验证回显响应。
nexus_ws {'payload': {'url': 'ws://127.0.0.1:8000/ws', 'sends': ['echo:ping'], 'max_messages': 2, 'extract': {'echoed': 'messages.0', 'done': 'messages.1'}, 'asserts': [{'path': 'messages.0', 'op': 'eq', 'value': 'echo:ping'}, {'path': 'messages.1', 'op': 'eq', 'value': 'done'}]}, 'concurrency': 1}

tool=nexus_ws total=1 ok=1 fail=0 elapsed_ms=5
agent_id=nexus ok=True kind=ws total=1 mission_id=nexus_1773075090025

nexus_ws ok=True
## WebSocket Echo 验证结果

✅ **所有验证条件 PASS**：

### 1. 基础状态验证
- **ok == true** ✓ - 整体执行成功
- **type == "ws"** ✓ - 工具类型为 WebSocket (kind=ws)

### 2. 消息内容验证
- **detail.messages.0 == "echo:ping"** ✓ - 第一条消息正确回显
- **detail.messages.1 == "done"** ✓ - 第二条消息为完成标志

### 3. 提取字段验证
- **detail.extract.echoed == "echo:ping"** ✓ - 提取的回显消息正确
- **detail.extract.done == "done"** ✓ - 提取的完成标志正确

### 4. 断言结果验证
所有 2 个断言全部通过：
1. `messages.0 == "echo:ping"` ✓
2. `messages.1 == "done"` ✓

### 执行详情
- **连接地址**: ws://127.0.0.1:8000/ws
- **发送消息**: ["echo:ping"]
- **接收消息**: ["echo:ping", "done"]
- **耗时**: 5ms
- **断言统计**: 2/2 通过

WebSocket echo 功能的验证全部成功完成。服务器正确实现了 echo 功能，先回显发送的消息，然后发送 "done" 完成标志。
Mind :: 2026-03-10 00:51:48.484 | DEBUG    | Chat done ...
``````

### GraphQL 接口实战
Mock 接口
```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI(title="GraphQL Mock")


@app.post("/graphql")
async def mock_graphql(request: Request) -> JSONResponse:
    body = await request.json()

    query = str(body.get("query") or "")
    variables = body.get("variables") or {}
    operation_name = body.get("operationName") or body.get("operation_name")

    # 1) 模拟 GraphQL errors
    if "forceError" in query or variables.get("force_error") is True:
        return JSONResponse(
            {
                "errors": [
                    {
                        "message": "mock graphql error",
                        "extensions": {"code": "MOCK_ERROR"}
                    }
                ]
            },
            status_code=200
        )

    # 2) 模拟正常 data
    return JSONResponse(
        {
            "data": {
                "mockUser": {
                    "id": 123,
                    "name": "Ace",
                    "active": True
                }
            },
            "extensions": {
                "trace_id": "trace_mock_001"
            },
            "meta": {
                "ok": True,
                "type": "graphql",
                "operation_name": operation_name,
                "variables": variables
            }
        },
        status_code=200
    )


if __name__ == '__main__':
    pass
```

启动
```
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

运行命令
```
mind --chat --file graphql.md
```

GraphQL 成功请求
``````
# name: graphql
请求 /graphql 来验证 GraphQL 提取与 ok 判定。

payload = {
    "url": "http://127.0.0.1:8000/graphql",
    "query": "query GetUser { mockUser { id name active } }",
    "operation_name": "GetUser",
    "extract": {
        "uid": "response.body_json.data.mockUser.id",
        "uname": "response.body_json.data.mockUser.name",
        "trace_id": "response.body_json.extensions.trace_id"
    },
    "asserts": [
        {"path": "response.status", "op": "eq", "value": 200},
        {"path": "response.body_json.data.mockUser.id", "op": "eq", "value": 123},
        {"path": "response.body_json.data.mockUser.name", "op": "eq", "value": "Ace"},
        {"path": "response.body_json.data.mockUser.active", "op": "eq", "value": True},
        {"path": "response.body_json.extensions.trace_id", "op": "eq", "value": "trace_mock_001"}
    ]
}

# rule_suffix: <<<
# PASS 条件：
# - ok == true
# - type == "graphql"
# - detail.response.status == 200
# - detail.response.body_json 不为空（能解析 JSON）
# - detail.response.body_json.data.mockUser.id == 123
# - detail.response.body_json.data.mockUser.name == "Ace"
# - detail.response.body_json.data.mockUser.active == true
# - detail.response.body_json.extensions.trace_id == "trace_mock_001"
# - detail.graphql.errors 为空
# - detail.extract.uid == 123
# - detail.extract.uname == "Ace"
# - detail.extract.trace_id == "trace_mock_001"
# >>>
---
``````

GraphQL 返回 errors
``````
# name: graphql_error
请求 /graphql 来验证 GraphQL errors 判定。

payload = {
    "url": "http://127.0.0.1:8000/graphql",
    "query": "query forceError { mockUser { id } }",
    "operation_name": "forceError",
    "extract": {
        "gql_errors": "response.body_json.errors"
    },
    "asserts": [
        {"path": "response.status", "op": "eq", "value": 200},
        {"path": "response.body_json.errors", "op": "not_empty"}
    ]
}

# rule_suffix: <<<
# PASS 条件：
# - ok == false
# - type == "graphql"
# - detail.response.status == 200
# - detail.graphql.errors 不为空
# - detail.response.body_json.errors 不为空
# - detail.extract.gql_errors 不为空
# >>>
---
``````

运行结果
``````
Mind :: 2026-03-10 00:32:29.365 | DEBUG    | Chat Streaming
我将使用 nexus_graphql 工具来验证 GraphQL 提取与 ok 判定。根据你的 payload 配置，我将执行这个 GraphQL 请求。
nexus_graphql {'payload': {'url': 'http://127.0.0.1:8000/graphql', 'query': 'query GetUser { mockUser { id name active } }', 'operation_name': 'GetUser', 'extract': {'uid': 'response.body_json.data.mockUser.id', 'uname': 'response.body_json.data.mockUser.name', 'trace_id': 'response.body_json.extensions.trace_id'}, 'asserts': [{'path': 'response.status', 'op': 'eq', 'value': 200}, {'path': 'response.body_json.data.mockUser.id', 'op': 'eq', 'value': 123}, {'path': 'response.body_json.data.mockUser.name', 'op': 'eq', 'value': 'Ace'}, {'path': 'response.body_json.data.mockUser.active', 'op': 'eq', 'value': True}, {'path': 'response.body_json.extensions.trace_id', 'op': 'eq', 'value': 'trace_mock_001'}]}}

tool=nexus_graphql total=1 ok=1 fail=0 elapsed_ms=76
agent_id=nexus ok=True kind=graphql total=1 mission_id=nexus_1773073965313

nexus_graphql ok=True
## 验证结果：✅ **PASS**

根据你提供的规则后缀，所有 PASS 条件均已满足：

### ✅ 核心条件验证：
1. **ok == true** ✅ - `data.ok: true`
2. **type == "graphql"** ✅ - `detail.graphql.query` 存在且 `meta.type: "graphql"`
3. **detail.response.status == 200** ✅ - `response.status: 200`
4. **detail.response.body_json 不为空** ✅ - `body_json` 包含完整数据

### ✅ 数据验证：
5. **detail.response.body_json.data.mockUser.id == 123** ✅ - 实际值：`123`
6. **detail.response.body_json.data.mockUser.name == "Ace"** ✅ - 实际值：`"Ace"`
7. **detail.response.body_json.data.mockUser.active == true** ✅ - 实际值：`true`
8. **detail.response.body_json.extensions.trace_id == "trace_mock_001"** ✅ - 实际值：`"trace_mock_001"`

### ✅ GraphQL 特定验证：
9. **detail.graphql.errors 为空** ✅ - `graphql.errors: null`

### ✅ 提取验证：
10. **detail.extract.uid == 123** ✅ - 提取值：`123`
11. **detail.extract.uname == "Ace"** ✅ - 提取值：`"Ace"`
12. **detail.extract.trace_id == "trace_mock_001"** ✅ - 提取值：`"trace_mock_001"`

### ✅ 断言验证：
所有 5 个断言全部通过：
- `response.status == 200` ✅
- `mockUser.id == 123` ✅
- `mockUser.name == "Ace"` ✅
- `mockUser.active == true` ✅
- `extensions.trace_id == "trace_mock_001"` ✅

**总结**：GraphQL 请求成功，所有提取、断言和验证条件均满足，ok 判定正确。
Mind :: 2026-03-10 00:33:10.327 | DEBUG    | Chat done ...
Mind :: 2026-03-10 00:33:11.456 | INFO     | ▶️  [2/2] graphql_error
Mind :: 2026-03-10 00:33:13.446 | DEBUG    | Chat Streaming
我将使用 nexus_graphql 工具来验证 GraphQL errors 判定。根据你的 payload 配置，我将执行这个 GraphQL 请求来测试错误处理。
nexus_graphql {'payload': {'url': 'http://127.0.0.1:8000/graphql', 'query': 'query forceError { mockUser { id } }', 'operation_name': 'forceError', 'extract': {'gql_errors': 'response.body_json.errors'}, 'asserts': [{'path': 'response.status', 'op': 'eq', 'value': 200}, {'path': 'response.body_json.errors', 'op': 'not_empty'}]}}

tool=nexus_graphql total=1 ok=0 fail=1 elapsed_ms=65
agent_id=nexus ok=False error=kind=graphql total=1 mission_id=nexus_1773074004007

nexus_graphql ok=False
## 验证结果：✅ **PASS**

根据你提供的规则后缀，所有 PASS 条件均已满足：

### ✅ 核心条件验证：
1. **ok == false** ✅ - `data.ok: false` (GraphQL 有 errors 时，ok 为 false)
2. **type == "graphql"** ✅ - `kind: "graphql"` 且 `detail.graphql` 存在
3. **detail.response.status == 200** ✅ - `response.status: 200`

### ✅ 错误验证：
4. **detail.graphql.errors 不为空** ✅ - `graphql.errors: [{"message": "mock graphql error", ...}]`
5. **detail.response.body_json.errors 不为空** ✅ - `body_json.errors: [{"message": "mock graphql error", ...}]`
6. **detail.extract.gql_errors 不为空** ✅ - `extract.gql_errors: [{"message": "mock graphql error", ...}]`

### ✅ 详细分析：
- **GraphQL 响应**：服务器返回了 HTTP 200 状态码，但响应体包含 `errors` 字段
- **错误内容**：`{"message": "mock graphql error", "extensions": {"code": "MOCK_ERROR"}}`
- **断言结果**：两个断言都通过了（status=200 和 errors not_empty）
- **assert_ok**：`false` - 这是因为 GraphQL 引擎检测到 `errors` 字段非空，即使所有断言都通过，整体结果仍为 false

### ✅ 关键观察：
1. **GraphQL 错误处理机制正确**：当响应包含 `errors` 字段时，nexus_graphql 正确地将 `ok` 设为 `false`
2. **断言与 ok 分离**：断言全部通过（2/2），但整体 `ok` 为 `false`，这符合 GraphQL 规范
3. **提取功能正常**：成功提取了 `gql_errors` 字段
4. **错误信息完整**：错误消息和扩展信息都被正确解析

**总结**：GraphQL errors 判定机制工作正常，当 GraphQL 响应包含 errors 时，即使 HTTP 状态码为 200 且所有断言通过，整体结果仍为 `false`，这符合 GraphQL 规范。
Mind :: 2026-03-10 00:33:53.430 | DEBUG    | Chat done ...
``````

### API Mocks
```python
import asyncio
from fastapi import (
    FastAPI,
    UploadFile,
    File,
    Form,
    Request,
    WebSocket,
    WebSocketDisconnect
)
from fastapi.responses import (
    JSONResponse,
    StreamingResponse
)

app = FastAPI(title="Mock")


@app.post("/http-upload")
async def mock_http_upload(
    note: str = Form(""),
    file: UploadFile = File(...)
) -> JSONResponse:
    # 只验证“收到文件”，不做实际处理
    content = await file.read()

    return JSONResponse(
        {
            "ok": True,
            "type": "http",
            "data": {
                "note": note,
                "file": {
                    "filename"     : file.filename,
                    "content_type" : file.content_type,
                    "size"         : len(content)
                }
            }
        },
        status_code=200
    )


def sse_pack(*, event: str | None = None, data: str = "", id_: str | None = None) -> str:
    lines: list[str] = []
    if event is not None:
        lines.append(f"event: {event}")
    if id_ is not None:
        lines.append(f"id: {id_}")
    for line in str(data).splitlines() or [""]:
        lines.append(f"data: {line}")
    return "\n".join(lines) + "\n\n"


@app.get("/sse")
async def mock_sse(request: Request) -> StreamingResponse:
    mode = str(request.query_params.get("mode") or "hello")

    async def gen():
        if mode == "hello":
            yield sse_pack(event="ready", data="hello_ack", id_="1")
            await asyncio.sleep(0.02)
            yield sse_pack(event="message", data="stream_ready", id_="2")
            await asyncio.sleep(0.02)
            yield sse_pack(event="done", data="bye", id_="3")
            return

        if mode == "error":
            yield sse_pack(event="error", data="mock failure", id_="1")
            await asyncio.sleep(0.02)
            yield sse_pack(event="done", data="closed", id_="2")
            return

        if mode == "json":
            yield sse_pack(event="message", data='{"code":0,"msg":"ok"}', id_="1")
            await asyncio.sleep(0.02)
            yield sse_pack(event="done", data='{"finished":true}', id_="2")
            return

        yield sse_pack(event="unknown", data=f"mode={mode}", id_="1")

    return StreamingResponse(gen(), media_type="text/event-stream")


@app.websocket("/ws")
async def mock_ws(ws: WebSocket) -> None:
    await ws.accept()

    try:
        first = await ws.receive_text()

        if first == "hello":
            await ws.send_text("hello_ack")
            await ws.send_text("stream_ready")
            await ws.close()
            return None

        if first == "force_error":
            await ws.send_text("error: mock failure")
            await ws.close()
            return None

        if first.startswith("echo:"):
            await ws.send_text(first)
            await ws.send_text("done")
            await ws.close()
            return None

        await ws.send_text(f"unknown:{first}")
        await ws.close()

    except WebSocketDisconnect:
        return None


@app.post("/graphql")
async def mock_graphql(request: Request) -> JSONResponse:
    body = await request.json()

    query = str(body.get("query") or "")
    variables = body.get("variables") or {}
    operation_name = body.get("operationName") or body.get("operation_name")

    # 1) 模拟 GraphQL errors
    if "forceError" in query or variables.get("force_error") is True:
        return JSONResponse(
            {
                "errors": [
                    {
                        "message": "mock graphql error",
                        "extensions": {"code": "MOCK_ERROR"}
                    }
                ]
            },
            status_code=200
        )

    # 2) 模拟正常 data
    return JSONResponse(
        {
            "data": {
                "mockUser": {
                    "id": 123,
                    "name": "Ace",
                    "active": True
                }
            },
            "extensions": {
                "trace_id": "trace_mock_001"
            },
            "meta": {
                "ok": True,
                "type": "graphql",
                "operation_name": operation_name,
                "variables": variables
            }
        },
        status_code=200
    )


if __name__ == '__main__':
    pass
```

---

## ⭐️ 构建发布 (Build & Release)

![LOGO](https://raw.githubusercontent.com/PlaxtonFlarion/SoftwareCenter/main/Assets/MindSource/app_compile.png)

支持 **macOS** 与 **Windows** 平台安装包发布

**发布地址：** [https://github.com/PlaxtonFlarion/SoftwareCenter/releases](https://github.com/PlaxtonFlarion/SoftwareCenter/releases)

---

## ⭐️ 合作支持 (Support)
如需技术合作、定制能力或企业级部署支持，请通过邮箱联系作者。

作者邮箱：`AceKeppel@outlook.com`

---

## ⭐️ 许可说明 (License)
当前仓库包含 `GPL-3.0` 授权文本（见 `LICENSE.md`）。  
如发布产物或常量中存在其他授权声明，请以 `LICENSE.md` 为准。

---

## ⭐️ 贡献指南（Contributing）
我们欢迎对 Mind 生态的任何形式贡献：新增工具域能力、修复缺陷、补充文档、优化可观测性与工程稳定性。

### 贡献范围
- **新工具 / 新能力**：按域注册（`automator / bench/ common / media `），补齐文档与示例
- **稳定性与可靠性**：超时/回收/错误边界/重试策略/证据链完备性
- **可观测性**：日志结构化、链路标识（cid/sid）、指标与报告落盘规范
- **文档与示例**：README、最佳实践、业务接入模板、常见问题（FAQ）

### 开发约定
- **执行优先**：任何能力必须可落地、可复现，避免“只看起来能用”
- **证据链优先**：新增能力必须产出可追踪证据（日志/媒体/指标/计划）
- **域隔离优先**：工具必须归属明确的 domain/class，不把能力写成“万能函数”
- **不破坏稳定性**：任何改动必须保持 CLI 行为兼容（尤其是 `plan` 的确定性链路）

### 提交流程
1. Fork & 新建分支：`feat/<name>` 或 `fix/<name>`
2. 本地自测：覆盖 `chat/fast/plan` 与 REPL（mind_loop）关键路径
3. 更新文档：新增/变更能力需同步 README
4. 提交 PR：描述动机、设计、影响范围与回滚策略

> 建议：为新工具补齐 1 个最小示例任务（自然语言输入）+ 1 个产物截图/报告说明，方便业务侧快速验证。

---

## ⭐️ 特别鸣谢（Special Thanks）
......

---
