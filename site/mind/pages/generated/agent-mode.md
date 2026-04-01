# 驻留与订阅模式

主 README 只负责入口摘要；`--agent` 的完整运行心智、协议链路和排障继续看这里。  
重点是讲清它为什么不是 `chat / fast / plan` 的附属状态，而是一条独立的驻留订阅执行面。

## 先判断是不是这页的范围

- 你要理解 `--agent` 做了什么，以及它和 `chat / fast / plan` 的边界：看这里
- 你要排查 `/agents/open`、`/agents/ws`、`resume`、断线重连和消息去重：看这里
- 你只是想在本地交互输入目标，切换 `CHAT / FAST / PLAN`：先看 `交互模式`
- 你只想理解项目整体分层，不需要进入协议细节：先看 `背景与架构`

## 怎么读这页

- 先看“模式定位”和“启动流程”，建立 `agent` 的基本心智
- 再看“协议时序”和“任务下发”，理解服务端如何把任务推到本地
- 最后看“恢复与排障”，确认 409、断线和重放时应该怎么看

## 模式定位
`--agent` 是一条独立的驻留订阅模式，不是 REPL 内部的第四个状态。

- `chat / fast / plan`：本地主动发起一次请求，再等待本轮执行结束
- `agent`：本地先向服务端注册驻留会话，再通过长链路持续接收服务端下发的任务

入口关系：
- CLI 参数层面，`--agent` 与 `--chat / --fast / --plan` 是同级互斥入口
- 运行时层面，`Mind.agent_loop()` 直接进入订阅循环，不经过 REPL 三态切换

一句话理解：

- `chat / fast / plan` 是本地主动请求
- `agent` 是本地驻留，等待服务端推任务

## 启动流程
当执行：

```text
mind --agent
```

本地会按下面的顺序进入驻留模式：

1. 构造 `AgentConfig`
2. 生成稳定 `device_id`
3. 调用 `/agents/open`
4. 从响应中提取 `session_id / ws_token / resume_token / ws_url`
5. 建立 `/agents/ws` 长链路
6. 发送 `hello`
7. 进入持续监听状态

启动时本地会带上这些身份信息：
- `agent_id`
- `device_id`
- `client_version`
- `platform`
- `arch`
- `hostname`

其中：
- `device_id` 是根据主机名、网卡地址、系统和架构做稳定摘要，不是随机临时值
- 服务端如果认为当前 `agent + device` 已有未释放会话，`open` 可能返回 `409`

## 协议时序
高层时序可以理解成：

```text
mind --agent
  ↓
POST /agents/open
  ↓
session_id / ws_token / resume_token
  ↓
connect /agents/ws
  ↓
hello
  ↓
ready
  ↓
ping / pong
  ↓
mind.forward
  ↓
mind.received
  ↓
本地执行 chat / fast / plan 或 code 任务
```

几个关键消息：

- `hello`：本地首次握手，声明当前客户端版本和设备身份
- `ready`：服务端确认长链路已进入可用状态，并返回心跳与恢复相关参数
- `ping / pong`：链路保活
- `mind.forward`：服务端正式下发任务
- `mind.received`：本地确认“我已经收到这条任务”，不是“任务已执行成功”
- `resume`：断线后告诉服务端，本地已经确认到哪个 `seq`
- `replay.batch`：服务端补发断线期间的历史消息

## 任务下发
`agent` 模式本身不直接定义新执行器；它做的是把服务端任务映射回本地已有运行面。

`mind.forward.payload.mode` 目前只允许：
- `chat`
- `fast`
- `plan`

`mind.forward.payload.profile` 目前只允许：
- 空字符串：按普通单次请求执行
- `code`：走 `mind_pack(...)`，把 `subject` 当作星图蓝本入口

映射关系：
- 普通任务：`mind.calling(message=..., mode=...)`
- 星图任务：`mind.mind_pack([subject], mode, ...)`

关键约束：
- `mode` 不是任意字符串，只能落回本地现有三种执行面
- `profile=code` 时必须提供 `subject`
- 非 `code` 任务必须提供 `message`
- 本地会先发 `mind.received`，再把实际执行放到后台任务里，避免阻塞 WS 心跳

## 恢复与重连
`agent` 模式默认把“不断线”当成不现实前提，所以恢复链路是核心能力，不是补丁逻辑。

### 正常恢复
当 WS 因网络、超时或服务端抖动断开后，本地会：

1. 保留 `session_id / resume_token / last_acked_seq`
2. 调用 `/agents/resume`
3. 如果服务端返回 `resumable=true`，复用原会话
4. 重连 WS 后发送 `resume`
5. 接收可能的 `replay.batch`

### 恢复失败后的回退
如果服务端认为会话已不可恢复：

1. 本地把状态标记为 `Resume Expired`
2. 再次调用 `/agents/open`
3. 打开一个全新的订阅会话

这就是文档里常说的 `resume or reopen`。

## 去重与确认
`agent` 模式同时维护两类确认信息：

- `last_acked_seq`：记录已经观测到的服务端消息序号，用于断线恢复
- `forwarded_message_ids`：记录已经转发执行过的 `mind.forward.message_id`，避免重放时重复执行

因此要注意：
- `mind.received` 解决的是“服务端知道你收到了”
- `forwarded_message_ids` 解决的是“本地不要把同一条任务执行两次”
- 它们不是一回事，不能混为“任务成功回执”

## 常见排障

### `/agents/open` 返回 409
通常表示服务端仍认为同一个 `agent` 持有旧会话。

排查建议：
- 先确认是否已有另一台同标识实例在线
- 看服务端是否还保留旧会话
- 本地实现会等待 5 秒后继续重试，不会立刻退出

### 一直在重连
优先看这几类问题：
- 服务端地址或 `ws_url` 是否正确
- `X-Agent-Token` 对应的 client secret 是否匹配
- 网络是否允许 HTTP 成功但 WS 被拦截
- 服务端是否在 `ready` 前主动断链

### 可以连上但不执行任务
优先确认：
- 是否收到了 `mind.forward`
- `payload.mode` 是否是 `chat / fast / plan`
- `payload.profile=code` 时是否提供了 `subject`
- 消息是否因为缺少 `message_id / call_id / cid / sid` 被本地丢弃

### 怀疑任务被重复执行
优先检查：
- 服务端是否重复投递了相同 `message_id`
- 本地日志里是否出现 `mind.forward replay skipped`
- 断线恢复后是否发生了 `replay.batch`

## 和其他文档的关系
- `交互模式` 讲的是 REPL 三态，不覆盖 `agent`
- `背景与架构` 讲系统骨架，不展开 `agent` 协议时序
- 如果后续 `agent` 引入新的下发消息类型、执行结果回传协议或服务端治理约束，应继续补这页，而不是把细节塞回入口文档
