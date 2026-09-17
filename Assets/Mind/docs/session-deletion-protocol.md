# 会话删除协议

正式服务端契约为 AppServer `services/contracts/session_deletion.py`、`routers/rt_session.py`、
`openapi.json` 及 `docs/PROTOCOL.md` 的 Session Deletion 节。客户端声明位于
`protocol/schema/session_deletion.py`，HTTP 调用位于 `protocol/client/session_deletion.py`。

`SessionDeletionRequest` 冻结 `request_id`、根 `cid/sid` 和最多 255 个后代身份。请求不接受
客户端指定所有者；服务端使用认证主体逐项核对。后代范围由本地代理树拥有者提供，协议层
不扫描图、读取文件或关闭运行资源。重复目标、额外字段及不匹配的身份均不能成为合法回执。

`delete_sessions()` 向 `POST /session/delete` 提交一次请求。只有 HTTP 200 且根身份、请求 ID、
`status=deleted` 和完整目标集合均匹配时，才返回 `SessionDeletionReceipt`。
`get_session_deletion()` 使用 `GET /session/delete?request_id=...` 查询同一意图，执行同样校验。
两者复用现有端点和应用鉴权配置，不生成新请求身份，不隐式重提命令。

| 结果 | 客户端含义 |
|---|---|
| 匹配的完成回执 | 远端删除完成；本地持久化清理仍由本地所有者完成 |
| `session_busy` / `owner_mismatch` / `session_missing` / `request_id_conflict` | 本次提交被明确拒绝，不能显示删除成功 |
| 传输失败、非法回执、服务端错误或 `session_cleanup_pending` | 结果未知，保留原意图并查询恢复 |
| 查询返回 `request_not_found` 或查询被拒绝 | 未获得原请求的完成证据，不代表原请求已取消 |
| 调用被取消 | 取消信号向生命周期所有者传播，不推断远端回滚 |

服务端将显式集合中的 Session、Turn、Queue、Transcript、事件及其关联执行记录原子删除。
活动或未 settled 的 Turn、未决 Effect 阻止整个集合删除；独立 fork 保留自己的历史副本，
不因来源删除而自动删除。未创建的后代也会记录身份墓碑，防止迟到创建。
服务端保留不含正文的幂等回执、身份墓碑及缓存停写标记，旧身份不可重用。
用户文件、共享配置、外部工具效果和独立 Agent/MCP 连接身份不属于远端会话删除范围。

本地资源分别归属于历史 Store（游标、用量、待完成 fork）、Transcript Store/Writer、
子代理图持久化（关系和邮箱）、Run Store（事件、快照、远端请求、outbox、事实）、
Effect Journal（沿 Run 的 effect_id 归属）和审批 Store。协议层不直接操作这些资源。
根 Harness 和子代理 Runtime 负责封锁新提交及收束 writer、Hook、事件投递和后台 flush；
关联身份必须保留至远端结果确定且本地清理完成，晚到写入不得恢复旧身份。

本 SDK 提供协议能力，不注册 `/delete` 交互命令。菜单和完整本地清理由前端及 Harness
接入后提供；仅调用 SDK 获得远端回执不能作为本地删除成功提示。
