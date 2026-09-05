# Agent Harness 最终架构

状态：现行架构决策（2026-09-02）

本文是 ProxyMind 客户端 Agent Harness 的唯一架构权威，定义职责归属、依赖方向、
状态所有权、生命周期和验收边界。需求、修复与重构必须先符合本文，再进入实现。

线上 `mind.chat` 的字段、端点、事件、错误和恢复语义只以服务端正式契约为准；客户端映射位于
`protocol/schema/` 和 `protocol/client/`。本文不复制服务端状态机，也不改变 `backend/` 的独立
打包边界。

文档边界：`AGENTS.md` 只规定代理的工作方式、代码质量和验证流程；本文件只规定系统架构、
职责、依赖、状态所有权、生命周期和稳定不变量；服务端正式契约与 `protocol/` 负责线上 wire
契约；领域细节由对应目录的局部文档维护。

## 架构目标

Agent Harness 必须同时满足以下约束：

- 可维护：领域规则、应用用例、运行编排、外部实现和展示各有唯一所有者。
- 可扩展：模型、工具、审批、持久化、传输和前端通过具名端口替换，不修改 Session 单写者或终态规则。
- 可恢复：Command、Run、外部 Effect 和线上游标具有稳定身份，未知结果进入显式对账。
- 可观测：结构化事件在职责边界产生，业务模块不直接创建标准库 logger，也不从日志文本推断状态。
- 可移植：路径、Shell、子进程和信号行为默认兼容 Windows、Linux、macOS，平台差异只在 infrastructure adapter 内出现。
- 可验证：依赖方向、公开 API、生命周期和协议边界由自动化守卫锁定。

## 系统边界

```text
mind.py
  -> composition.py
      -> agent
      -> protocol
      -> infrastructure
          -> sidecars
      -> observability
  -> frontends

frontends
  -> agent application/ports
  -> protocol client
  -> infrastructure adapters

infrastructure
  -> agent application/domain/ports/stores
  -> protocol schema
  -> observability
```

顶层职责固定如下：

| 边界 | 唯一职责 | 不得拥有 |
| --- | --- | --- |
| `mind.py` | 稳定进程入口、具体工厂选择和最终启动 | 领域规则、前端状态、隐式服务定位 |
| `composition.py` | 组装 `ApplicationHost`、进程资源和公开能力 | 业务分支、协议解析、UI 逻辑 |
| `agent/` | 本地 Agent Harness 的领域、用例、编排、端口和本地事实 | 具体 UI、配置文件路径、HTTP 实现 |
| `protocol/` | 可供多前端复用的 `mind.chat` wire SDK | Harness 生命周期、本地 UI 或配置策略 |
| `frontends/` | CLI、TUI、stdio MCP、Subscription 和终端展示适配 | Run/Effect 权威状态、具体能力组装 |
| `infrastructure/` | 配置、平台、MCP、持久化、服务、技能、工作区和内置宿主实现 | 前端状态、线上 Turn 权威状态 |
| `sidecars/` | 随客户端发布的隔离子进程入口和私有运行时资产 | Harness 编排、审批决策、线上协议语义 |
| `observability/` | 结构化日志、报告和异常观测入口 | 业务状态机、用户交互策略 |
| `metadata/` | 产品名称、版本、编码和展示元数据 | 运行状态、配置读取 |
| `infrastructure/services/configuration_host/` | 客户端内置的可选配置 HTTP 宿主、配置页和健康检查 | Harness 状态、`mind.chat` 服务端语义 |
| `npm/` | npm launcher、平台运行时包和发布工作区 | Python 运行时、Harness 状态、线上协议语义 |
| `backend/` | 独立打包服务 | 对客户端包的反向依赖 |

## Agent 包结构

```text
agent/
├── protocol/       # 进程内 Command/Event/Item/能力值，不是 wire SDK
├── domain/         # 纯领域规则、身份、状态转换、权限和补丁模型
├── ports/          # 跨职责的最小能力契约
├── application/    # 用例、执行上下文、稳定结果和展示 projection
├── harness/        # Session/Run/Agent/Hook/Tool 的并发与生命周期编排
├── stores/         # Run、Agent、Session、Transcript、Approval、Effect 事实
├── capabilities/   # 通过端口提供的本机能力
├── adapters/       # 线上协议和外部 Agent 的映射
└── composition.py  # 仅组合 agent 内部能力，不导入 infrastructure
```

### `agent.protocol`

负责进程内、与传输无关的类型化契约：

- `SubmitTurnCommand` 等 Command；
- `RunEvent`、事件类别和稳定顺序；
- `CanonicalItem` 等 Harness 内部投影；
- 模型能力及不可变 JSON 值。

它不是 HTTP、SSE 或 WebSocket schema。不得导入 `protocol.client`、具体网络客户端、
配置、持久化、前端或平台实现。

### `agent.domain`

负责无 IO 的业务规则和值对象，包括 Run 状态、身份、权限组合、执行策略、工具可见性、
Hook 匹配、Transcript 合并和补丁语义。领域函数只依据显式输入返回决定，不读取环境、
文件、数据库或当前前端。

领域层可以复用稳定的 wire 值枚举，但不得发起协议请求或依赖具体 adapter。

### `agent.ports`

负责跨层契约。端口应按一个可替换能力或生命周期命名，参数与返回值必须准确描述真实
契约。端口不得成为聚合所有能力的 Service Locator，也不得为单个函数增加等价 facade。

跨层对象满足以下要求：

- 使用 `Protocol`、ABC、dataclass 或具名结果；
- 生命周期由创建方关闭，消费者不得猜测实现类型；
- 可空依赖只表示真实可选能力，不能作为未注入时的兼容回退；
- 端口实现失败返回稳定结果或抛出职责明确的异常，不通过动态属性传递状态。

### `agent.application`

负责调用方可见的用例和投影：Turn 提交、环境快照、工具执行、审批协调、Hook 输入输出、
Agent 消息、RunResult 和 PresentationView。它协调领域规则与端口，但不拥有事件循环、
数据库连接、网络会话或 UI 控件。

`agent.application` 的包级公开面保持小型；消费者从职责模块导入内部值对象，不通过根包
暴露所有实现。

### `agent.harness`

负责长生命周期和并发所有权：

- `sessions/`：Session 单写者、Command 队列、恢复和关闭；
- `execution/`：Run actor、根 Turn、Subagent、压缩、终结和 Sidecar 等执行资源；
- `agents/`：Agent 树、活动 Turn、mailbox 投递和根会话注册；
- `hooks/`：Hook 作用域、注册、调用顺序和收束；
- `tools/`：客户端工具、计划工具和调用闭环；
- `mcp/`、`subscription/`：对应长驻运行资源的 owner；
- `process_lifecycle.py`、`process_resources.py`：进程关闭顺序和失败收敛。

Harness 可以协调 application 用例和 ports，不得读取具体配置文件、构造 HTTP client、
创建 UI 对象或把本地 Run 状态冒充为线上 Turn 状态。

### `agent.stores`

负责本地权威事实和 CAS/幂等边界。按 `agents`、`approvals`、`effects`、`runs`、
`sessions`、`transcripts` 分组。Store 接收已解析的路径或连接，不自行发现应用目录；
文件和数据库 IO 的具体媒介可由 infrastructure 提供。

Redis、缓存和内存视图只能作为可重建镜像，不得覆盖持久事实。

### `agent.capabilities` 与 `agent.adapters`

Capabilities 实现本机文件、进程、环境、MCP、Helix 等端口，不读取前端状态。
Adapters 负责边界映射：

- `adapters/protocol` 将 Harness 请求映射到顶层 wire SDK，并维护线上游标和
  Canonical Item reducer；
- `adapters/agents` 连接子 Agent 执行、消息和 fork context；
- `adapters/turns` 连接稳定入口与根 Turn 用例。

Adapter 是外部变化的隔离边界；跨层只暴露已经确定的领域或 application 契约。

## 依赖规则

依赖只能朝向职责更稳定的一侧：

```text
domain / agent.protocol
        ^
        |
      ports
        ^
        |
   application
        ^
        |
     harness

stores / capabilities / adapters / infrastructure / frontends
        -> 通过上述公开契约接入
```

规则解释：

1. `domain` 与 `agent.protocol` 不依赖 application、harness、stores、capabilities、
   adapters、infrastructure 或 frontends。
2. `application` 不依赖 harness、stores、capabilities、infrastructure 或 frontends。
3. `harness` 通过 application、domain、protocol 和 ports 组织生命周期，不导入前端。
4. `agent.composition` 只组装 agent 内部对象，不导入 infrastructure。
5. `infrastructure` 可以实现 agent ports，也可以消费 application 的具名工具契约；它不
   反向控制 Harness 生命周期。
6. `frontends` 只调用 application/ports/protocol 或显式注入的 infrastructure adapter，
   不构造模型、Store、MCP runtime 或进程 owner。
7. `protocol` 不依赖 `agent`、frontends、infrastructure、server 或 backend。
8. `backend` 只依赖自身、标准库和第三方库；客户端代码不导入 backend。
9. `sidecars` 不导入 Python 业务包；只有 `infrastructure.sidecars` 可以解析、启动并通过
   私有 IPC 驱动对应宿主，其他包只依赖 agent ports。

## 组合与生命周期

`mind.py` 和 `composition.py` 共同构成唯一具体组合边界：

1. `mind.py` 选择应用目录、平台实现、模型/MCP/工具工厂和前端入口。
2. `agent.composition.create_runtime_services` 创建与 UI 无关的 Harness 服务集合。
3. `composition.py` 组装 `ApplicationHost`、Session、执行资源、持久化和服务 owner。
4. CLI/TUI/MCP/Subscription 接收已组装的 host、factory 或 port。
5. `ProcessResourceOwner` 按确定顺序关闭前台 Turn、后台任务、MCP、Sidecar、服务、
   Sandbox、Store 和观测资源；清理失败必须可观测且不得跳过后续资源。

跨前端传递的完整组合对象统一命名为 `host`，不得以产品名命名参数或成员；进入 feature
或 application 用例后继续收窄为实际消费的具名 port，不把 `ApplicationHost` 当作通用
服务定位器。`Mind`/`mind` 只保留在品牌、稳定入口和正式 wire/MCP 标识中。

业务模块不得从 `Mind`、Controller、frontend 或全局变量反射发现能力。需要的新能力应先
形成最小端口，再由组合边界注入完整调用链。

## Command、Session 与 Run

### 身份

本地身份和线上身份必须分开：

| 范围 | 稳定身份 | 序号/幂等键 |
| --- | --- | --- |
| 本地 Harness | `session_id`、`run_id` | `command_id`、`idempotency_key`、Run 内 `sequence` |
| 线上协议 | `cid`、`sid`、`turn_id`、`attempt`、`item_id` | `request_id`、`client_message_id`、`event_seq` |
| Subscription | 订阅 `session_id`、任务 `call_id` | `message_id`、订阅 `seq`、`last_acked_seq` |

三组序号不得互相赋值或比较。Adapter 显式保存映射，不依赖字符串碰巧相等。

### 命令入口

CLI、TUI、stdio MCP 与 Subscription 最终都把主动执行映射为同一 application Command：

```text
Inbound adapter
  -> immutable Command
  -> Session command queue
  -> RunActor
  -> model / tool / approval ports
  -> durable event + projection
  -> frontend adapter
```

Command 必须在入队前冻结完整语义与 `exec_env` 快照；重试和安全 redispatch 复用原快照，
不能重新读取当前进程环境。相同幂等键和相同语义返回既有结果；不同语义必须冲突。

### 单写者

每个 Session 只有一个状态写入者。调用方提交 Command，不直接修改 Session、Run、计划、
工具或审批状态。并发输入、取消、审批和恢复都经由队列或具名 mailbox 协调。

Run 的状态转移由领域规则和 actor 共同约束。终态不可离开；连接关闭、局部展示完成或
异常文本不能代替逻辑结算事实。

### Durable Queue

显式 Durable Queue 与 TUI 当前 Turn 内的普通 pending input 是两个不同入口。普通 pending
input 由 TUI Session actor 持有，中断后恢复编辑器；只有用户显式选择持久排队时才能调用
服务端 Queue 命令，二者不得自动互相转换。

服务端 Queue snapshot/receipt 是队列成员、顺序、版本和 Queue 到 Turn 转换的唯一真相。
客户端不得维护第二套权威队列；但必须在外部命令发送前，把入队时完整模型请求、本地 Run
Command、`submission_id`、`client_message_id` 及 add/start `request_id` 写入独立本地恢复账本。
该账本只拥有客户端工具、权限、环境和输入的冻结执行语义，以及不确定命令的幂等恢复身份。

add/start 响应丢失时复用已持久化的原 request id；服务端明确拒绝 start 后才允许下一次显式
尝试生成新 request id。`queue.start` 成功只绑定一个已经由服务端创建的 Turn，后续客户端必须
通过 attach/replay 观察它，不得再调用 `/mind-chat`。本地执行快照缺失时仍可展示服务端 Queue
item，但不得用当前配置猜测并执行。

直接提交的 Durable Run 同样必须在提交 Hook 和工具目录冻结完成后、首次 `/mind-chat` 网络操作前，
持久化完整 `ModelStreamRequest`。进程恢复时 `/turn/status` 只确定应观察的最新 Turn 及 replay
目标水位；只要本地 Run 持有冻结请求，就必须通过 `/mind-attach` 消费缺失正文和唯一终态后才能
解除本地执行门。内存 Session cursor 或终态 status 不证明 Transcript 已持久化，不能据此跳过重放。

## 线上协议边界

`protocol/` 是独立 wire SDK：

```text
protocol/schema     # 严格字段、判别联合、身份和值约束
protocol/transport  # 认证、端点、可靠请求、SSE 与报告传输
protocol/client     # chat、turn control、tool、effect、fork、compact 等用例
```

TUI、桌面端和 Web 可以复用同一线上协议，但不要求共享 Python UI。可替换前端只需要：

- Protocol Client：命令、attach/replay、游标和可靠交付；
- Canonical Item reducer：按 `event_seq` 去重并处理 retry/presentation 替代；
- 本地能力 adapter：工具、审批、附件和展示。

`agent.protocol` 的本地 Event 不得暴露为浏览器或远程 SDK；`protocol` 也不得拥有本地
SessionLoop、RunActor、工具执行器或前端生命周期。

线上 `event_seq` 在 `cid + sid` 范围内跨 Turn 单调。Protocol Client 只在完整处理后推进
确认游标，并以唯一权威事件 `turn.completed` 结束逻辑轮次。该事件的 `status` 区分
`completed`、`interrupted`、`failed` 与 `cancelled`；正文或单项完成、interrupt HTTP 回执、
SSE 关闭和前端退出都不能替代它。服务端内部 settled 存储标志不得暴露为第二个公开终态。

## Canonical Item 与展示

正式可展示事件先由 `CanonicalItemReducer` 归约，再交给前端：

- active 视图只包含未被 provider retry 或 `presentation.superseded` 替换的 revision；
- audit 视图保留所有展示 attempt；
- 最终 `assistant_text` 只从 active text Items 派生；
- approval snapshot 只裁决旧审批状态，不推进客户端确认游标；
- `stream.gap` 等控制信号不创建 Item；
- sources、工具、审批和正文归属不能由各前端重复实现。

Application 产出与 UI 工具包无关的 PresentationView。Terminal/TUI/未来桌面端只负责布局、
交互和渲染，不从异常文本或原始 provider payload 重建业务语义。

### 前端终端能力与样式

CLI 组合根必须在 TUI 开始读取输入前创建一次不可变 `TerminalCapabilities` 快照，并在该会话内
复用。终端身份、颜色支持的来源与有效等级、默认前景/背景及探测结果是彼此独立的事实；环境、
平台 API、控制序列和终端 IO 只允许在对应检测或探测 adapter 中读取，renderer 不得重新读取
环境、操作系统状态或进程级缓存。

常规 Terminal/TUI 组件只消费语义样式角色；prompt_toolkit style 是语义结果的投影，不是第二套
palette。组件不得按审批类型、终端品牌或局部状态选择具体 RGB、blue 或 yellow。TrueColor 与
ANSI 256 由唯一 resolver 解析和量化，ANSI 16 只使用命名色，显式无色或未知能力不得输出自定义
前景和背景。选中、强调、成功、失败、警告、品牌及用户/审批 surface 在所有组件中共享同一语义。

Patch/diff 是富渲染边界：每次渲染由调用方创建一个不可变 `DiffRenderStyleContext`，syntax scope
背景只属于该上下文，不属于终端默认主题快照。TrueColor 与 ANSI 256 可以使用整行背景和 scope
覆盖；ANSI 16 只使用语义前景或修饰符；显式无色和未知能力只保留修饰符及终端默认颜色。语法
高亮不得绕过该上下文向低色深或无色输出泄漏 RGB。

终端身份消费者必须按最小事实设计。OSC 8 和键盘映射只读取 `TerminalIdentity`；scrollback、
resize 和同步输出只读取实际 `Output` 支持。任何消费者不得把颜色能力、终端身份或 VT 输出能力
复用为总能力开关。

### TUI Turn Presentation

每次 Turn 创建一个具有不可变 `surface_id + cid + sid + turn_id + agent_id` scope 的
`OutputSession`。该会话聚合四个正交出口：`OutputControlPort` 管理流式输出资源，
`ContentSink` 接收正文事实，`PresentationSink` 接收稳定展示单元，`OutputActivityPort`
接收活动展示事实。四者共享 scope，但不得互相读取内部状态或替代彼此的生命周期。

Turn 活动提示的唯一链路固定为：

```text
protocol / harness fact
  -> TurnActivityProjector
  -> OutputActivityEvent
  -> reduce_turn_surface()
  -> TuiTurnSurfaceCoordinator
  -> one TUI foreground projection
```

`OutputActivityEvent` 使用正式身份表达 model wait、assistant 可见性、展示代次替换、工具批次和调用、后台
终端、审批、provider/transport retry、恢复水位与唯一 Turn 终态。Reducer 是无 IO 的
纯状态转换；Coordinator 是 generation timer、tool/approval lease、replay 抑制和画面投影的
唯一 owner。协议 adapter、工具执行器、审批协调器和终结器不得直接开始、结束或延迟 TUI
状态，也不得通过匿名状态字符串恢复动画。

同一因果交接中不可分割的活动事实必须通过 `OutputActivityPort` 的非空原子批次提交；Coordinator
先在局部状态中完整归约批次，全部事实合法后才替换正式状态，并且只为最终状态生成一次前景投影。
工具活动释放并把前景所有权交给 model wait 属于此类交接，不得产生中间 hidden 帧。

正文只有在渲染器确认至少一行实际进入活动画布时才产生 `AssistantVisible`。该事件在同一个
`visual_update()` 中撤下活动提示并提交正文，避免等待动画、空白帧和 assistant 正文同时出现；
实际撤下活动提示时，在支持的终端上还必须把下一次绘制作为同步输出帧提交，使旧提示清除和
assistant 正文绘制对终端一次可见。
传输断线是唯一例外：transport retry 临时在已上屏正文之上恢复 `Retrying` 活动提示，但不释放、
替换或重新提交正文；进入 replay 后立即静默，追平权威水位后由最新 reducer 快照恢复画面。
`AssistantSettled` 只允许 Coordinator 按本地策略安排后续等待；`turn.completed` 在同一次归约中结束
逻辑输入边界并同步清空 timer、retry、工具和审批 lease，不再等待第二个结算事件。
provider retry 在登记新 Attempt 的同一次归约中释放旧 Attempt 的正文所有权；
`PresentationSuperseded` 使旧 epoch 的正文、等待和 retry 失效，迟到旧事件不得重新取得画面。
同步正文帧可以抢占正在等待的异步投影，Coordinator 必须按 reducer revision 撤销陈旧结果，
不得以锁冲突使 Turn 失败。

远端 `/turn/interrupt` 的 `204` 只确认中断事实已经登记，不代表活动 Turn 已释放。客户端预先持有
`turn_id`，因此中断意图登记后应立即异步提交 queued/running Turn 的幂等中断命令，不等待
`turn.started`。若命令抢在 `/mind-chat` 持久化之前得到 `404 turn_not_found`，只能在有界创建竞态窗口
内复用同一 `request_id` 重试；窗口结束后等待匹配的 start 再唤醒同一命令身份。同一 Turn 的重复中断
请求必须合并，steer 仍必须等待 `turn.started`。
中断请求发出后，TUI 保留当前 Thinking/Working 和执行门，尚未确认的 steer 可以立即切换为等待结算
的队列预览，但不得提前写入最终中断文案。结算期间的新输入必须进入可见的下一轮队列，不得作为
steer 发送，也不得进入尚无消费者的普通消息 handoff。只有已经完整消费的 `turn.completed`，或无需
恢复本地正文时的权威 `/turn/status` 同构终态快照，可以在同一次展示交接中撤下活动画面、提交一次
中断文案、恢复普通输入并开放下一次 `/mind-chat`。冷恢复若存在冻结请求，终态快照只提供 attach 的
目标 `last_event_seq`，不得直接解除本地 Run 门禁；HTTP 回执、本地 observer 结束、任务取消或 SSE
关闭都不能替代该屏障。
第一次 `Ctrl+C` 必须保留上述权威终态屏障；退出确认窗口内的第二次 `Ctrl+C` 表示用户明确结束
客户端进程，可以取消本地 status/reconcile 等待并退出，但不得因此启动下一 Turn、重复提交输入或
把未知归属输入自动重投。远端 Turn 仍由服务端自身生命周期最终收束。
活动 Turn 已存在普通 pending steer 时，`Esc` 是独立的“中断并提交即时输入”意图：仅冻结按键当时
的 pending steer 身份，在权威中断终态到达后按 FIFO 合并成一条新 Turn 输入并自动提交；Tab 队列
和当前编辑草稿保持原位。该路径展示 `Model interrupted to submit steer instructions.`。`Ctrl+C` 不得
设置这一意图，其终态恢复仍把普通 pending、Tab 队列和当前草稿合并回编辑器。
输入提交按键在解析命令前确定产品意图：空闲普通文本的 `Tab` 与 `Enter` 都提交新 Turn，空闲
Shell 草稿的 `Tab` 只编辑草稿；活动 Turn 的 `Enter` 尝试 steer，`Tab` 一律形成普通下一轮输入。
因此活动 Turn 中通过 `Tab` 排入的 slash 或 Shell 文本只能在出队后解析，不得在按键当下执行。

正常模型等待和工具执行统一投影为单行 `Thinking`；活动 Turn 的状态行统一显示
`(<elapsed> • esc to interrupt)`，其中经过时间按整数秒及紧凑的分钟/小时格式展示。工具名只在
工具自身的展示单元中出现，不得追加到活动提示。后台终端数量由独立进程状态 owner 投影，
可以在活动提示可见时合并到同一行，但不改变 Turn reducer 的阶段或生命周期。活动 Turn 中
`/ps` 只读取并展示持久终端快照；`/stop` 只停止快照中的终端会话并清除其状态，不得解释为
Turn interrupt 或逻辑结算。

审批卡、菜单和其他独占交互表面只拥有焦点、选择和布局遮挡。它们可以暂时隐藏活动区域，
但不修改 reducer 状态；交互结束后由后续 typed fact 或现有 projection 决定可见内容。后台终端
同样通过 `call_id + session_id` 的 `TerminalWaitStarted/Completed` 进入 reducer，不存在独立的
TUI terminal wait 控制面。

attach/replay 期间，历史事件只归约状态，不启动瞬时 timer。追平权威水位后 Coordinator 只
投影一次最终快照；内部 gap 进入对账展示，不能降级为普通 Thinking。`OutputSession` 只有在
activity 和输出控制均成功打开后才可接收终态或失败投影；打开失败先收束已经取得的资源。
replay 中的客户端工具批次只登记为待核对状态；退出 replay 抑制前必须通过
`/tool-result/status` 裁决每个 `call_id`。已 `result_received` 或已关闭的调用只收束本地投影，
不得重新执行 Hook、审批、工具或 `/tool-result` 投递；仅仍为 `waiting_result` 的调用可在
追平水位后由当前进程接管。缺失、未就绪或需要对账且无本地确定结果时必须保持
recovery gate，不得把不确定性降级为副作用重放。
`OutputSession.close()`
先停止输出资源，再关闭 activity scope；两步均幂等，任一步失败都必须继续清理另一项。text、
JSONL、silent、stdio MCP 和 Subagent 使用相同会话契约，并以 `PassiveOutputActivity` 明确表示
没有活动画面，而不是实现空状态 facade。

## 工具、审批与 Effect

工具调用的职责链固定为：

```text
model intent
  -> application tool contract
  -> execution policy
  -> approval coordinator when required
  -> durable effect preparation
  -> capability/infrastructure execution
  -> typed result
  -> protocol delivery and reconciliation
```

约束如下：

- 本地工具、provider built-in tool 和 hosted tool 是不同边界，不通过字段猜测互换。
- 工具参数在执行前完成 schema 校验，结果在 adapter 边界归一化。
- 审批只决定当前动作，不成为底层平台或服务端的全局安全策略。
- Approval、Tool Call 与 Effect 各有稳定 identity，`request_id` 只承担传输幂等。
- 外部 MCP 调用即使由策略免除交互审批，也必须先校验完整 Tool Call 与 Turn identity；
  基础设施调用边界不得把缺失 identity 解释为受信任调用。
- MCP Session grant 只在相同 Session、Environment、server、connector 和 tool 范围复用，
  不绑定单次调用参数，也不得跨 Session 或执行环境传播。
- MCP 持久允许只能由配置端口原子写入工具级策略；本地展示决定不得扩展正式 wire 审批契约。
- MCP 调用只消费正式调用携带的 Effect identity；缺失时不得合成本地 Effect 冒充线上权威事实。
- MCP 审批由 application 投影可信身份、领域风险及经过脱敏和限长的参数摘要；前端只按语义
  Token 排版和降级颜色，不从第三方对象或原始载荷重新推断权限。
- 交互审批卡只拥有待决请求和当前选项；决定一经提交即锁定并释放交互表面，允许、拒绝、
  取消和失效等终态只通过结构化 trace 投影，不把终态卡片建立为第二事实来源。
- 用户配置的外部 MCP STDIO、SSE 和 Streamable HTTP 连接属于显式配置的传输信任边界；建连
  本身不消费 MCP tool grant 或网络 grant，但模型可达的每次外部工具效果仍必须通过 MCP 策略链。
- 外部 MCP HTTP client 不继承环境代理；传输凭据只在配置与 transport adapter 内解析，状态和
  日志只能使用脱敏摘要，关闭时必须收束 owner 任务并解除工具、会话和凭据引用。
- 外部效果成功与本地提交之间存在未知窗口时进入 reconciliation，不伪装为普通失败。
- 不可重放效果不得由接管 actor 自动重试；只读或有供应商幂等保证的效果按明确策略恢复。
- `/tool-result` 只发送正式协议字段，本地工作区、sidecar 或 UI 状态不能混入 wire payload。

## 持久化与恢复

持久状态按事实类型分开：

| 事实 | 所有者 | 恢复原则 |
| --- | --- | --- |
| Run/Command/Event | `agent.stores.runs` | 幂等写入、单调事件、终态不可离开 |
| Remote Turn request | `agent.stores.runs` | 网络提交前冻结；按原坐标 attach/replay，不重新提交 |
| Agent graph/mailbox | `agent.stores.agents` | 活动投递可恢复，消息身份稳定 |
| Session cursor | `agent.stores.sessions` | 只保存本地会话索引和分支事实 |
| Transcript | `agent.stores.transcripts` + persistence adapter | 规范记录与 IO 分离，损坏可观测 |
| Approval | `agent.stores.approvals` | 首个决定权威，重复请求幂等 |
| Effect | `agent.stores.effects` | prepared/committed/unknown 等事实可对账 |

恢复必须从持久事实和安全点开始，不能以 Redis、当前连接、前端缓存或日志作为 authority。
进程退出后，已提交事件不丢失，未确认外部效果不重复执行，无法确定的结果进入显式对账。

## 基础设施边界

`infrastructure/` 按外部变化来源分组：

- `config/`：应用目录、配置 schema、分层、偏好、信任和执行策略文件；
- `platform/`：进程、Sandbox、Shell、信号、编码、图片和平台差异；
- `workspace/`：工作区命令、补丁应用、diff 和运行资源；
- `mcp/`：外部/本地 MCP session、工具目录、调用和结果适配；
- `persistence/`：Transcript 与会话索引的具体存储；
- `services/`：可选服务 owner、健康、许可、Helix、Turn 环境和进程内配置宿主；
- `skills/`：技能发现、解析和不可变 payload；
- `hooks/`：Hook 文件发现；
- `sidecars/`：私有子进程协议、进程托管、会话连接和资源关闭；
- `update/`：升级资产和运行流程。

用户配置根和可写运行状态根是两个独立路径契约。`MIND_HOME` 只拥有 `config.toml`、
用户规则和 Hook 配置；`MIND_STATE_HOME` 拥有 history、sessions、reports、Helix 及本地
SQLite，未设置时才使用 `MIND_HOME` 作为默认值。配置文件只要求可读；状态根必须可创建、
可写并支持 SQLite 文件锁。任何显式状态根失败都必须中止启动，不得回退到其他账本。

Infrastructure 不得读取 TUI 控件、构造前端文案或修改 Harness 内部状态；它通过 ports、
具名 application 契约和返回值交互。

### 内置配置宿主

`infrastructure/services/configuration_host/` 是客户端进程内的可选配置服务，不是独立部署
边界，也不实现线上 `mind.chat` 语义。它只负责 FastAPI 组合、配置页路由、配置操作映射、
本地端口生命周期和健康检查；持久配置事实仍由 `infrastructure.config` 所有，Harness 不依赖
该宿主。

配置页面和静态文件位于宿主的 `assets/` 下，由宿主统一解析。源码运行读取该目录；Nuitka
standalone 构建通过 `--include-data-dir` 将同一资产映射到发布目录根下的 `web/`，运行时
优先读取可执行文件旁的 `web/`，因此启动工作目录变化或源码目录不存在都不影响页面加载。
`ConfigServiceRuntime` 持有当前实例的不可变地址，组合根将地址提供给 TUI 和 Subscription；
配置宿主关闭由 `ApplicationHost` 的进程资源 owner 统一收束，不使用模块级地址单例。
`build.py` 只负责发布资源包含，不改变 Python 包或 wheel 边界。

### npm 分发工作区

`npm/` 是独立的 npm workspace，所有权只覆盖 launcher、平台运行时包、产物同步脚本和发布
流程文档。`npm/PUBLISHING.md` 与 workspace 同属该边界；发布操作必须从 workspace 根目录执行。
该目录不承载 Python 实现、Harness 状态或 `mind.chat` 协议，不能被运行时模块导入。平台运行时
由 `npm/scripts/sync-applications.js` 从仓库构建产物同步，npm 包发布不改变 Python wheel 的
内容或边界。

## JavaScript Sidecar

JavaScript REPL 是受 Harness 管理的本地执行能力，模型侧稳定工具名为 `js_repl` 和
`js_repl_reset`。它不是线上协议、Workspace 聚合能力或前端特性；工具授权、审批、
嵌套工具调用和结果投影仍由 application/Harness 裁决，Sidecar 只执行已经授权的代码并
返回具名结果。`kernel.js` 及其 `vendor` 目录是来自 Codex 的稳定、不可变运行时资产；架构
重组只调整资产位置和 Python 托管边界，不重写或拆解该运行时。

### 最终结构

```text
agent/
├── ports/
│   └── javascript.py             # 执行与会话生命周期端口
└── application/
    └── tools/
        └── javascript.py         # 模型工具、参数校验、授权和结果投影

infrastructure/
└── sidecars/
    └── javascript/
        ├── bundle.py             # 不可变资产清单、散列和路径校验
        ├── protocol.py           # 既有 JSONL 消息的具名模型和边界校验
        ├── process.py            # Node 发现、权限参数、启动和终止
        ├── session.py            # 执行串行化、请求关联和回调任务
        └── provider.py           # 会话索引、创建、重置和关闭

sidecars/
└── js_repl/                      # Codex 原始资产目录，内容不可变
    ├── kernel.js                 # 完整 Host、Runtime、转换和 JSONL 入口
    └── vendor/
        └── meriyah.umd.min.js
```

`agent.ports.javascript` 分离消费者所需的执行端口与 Harness 所需的会话生命周期端口，
不得重新形成包含 Shell、补丁、Workspace 和 JavaScript 的聚合接口。具体 Provider 由
`composition.py` 创建：application 工具只接收执行端口，Harness 资源 owner 只接收生命周期
端口，二者不发现或向下转换具体实现。

### 状态与进程所有权

- Provider 以 `session_id` 索引唯一活动 JavaScript 会话，并保存已经规范化的工作目录和
  `sandbox_mode` 安全信封。
- 每个活动安全信封拥有独立 Node 进程。不同 Session 不共享宿主，因为 Node 文件权限、
  工作目录和进程环境是进程级安全边界。
- 同一 Session 的工作目录或 `sandbox_mode` 发生变化时，必须先关闭原进程，再用新的不可变
  安全信封创建会话；不得在活动进程上扩大权限。
- Process 对象拥有子进程、stdin/stdout/stderr 和进程终止；Session 对象拥有执行锁、当前
  request 和 delegate callback；不可变 JavaScript Kernel 只拥有进程内的 REPL 变量与当前
  execution。
- 每个 Session 只有一个 execution 写入者。外部执行按 FIFO 串行进入 Host，delegate callback
  只归属于触发它的 execution；`reset` 和 `close` 是阻止后续执行越过的生命周期屏障。
- Workspace 能力只负责工作区命令、补丁和文件操作，不拥有 JavaScript 会话或清理回调。
- 根 Session、Subagent 和进程退出均通过同一生命周期端口关闭对应会话；关闭操作幂等，
  单个资源清理失败不得阻止其余资源收束。

### 私有 IPC

Python Client 与不可变 JavaScript Kernel 沿用现有 UTF-8 JSONL 协议，不增加握手、版本协商、
cancel、reset 或 shutdown 消息，也不增加包装进程。Client 只发送：

- `exec`：携带 `id`、`code` 和 `timeout_ms`；
- `run_tool_result`：按 `id` 返回嵌套工具结果；
- `emit_image_result`：按 `id` 返回图片接收结果。

Kernel 只返回：

- `exec_result`：按 `id` 返回执行结果；
- `run_tool`：按 `exec_id` 和 `id` 请求嵌套工具；
- `emit_image`：按 `exec_id` 和 `id` 请求附加图片。

`protocol.py` 对 Python 发出的消息执行具名构造，对收到的完整帧执行判别、字段、标识和大小
校验；未知类型、未知字段、非法 JSON、错误字段类型、越界帧和无法关联的执行结果均使当前
Session 失败并关闭进程，不能静默忽略或猜测。合法但已经离开活动 Cell 的迟到 delegate 按
既有契约返回 `js_repl exec context not found`，不恢复旧 execution。stdout 只承载协议帧；
stderr 只作为受限诊断输入，不拥有状态语义。

Kernel 没有控制面消息，因此执行超时、调用方取消、reset 和 close 均由 Python 终止整个
子进程，并使当前 request 与 delegate task 确定收敛；下一次执行按需创建新进程。Host EOF、
崩溃和残缺帧采用同一失效路径。

基础设施以具名失败类型向上层报告 `unavailable`、`protocol_error`、`execution_timeout`、
`cancelled` 和 `runtime_error`；application 依据类型构造工具结果，不解析异常文本、stderr
或进程退出文案。失败类型不直接成为线上协议错误码。

### 安全与边界

- `sidecars/js_repl` 只允许从原 `js_repl` 目录机械迁移。`kernel.js` 和 `vendor/meriyah.umd.min.js` 的文件名、目录关系和字节必须保持不变；禁止拆分、重写、格式化、 添加注释、转换行尾或注入握手。构建和测试以固定 SHA-256 校验该约束。
- Node 可执行文件、最低版本和 Sidecar bundle 路径由 composition 解析后以不可变值传入 Provider；业务模块和 Kernel 不读取客户端配置目录。
- `sandbox_mode` 在启动参数中落实，平台差异只存在于 `process.py`。Sidecar 不自行放宽文件、 网络或子进程权限。
- `delegate.call` 只是调用提案；Python application 必须重新执行工具可见性、schema、审批和 Effect 规则，Host 无权绕过这些规则直接调用本地工具。
- Sidecar 内部状态不得进入 `/tool-result`、线上事件、Transcript 元数据或前端状态。
- Sidecar 模块只使用 `observability` 的结构化入口；代码正文、完整输出、凭据和未筛选回调载荷不得写入日志。

### 发布与验收

`sidecars/js_repl` 作为完整目录随 wheel、源码分发和独立可执行包发布，运行时路径解析不
依赖当前工作目录。发布验证必须先校验资产散列，再从安装产物启动真实 Kernel，完成跨 Cell
状态保持、reset 和关闭，不能只检查文件存在。

JavaScript Sidecar 边界只有在以下事实持续成立时才视为健康：

- JavaScript 运行时资产只位于 `sidecars/js_repl`，Python 进程实现只位于
  `infrastructure/sidecars/javascript`；
- 两个 JavaScript 资产与迁移前的固定 SHA-256 完全相同，且不存在复制品、包装 Host 或拆分后的运行时文件；
- application 工具、Harness 生命周期和 Sidecar 实现通过两个最小端口协作；
- Session 隔离、权限冻结、取消、超时、崩溃、EOF、重置和关闭具有确定行为；
- 嵌套工具调用完整经过现有授权、审批和 Effect 链路；
- Windows、Linux、macOS 的 Node 发现、启动、终止和打包安装路径均有验证；
- 架构守卫禁止 Workspace 所有权、跨 Session 共享宿主、直接 Sidecar 导入和私有状态进入线上协议。

## 可观测性

业务代码只调用 `observability` 的结构化入口。标准库 `logging.getLogger(__name__)`、直接
logger 方法、吞异常和日志文本协议都被架构守卫禁止。

观测事件至少携带可用的 `session_id`、`run_id`、线上坐标、command/effect identity、环节、
结果类别和异常来源。敏感正文、凭据、完整工具输出和未筛选 provider payload 不进入日志。

可观测性是事实的投影，不拥有重试、取消、审批或终态决定。

## 扩展规则

新增能力时按以下判断顺序：

1. 确认状态所有者和生命周期 owner。
2. 确认是领域规则、application 用例、Harness 编排还是外部 adapter。
3. 优先复用现有端口；只有出现真实可替换边界时新增端口。
4. 由组合边界注入实现，删除动态发现和备用构造路径。
5. 同次变更删除被替代的字段、路径和回退，不保留无期限兼容层。

不允许：

- 创建没有明确所有者的 `core`、`common`、`shared` 或 `utils` 层；
- 在前端复制协议 reducer、Run 状态机或效果对账；
- 让 adapter 的第三方类型穿透 application/domain；
- 让测试替身扩大生产公开面或改变生产依赖方向；
- 让 sidecar、配置宿主或 npm workspace 取得 Harness 状态所有权；
- 以目录移动或命名变化代替完整用例和边界迁移。

## 架构验收

一次跨边界变更至少满足：

- 职责归属、依赖方向、状态所有权和关闭顺序可由代码直接看出；
- 新路径接入完整用例，旧路径与回退已经删除；
- Command、Event、Effect、Approval 和线上 identity 保持稳定；
- CLI、TUI、stdio MCP、Subscription 中受影响入口使用同一 application 语义；
- 协议变更同时更新服务端正式契约、`protocol/schema/`、`protocol/client/` 和契约测试。

具体测试选择、静态检查命令和架构守卫执行频率由 `AGENTS.md` 规定。

## 现行完成定义

当前架构只有在以下事实持续成立时才视为健康：

- `mind.py`/`composition.py` 是唯一具体组合边界；
- `agent.application`、`agent.harness`、stores、capabilities 和 adapters 职责化分组；
- 顶层 `protocol` 独立于 Harness，可供替换前端复用；
- 所有具体前端只消费显式 host、factory 或 port；
- 本地执行状态、线上协议状态和 Subscription 状态相互隔离；
- 持久事实能够驱动恢复，未知 Effect 有确定的对账路径；
- 结构化观测由 `observability` 统一承载，运行时模块不拥有日志实现。
