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
模型响应和自动压缩使用实际 Turn ID。

| 字段                   | 类型与语义                                                 |
|------------------------|------------------------------------------------------------|
| `model_context_window` | 大于 1 的整数或 `null`，该次调用最终执行窗口               |
| `last_token_usage`     | `{"total_tokens": 非负整数}` 或 `null`，最近有效上下文占用 |
| `total_token_usage`    | 同一计数结构或 `null`，权威账本累计消耗                    |
| `usage_source`         | `provider`、`estimate` 或 `unknown`，仅描述最近用量的来源  |
| `model`                | 非空字符串，与窗口、最近用量同时冻结的模型                 |
| `route`                | 非空字符串，与该快照对应的实际调用路由                     |

`last_token_usage` 为 `null` 当且仅当 `usage_source` 为 `unknown`。累计值可以独立未知。
所有整数拒绝布尔值、浮点数、数字字符串和负数，不做类型转换。计数对象只接受
`total_tokens`；不同 provider 的缓存、reasoning 和输入输出计数应在服务端归一化。

配套样例和百分比期望值见
[`tests/fixtures/protocol/context_usage.json`](../tests/fixtures/protocol/context_usage.json)。
样例的最近占用为 20,000，累计消耗为 250,000，有效窗口为 100,000，显示为 91%。
此样例包含用于验证累计值不影响百分比的合成账本值；当前 AppServer 尚无完整计费账本，
真实事件的 `total_token_usage` 为 `null`。自动压缩阈值仍属于既有模型执行配置，
不属于这个展示事件，也不从累计消耗计算。

## 提交、压缩和恢复

每次完成且已提交的模型调用发布一份完整快照；后续调用替换最近用量。客户端不会从终态
`usage`、历史正文或字符数重建缺失快照，不会把事件重放累加到计费总数。

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

客户端通过既有 `/reports/open` 取得会话查看授权，并分页读取 `/mind-replay` 的
`data.context_usage` 完整事件。分页完成前保持 pending；快照不推进聊天流确认游标。
此读取有整体超时边界，不增加后台轮询。历史裁剪信号会作废区间内的旧缓存；服务端
独立保留的权威快照可以早于裁剪水位，客户端在完成恢复后使用它。鉴权、协议或读取失败
时隐藏用量，不通过重新调用模型补齐显示。

## 显示口径

`initial` 仅用于尚未执行的新会话，可显示 `100% context left`。首个请求开始后没有可靠
计数即为未知；`pending` 和 `unknown` 隐藏用量。`known` 使用最近用量与有效窗口计算：

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

右侧文字统一 dim、非 bold，并保留一列右边距及至少一列左右间隔。普通模式按现有顺序
截短左侧信息；排队模式先尝试完整提示，再尝试简短提示，仍放不下则隐藏用量。
历史搜索、退出确认、回看、菜单和隐藏模式遵循原有表面优先级。
