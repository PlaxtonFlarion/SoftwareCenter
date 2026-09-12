# ProxyMind 客户端架构

本文是 ProxyMind 客户端的架构权威，只定义客户端内部职责、包边界、依赖方向、状态所有权、
生命周期和稳定不变量。需求、修复和重构必须先符合本文，再进入实现。

Mind、AppServer 与 Fabric 的跨系统职责、Authority 和集成边界以
`ARCHITECTURE_SYSTEM.md` 为准；本文受其约束，不重新定义跨系统事实。

本文不复制以下契约：

- 线上 `mind.chat` 字段、端点、事件和错误以服务端正式契约及 `protocol/schema/`、
  `protocol/client/` 为准；
- 编码代理的工作方式、代码质量和验证流程以 `AGENTS.md` 为准；
- 功能参数、操作说明和领域细节由对应代码、测试及 `docs/` 文档维护；
- `backend/` 是独立打包服务，不属于客户端运行时。

## 架构原则

- 每类状态只有一个权威所有者，缓存和展示均可从事实重建。
- 领域规则、应用用例、运行编排、外部实现和前端展示分层维护。
- 模型、工具、审批、持久化、传输和前端通过具名端口组合。
- Command、Run、外部 Effect 和线上游标具有稳定身份；未知结果进入显式对账。
- 路径、Shell、子进程和信号默认兼容 Windows、Linux、macOS，平台差异集中在 adapter。
- 结构化事件用于观测，不从日志文本、异常文案或 UI 状态反推业务事实。

## 系统边界

```text
mind.py
  -> composition.py
      -> agent
      -> protocol
      -> infrastructure
      -> observability
  -> frontends
```

| 边界              | 职责                                         | 不得拥有                          |
|-------------------|----------------------------------------------|-----------------------------------|
| `mind.py`         | 稳定进程入口和具体工厂选择                   | 领域规则、前端状态、隐式服务定位  |
| `composition.py`  | 组装应用宿主、运行资源和公开能力             | 业务分支、协议解析、UI 逻辑       |
| `agent/`          | 本地代理的领域、用例、编排、端口和持久事实   | 具体 UI、配置路径、HTTP 实现      |
| `protocol/`       | 可供多前端复用的 `mind.chat` wire SDK        | 本地运行生命周期、UI 和配置策略   |
| `frontends/`      | CLI、TUI、stdio MCP、Subscription 和终端适配 | Run/Effect 权威状态、具体能力组装 |
| `infrastructure/` | 配置、平台、持久化、服务、工作区和外部实现   | 前端状态、线上 Turn 权威状态      |
| `sidecars/`       | 随客户端发布的隔离子进程入口和固化资产       | 运行编排、审批决定、线上协议语义  |
| `observability/`  | 结构化日志、报告和异常观测                   | 业务状态机、用户交互策略          |
| `metadata/`       | 产品名称、版本、编码和展示元数据             | 配置读取、运行状态                |
| `npm/`            | npm launcher、平台包和发布流程               | Python 运行时、本地执行状态       |
| `backend/`        | 独立打包服务                                 | 对客户端包的反向依赖              |

## `agent` 分层

```text
agent/
├── protocol/       # 进程内 Command、Event、Item 和能力值
├── domain/         # 纯规则、身份、状态转换、权限和补丁模型
├── ports/          # 跨职责的最小能力契约
├── application/    # 用例、执行上下文、稳定结果和展示投影
├── harness/        # Session、Run、Agent、Hook、Tool 的生命周期编排
├── stores/         # 本地权威事实和幂等边界
├── capabilities/   # 本机能力实现
├── adapters/       # 线上协议和外部代理映射
└── composition.py  # 只组合 agent 内部能力
```

各层职责如下：

- `agent.protocol` 保存与传输无关的本地类型化契约，不是 HTTP、SSE 或 WebSocket schema。
- `agent.domain` 只依据显式输入计算规则，不读取环境、文件、数据库或前端状态。
- `agent.ports` 描述真实可替换能力和生命周期，不充当 Service Locator。
- `agent.application` 协调领域规则与端口，不拥有事件循环、连接、进程或 UI 控件。
- `agent.harness` 拥有 Session、Run、Agent、Hook、Tool、MCP 和 Subscription 的并发与关闭。
- `agent.stores` 拥有本地事实、CAS 和幂等边界；Store 接收已解析路径或连接。
- `agent.capabilities` 实现本机能力，`agent.adapters` 隔离线上协议和外部代理变化。

跨层契约使用 `Protocol`、ABC、dataclass 或具名结果。创建方负责关闭生命周期；可空依赖
只表示真实可选能力，不作为未注入时的兼容回退。第三方对象必须在 adapter 边界转换，不能
穿透到 application 或 domain。

恢复历史会话时，`ConfigSession` 保留启动目录和 CLI/Profile 覆盖，`SettingsSession`
准备目标目录的配置、偏好与权限。组合根先构建目标工作区能力和工具注册表，再交给
`agent.harness.sessions.workspace_change.WorkspaceChange` 持有。`RootConversationSession`
在旧目录结束旧会话后同步提交工作区，随后更新历史游标。切换收尾释放旧编码资源并重新
建立外部 MCP；准备失败只释放待采用资源，提交后的清理错误不回退活动会话。
项目 Skills 的发现及缓存以显式工作区为键，子代理只在会话边界更新后续提交的依赖。
冻结 Turn 和已保存的子代理线程保留原始 cwd；恢复执行前校验与活动工作区一致，目录不同
时拒绝继续执行并要求回到原目录，不能修改冻结快照来适配新的工具注册表。

## 依赖方向

```text
domain / agent.protocol
        ^
      ports
        ^
   application
        ^
     harness

stores / capabilities / adapters / infrastructure / frontends
        -> 通过上述契约接入
```

依赖规则：

1. `domain` 与 `agent.protocol` 不依赖 application、harness、stores、capabilities、
   adapters、infrastructure 或 frontends。
2. `application` 不依赖 harness、stores、capabilities、infrastructure 或 frontends。
3. `harness` 通过 application、domain、protocol 和 ports 组织生命周期，不导入前端。
4. `agent.composition` 只组装 agent 内部对象，不导入 infrastructure。
5. `infrastructure` 可以实现 agent ports 或消费 application 契约，但不反向控制运行生命周期。
6. `frontends` 只调用 application、ports、protocol 或显式注入的 infrastructure adapter。
7. 顶层 `protocol` 不依赖 agent、frontends、infrastructure、server 或 backend。
8. `backend` 只依赖自身、标准库和第三方库；客户端代码不导入 backend。
9. `sidecars` 不导入 Python 业务包；只有 `infrastructure.sidecars` 可以驱动其私有 IPC。

`tests/test_package_architecture.py` 与 `tests/architecture/` 中的专题审计持续检查这些边界；根文件
保持稳定入口，专题审计共享单一源码清单与 AST 缓存。

## 组合与生命周期

`mind.py` 和根 `composition.py` 是唯一具体组合边界：

1. `mind.py` 选择应用布局、平台实现、能力工厂和前端入口。
2. `agent.composition.create_runtime_services` 创建与 UI 无关的运行服务。
3. 根 `composition.py` 组装应用宿主、Session、执行资源、持久化和服务 owner。
4. CLI、TUI、MCP 和 Subscription 接收已组装的 host、factory 或 port。
5. `ProcessResourceOwner` 依序关闭前台 Turn、后台任务、MCP、Sidecar、服务、Sandbox、
   Store 和观测资源；单项清理失败不得跳过后续资源。

跨前端传递的完整组合对象统一命名为 `host`。进入 feature 或 application 后继续收窄为
实际消费的端口，不把应用宿主当作通用服务定位器。业务模块不得通过全局变量、Controller、
前端对象或产品名反射发现能力。

## Command、Session 与 Run

### 身份与入口

| 范围         | 稳定身份                                      | 序号或幂等键                                    |
|--------------|-----------------------------------------------|-------------------------------------------------|
| 本地运行时   | `session_id`、`run_id`                        | `command_id`、`idempotency_key`、Run `sequence` |
| 线上协议     | `cid`、`sid`、`turn_id`、`attempt`、`item_id` | `request_id`、`client_message_id`、`event_seq`  |
| Subscription | 订阅 `session_id`、任务 `call_id`             | `message_id`、`seq`、`last_acked_seq`           |

这些身份和序号不得互相赋值或比较。Adapter 显式保存映射，不依赖字符串碰巧相等。

所有主动执行入口最终映射为同一应用命令链：

```text
frontend adapter
  -> immutable Command
  -> Session command queue
  -> Run actor
  -> model / tool / approval ports
  -> durable event and projection
  -> frontend adapter
```

Command 入队前必须冻结完整语义、会话创建或续用意图和 `exec_env`。重试与安全 redispatch 复用原快照；相同幂等键
和相同语义返回既有结果，不同语义产生冲突。

Review 使用独立 `SubmitReviewCommand`，在本地 Run 入账前冻结 target、Git workspace、execution、
environment、`session_mode`、`request_id` 和远端 Turn 坐标。执行与恢复上下文均使用冻结的
`session_mode`。确认登记后只观察既有 Turn；冷恢复对已登记项执行
attach/replay，对尚未开始网络操作的 queued Review 以原 Command 安全 redispatch，不把它恢复
成普通 message 或重新打开旧菜单。

Review 复用工作区的 `exec_command` 和 `write_stdin`，按需读取 diff、仓库指令和相关文件；
工具目录在提交时冻结，命令执行使用 `read-only` 沙箱和 `never` 审批策略。

### 单写者与终态

每个 Session 只有一个状态写入者。调用方提交 Command，不直接修改 Session、Run、计划、工具
或审批状态。并发输入、取消、审批和恢复均经命令队列或具名 mailbox 协调。

Run 终态不可离开。连接关闭、展示完成、HTTP 回执、任务取消、SSE EOF 或异常文本都不能替代
逻辑终态事实。

### 待发送输入与运行恢复

pending input 由 TUI Session actor 持有，中断后恢复编辑器。

提交的 Durable Run 必须在首次网络操作前持久化完整模型请求。恢复时 status 只确定
待观察 Turn 和 replay 水位；本地持有冻结请求时，必须完成 attach 并持久化缺失正文及唯一终态，
才能解除执行门。历史残留若既无冻结请求也无远端 Turn 身份，只能记录失败的恢复决议并解除
本地门禁，不得猜测远端结果或自动重投原输入。

## 线上协议

`protocol/` 是独立 wire SDK：

```text
protocol/schema     # 严格字段、判别联合、身份和值约束
protocol/transport  # 认证、端点、可靠请求、SSE 和报告传输
protocol/client     # chat、review、turn control、tool、effect、fork、compact 等用例
```

前端可以复用协议 SDK，但不要求共享 Python UI。协议层不拥有本地 Session、Run、工具执行器、
配置或前端生命周期；`agent.protocol` 的本地事件也不得暴露为远程 SDK。

线上 `event_seq` 在 `cid + sid` 范围内跨 Turn 单调。客户端只在完整处理后推进确认游标，并以
`turn.completed` 作为唯一逻辑终态。其 `status` 区分 completed、interrupted、failed 和
cancelled；服务端内部存储标志不得成为第二个公开终态。

## Item 与前端展示

正式展示事件先由 `CanonicalItemReducer` 归约：

- active 视图只包含未被 retry 或 `presentation.superseded` 替代的 revision；
- audit 视图保留所有展示 attempt；
- 普通 assistant 正文只从 active text item 派生；结构化 Review 正文只从 active review item 的严格 `output` 派生；
- approval snapshot 只裁决旧审批，不推进确认游标；
- gap 等控制信号不创建展示 item。

Application 只产出与 UI 工具包无关的展示值。前端负责交互、布局和渲染，不从原始 provider
载荷、异常文本或日志重建业务语义。

上下文用量是非 Item 的独立事实。`RootConversationSession` 持有应用层用量投影，按
`cid + sid` 和线上 `event_seq` 替换完整快照；它跨越单个 OutputSession，既不取得活动表面，
也不改变 Turn 终态。缓存只保存已确认的远端记录，随本地历史游标淘汰，不是第二个计数
权威。TUI 通过只读订阅消费投影，关闭运行时时解除订阅；恢复中间值沿既有传输追平边界
抑制，Review 和子代理不写入主会话用量。冷恢复及历史裁剪通过注入的用量恢复端口读取
既有报告授权和分页回放中的保留快照；该读取有超时边界，不推进聊天确认游标。TUI 在
恢复目标尚未绑定时隐藏默认新会话用量，完成权威恢复后才展示。

### 终端能力

TUI 读取输入前创建一次不可变终端能力快照。终端身份、颜色、默认前景背景和输出能力是独立
事实；探测只发生在 platform adapter，renderer 不重新读取环境或平台状态。组件消费语义样式，
由唯一 resolver 适配 TrueColor、ANSI 256、ANSI 16 和无色模式。终端身份或颜色能力不得被
当作所有终端特性的总开关。

原始色深与渲染色深分离：未知能力按 ANSI 16 渲染，明确无色保持无色。IDE 背景策略由
共享 resolver 派生，组件在合成样式前应用，输出边界保证背景不泄漏；禁背景不禁用语法
前景或增删提示。补丁无背景时，未识别语法的正文使用增删前景，行号使用次要文本样式。

补丁、Markdown 与工具代码预览共享语法主题和词法器边界；主题仅产生前景样式，语法角色
按目标色深映射。流式解析器由对应展示生命周期持有，完整渲染和历史重绘从同一冻结能力
选择主题。语言识别只使用显式语言、文件路径和结构化内容中确实可用的首行，不重读工作区。
补丁逐 hunk 独立解析旧侧和新侧，删除行使用旧侧状态，上下文与新增行使用新侧状态。
不连续 hunk 不共享词法状态；缺少前文时只基于可见片段高亮，超过输入上限时保留原文和增删前景。

### Turn 表面

每个 Turn 创建带稳定 scope 的 `OutputSession`，并区分四类出口：

- `OutputControlPort`：流式输出资源；
- `ContentSink`：正文事实；
- `PresentationSink`：稳定展示单元；
- `OutputActivityPort`：等待、工具、审批、重试和恢复等活动事实。

四者共享 scope，但不读取彼此状态或替代彼此生命周期。协议和工具活动由
`TurnActivityProjector` 发布；人工审批批次由实际展示端发布 `ApprovalPresentationChanged`，
其事实出口随 TUI OutputSession 打开时绑定、关闭时解除。所有活动通过
`reduce_turn_surface() -> TuiTurnSurfaceCoordinator` 形成一个前景投影。
Reducer 是纯状态转换；Coordinator 独占 timer、lease、replay 抑制和画面提交。

Turn 表面遵循以下不变量：

- `lifecycle` 表示 Turn 是否运行，`status_requested` 表示是否请求状态行，两者相互独立；
- 正文和审批可以临时隐藏状态行；replay 抑制历史活动动画并显示当前恢复状态，不能结束 Turn；
- 自动评审、策略决定和已有授权不取得人工审批表面；真实人工审批批次暂停等待及重试、恢复提示，连续换卡不恢复状态行；
- 工具开始立即请求状态行，工具完成只释放工具 lease；
- 同一因果交接（包括同来源重试替换及重连到 replay 的转换）以原子批次归约，只提交最终投影，不产生中间空帧；
- 终端可见内容未变化时只推进 revision，不重建组件、重置 elapsed time 或推迟待交接投影的截止时间；
- 重试与恢复提示遵循本地最短可见时间；结束后恢复 Thinking 沿用生命周期延时，正文、人工审批和终态可以立即接管；
- 正文实际进入画布后才产生 `AssistantVisible`，状态行撤下与正文提交属于同一视觉事务；
- 旧正文、工具记录和完成分隔线先提交，再绑定新正文身份；恢复状态槽的首帧直接使用新标题和明细；
- commentary 正文完成后只在正文流已经 idle 且 Turn 仍运行时恢复状态行；final answer 和
  phase 未声明的正文不自行恢复，后续状态只能由明确活动事实请求；
- transport retry 可以暂时覆盖已显示正文，但不释放、替换或重复提交正文；
- retry、supersede 和 replay 的迟到旧事件不得重新取得画面；
- 只有唯一 Turn 终态可以清空 timer、retry、工具和审批 lease 并释放输入边界。

中断和输入必须保持以下语义：

- `/turn/interrupt` 的 `204` 只确认中断已登记，不表示 Turn 已结束；创建竞态中的 404 只能在
  有界窗口内复用同一 `request_id` 重试；
- 第一次 `Ctrl+C` 保留执行门并等待权威终态；确认窗口内再次 `Ctrl+C` 可以退出本地进程，
  但不得启动下一 Turn、重复提交输入或自动重投未知输入；
- 活动 Turn 中的 `Esc` 可以冻结当前 pending steer，并在中断终态后按 FIFO 形成一个新 Turn；
  `Ctrl+C` 不设置这一自动提交意图；
- 空闲普通文本的 Tab 与 Enter 均提交 Turn；活动 Turn 中 Enter 尝试 steer，Tab 排入下一 Turn；
  排队文本只在出队后解析 slash 或 Shell 语义；
- 本地存在冻结请求时，冷恢复必须 attach 到目标水位并补写正文和终态后再解除执行门。

attach/replay 只归约历史事实，不启动历史工具的瞬时 timer。退出 replay 前必须按 `call_id` 对账客户端工具：
已收到结果的调用只收束投影，仅仍等待结果的调用可由当前进程接管；不确定状态保持 recovery
gate，不得重放副作用。

`OutputSession.close()` 先停止输出资源，再关闭 activity scope；两步均幂等，任一步失败仍继续
另一项。无活动画面的前端使用明确的被动实现，不创建伪状态。

## 工具、审批与 Effect

单个 Turn 的工具分派器拥有顺序执行任务和完成 mailbox；事件消费所有者在等待工具期间继续
处理输入确认、控制和远端终态，并归约工具异常。工具批次完整性、调用去重和 Effect 对账仍
经过原有账本。权威终态或观察结束时回收执行任务，完成本地清理后才交还输入调度。
空终端轮询的等待活动由 Harness 从实际执行开始配对释放，直接调用与嵌套调用共用此路径。

```text
model intent
  -> application tool contract
  -> execution policy
  -> approval when required
  -> durable effect preparation
  -> capability / infrastructure execution
  -> typed result
  -> protocol delivery and reconciliation
```

核心规则：

- 本地工具、provider 内置工具和 hosted tool 是不同边界，不通过字段猜测互换。
- 参数在执行前校验，第三方结果在 adapter 边界转换。
- Approval、Tool Call 和 Effect 各有稳定身份；`request_id` 只承担传输幂等。
- 审批只决定当前动作，不成为平台或服务端的全局安全策略。
- MCP 调用必须校验完整调用身份，并消费正式 Effect identity；缺失时不得本地合成权威事实。
- 外接 MCP 控制以运行实例、工作区和原始配置键定位；连接及工具路由由 infrastructure 的逐服务 owner 维护，资源栈必须在进入它的任务中退出。
- 配置启用、连接状态和工具数量是不同事实。已观察到断线时撤下该连接的工具；清理未确认时保留资源所有权，不建立重叠连接。
- Session grant 只在相同 Session、Environment、server、connector 和 tool 范围内复用。
- 交互审批只拥有待决请求和选择；决定提交后即锁定，终态由结构化事实投影。
- 外部效果成功但本地提交未知时进入 reconciliation，不伪装成失败或自动重放。
- 不可重放效果不得由接管 actor 自动重试；可重试效果必须有明确幂等保证。
- `/tool-result` 只发送正式协议字段，不携带工作区、Sidecar 或 UI 私有状态。

## 持久化与恢复

| 事实                 | 所有者                                                    | 恢复原则                                  |
|----------------------|-----------------------------------------------------------|-------------------------------------------|
| Run、Command、Event  | `agent.stores.runs`                                       | 幂等写入、单调事件、终态不可离开          |
| Remote Turn request  | `agent.stores.runs`                                       | 网络前冻结，按原坐标 attach/replay        |
| Agent graph、mailbox | `agent.stores.agents`                                     | 活动投递可恢复，消息身份稳定              |
| Session cursor       | `agent.stores.sessions`                                   | 只保存本地会话索引和分支事实              |
| Transcript           | `agent.domain.transcripts` + `infrastructure.persistence` | 值契约与 IO 分离，损坏可观测              |
| Approval             | `agent.stores.approvals`                                  | 首个决定权威，重复请求幂等                |
| Effect               | `agent.stores.effects`                                    | prepared、committed、unknown 等事实可对账 |

恢复只从持久事实和安全点开始。Redis、当前连接、前端缓存和日志都不是 authority。已提交事件
不得丢失，未确认效果不得重复执行，无法确定的结果必须显式对账。

## 基础设施

`infrastructure/` 按外部变化来源分组：

- `config/`：配置 schema、分层、偏好、信任和路径契约；
- `platform/`：进程、Sandbox、Shell、信号、编码和平台差异；
- `workspace/`：工作区命令、补丁、diff 和运行资源；
- `mcp/`：MCP session、目录、调用和结果适配；
- `persistence/`：Transcript 和会话索引的具体存储；
- `services/`：服务 owner、健康、Helix、Turn 环境和配置宿主；
- `skills/`、`hooks/`、`sidecars/`、`update/`：对应外部资源的适配与生命周期。

本地进程输出以字节进入 `infrastructure.platform` 的统一解码生命周期；stdout 与 stderr
分别持有增量状态，系统读取块不构成字符边界。只有完整字符或 EOF 收束后的文本才能进入
workspace 和 frontend，展示层不得再次猜测进程输出编码。

Sandbox sidecar 的父控制终端隔离由 `infrastructure.platform` 在启动时建立：Windows 使用
无控制台启动，POSIX 使用独立会话；标准输入、协议输出和诊断 stderr 经各自管道传递。
命令中断和关闭经 sidecar 协议交付，交互命令的 PTY 由 sidecar 单独创建，不能依赖前端终端的
进程组信号。正常关闭和父进程退出造成的 IPC 断开均须收束 sidecar 及其命令进程。

进程管理器独立持有后台命令及原始 `cid/sid/turn_id/call_id`。进程退出并收束输出后发布只读
完成快照；模型轮询消耗的增量缓冲与展示缓冲分离。完成事实按进程会话容量有界保留，已退出
会话的资源移除不立即删除完成快照。TUI 按所属会话、进程身份提交一次命令完成记录，普通
历史、transcript 和复制内容使用同一份保留输出；工具等待取消不等于后台进程退出。

`MIND_HOME` 是配置根，拥有 `config.toml`、用户规则和 Hook 配置。`MIND_STATE_HOME` 是运行
状态根，拥有 history、sessions、reports、Helix 和本地 SQLite；未设置时才默认使用
`MIND_HOME`。配置文件只要求可读，状态根必须可创建、可写并支持 SQLite 文件锁。显式状态根
失败时必须中止启动，不得回退到其他账本。

内置配置宿主只负责配置 HTTP 页面、路由和进程内生命周期；配置事实仍由
`infrastructure.config` 所有。`npm/` 只负责 launcher、平台包、产物同步和发布，不参与 Python
运行时或协议。两者都不得取得本地执行状态所有权。

## JavaScript Sidecar

JavaScript REPL 是本地执行能力，稳定工具名为 `js_repl` 和 `js_repl_reset`。Application 负责
参数、授权和结果投影；Harness 负责会话生命周期；`infrastructure.sidecars.javascript` 负责
进程、私有 IPC 和固化资产；`sidecars/js_repl` 只保存随产品发布的运行时文件。

Sidecar 必须满足：

- 执行端口与会话生命周期端口分离，由组合根注入；
- Provider 按 `session_id` 隔离会话，并冻结工作目录和 `sandbox_mode`；
- 每个安全信封拥有独立 Node 进程，同一会话内执行按 FIFO 串行；
- 权限信封变化、超时、取消、reset、close、EOF 或协议错误均关闭原进程；
- 私有 JSONL 帧在边界完成类型、字段、身份、关联和大小校验；
- 嵌套工具提案必须重新经过工具可见性、schema、审批和 Effect 链；
- Sidecar 私有状态不得进入线上协议、Transcript 元数据或前端状态；
- 固化的 kernel 与 vendor 资产不得重写，构建和测试以固定散列验证完整性；
- wheel、源码分发和独立可执行包均包含完整资产，路径不依赖当前工作目录。

## 可观测性

业务代码只调用 `observability` 的结构化入口，不直接创建标准库 logger，不吞异常，也不以日志
文本作为协议。事件按可用范围携带 session、run、线上坐标、command/effect identity、环节、
结果类别和异常来源；正文、凭据、完整工具输出及未筛选载荷不得进入日志。

可观测性只投影事实，不拥有重试、取消、审批或终态决定。

## 扩展与验收

新增或替换能力时：

1. 先确定状态所有者、生命周期和依赖方向。
2. 判断职责属于 domain、application、harness、adapter 还是 frontend。
3. 优先复用现有端口；只有出现真实可替换边界时才新增端口。
4. 由组合边界注入实现，并删除动态发现、旧字段、旧路径和备用回退。
5. 同步受影响的正式协议、稳定文档和契约测试。

禁止创建无明确所有者的聚合 `core`、`common`、`shared` 或 `utils` 层；禁止前端复制协议
reducer、Run 状态机或 Effect 对账；禁止测试替身扩大生产公开面；禁止让 Sidecar、配置宿主或
npm workspace 取得运行状态所有权。

跨边界变更的准出条件：

- 职责、依赖、状态所有权和关闭顺序可由代码直接确认；
- 新路径覆盖完整用例，被替代路径和回退已经删除；
- Command、Event、Effect、Approval 和线上身份保持稳定；
- 受影响的 CLI、TUI、MCP 和 Subscription 入口使用同一应用语义；
- 协议变更同步更新服务端正式契约、schema、client 和契约测试；
- 持久事实可以驱动恢复，未知 Effect 有明确对账路径；
- 包边界审计、定向行为测试和发布检查按 `AGENTS.md` 通过。
