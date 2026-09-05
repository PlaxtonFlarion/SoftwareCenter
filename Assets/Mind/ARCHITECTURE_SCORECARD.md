# Mind Agent Runtime

## Architecture Review & Scorecard

> 本文是阶段性架构评审与成熟度记录，不定义 Architecture Truth。系统级职责与边界以
> [ARCHITECTURE_SYSTEM.md](ARCHITECTURE_SYSTEM.md) 为准，ProxyMind 客户端内部架构以
> [ARCHITECTURE.md](ARCHITECTURE.md) 为准。

> **System Architecture · Runtime Architecture · Durability · Compute**

### Architecture Grade

# **A+**

### Overall Architecture Score

# **9.6 / 10**

```text
███████████████████▎  9.6 / 10
```

**Architecture Stage**

> **Core Architecture Mature · Verification & Production Hardening**

---

## 01 · Executive Summary

Mind Agent Runtime 已经从传统的 Agent Framework 演进为一套具有明确 **Runtime Authority、Durable Lifecycle、Compute Boundary 和 Recovery Model** 的完整 Agent Runtime Platform。

当前系统由三个独立但协同的 Runtime Domain 组成：

```text
┌─────────────────────────────────────────┐
│                  Mind                   │
│                                         │
│     Agent Intelligence & Execution      │
│                Runtime                  │
└───────────────────┬─────────────────────┘
                    │
             Intent / Command
                    │
                    ▼
┌─────────────────────────────────────────┐
│               AppServer                 │
│                                         │
│       Durable Lifecycle & Control       │
│                 Plane                   │
└───────────────────┬─────────────────────┘
                    │
           Compute Capability
                    │
                    ▼
┌─────────────────────────────────────────┐
│                 Fabric                  │
│                                         │
│          Cloud Compute Runtime          │
└─────────────────────────────────────────┘
```

三个系统最核心的职责划分已经稳定为：

```text
Mind
owns Intent, Local Execution and Experience.

AppServer
owns Durable Lifecycle Truth.

Fabric
owns Cloud Compute Execution.
```

而贯穿整个体系的最高架构原则是：

> **One Fact, One Authoritative Owner.**

System Architecture 已经明确区分三套 Runtime 的 Authority、Identity、Persistence、Recovery 和 Failure Boundary，而客户端架构进一步把这些原则落实到 `domain / ports / application / harness / stores / adapters / frontends` 的实际包边界中。

---

# 02 · Architecture Score

| Architecture Dimension         |   Score | Grade | Assessment                                        |
|--------------------------------|--------:|:-----:|---------------------------------------------------|
| **System Boundary**            | **9.9** |  A+   | Mind / AppServer / Fabric 边界高度清晰            |
| **State Authority**            | **9.9** |  A+   | One Fact / One Owner 已形成核心架构法律           |
| **Lifecycle Model**            | **9.8** |  A+   | Turn / Interrupt / Queue / Terminal 模型成熟      |
| **Protocol Model**             | **9.8** |  A+   | Submit / Observe、Command / Fact 边界稳定         |
| **Concurrency & Ownership**    | **9.7** |  A+   | Single Writer、Lease、Fencing 模型完整            |
| **Recovery Model**             | **9.7** |  A+   | Observation / Execution / Compute Recovery 已拆分 |
| **Effect Safety**              | **9.7** |  A+   | Unknown Effect → Reconciliation 模型成熟          |
| **Dependency Architecture**    | **9.7** |  A+   | 内部依赖方向稳定且具备自动化守卫                  |
| **Compute Architecture**       | **9.4** |   A   | Fabric 与 Agent Lifecycle 解耦正确                |
| **Presentation Architecture**  | **9.5** |  A+   | Presentation 与 Lifecycle 已彻底拆分              |
| **Observability Architecture** | **9.1** |   A   | 模型正确，跨 Runtime Trace 仍有增强空间           |
| **E2E Proof**                  | **9.0** |   A   | 架构已成熟，剩余主要是系统级证明                  |

### Composite Score

```text
System Boundary          ███████████████████▊  9.9
State Authority          ███████████████████▊  9.9
Lifecycle Model          ███████████████████▋  9.8
Protocol Model           ███████████████████▋  9.8
Concurrency              ███████████████████▍  9.7
Recovery                 ███████████████████▍  9.7
Effect Safety            ███████████████████▍  9.7
Dependency Design        ███████████████████▍  9.7
Presentation             ███████████████████   9.5
Compute Runtime          ██████████████████▊   9.4
Observability            ██████████████████▏   9.1
E2E Proof                ██████████████████    9.0
```

# **Overall · 9.6 / 10**

---

# 03 · Mind Runtime

## **9.7 / 10**

### Mature Agent Execution Runtime

Mind 已经超出了普通 Agent Loop 的范畴。

传统模型通常是：

```text
Prompt
  ↓
Model
  ↓
Tool
  ↓
Answer
```

Mind 当前实际模型更接近：

```text
User / Frontend
       │
       ▼
Immutable Command
       │
       ▼
Session Single Writer
       │
       ▼
Run Actor
       │
       ├── Model
       ├── Tool
       ├── Approval
       ├── Hook
       └── Effect
       │
       ▼
Protocol / Durable Runtime
       │
       ▼
Canonical Projection
       │
       ▼
Presentation
```

客户端内部已经形成明确的职责层：

```text
agent/
├── protocol
├── domain
├── ports
├── application
├── harness
├── stores
├── capabilities
├── adapters
└── composition
```

并且规定 Domain、Application、Harness 和外围 Adapter 的依赖只能沿固定方向流动，包架构还有自动化审计。

### Key Strengths

```text
Single Writer
Stable Identity
Immutable Command
Explicit Ownership
Durable Evidence
Effect Reconciliation
Protocol Isolation
Presentation Projection
```

尤其成熟的是：

> **Local Run ≠ Remote Turn**

以及：

> **Presentation ≠ Lifecycle**

这两条直接消除了 Agent Runtime 中非常常见的“客户端状态冒充服务端事实”和“UI 状态反向控制执行生命周期”问题。

---

# 04 · AppServer

## **9.8 / 10**

### Durable Agent Control Plane

AppServer 是整套 Runtime 最强的可靠性基础。

它解决的问题已经不是：

> “一次请求能不能返回结果？”

而是：

> **“一旦一次 Agent Execution 被接受，这个执行生命周期是否拥有唯一、持久、可恢复的事实。”**

核心结构：

```text
Session
   │
   ▼
Execution Gate
   │
   ▼
Durable Turn
   │
   ▼
Worker Lease / Fencing
   │
   ▼
Execution
   │
   ▼
Finalizing
   │
   ▼
Terminal Fact
```

System Architecture 已经明确把 Remote Turn、Session Gate、Durable Queue、`event_seq`、Worker fencing 和 Terminal Fact 的 Authority 归属 AppServer。

### Architecture Highlights

**Command ≠ Fact**

```text
Interrupt Accepted
        ≠
Turn Interrupted
```

**Worker ≠ Authority**

```text
Worker
  may disappear

Turn Fact
  remains durable
```

**Execution ≠ Finalization**

```text
Execution
  cancellable

Finalization
  durable
```

**HTTP Connection ≠ Lifecycle**

```text
Disconnect
    ≠
Turn termination
```

这些不是实现技巧，而已经成为正式 Architecture Law。

---

# 05 · Fabric

## **9.3 / 10**

### Clean Cloud Compute Runtime

Fabric 最大的架构价值，是保持了 Compute Runtime 的纯度。

它不是：

```text
Remote Agent Runtime
```

也不是：

```text
Second AppServer
```

而是：

```text
Compute Substrate
```

System Architecture 已经明确：

```text
Fabric owns

Sandbox
Compute Run
Compute Resource
GPU / Model Execution
```

但不得取得：

```text
Agent Session
Turn
Interrupt
Steer
Durable Queue
Agent Terminal
```

因此即使 Mind 或 AppServer 调用了 Fabric：

> **调用关系不会改变 Authority Ownership。**

这是非常重要的长期可扩展性基础。

未来：

```text
Fabric

Local Sandbox

Private GPU Cluster

Other Cloud Compute Runtime
```

都可以继续存在，而不会迫使 Agent Domain 重写。

---

# 06 · Authority Model

## **9.9 / 10**

这是当前整个架构最强的一项。

```text
                  AUTHORITY MODEL

                 ┌───────────────┐
                 │     Mind      │
                 │               │
                 │    Intent     │
                 │ Local Runtime │
                 │  Experience   │
                 └───────┬───────┘
                         │
                         ▼
                 ┌───────────────┐
                 │   AppServer   │
                 │               │
                 │ Durable Truth │
                 │   Lifecycle   │
                 └───────┬───────┘
                         │
                         ▼
                 ┌───────────────┐
                 │    Fabric     │
                 │               │
                 │    Compute    │
                 │   Execution   │
                 └───────────────┘
```

三个系统拥有不同种类的事实。

系统不存在：

```text
GlobalRuntimeState
SharedTurnState
ClientTurnMirror
FabricTurn
UniversalRecoveryManager
```

这样的第二 Authority。

System Architecture 还进一步禁止通过修 Bug 的方式逐渐引入这些全局聚合模型。

这说明架构不仅定义了：

> **应该怎么设计**

也定义了：

> **以后不允许怎么长。**

这是架构成熟的重要标志。

---

# 07 · Identity Architecture

## **9.8 / 10**

三个 Runtime 的 Identity 已经彻底分离：

```text
Mind
────────────────
session_id
run_id
command_id
idempotency_key


AppServer
────────────────
cid
sid
turn_id
attempt
request_id
client_message_id
event_seq


Fabric
────────────────
sandbox_id
fabric_run_id
compute identity
```

核心原则：

```text
Mind Run
   ≠
Remote Turn
   ≠
Fabric Compute Run
```

跨系统只通过明确 Adapter 建立映射，而不是依赖 ID 字符串偶然相等。

Identity Boundary 的成熟，直接支撑了：

```text
Idempotency
Recovery
Replay
Fencing
Deduplication
Reconciliation
```

---

# 08 · Durable Lifecycle

## **9.8 / 10**

一个标准在线 Turn 已经形成非常完整的生命周期：

```text
User
 │
 ▼
Mind Command
 │
 ▼
Freeze Request
 │
 ▼
Submit
 │
 ▼
AppServer Durable Turn
 │
 ▼
Worker
 │
 ▼
Provider / Tool
 │
 ├──── Optional Compute ───► Fabric
 │
 ▼
Runtime Event
 │
 ▼
AppServer Event Plane
 │
 ▼
Mind Observe
 │
 ▼
Projection
 │
 ▼
User
```

最关键的分离是：

```text
Submit
  ≠
Observe
```

新 Turn：

```text
Submit
  ↓
Turn Created
  ↓
Observe
```

已有 Turn：

```text
Attach / Replay
      ↓
Observe
```

### Architectural Law

> **Existing Turn must never be resubmitted.**

这条规则对解决网络响应丢失、Queue Start、Cold Recovery、Reconnect 场景中的 Duplicate Turn 极其重要。

---

# 09 · Recovery Architecture

## **9.7 / 10**

Recovery 已经不再被抽象成一个模糊的“恢复机制”。

现在被明确分成：

```text
Observation Recovery
────────────────────
Mind + AppServer

disconnect
   ↓
attach
   ↓
replay
   ↓
observe


Execution Recovery
──────────────────
AppServer

worker lost
   ↓
lease expires
   ↓
claim
   ↓
checkpoint
   ↓
continue / finalize


Compute Recovery
────────────────
Fabric

compute failure
   ↓
compute state
   ↓
retry / reconcile
```

三者拥有完全不同的 Owner。

> **Recovery Boundary follows Authority Boundary.**

这一点对降低未来 Runtime Complexity 非常关键。

---

# 10 · Effect Safety

## **9.7 / 10**

Agent Runtime 真正危险的不是模型回答错，而是：

> **外部副作用已经发生，但系统不知道它有没有发生。**

当前架构已经明确：

```text
Prepare
   ↓
Execute
   ↓
Commit
```

如果结果未知：

```text
UNKNOWN
   ↓
Reconciliation
```

而不是：

```text
UNKNOWN
   ↓
FAILED
   ↓
Retry
```

核心 Architecture Law：

> **Unknown Effect ≠ Failed Effect.**

客户端内部同样把 Approval、Effect、Tool Call 和传输幂等身份拆开，不通过一个 `request_id` 冒充所有业务身份。

---

# 11 · Presentation Architecture

## **9.5 / 10**

Mind 的 TUI 已经不是简单消费 Streaming Text。

当前展示链路具备独立 Projection：

```text
Runtime Event
      ↓
CanonicalItemReducer
      ↓
TurnActivityProjector
      ↓
reduce_turn_surface()
      ↓
TuiTurnSurfaceCoordinator
      ↓
Physical Terminal
```

内部还明确区分：

```text
Content
Presentation
Activity
Output Control
```

因此：

```text
Thinking hidden
      ≠
Turn ended

Assistant visible
      ≠
Turn terminal

SSE closed
      ≠
Turn completed
```

客户端架构已经把 UI Projection 从 Runtime Truth 中彻底剥离。

---

# 12 · Complexity Assessment

### Runtime Complexity

# **8.5 / 10**

> 此分数表示系统本身复杂度，不代表质量高低。

```text
Mind          7.8
AppServer     9.2
Fabric        6.7

System        8.5
```

复杂度主要来自：

```text
Concurrency
Interrupt
Steer
Durable Queue
Replay
Cursor
Worker Lease
Fencing
Finalization
Effect Reconciliation
Cross-process Recovery
Presentation Coordination
```

但目前整体复杂度已经有一个非常重要的变化：

```text
Before

Complexity
   ↓
hidden in race conditions


Current

Complexity
   ↓
explicitly modeled
   ↓
Authority
Identity
State
Lifecycle
Invariant
```

因此当前的复杂度主要属于：

> **Essential Complexity**

而不是无意义的：

> **Accidental Complexity**

### Complexity Quality

# **9.3 / 10**

> 系统虽然复杂，但复杂性已经基本做到 **可命名、可定位、可解释、可测试**。

---

# 13 · Architecture Maturity

可以把 Agent 系统成熟度划成五级：

```text
L1
Agent Script
│
│ Prompt + Tool
│
▼
L2
Agent Framework
│
│ Context + Session + Tool
│
▼
L3
Agent Runtime
│
│ Lifecycle + Execution + State
│
▼
L4
Durable Agent Runtime
│
│ Replay + Recovery + Idempotency
│
▼
L5
Agent Runtime Platform
│
│ Control Plane
│ Compute Plane
│ Observability
│ Governance
▼
```

当前 Mind：

```text
                L5
                 │
                 │       ●
                 │    Mind Agent Runtime
                 │
─────────────────┼──────────────────
                L4
```

## Current Maturity

# **L4.7 / L5**

已经具备：

```text
✓ Agent Runtime
✓ Durable Lifecycle
✓ Command Idempotency
✓ Replay
✓ Recovery
✓ Effect Reconciliation
✓ Durable Queue
✓ Control Plane
✓ Compute Plane
✓ Architecture Governance
```

距离完整 L5，剩余主要集中在：

```text
Production Proof
Cross-Runtime Observability
Long-running Soak
Release Automation
Operational Experience
```

---

# 14 · Architecture Risk

现在最大的架构风险已经不是：

> **“设计方向是不是错的？”**

而变成：

> **“实现能否长期保持这些 Architecture Laws 不被破坏？”**

风险重心已经完成迁移：

```text
Architecture Risk
      ↓↓↓

Implementation Drift
      ↓

Integration Risk
      ↓

Operational Risk
      ↑↑↑
```

因此下一阶段最应该保护的是：

```text
Authority
Identity
Lifecycle
Invariant
```

而不是继续寻找新的 Runtime 抽象。

---

# 15 · Verification Gate

完整系统级验收应该继续围绕：

```text
Normal Turn
Multi Turn
Long Streaming

Interrupt Thinking
Interrupt Assistant
Interrupt Tool
Interrupt Approval

Multiple Steers
Steer + Interrupt

Queue Add
Queue Start
Queue FIFO

Disconnect
Reconnect
Attach
Replay

Worker Failure
Finalizer Takeover

Fabric Success
Fabric Timeout
Fabric Failure

Terminal → Next Turn
```

核心指标：

```text
Duplicate Turn       = 0
Duplicate Tool       = 0
Duplicate Terminal   = 0

Input Loss           = 0
FIFO Violation       = 0

False Cursor Gap     = 0
Cursor Corruption    = 0

Session Gate Stuck   = 0
Provider Replay      = 0

Unknown Effect Retry = 0
```

---

# 16 · Architecture Laws

整个 Mind Agent Runtime 可以最终压缩成这些不变量：

```text
One Fact
    =
One Authoritative Owner


Command
    ≠
Fact


Submit
    ≠
Observe


Presentation
    ≠
Lifecycle


HTTP Ack
    ≠
Terminal


Connection
    ≠
Execution


Local Run
    ≠
Remote Turn


Remote Turn
    ≠
Compute Run


Worker
    ≠
Authority


Cache
    ≠
Truth


Unknown
    ≠
Missing


Unknown Effect
    ≠
Failed Effect


Compute
    ≠
Agent Lifecycle


Projection
    ≠
Source of Truth
```

这些原则已经同时贯穿系统级设计与 ProxyMind 内部实现约束。

---

# 17 · Final Score

```text
╔════════════════════════════════════════════╗
║                                            ║
║           MIND AGENT RUNTIME               ║
║                                            ║
║        ARCHITECTURE SCORECARD              ║
║                                            ║
║              A+ · 9.6 / 10                 ║
║                                            ║
╚════════════════════════════════════════════╝
```

| Area                       |    Status     |
|----------------------------|:-------------:|
| System Architecture        |   ✅ Mature   |
| Runtime Architecture       |   ✅ Mature   |
| Authority Model            |   ✅ Mature   |
| Lifecycle Model            |   ✅ Mature   |
| Protocol Boundary          |   ✅ Mature   |
| Recovery Model             |   ✅ Mature   |
| Effect Model               |   ✅ Mature   |
| Compute Boundary           |   ✅ Mature   |
| Architecture Documentation |   ✅ Mature   |
| E2E Proof                  |   ◐ Closing   |
| Observability              |  ◐ Hardening  |
| Production Validation      | ◐ In Progress |

---

# Final Verdict

> **Mind Agent Runtime 的核心架构已经成熟。**

现在形成的不是简单的三个仓库组合，而是三个拥有独立 Authority 的 Runtime：

```text
Mind
Agent Intelligence & Execution Runtime

AppServer
Durable Lifecycle & Control Plane

Fabric
Cloud Compute Runtime
```

三者通过稳定 Identity、Command、Event 和 Capability Boundary 协作，而不共享一套模糊的 Global State。

因此下一阶段已经不应该继续以：

```text
Architecture Redesign
Large Runtime Refactor
New Coordinator
New Global State
```

作为主要演进方向。

更合理的工程阶段是：

```text
                Architecture
                    FROZEN
                       │
                       ▼
               ┌──────────────┐
               │ Verification │
               └──────┬───────┘
                      ▼
               ┌──────────────┐
               │ Stabilization│
               └──────┬───────┘
                      ▼
               ┌──────────────┐
               │ Observability│
               └──────┬───────┘
                      ▼
               ┌──────────────┐
               │  Production  │
               └──────────────┘
```

### Architecture Signature

> **Mind thinks and orchestrates.**
> **AppServer makes execution durable.**
> **Fabric provides the compute substrate.**

### Final Rating

# **A+ · 9.6 / 10**
