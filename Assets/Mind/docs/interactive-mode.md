# 交互模式

> 权威参考：本页维护全部 REPL slash 命令、参数和行为。README 与官网入口页只保留摘要和跳转链接。

入口页只负责交互入口；REPL 指令、会话管理和输入约束继续看这里。
重点是讲清进入 REPL 之后能做什么、怎么管理上下文、哪些输入适合留在交互模式里。
`agent listen` 会在普通 TUI 中启动远端请求监听器，另见 `订阅模式`。

## 先判断是不是这页的范围

- 你要连续试多个目标并管理同一会话：看这里
- 你要查 `/new /resume /archive /fork /permissions /model /provider /effort /preferences /compact /tools /hooks /agent /listen /mailbox /queue /diff /copy /ps /stop /mcp /helix-link /helix-mode /helix-unlink /helix-home /helix-stop /skills /shutdown /quit` 这些 REPL 指令：看这里
- 你要理解 `agent listen` 的订阅链路：这页不展开，直接看 `订阅模式`
- 你要理解单次命令行入口，不要先从交互模式文档开始
- 你只是偶尔跑一条命令，不一定需要先读这页

## 怎么读这页

- 先看“启动与提示”，建立 REPL 的基本运行心智
- 再看指令索引，确认管理会话、查看工具和退出的方式
- 最后看输入约束，判断哪些任务适合继续留在 REPL

## 启动与提示
`mind` 进入循环后，会持续读取用户输入并通过统一模型轮次执行。

- 每轮输入框持续接收目标或 `/` 命令
- 会话会生成 `cid / sid`，用于链路追踪与调用元数据

一句话理解：

- REPL 是连续交互入口
- 工具范围由本地 runtime、外接 MCP 和 Helix 连接状态共同决定

### 完整记录与按键配置

`Ctrl+T` 打开完整会话记录。按键可以在用户 `config.toml` 或 Profile 中覆盖，
配置在下次启动时生效：

```toml
[tui]
scrollback_reflow_line_limit = 10000

[tui.keymap.global]
open_transcript = "f12"

[tui.keymap.pager]
scroll_down = ["down", "n"]
page_down = ["page-down", "space"]
close = ["q", "ctrl-c"]
```

`pager` 还支持 `scroll_up`、`page_up`、`half_page_up`、
`half_page_down`、`jump_top`、`jump_bottom` 和 `close_transcript`。
值可以是单个按键字符串或字符串数组；空数组表示显式解绑。支持普通字符、
`ctrl-<字符>`、`alt-<键>`、`shift-<字母/Tab>`、`f1` 到 `f24`，以及
方向键、Home/End、PageUp/PageDown 等命名键。同一上下文中的重复按键会导致配置校验失败。
`scrollback_reflow_line_limit` 限制终端尺寸变化时从稳定记录中重新输出的逻辑行数，
默认是 `10000`，值必须是正整数。项目级配置不能覆盖 TUI 配置。

空输入时连续按两次 `Esc` 可以直接选择最近的用户消息；在完整记录中使用
`Esc/Left` 向前选择、`Right` 向后选择，按 `Enter` 从选中消息前创建分支并恢复输入。

## 指令索引
- `/new [title]`：开始新对话，重置 `cid / sid`，可选保存会话标题，保留模型和本地配置
- `/resume`：从最近 24 小时内的本地会话游标中恢复对话
- `/archive`：归档当前会话并退出前台；执行前会请求确认
- `/fork`：复制当前对话上下文并切换到新的会话分支
- `/permissions`：在 `Read Only`、`Auto`、`Full Access` 三个权限预设间切换；分别对应 `read-only + on-request`、`workspace-write + on-request`、`danger-full-access + never`
- `/model <model-id>`：持久化主模型 ID；写入当前 Provider Profile，下一轮模型请求生效
- `/provider`：切换当前使用的模型 Provider Profile
- `/effort`：设置主模型推理强度
- `/preferences`：打开本地 Preferences 页面，用于维护模型、密钥、Base URL 和服务域名配置
- `/compact`：压缩当前对话上下文，减少后续请求携带的历史体积
- `/tools`：查看当前可用 MCP 工具，包含 Mind native、外部 MCP 和已接入 Helix MCP 工具
- `/hooks`：查看、信任和启停生命周期 Hooks
- `/agent`：查看和管理当前会话的子 Agent 线程
- `/listen [start|stop|status]`：管理远端请求监听器；省略动作时打开操作菜单
- `/mailbox`：查看远端请求摘要，运行、删除、展开消息或切换当前会话的 Auto-run
- `/queue [list|add <message>|retry <id>|delete <id>|move <id> <position>|start [id]]`：管理当前会话的持久消息队列
- `/diff`：查看当前 Git 工作区差异（包含未跟踪且未被忽略的文件）
- `/copy`：复制最近一次助手回复原文
- `/ps`：查看运行中的后台终端
- `/stop`：停止全部后台终端
- `/mcp [start|force|stop|restart|status]`：管理外部 MCP 服务

- `/helix-link`：启动或复用 Helix 服务，并将 MCP 接入当前会话
- `/helix-mode`：在已连接 Helix 的会话中选择 `app / api` 工具过滤器
- `/helix-unlink`：从当前会话移除 Helix MCP，不停止本地 Helix 服务
- `/helix-home`：在已连接 Helix 的会话中打开首页
- `/helix-stop`：停止本地 Helix 服务
- `/skills`：打开 Skills 列表，可查看并启用或禁用当前可用 Skill
- `/shutdown`：退出前台并停止本地运行时
- `/quit`、`/q`、`quit`、`exit`：安全退出

`/listen start` 最多等待 30 秒进入 ready；超时会停止本次监听并输出失败状态。
断线期间 Listener 会清除 ready，Mailbox Auto-run 会等待新连接重新 ready 后再继续。

原生 coding 专项用法见 [原生 coding 链路](playbook.nativecoding.md)。

## `/new` 指令
- `/new` 或 `/new <title>`：开始一个新的模型对话，并为后续请求生成新的 `cid / sid`；提供标题时保存为当前会话标题
- 该指令不会发送给模型，也不会重启本地后台服务
- 当前偏好配置会保留
- 适合在同一个 REPL 里结束上一段上下文、开启独立问题时使用

## `/resume` 指令
- `/resume`：打开最近 24 小时内的本地会话游标列表，并把当前会话恢复到选中的 `cid / sid`
- 恢复列表按工作区和会话来源筛选
- 本地只保存恢复所需的 `cid / sid`、标题、工作区和过期时间；完整对话内容仍以服务端历史为准
- 菜单中使用 `↑/↓` 滚动，`PgUp/PgDn` 跳转，`Enter` 选择，`q` 取消
- 适合重启 REPL 后接回某一段对话；如果要开启新上下文，继续使用 `/new`

## `/archive` 与 `/fork` 指令
- `/archive`：归档当前会话。确认后会写入归档状态并退出前台；没有已建立的会话时会提示失败。
- `/fork`：请求服务端复制当前对话上下文，成功后切换到新的 `cid / sid`；当前输入和已保存的配置不会被清空。
- 在 Resume picker 中归档其他会话不需要退出；当前会话必须回到 REPL 使用 `/archive`。

## `/provider`、`/model` 与 `/preferences`
- `/provider`：打开二级选单，动态加载本地 `config.toml` 中的 Provider Profile
- Provider 选择写入本地 `config.toml` 的顶层 `model_provider`
- `/model <model-id>`：更新当前 Provider Profile 的模型 ID
- 模型写入目标是 `model_providers.<profile-id>.model`
- 写入成功后会刷新当前进程中的偏好缓存；REPL 每轮请求前也会重新读取配置，所以下一轮模型请求会使用新模型
- 正在进行中的一轮不会中途切换模型；需要等下一轮输入
- `/preferences`：打开本地配置页面，通过短卡片和编辑弹窗维护多个 Provider Profile

`config.toml` 使用独立 Profile 配置：

```toml
model_provider = "openai-main"

[model_providers.openai-main]
name = "openai-main"
kind = "openai"
model = "gpt-5.2"
route = "responses"
reasoning_effort = "high"
api_key = "..."
base_url = ""
```

## `/effort`
- `/effort`：打开二级菜单设置推理强度，可选 `low / medium / high / xhigh`
- 写入目标是当前 `model_providers.<profile-id>.reasoning_effort`
- 写入成功后会刷新当前进程中的偏好缓存；REPL 每轮请求前也会重新读取配置，所以下一轮模型请求会使用新的推理强度
- 当前正在进行中的一轮不会中途切换推理强度；需要等下一轮输入

## `/permissions`
- `/permissions`：打开权限预设菜单，在 `Read Only`、`Auto`、`Full Access` 间切换。
- 预设分别对应 `read-only + on-request`、`workspace-write + on-request`、
  `danger-full-access + never`；选择结果同时更新当前会话的执行上下文。

## `/hooks`、`/agent` 与 `/skills`
- `/hooks`：打开生命周期 Hook 管理界面，可查看发现结果、审核当前内容、切换启用状态。
  Hook 的来源、信任摘要和事件边界见 [Hooks 配置](hooks.md)。
- `/agent`：打开当前根会话的子 Agent 列表。选中线程后可查看快照、打断运行中的线程、
  恢复已关闭线程，或关闭线程及其后代。
- `/skills`：打开 Skills 菜单。可以先查看本地 Skills，再把选中的 Skill token 写入输入框。

## `/listen` 与 `/mailbox`
- `/listen`：打开监听器菜单；`/listen start` 启动并等待 ready，`/listen stop` 停止传输，
  `/listen status` 只显示连接状态和待处理消息数。
- `/listen start` 最多等待 30 秒进入 ready；超时会停止本次监听并输出失败状态。
- `/mailbox`：打开远端请求收件箱。每条消息可选择立即运行、删除或查看详情；摘要菜单还可以切换当前会话的 Auto-run。
- 断线期间 Listener 会清除 ready，Mailbox Auto-run 会等待新连接重新 ready 后再继续。

## `/queue`
- `/queue` 或 `/queue list`：显示服务端权威队列顺序，以及本地仍待确认或待恢复观察的项目。
- `/queue add <message>`：把消息和当前待发送附件加入持久队列；使用该命令前必须先建立当前对话。
- `/queue retry <id>`：使用原请求标识重试一项结果未知的 Queue add，不创建新的队列项目。
- `/queue delete <id>`：删除一项远端队列项目；`id` 可以使用列表中可唯一匹配的前缀。
- `/queue move <id> <position>`：把项目移动到以 `1` 开始的目标位置。
- `/queue start [id]`：显式启动指定项目；省略 `id` 时优先接回已启动或启动结果未知的项目，否则启动队首。
- `start` 不能在另一个 Turn 活动期间执行；冷启动发现已启动但尚未完成观察的项目时，会继续恢复该 Turn。

## `/copy`
- `/copy`：复制最近一次成功完成的 assistant 输出原文到系统剪贴板
- 一轮中如果先输出 assistant 文本、再调用工具、再继续输出 assistant 文本，复制内容只取最后一次 assistant 输出
- 复制内容是模型返回的 Markdown 原文，不包含终端颜色、打字机动画、工具输出、Sources footer 或耗时 footer
- 如果还没有可复制回复，会提示没有 assistant message
- 该指令不会发送给模型，也不会修改对话上下文

## Helix 指令
- `/helix-link`：检查或下载 runtime asset，启动或复用 Helix 服务，并以默认 `app` 过滤器接入当前会话
- `/helix-mode`：仅在 Helix 已连接时选择 `app / api` 工具过滤器，不启动或接入服务
- `/helix-unlink`：只从当前会话移除 Helix MCP，不停止本地 Helix 服务；需要时可再次使用 `/helix-link` 接入
- `/helix-home`：仅在 Helix 已连接时打开首页，不启动或接入服务
- `/helix-stop`：停止 Helix 服务；Mind native tools 和已连接 external MCP tools 仍可用
- `/helix-mode` 或 `/helix-home` 发现 runtime asset 缺失时会先显示确认菜单；确认后只下载，完成后需要重新打开应用，取消后不下载
- runtime asset 已存在但 Helix 未连接时，`/helix-mode` 和 `/helix-home` 会直接提示未连接
- 接入失败时保留当前会话和已有工具目录
- 这些指令是本地控制命令，不会发送给模型，也不会作为 MCP 工具调用

## `/shutdown`
- `/shutdown`：退出前台 Mind，并停止本地运行时
- 该指令会在退出清理阶段释放本地运行时监听端口
- 普通 `/quit`、`/q`、`quit`、`exit` 和 `Ctrl+C` 仍只退出前台，不主动停止本地运行时

## `/compact`
- `/compact`：请求压缩当前对话上下文，成功后后续请求会基于压缩后的历史继续
- 该指令不会发送给模型；它会调用对话压缩接口，并在完成时展示压缩前后的 item 数
- 适合长会话、工具调用较多或上下文体积变大后继续留在同一段会话里使用

## `/tools`
- `/tools`：列出当前 REPL 模式下可见的 MCP 工具
- Helix 未启动时，仍会显示 Mind native coding tools 和已连接 external MCP tools
- Helix 启动后，会追加 Helix MCP tools
- 该指令只做诊断，不会调用任何工具，也不会发送给模型

## `/ps` 与 `/stop`
- `/ps`：打开后台终端列表，查看正在运行的命令及其输出。
- `/stop`：停止全部后台终端；不会退出当前会话，也不会停止本地 Mind runtime。

## `/diff`
- `/diff`：异步计算当前工作目录的 Git 工作区差异，并在全屏 `D I F F` pager 中展示
- 包含未 staged 的 tracked 修改和未跟踪且未被忽略的文件；不包含 staged-only 修改
- 不调用模型；Git helper、hook、filter、textconv 和 external diff 会按受控命令策略隔离
- 空 diff 在 pager 中显示 `No changes detected.`；非 Git 目录和 Git 执行失败分别展示明确状态
- 退出 pager 后恢复原输入和主 TUI；当前轮 `apply_patch` 的精确净差异仍由内部 tracker 独立维护

## `/mcp`
- `/mcp`：管理外部 MCP 服务
- `start    enabled servers`：启动配置文件里 `enabled=true` 的外接 MCP 服务；如果当前已启动，则保持当前连接。
- `force    all configured servers once`：本轮临时启动所有已配置的外接 MCP 服务，包括 `enabled=false` 的。不会修改配置文件，下次启动仍按配置来。
- `stop     all external MCP connections`：断开当前所有外接 MCP 连接。HTTP/SSE 只是断开连接；stdio 类型会随连接释放关闭对应子进程。
- `restart  enabled servers`：先断开当前外接 MCP，再重新读取配置并启动 `enabled=true` 的服务。
- `status   show current external MCP status`：只查看状态，不启动、不停止。显示 configured、started、tools，以及已连接工具分组。

## 退出
任意时刻输入以下任一指令即可退出：
```text
/quit
/q
quit
exit
```

## 输入约束
- REPL 当前支持单行和多行输入
- 多行输入适合临时探索、长提示和分段目标描述
- 重复任务应固定输入与验收条件，并由外部脚本或调度系统发起独立请求
