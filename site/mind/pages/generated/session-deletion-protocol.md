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
Effect Journal（独立保存工具 Effect 的 `cid/sid` 归属）和审批 Store。Run outbox 的
`effect_id` 是本地派发身份，与服务端工具 Effect 不属于同一身份空间，不能用来互相关联。
协议层不直接操作这些资源。
根 Harness 的 `RootConversationSession.delete_current()` 是删除生命周期入口。它先收束子代理、
关闭当前运行时提交边界，再通过 `ProtocolSessionDeletionAdapter` 提交冻结的正式请求；适配器
只转换正式 SDK 的请求、回执和拒绝/未知结果，不在协议层发现本地资源。只有远端完整回执确认后，
才分发 `SessionEnd(reason="deleted")` 并调用本地清理 Store。Hook、事件报告关闭和后台 flush
仍由各自 owner 负责，清理 Store 取得 Transcript 独占锁并写入持久停写标记后，迟到写入会被
已有触发器和文件标记拒绝，不能重新创建旧会话记录。

## 本地持久化删除

`SQLiteSessionDeletionStore` 通过 `SessionDeletionStore` 端口接收 `LocalDeletionPlan`。
调用方必须先确认远端删除，并通过既有生命周期关闭目标运行资源；该 Store 不发送远端请求，
不结束任务或关闭 Hook。阻塞的文件及 SQLite 操作应由调用方调度到工作线程。

计划固定请求身份、完整会话集合和已确认映射的本地 Run Session 身份。CLI/TUI 的确定性
本地身份由现有身份派生函数补齐；Run Store 同时核对 Command 中冻结的远端绑定与已持久化
的远端请求映射，尚未发出请求的 queued Run 也属于清理范围。不能将
线上 `sid` 当作 Run 的 `session_id`。目标内代理图若仍包含集合外子会话，清理拒绝完成，
不能静默扩大远端已经确认的范围。

历史库中的 `session_deletions` 在清理前提交计划和所有存储的实际路径。文件适配器校验
会话标识、目录及实际路径，拒绝符号链接、Windows 重解析点、硬链接和非普通文件，并先
取得全部目标的独占锁。Transcript writer 在打开期间持有共享锁；其他进程仍在写入时，
删除报告占用错误，释放前已取得的锁。进程退出会释放操作系统锁。

文件锁取得后先保存 Transcript 停写标记，再依序清理 Effect/工具结果、审批事实、Run 的
关联表、Transcript 正文、代理图及邮箱、历史游标/用量/待完成 fork。各数据库在自己的
事务中同时提交停写标记与删除，触发器拒绝新插入、更新及其他进程的迟到写入。
整个过程不声称拥有跨数据库及文件的原子事务。

仅当所有步骤完成时，计划标记为完成。文件缺失可以继续；占用、权限或 SQLite 错误向上
传播，已完成的清理不回滚，原计划由 `pending()` 读取并幂等重试。同请求的范围变化、
存储目录或时区导致的路径变化均被拒绝，避免在新位置执行空清理后误报旧位置已删除。
目标关系保存在计划中，恢复不依赖可能已过期的游标或已删除的代理图。

Effect Journal 创建时要求明确的会话坐标；旧表仅从保存的正式核对结果迁移归属。
缺少归属证据的旧 Effect 会导致本地清理明确失败并保留待恢复计划，不猜测所有者、删除
无关记录或报告成功。已提交的确定结果及未确定效果的幂等语义保持不变。

最小身份停写记录、已完成请求的身份回执、空的 `.deleted` 标记和稳定的 `.lock` 文件不
保存正文且不自动过期。只有整个本地状态目录被显式重置并停用所有使用它的进程时，才可
一起移除；单独回收标记会失去旧身份不可重用的保证。用户文件、共享配置、永久权限规则
及对照会话不属于清理范围。

当前已提供正式协议 SDK、本地持久化清理和 Harness 生命周期协调。未知结果会先把完整计划
写入 `session_deletions`，`recover_delete()` 使用原请求 ID 查询并继续清理；远端已完成而本地
失败时返回 `local_failed` 并保留同一计划。前端 `/delete` 命令和原生 TTY 菜单仍在后续阶段接入，
仅获得远端回执不能作为本地删除成功提示。
