# 订阅模式

入口页只负责入口摘要；`agent listen` 的完整运行心智、协议链路和排障继续看这里。
重点是讲清监听器如何在 TUI 生命周期内维持独立的远端请求接收状态。

## 先判断是不是这页的范围

- 你要理解 `agent listen` 做了什么，以及它和主动执行链路的边界：看这里
- 你要排查 `/agents/open`、`/agents/ws`、`resume`、断线重连和消息去重：看这里
- 你只是想在本地交互输入目标：先看 `交互模式`
- 你只想理解项目整体分层，不需要进入协议细节：先看 `背景与架构`

## 怎么读这页

- 先看“模式定位”和“启动流程”，建立 `agent` 的基本心智
- 再看“协议时序”和“任务下发”，理解服务端如何把任务推到本地
- 最后看“恢复与排障”，确认 409、断线和重放时应该怎么看

## 模式定位
`agent listen` 会启动普通 TUI，并在同一进程内开启远端请求监听器。

- `exec` 或交互会话：本地主动发起请求，再等待本轮执行结束
- `agent listen`：保持普通 TUI 交互，同时通过长链路接收服务端下发的任务
- `/listen`：打开带当前状态的监听器菜单，选择启动或停止
- `/listen start|stop|status`：直接启动、停止或输出同一个监听器的状态
- `/mailbox`：查看消息摘要，运行、删除或展开单条消息，并管理会话级 Auto-run

入口关系：
- CLI 参数层面，`agent listen` 与 `exec` 是同级互斥入口
- 运行时层面，listener 作为 TUI 会话拥有的后台任务启动和停止

一句话理解：

- `exec` 和交互会话是本地主动请求
- `agent` 是本地订阅，等待服务端推任务

## 启动流程
当执行：

```text
mind agent listen
```

本地会按下面的顺序进入监听模式：

1. 启动普通 TUI
2. 构造 `AgentConfig`
3. 生成稳定 `device_id`
4. 调用 `/agents/open`
5. 从响应中提取 `session_id / ws_token / resume_token / ws_url`
6. 建立 `/agents/ws` 长链路并发送 `hello`
7. 把服务端请求加入当前进程的临时收件箱

收件箱数量显示在现有单行 footer 中，不增加画布高度。`/listen` 菜单把 `ready`、
`starting` 或 `stopped` 放在标题行，菜单项只负责选择启动或停止。启动会在活动状态区
显示进度，直到收到服务端 `ready`，随后把稳定结果写入正文；停止使用相同的前台状态
交接。单条连接 15 秒内没有收到 `ready` 会主动关闭并进入现有重连流程；通过
`/listen start` 启动时，整体等待 30 秒仍未 ready 会停止本次监听并展示失败结果，
不会让 spinner 无限保留。停止监听只关闭传输，当前进程的待处理消息仍然保留。

`/mailbox` 的一级菜单把待处理数量、Auto-run 和监听状态放在标题行。选择消息后进入
`Run / Delete / Detail` 二级菜单；Detail 使用同一个 TUI Application 切换到全屏只读
正文，关闭后返回该消息的操作菜单。Delete 只删除本地内存消息和连接上下文，不向
服务端发送删除或拒绝事件。

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
mind agent listen
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
加入本地临时收件箱
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
订阅链路只接收和保存服务端任务，不在 WebSocket handler 中直接启动模型轮次。

任务通过非空 `message` 下发，并和可选的意图摘要、metadata 一起保存在内存中。
默认不会因为收到消息或执行 `/listen` 命令自动运行任务。用户可以从 `/mailbox`
手动 Run，或在该菜单中启用 Auto-run。

关键约束：
- `message` 必须是非空字符串
- 意图摘要可以为空
- 本地会先完成内存入箱，再发送 `mind.received`，避免确认后未能保存消息
- 收件箱只在当前进程内有效，退出或重新打开应用后不恢复
- Auto-run 只在当前 TUI 会话有效，不写入配置；退出后恢复为关闭
- Auto-run 只在监听器 ready 时工作，并通过 TUI 主循环一次执行一条，不在 WS 回调中并发模型轮次
- 已运行或删除的消息会从进程内收件箱释放，不保留本地历史副本

## 恢复与重连
`agent` 模式默认把“不断线”当成不现实前提，所以恢复链路是核心能力，不是补丁逻辑。

### 正常恢复
当 WS 因网络、超时或服务端抖动断开后，本地会：

1. 保留 `session_id / resume_token / last_acked_seq`
2. 立即清除当前连接的 ready 状态，避免 Auto-run 使用失效连接
3. 调用 `/agents/resume`
4. 如果服务端返回 `resumable=true`，复用原会话
5. 新连接建立后，把尚未处理的本地消息重新绑定到当前连接

正常退出、TUI 异常退出和 Ctrl+C 都会取消订阅 Supervisor。WS 由异步上下文管理，
Supervisor 退出时会等待连接上下文关闭；最终 Controller 清理还会再次执行幂等的
Listener 停止，避免后台长链路遗留到进程退出之后。
6. 重连 WS 后发送 `resume`
7. 接收可能的 `replay.batch`

### 恢复失败后的回退
如果服务端认为会话已不可恢复：

1. 本地把状态标记为 `Resume Expired`
2. 再次调用 `/agents/open`
3. 打开一个全新的订阅会话

这就是文档里常说的 `resume or reopen`。

## 去重与确认
`agent` 模式同时维护两类确认信息：

- 已确认的服务端消息序号：用于断线恢复
- 已接收的任务消息标识：避免重放时重复入箱

因此要注意：
- `mind.received` 解决的是“服务端知道你收到了”
- 本地去重缓存解决的是“本地不要把同一条任务加入收件箱两次”
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
Auto-run 默认为关闭；需要自动消费时，从 `/mailbox` 开启。若消息没有出现在 footer
计数中，或启用 Auto-run 后仍未运行，再继续确认：

优先确认：
- 是否收到了 `mind.forward`
- 下发的 `payload.message` 是否为非空字符串
- 消息是否因为缺少必要的任务标识或会话标识被本地丢弃
- Listener 是否已经进入 ready

### 怀疑任务被重复执行
优先检查：
- 服务端是否重复投递了相同任务消息标识
- 本地日志里是否出现 `mind.forward replay skipped`
- 断线恢复后是否发生了 `replay.batch`

## 和其他文档的关系
- `交互模式` 讲 REPL 会话以及 `/listen`、`/mailbox` 的本地入口
- `背景与架构` 讲系统骨架，不展开 `agent` 协议时序
- 如果后续 `agent` 引入新的下发消息类型、执行结果回传协议或服务端治理约束，应继续补这页，而不是把细节塞回入口文档
