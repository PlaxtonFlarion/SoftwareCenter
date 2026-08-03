# 交互模式

入口页只负责交互入口；REPL 指令、会话管理和输入约束继续看这里。
重点是讲清进入 REPL 之后能做什么、怎么管理上下文、哪些输入适合留在交互模式里。
`agent listen` 是独立的订阅入口，另见 `订阅模式`。

## 先判断是不是这页的范围

- 你要连续试多个目标并管理同一会话：看这里
- 你要查 `/new /resume /permissions /model /effort /preferences /compact /tools /diff /copy /ps /mcp /helix-link /helix-mode /helix-unlink /helix-home /helix-stop /shutdown /quit` 这些 REPL 指令：看这里
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
- `/new`：开始新对话，重置 `cid / sid`，保留模型和本地配置
- `/resume`：从最近 24 小时内的本地会话游标中恢复对话
- `/permissions`：在 `Read Only`、`Auto`、`Full Access` 三个权限预设间切换；分别对应 `read-only + on-request`、`workspace-write + on-request`、`danger-full-access + never`
- `/model <model-id>`：持久化主模型 ID；写入本地 `config.toml`，下一轮模型请求生效
- `/effort`：设置主模型推理强度
- `/preferences`：打开本地 Preferences 页面，用于维护模型、密钥、Base URL 和服务域名配置
- `/compact`：压缩当前对话上下文，减少后续请求携带的历史体积
- `/tools`：查看当前可用 MCP 工具，包含 Mind native、外部 MCP 和已接入 Helix MCP 工具
- `/diff`：查看本轮补丁净差异
- `/copy`：复制最近一次助手回复原文到剪贴板
- `/ps`：查看运行中的命令
- `/mcp`：管理外部 MCP 服务
- `/helix-link`：启动或复用 Helix 服务，并将 MCP 接入当前会话
- `/helix-mode`：在已连接 Helix 的会话中选择 `app / api` 工具过滤器
- `/helix-unlink`：从当前会话移除 Helix MCP，不停止本地 Helix 服务
- `/helix-home`：在已连接 Helix 的会话中打开首页
- `/helix-stop`：停止本地 Helix 服务
- `/shutdown`：退出前台并停止本地运行时
- `/quit, /q, quit, exit`：安全退出

原生 coding 专项用法见 [原生 coding 链路](playbook.nativecoding.md)。

## `/new` 指令
- `/new`：开始一个新的模型对话，并为后续请求生成新的 `cid / sid`
- 该指令不会发送给模型，也不会重启本地后台服务
- 当前偏好配置会保留
- 适合在同一个 REPL 里结束上一段上下文、开启独立问题时使用

## `/resume` 指令
- `/resume`：打开最近 24 小时内的本地会话游标列表，并把当前会话恢复到选中的 `cid / sid`
- 恢复列表按工作区和会话来源筛选
- 本地只保存恢复所需的 `cid / sid`、标题、工作区和过期时间；完整对话内容仍以服务端历史为准
- 菜单中使用 `↑/↓` 滚动，`PgUp/PgDn` 跳转，`Enter` 选择，`q` 取消
- 适合重启 REPL 后接回某一段对话；如果要开启新上下文，继续使用 `/new`

## `/model` 与 `/preferences`
- `/model <model-id>`：只更新主模型 ID，适合临时切换模型后继续留在 REPL 里验证
- 不带模型 ID 时会把主模型 ID 清空
- 写入目标是本地 `config.toml` 的顶层 `model`
- 写入成功后会刷新当前进程中的偏好缓存；REPL 每轮请求前也会重新读取配置，所以下一轮模型请求会使用新模型
- 正在进行中的一轮不会中途切换模型；需要等下一轮输入
- `/preferences`：打开本地配置页面，适合同时维护模型名、API key、Base URL、route 和服务域名

## `/effort`
- `/effort`：打开二级菜单设置推理强度，可选 `low / medium / high / xhigh`
- 写入目标是本地 `config.toml` 的顶层 `model_reasoning_effort`
- 写入成功后会刷新当前进程中的偏好缓存；REPL 每轮请求前也会重新读取配置，所以下一轮模型请求会使用新的推理强度
- 当前正在进行中的一轮不会中途切换推理强度；需要等下一轮输入

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

## `/diff`
- `/diff`：展示当前轮 `apply_patch` 累积后的净 unified diff
- 该指令只读取 Mind native coding 记录的精确 delta，不调用模型，也不主动运行 `git diff`
- 如果当前轮没有成功的 `apply_patch`，会提示没有可展示的 diff；超长内容会按展示上限截断

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
