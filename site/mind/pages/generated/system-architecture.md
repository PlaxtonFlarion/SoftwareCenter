# Mind 系统架构

Mind 负责代理意图、本地运行和用户体验；AppServer 负责远端持久生命周期；Fabric 负责云端
计算执行。

## 1. 文档权威

本文是 Mind、AppServer 与 Fabric 之间的系统级架构权威，只定义跨系统职责、状态所有权、
生命周期、失败边界和集成准出条件，不复制各仓库内部实现。

```text
ARCHITECTURE_SYSTEM.md
  -> Mind / AppServer / Fabric 跨系统架构权威

ARCHITECTURE.md
  -> Mind 客户端内部架构权威，受本文约束

AppServer architecture and contracts
  -> 远端持久运行时及服务端状态机权威

Fabric architecture and contracts
  -> 云端计算运行时及资源模型权威

Server contract + protocol/schema + protocol/client
  -> 线上字段、端点、事件和错误权威
```

README 和 `docs/` 只负责入口、解释与教学，不能反向定义架构事实。发生冲突时，先按事实所属
范围确定权威文档，再修正非权威描述，不增加兼容口径。

## 2. 系统定位

Mind 不是单纯的模型客户端或聊天界面，而是面向用户的代理运行时。它理解输入、组织本地
执行、调用远端生命周期服务，并把持久事件投影为可交互体验。

```text
User
  |
  v
Mind
  Agent intent / local runtime / experience
  |
  | command and observation
  v
AppServer
  durable lifecycle truth
  |
  +------ provider and remote tools
  |
  +------ optional compute capability ------> Fabric
                                                cloud compute
```

Fabric 不是每个 Turn 的必经层。只有 Sandbox、GPU、Embedding、Vision 或其他隔离计算需要
云端执行时，Mind 或 AppServer 才通过明确能力边界调用 Fabric。

## 3. Runtime 职责

| 系统 | 定位 | 拥有 | 不拥有 |
| --- | --- | --- | --- |
| Mind | Agent Runtime | Intent、本地 Session/Run、本地执行证据、交互和协议客户端 | Remote Turn truth |
| AppServer | Durable Lifecycle Runtime | 远端 Session、Turn、Queue、Event、执行门、Worker lease、终态 | UI、本地运行时、计算资源 |
| Fabric | Cloud Compute Runtime | Sandbox、Compute Run、模型与视觉计算资源 | Agent Session、Turn、Queue、Terminal |

三个 Runtime 分别回答：

```text
Mind       -> 代理想做什么，用户看见和操作什么
AppServer  -> 持久代理生命周期当前是什么
Fabric     -> 云端计算如何执行和恢复
```

不存在跨三者的万能 Runtime 或共享状态机。

## 4. Authority 模型

核心原则是：

> One fact, one authoritative owner.

| 事实 | Authority |
| --- | --- |
| User input、Intent | Mind |
| Local Session、Run、Command | Mind |
| Local Tool、Approval、Effect evidence | Mind |
| TUI、Presentation | Mind |
| `cid`、`sid`、`turn_id`、`event_seq` | AppServer |
| Remote Turn lifecycle、Session execution gate | AppServer |
| Durable Queue、Terminal fact | AppServer |
| Worker lease、fencing | AppServer |
| Remote Tool、Approval、Effect lifecycle | AppServer |
| Fabric Sandbox、Compute Run | Fabric |
| GPU、Model、Vision compute resource | Fabric |

本地证据可以支持恢复和对账，但不能覆盖远端生命周期。远端工具事实也不能替代 Mind 对本地
进程、权限交互和执行证据的所有权。Fabric 完成计算不代表它取得 Agent 生命周期所有权。

## 5. Mind 内部边界

Mind 客户端采用以下分层：

```text
mind.py / composition.py
  -> agent
      protocol / domain / ports / application / harness
      stores / capabilities / adapters
  -> protocol
  -> infrastructure
  -> observability
  -> frontends
```

系统文档只约束 Mind 不得冒充远端或计算 Authority。客户端包边界、依赖方向、状态所有者和
关闭顺序以 `ARCHITECTURE.md` 为准。

Mind 的系统级职责包括：

- 把用户输入冻结为本地 Command 和执行环境；
- 组织 Agent、Subagent、Hook、本地工具和审批交互；
- 提交或观察远端 Turn，并维护本地恢复证据；
- 归约线上事件，渲染正文、活动状态、工具、审批和重试；
- 通过显式能力端口连接本地服务、外部 MCP 和可选云端计算。

## 6. 身份模型

| 范围 | 身份 |
| --- | --- |
| Mind local runtime | `session_id`、`run_id`、`command_id`、`sequence`、`idempotency_key` |
| AppServer durable runtime | `cid`、`sid`、`turn_id`、`attempt`、`item_id`、`request_id`、`client_message_id`、`event_seq` |
| Fabric compute runtime | `sandbox_id`、`fabric_run_id`、compute/task identity |

```text
Mind run_id != AppServer turn_id != Fabric run_id
```

即使底层值都是字符串，也不得互相赋值、比较或隐式复用。跨系统关联由 adapter 显式保存，
Fabric 返回的运行身份在 Mind 和 AppServer 边界统一命名为 `fabric_run_id`。

## 7. Turn 生命周期

一次正常 Turn：

```text
User input
  -> Mind immutable Command
  -> freeze request and environment
  -> submit
  -> AppServer creates durable Turn and acquires session gate
  -> Worker executes provider / tool
  -> optional Fabric compute
  -> AppServer persists events and terminal
  -> Mind observes and reduces events
  -> presentation
```

Mind 发起意图，AppServer 决定持久 Turn 事实。系统必须区分：

```text
Command != Fact
Submit  != Observe
HTTP Ack != Terminal
```

新 Turn 先 submit，确认身份后 observe。已存在 Turn 只能 attach/replay，不得为了保险再次调用
创建接口。`turn.completed` 或服务端正式定义的同构 terminal snapshot 是唯一远端终态来源。

Review 是独立的类型化 Command，不是普通聊天文本。Mind 拥有用户选择的 Review target，并在
首次网络操作前冻结本地 Git 工作区和本地 Run 事实；AppServer 原子登记远端 Session、Turn、
Review Item 和执行门。首次 `/review` 可以创建此前不存在的源 Session；已登记 Review 的恢复
只能 status 后 attach/replay，未知提交结果不得生成新身份重投。`review.completed` 只终结
Review Item，仍须由匹配的 `turn.completed` 释放远端和本地执行门。

## 8. 输入、中断与队列

中断命令只是意图，不是终态：

```text
Mind interrupt command
  -> AppServer accepts and fences execution
  -> execution child stops
  -> durable finalizer
  -> turn.completed(interrupted)
  -> Mind releases local gate
```

第一次 `Ctrl+C` 必须保留本地执行门并等待权威终态。再次 `Ctrl+C` 可以退出 Mind 进程，但不能
把本地退出解释为远端 Turn 已结束，也不能启动下一 Turn 或重投未知输入。

Mind 的 pending input 与 AppServer Durable Queue 是两种事实：

- pending input 属于 TUI 当前交互状态，中断后可以恢复编辑器；
- Durable Queue 属于 AppServer，只有显式 `/queue` 命令可以修改；
- 普通 pending input 不得自动转换为 Durable Queue；
- Queue start 绑定服务端已经创建的 Turn，Mind 只能 attach/replay；
- Queue 顺序、版本、成员和 start 结果以服务端 snapshot/receipt 为准。

活动 Turn 中 Enter、Tab、Esc 和 Ctrl+C 的具体交互语义由 `ARCHITECTURE.md` 约束，但不得改变
上述 Authority 和终态规则。

## 9. Tool、Approval 与 Effect

工具链跨越三个系统，但每类事实仍只有一个所有者：

```text
Agent intent
  -> tool semantic identity
  -> policy and approval
  -> effect preparation
  -> local or cloud execution
  -> execution evidence
  -> AppServer durable result and reconciliation
```

AppServer 拥有远端 Turn 中 Tool、Approval 与 Effect 的生命周期、持久结果和对账状态。Mind
可以拥有本地工具实现、能力进程、审批交互、Effect journal 和本地执行证据。Fabric 只拥有
Sandbox、Compute Run 和计算资源。

对外部副作用使用 `prepare -> execute -> commit`。执行结果无法确定时进入 `unknown` 和显式
reconciliation，不得伪装为 failed 后自动重试。不可重放副作用不得由恢复进程重复执行。

## 10. Fabric Compute Plane

Fabric 是可替换的计算平面，可以提供 Sandbox、模型、Embedding、Rerank、Vision 和其他隔离
计算能力。它通过显式能力端口接入：

```text
Mind or AppServer application
  -> ComputePort
  -> Fabric adapter
  -> Fabric API
```

领域层不得直接调用 Fabric transport。调用方必须持有 `fabric_run_id`、幂等信息、超时和结果
语义。Fabric 不拥有 Agent Session、Turn、Steer、Interrupt、Durable Queue、Terminal 或 TUI。

## 11. Event、Replay 与 Presentation

AppServer 是线上 Agent Event 的 Authority。持久事件日志是事实来源；Redis、消息通知和进程内
EventHub 只承担加速与唤醒，不能覆盖持久事实。

`event_seq` 属于 `cid + sid` 范围，不是 Turn 内局部序号。Mind 观察单个 Turn 时可能看不到同一
Session 中属于其他事实的序号，因此不能仅凭可见序号不连续推断 gap。真正的 gap 由完整 Session
事件流和服务端契约判断。

Provider 输出必须保留上游语义。可选字段缺失就是 unknown；服务端、Replay 和 Mind 前端不得
依据正文内容补猜 phase 或其他协议事实。

Mind 是 Presentation Authority，但 Presentation 不拥有 Lifecycle：

```text
AppServer event
  -> protocol client
  -> canonical item reducer
  -> application projection
  -> frontend
```

自动上下文压缩属于 AppServer 的远端运行时状态机，并作为同一 `turn_id` 中的
`context.compaction.started/completed/failed` Canonical Item 生命周期交付。Mind 只按
`item_id + event_seq` 归约、记录无摘要的完成标记并建立展示边界；收到这些事件不得再次调用
Turn 创建或压缩端点，也不得运行能够阻断云端压缩的本地 Hook。`completed` 不是 Turn 终态，
后续 assistant 内容继续归属于原 Turn。TUI 只在该 Turn 已发生实际工具或命令工作时，于完成
提示后的下一段 assistant 内容前展示分隔线。

Thinking 消失、正文上屏和连接 EOF 都不等于 Turn completed。只有权威 terminal 才能释放运行
资源和下一 Turn 执行门。

## 12. Recovery 与 Failure Isolation

恢复分为三类：

| 恢复类型 | 所有者 | 典型链路 |
| --- | --- | --- |
| Observation recovery | Mind + AppServer | reconnect -> attach -> replay -> observe |
| Execution recovery | AppServer | lease expiry -> claim -> checkpoint -> continue/finalize |
| Compute recovery | Fabric | query -> retry/reconcile -> compute result |

三者不得合并为全局 `RecoveryManager`。每个 Runtime 可以独立失败：

- Mind 崩溃时，AppServer Turn 可以继续；
- AppServer HTTP 进程崩溃时，持久 Turn 事实仍由 durable store 保存；
- Worker 崩溃由 AppServer lease、fencing 和恢复流程处理；
- Fabric 失败只决定计算结果，不能直接改写 Agent terminal。

失败边界必须与所有权边界一致。

## 13. Persistence 与 Observability

| 系统 | 持久事实 |
| --- | --- |
| Mind | Local Command/Run、冻结请求、Transcript、审批与 Effect evidence、本地恢复状态 |
| AppServer | Session、Turn、Queue、Command receipt、Event、Checkpoint、Terminal、Worker fencing、远端 Effect lifecycle |
| Fabric | Sandbox、Compute Run、Compute result、临时计算状态 |

事实存放位置服从 Authority，而不是服从访问便利性。

三个系统共享 trace context，但不共享状态 Authority。链路按可用范围携带 Mind 本地身份、
AppServer Turn/Request/Event 身份及 Fabric compute 身份。日志、指标和错误平台只能观察事实，
不能成为恢复、重试、审批或终态判断来源；敏感正文、凭据和未筛选载荷不得进入观测数据。

## 14. 依赖与扩展规则

系统依赖方向是：

```text
User -> Mind -> AppServer -> provider / remote capability
          |          |
          +----------+----> Fabric through explicit compute capability
```

Mind adapter 或 AppServer capability 都可以调用 Fabric，但调用关系不转移 Authority。新增能力前
必须明确回答：

1. 谁拥有事实？
2. 谁执行？
3. 谁展示？
4. 谁恢复？

禁止新增跨系统 `GlobalRuntimeManager`、`UniversalState`、`SharedTurnState` 或第二套 Turn mirror；
禁止 Mind 保存远端 Turn 状态机、Fabric 保存 Agent Session、AppServer 依据 UI 状态决定 terminal；
禁止根据网络 unknown 自动 resubmit 或重试 unknown Effect。

## 15. E2E Architecture Gate

跨仓集成至少覆盖：

- Normal、Multi-turn 和 Streaming；
- Thinking、正文、Tool、Approval 阶段的 Interrupt；
- 多个 Steer、Steer + Interrupt、Terminal -> Next Turn；
- Durable Queue add/start；
- Disconnect、Attach、Replay；
- Worker crash、Finalizer takeover；
- Fabric success、timeout 和 failure。

准出不变量：

```text
Duplicate Turn       = 0
Duplicate Tool       = 0
Duplicate Terminal   = 0
Input Loss           = 0
FIFO Violation       = 0
False Cursor Gap     = 0
Session Gate Stuck   = 0
Provider Replay      = 0
Unknown Effect Retry = 0
```

各仓库先通过自身契约测试，再以真实跨进程场景验证身份映射、持久恢复和失败隔离。

## 16. Architecture Laws

```text
Command != Fact
Presentation != Lifecycle
HTTP Ack != Terminal
Connection != Execution
Submit != Observe
Unknown != Missing
Unknown Effect != Failed Effect
Local Run != Remote Turn
Remote Turn != Fabric Compute Run
Compute != Agent Lifecycle
Worker != Authority
Cache != Truth
Projection != Source of Truth
```

最核心的规则是：

> One fact, one authoritative owner.
