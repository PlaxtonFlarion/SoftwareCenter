# 上下文用量客户端契约

本页描述客户端对 AppServer 正式 Context Usage 契约的实现。线上快照结构以
`protocol/schema/context_usage.py`、`protocol/schema/stream_events.py` 为准；压缩与恢复
分别由 `protocol/client/compact.py` 和 `protocol/client/context_usage.py` 消费。

## 事件与校验

`context.usage.updated` 是非 Item 的持久事件，共用 `mind.chat` 信封中的 `cid`、`sid`、
`turn_id`、`event_seq`、`presentation_epoch`。两个序号均为正整数；`event_seq` 属于
`cid + sid`，不新增独立用量版本号。事件不携带 Item 字段或非空 `display`，不是 Turn 终态。

以下六个字段全部位于必填的 `context_usage` 对象内。显式 `null` 表示未知，缺失字段和
未声明的业务字段均拒绝解析。手动压缩及其用量属于 Session，`turn_id` 必须为空字符串；
inline Review 的累计变化同样使用空 `turn_id`；模型响应的最近占用及其他 Worker 调用使用实际 Turn ID。

| 字段                   | 类型与语义                                                 |
|------------------------|------------------------------------------------------------|
| `model_context_window` | 大于 1 的整数或 `null`，该次调用最终执行窗口               |
| `last_token_usage`     | `{"total_tokens": 非负整数}` 或 `null`，最近有效上下文占用 |
| `total_token_usage`    | 下述 `SessionTokenUsage` 结构或 `null`，本会话累计实报     |
| `usage_source`         | `provider`、`estimate` 或 `unknown`，仅描述最近用量的来源  |
| `model`                | 非空字符串，与窗口、最近用量同时冻结的模型                 |
| `route`                | `responses`、`chat_completions` 或 `messages`，实际调用路由 |

`last_token_usage` 为 `null` 当且仅当 `usage_source` 为 `unknown`。累计值可以独立未知。
所有整数拒绝布尔值、浮点数、数字字符串和负数，不做类型转换。最近占用对象只接受
`total_tokens`；累计对象使用完整明细。不同 provider 的计数在服务端归一化。

AppServer 的 Provider 适配层已接收每次实际请求的输入、缓存、输出及可用推理明细，重试和压缩
摘要具有独立调用身份，并通过持久账本累计。缺失缓存或推理明细保持未知，不能由客户端补成零；
Messages 缺失构成原始总数的缓存计数时整次消耗未知。最近占用可由服务端估算，估算不计入消耗。

配套样例和百分比期望值见
[`tests/fixtures/protocol/context_usage.json`](../tests/fixtures/protocol/context_usage.json)。
样例的最近占用为 20,000，累计消耗为 250,000，有效窗口为 100,000，显示为 91%。
此样例包含用于验证累计值不影响百分比的合成账本值；AppServer 事件读取实际调用账本，
尚无调用登记时 `total_token_usage` 为 `null`。自动压缩阈值仍属于既有模型执行配置，
不属于这个展示事件，也不从累计消耗计算。

## 累计实报结构

SDK 的 `SessionTokenUsage` 与 AppServer 同名正式契约一致。以下八个字段全部必填，缺失、
额外字段和旧的单字段累计对象均拒绝；不提供兼容猜测：

| 字段 | 类型与含义 |
|---|---|
| `total_tokens` | 非负严格整数；已实报调用的原始总和，包含缓存输入及推理输出 |
| `input_tokens` | 非负严格整数或 null；包含缓存读取和写入的输入总和 |
| `cached_input_tokens` | 非负严格整数或 null；输入中的缓存读取部分 |
| `cache_write_input_tokens` | 非负严格整数或 null；输入中的缓存写入部分，与读取不重叠 |
| `output_tokens` | 非负严格整数或 null；包含推理的输出总和 |
| `reasoning_output_tokens` | 非负严格整数或 null；输出中的推理部分 |
| `reported_calls` | 非负严格整数；合法 total 报告的实际调用数，包含零值报告 |
| `unreported_calls` | 非负严格整数；已登记但无合法 total 的调用数，包含在途、失败、取消和缺报 |

整个对象为 null 表示没有账本事实。非空对象只累计已实报调用；某一明细在任一实报调用中
未知，其累计即为 null，不发布已知部分的小计。所有已知明细不得超过 total；input 与 output
均已知时，两者之和必须等于 total；缓存读取与写入合计不得超过 input，reasoning 不得超过
output；父项未知时，已知输入/输出明细下界之和仍不得超过 total。
reported_calls 为零时 total 必须为零，明细只能为零或 null。

`is_complete` 是类型派生属性，不进入 wire：unreported_calls 为零且 input、cached input、
output 均已知。对象存在而条件不满足就是部分统计；额外的缓存写入或推理明细未知，不阻止
核心数字完整，但不能伪装成已知零。零次调用的空累计与一次零值报告通过 reported_calls 区分。
当前本地 `ContextUsageRecord` 尚只保留完整累计的原始 total，部分统计映射为未知，避免旧有
`used` 展示将小计当作完整总数；完整明细缓存与退出快照尚待接入。

计数范围为当前 `cid + sid`，不汇总代理树。主模型、工具循环、截断续写、所有实际重试、失败/
取消请求、压缩摘要（包括无收益或 CAS 失败）和本 Session 触发的模型校验均应登记；本地校验、
确定性裁剪、replacement 估算不是模型消耗。inline Review 归共享 Session 累计，但不替换主
上下文占用；子代理与 detached Review 归各自 Session。fork 不复制来源消耗，恢复同一 Session
保持连续，切换模型或路由不清零。无 Session 的独立服务调用及外部工具自有模型调用不在此范围。

服务端在发送前分配独立 model_call_id 并持久登记；同一调用的报告重交、事件重放或接管只记
一次，实际重新请求必须使用新身份。Provider 未报告的数据保持缺报，不因业务失败被删除，也不
从日志补数。完整性只针对截至 event_seq 的已记录调用，不等同于供应商账单或仍在运行任务的最终
消耗。累计通过既有用量事件和回放完整替换，客户端从不对快照求和。

双端共享内容的合成样例见
[`session_token_usage.json`](../tests/fixtures/protocol/session_token_usage.json)，覆盖完整、零、
未知、明细不全、缺报调用和只有总数的情况。服务端持久记录、累计、事件与 outbox 原子提交，
登记中的调用计入缺报；数据库必须匹配当前完整基线与 schema manifest。SDK 已支持完整结构，
详细本地投影与退出快照仍待接入。源码推送不代表服务已部署。

## 提交、压缩和恢复

每次被接受且已提交的模型响应发布一份完整快照；后续响应替换最近用量。客户端不会从终态
`usage`、历史正文或字符数重建缺失快照，不会把事件重放累加到消耗总数。

自动或手动压缩提交 replacement 后发布 `estimate` 快照；累计用量由账本决定，不因本次
重算增加。失败的压缩不发布成功重置。`/compact` 中，用量事件与同一操作的压缩 Item
共用空 `turn_id`，须在 `context.compaction.completed` 前到达。客户端在交付压缩终态前关闭
HTTP 流，用量事件不参与 Item 终态判断。

根会话拥有用量展示投影，订阅跨越单个 OutputSession；Review 和子代理不会写入主会话
快照。最新记录缓存于本地会话历史库，按 `cid + sid` 和 `event_seq` 单调替换，随历史游标
过期或容量淘汰而删除。缓存是已确认事实的副本，不推进聊天流确认游标。

冷恢复从首屏起隐藏默认 100%，读取目标会话缓存及服务端完整快照；没有可靠值时为 `unknown`。
attach/replay 期间隐藏中间投影，收到既有传输的 `caught_up` 确认后发布最终快照。新分支没有目标会话的
权威快照时保持未知，不复制源会话最新用量。选择新模型或配置不会修改旧快照中的窗口；
下一份事件到达前，保留的值仍归属于最近实际执行的模型。

inline Review 共用主会话身份，但其最近占用属于独立审查上下文：客户端不将它投影到主
上下文，服务端也不以审查上下文替换主会话的恢复快照。累计契约要求它的调用实报归共享
Session，以空 `turn_id` 发布累计变化并保留主上下文 last/window/source/model/route。
审查响应的最近占用仍留在 Review Turn。detached Review 只更新自身 Session，
不使根会话最近占用从未知变为已知。

客户端通过既有 `/reports/open` 取得会话查看授权，并分页读取 `/mind-replay` 的
`data.context_usage` 完整事件。分页完成前保持 pending；快照不推进聊天流确认游标。
此读取有整体超时边界，不增加后台轮询。历史裁剪信号会作废区间内的旧缓存；服务端
独立保留的权威快照可以早于裁剪水位，客户端在完成恢复后使用它。鉴权、协议或读取失败
时隐藏用量，不通过重新调用模型补齐显示。

## 显示口径

默认状态栏只在 Turn 运行中且输入框含待排队草稿时显示右侧用量；空闲、空输入、Shell、
前台命令和等待 Turn 启动时不显示。退出排队提示不删除用量快照。Codex 默认启用模型与目录
状态栏，其普通状态栏同样不显示此独立右侧计数；禁用状态栏时的回退 footer 不属于默认行为。

`initial` 仅用于尚未执行的新会话，其候选文案为 `100% context left`，不代表空闲首屏显示。
首个请求开始后没有可靠计数即为未知；`pending` 和 `unknown` 隐藏用量。
`known` 使用最近用量与有效窗口计算：

```text
B = 12000
W <= B: left = 0
W > B:
  available = W - B
  used = max(last_total_tokens - B, 0)
  remaining = max(available - used, 0)
  left = (200 * remaining + available) // (2 * available)
```

结果限制到 0..100；未知最近用量不能当作零。窗口未知且累计值可靠时，显示如 `250K used`。
窗口不再乘 95%，也不重复扣除输出预留。12,000 是显示基线，不是服务端新增预算预留。
该算法与 Codex footer 对齐，但不保证跨 provider 的 token 数值或服务端预算策略相同。

右侧文字统一 dim、非 bold，相对终端物理右边缘保留两列，并与左侧至少间隔一列。
输出适配器明确计入 Windows 后端在可绘制宽度之外预留的一列，普通 VT 输出不扣除该列；
不扩大底层安全写入宽度。排队模式为百分比预留固定宽度，位数变化和恢复隐藏期间不改变
排队提示的完整或简短版本；仍放不下则隐藏用量。更新隐藏或裁剪掉的用量不请求额外重绘。
历史搜索、退出确认、回看、菜单和隐藏模式遵循原有表面优先级。

## 退出摘要契约

以下规则规定退出展示接入时的目标行为；当前实现仍只有普通退出的单行恢复提示，尚未接入
用量行、分行恢复提示和 `/exit` 别名。用量行与恢复指引分别判定：完整、原始 total 非零才显示
精确用量；可靠可恢复身份独立决定 resume，不用本进程 turn_count 代替持久会话存在性。

与本地 Codex `tui/src/token_usage.rs` 一致，显示 input 为原始 input 减 cached input，显示
total 为该 input 加 output；reasoning 已在 output 内，不再相加。缓存写入保留在 input 中。
数字用千位逗号，已知非零缓存追加 ` (+ N cached)`，已知非零推理追加 ` (reasoning N)`；
未知明细省略，核心字段未知或存在缺报时不输出精确用量行。已知原始 total 为零时整行省略；
全缓存输入可能使显示 total 为零，仍可显示实际非零缓存消耗。

原始 input=17,663、cached=14,976、output=14、reasoning=0 的排版目标为：

```text
■ Token usage: total=2,701 input=2,687 (+ 14,976 cached) output=14
■ To continue this session, run:
  mind resume <sid>
```

删除成功只保留适用的第一行。正文前保留 ProxyMind 的 `■`，恢复命令独占下一行并缩进两个
空格，继续使用现有命令语义色。Codex 本身没有这两个前导方格；这是明确保留的客户端样式。
产品名取 `metadata.const`，不在业务层写死。终端释放前只清理临时交互区域，保留历史和滚屏；
退出不清屏、不增加动画，删除等待额外的 operation 转圈应随展示接入移除。

| 入口或状态 | 唯一退出结果 |
|---|---|
| `/quit`、`/q`、`quit`、`exit`，以及待接入的 `/exit` | 正常关闭；可靠用量和可恢复身份分别展示 |
| Ctrl+C 确认退出、空闲空草稿 Ctrl+D | 共用关闭流程，Ctrl+C 保持 130，普通退出保持 0 |
| Ctrl+C 仅清草稿或中断任务、菜单 Esc、删除取消 | 不构成退出，不输出摘要 |
| `/shutdown` | 执行既有服务关闭职责后，根据会话事实输出一次摘要 |
| `/archive` 成功 | 可靠用量与 `Session archived: <sid>`；不提示普通 resume |
| `/delete` 完整成功或恢复当前会话删除并完整清理成功 | 可靠用量；不提示 resume |
| `/delete recover` 清理其他会话 | 当前会话继续，不输出摘要、不替换当前用量 |
| 删除被拒绝、结果未知或本地清理未完成后主动退出 | 不声称删除成功；未决删除保留对应恢复指引，不给无法使用的 resume |
| 冷恢复后立即退出 | 使用已恢复事实，不因本进程未发起 Turn 而丢失摘要 |
| 空会话且没有可靠非零用量 | 静默，不伪造统计或恢复身份 |
| 启动失败、收尾异常、强制终止 | 不显示正常完成假象；强制终止不保证输出 |

仅停止客户端观察、尚未确认远端停止时，已知累计行使用 `Token usage so far:` 并保留未停止
事实，不能称作最终总消耗；完整性仍以最后确认的 event_seq 为界。此限制与 Codex
`app/exit_summary.rs` 的远端断开分支一致，不改变当前服务关闭与取消职责。

### 入口调用链与快照所有权

| 当前入口 | 路径及状态边界 |
|---|---|
| 空闲退出别名 | `prompting/commands.py` → `session/dispatch.py` → lifecycle.request_stop → DispatchAction.EXIT |
| 流式执行中的退出或 shutdown | dispatcher → `session/barriers.py.handle_stream_command` → stop/cancel → `session/loop.py` 收束 |
| 前台等待、删除或恢复删除屏障 | `barriers.py._handle_wait_command` 接受退出/shutdown并取消本地等待；不伪造远端完成 |
| Ctrl+C | `core/submission.py.interrupt_input` 按草稿、活动中断、退出确认处理 → `loop.py` 捕获中断或消费退出请求 |
| Ctrl+D | keymap 的空闲空输入过滤 → submission.exit_input → EOF → loop.request_stop |
| 启动恢复/重新附着 | `loop.py` 恢复等待也捕获 TuiInterruptRequested/EOF；流式附着复用 dispatcher；未追平前不显示中间用量 |
| archive/delete成功 | dispatch → conversation 生命周期操作 → 完成事实 → stop → 统一收尾；恢复其他会话不 stop |
| 所有正式退出 | `frontends/cli/bootstrap.py.finalize_application` → conversation.end → runtime.close → resources.close → 摘要 |

用量 owner 仍为 `RootConversationSession` 持有的应用层投影。退出展示接入必须由该 owner 在
会话身份锁和现有生命周期内取得不可变快照：普通结束在清空投影前；归档在成功状态清空前；
删除在破坏本地资源前保存候选，仅在当前会话远端删除与本地清理完整成功后标记为删除退出。
候选不等于成功，失败、恢复其他会话和身份切换不得误用；新建、reset、bind、fork 清除不属目标
身份的候选。删除不可为了摘要保留数据库行，也不能由前端在删除后重建历史。

快照包含身份、最后确认 event_seq、已校验用量、可恢复/归档/删除/未决删除事实与远端是否
已确认停止，不能只保存格式化文字。通过既有 conversation 边界交给 bootstrap，不建立另一套
退出状态机。`finalize_application` 持有退出期间的展示值，在所有既有收尾成功且 runtime
释放终端后调用现有输出入口一次；各个命令不得自行打印摘要。失败不输出正常完成，消费或
关闭后释放快照。完整字段缓存与该快照生命周期目前尚未实现。
