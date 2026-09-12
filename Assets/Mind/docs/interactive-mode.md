# 交互模式

> 权威参考：本页维护全部 REPL slash 命令、参数和行为。README 与官网入口页只保留摘要和跳转链接。

入口页只负责交互入口；REPL 指令、会话管理和输入约束继续看这里。
重点是讲清进入 REPL 之后能做什么、怎么管理上下文、哪些输入适合留在交互模式里。
`agent listen` 会在普通 TUI 中启动远端请求监听器，另见 `订阅模式`。

## 先判断是不是这页的范围

- 你要连续试多个目标并管理同一会话：看这里
- 你要查 `/new /resume /archive /fork /permissions /model /provider /effort /preferences /compact /tools /hooks /review /agent /listen /mailbox /diff /copy /export /raw /ps /stop /mcp /helix-link /helix-mode /helix-unlink /helix-home /helix-stop /skills /shutdown /quit` 这些 REPL 指令：看这里
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

### 上下文余量

Turn 运行中且输入框有待排队草稿时，底部左侧显示 `tab to queue message`，右侧显示淡色的
`N% context left`，表示最近一次实际执行模型的上下文余量。空输入、空闲状态和 Turn 结束后
恢复普通状态栏，不显示右侧用量；快照仍保存在会话中。
它采用服务端返回的有效窗口和最近用量，包含 12,000 token 的显示基线，因此是上下文预算
提示，不能作为精确计费数字。工具循环中每份已提交的用量事件都可以更新快照；
成功压缩后使用服务端重算值，失败时保留原值。

新会话空闲时不显示默认 100%；恢复期间或没有可靠数据时隐藏。窗口未知但累计用量可靠时显示
如 `250K used`。切换会话读取目标会话缓存并恢复服务端保留快照，读取失败时隐藏用量，
分支不沿用源会话最新占用；切换模型配置后，
下一份快照到达前仍保留最近实际执行模型的值。右侧统一保留两个终端字符位，百分比位数变化
不移动右边缘或排队提示；窄窗口先缩短排队提示，再隐藏用量，排队操作提示优先。该显示需要服务端交付
[`context.usage.updated`](context-usage-protocol.md)，旧服务端缺少事件时不会由客户端估算补齐。

### 完整记录与按键配置

`Ctrl+T` 打开完整会话记录。按键可以在用户 `config.toml` 或 Profile 中覆盖，
配置在下次启动时生效：

```toml
[tui]
raw_output_mode = false
scrollback_reflow_line_limit = 10000

[tui.keymap.global]
open_transcript = "f12"
toggle_raw_output = "alt-r"

[tui.keymap.chat]
interrupt_turn = "esc"
edit_queued_message = ["alt-up", "shift-left"]

[tui.keymap.composer]
submit = "enter"
queue = "tab"
toggle_shortcuts = "?"

[tui.keymap.editor]
insert_newline = ["ctrl-j", "alt-enter"]
move_word_left = ["alt-b", "ctrl-left"]

[tui.keymap.pager]
scroll_down = ["down", "n"]
page_down = ["page-down", "space"]
close = ["q", "ctrl-c"]

[tui.keymap.list]
accept = "enter"
cancel = "esc"

[tui.keymap.approval]
accept_once = "y"
decline = ["esc", "n"]
```

可配置上下文为 `global`、`chat`、`composer`、`editor`、`pager`、`list` 和
`approval`。`?` 打开的只读 Keyboard shortcuts 页面显示当前进程实际使用的完整映射；
运行时映射是启动快照，修改用户配置或 Profile 后在下一次启动生效。

值可以是单个按键字符串或字符串数组；数组中的项目是同一动作的替代键，空数组表示显式解绑。
两键 chord 写在同一个字符串中，例如 `"ctrl-x ctrl-t"`；等待窗口为 1 秒，期间按 `Esc`
取消。支持组合修饰键、`f1` 到 `f24`，以及方向键、Home/End、PageUp/PageDown 等命名键。
上下文配置优先于合法的 `global` 回退，之后才使用内置默认值；Profile 按动作合并，显式空数组
不会被用户层默认值补回。

启动校验会拒绝同一或重叠上下文中的重复绑定、chord 前缀遮蔽、固定取消/退出键覆盖、
可能成为 AltGr 文本输入的 `Ctrl+Alt+字符`，以及会吞掉普通输入的 printable key。
TUI 在 raw mode 生命周期内按 Codex 的策略启用增强键盘协议，使 `Ctrl+M/Enter`、
`Ctrl+I/Tab`、`Ctrl+H/Backspace`、Shift 修饰键和 chord 第二键的 Alt 修饰保持独立；
退出或临时进入 cooked mode 时会成对恢复终端状态。iTerm2、Ghostty 和 tmux xterm 使用不报告
Release 的兼容模式，tmux csi-u 同时启用 modifyOtherKeys 2；WSL 的 VS Code 终端默认禁用，
可用 `MIND_TUI_DISABLE_KEYBOARD_ENHANCEMENT=false` 显式覆盖。其他不支持增强协议的终端继续
使用可区分的旧式按键，增强协议专属别名不会错误触发其他动作。
菜单、审批、排队提示、footer 和帮助页均从同一运行时映射生成快捷键标签。

各上下文可配置的动作名如下：

- `global`：`open_transcript`、`copy_last_response`、`toggle_raw_output`、`clear_terminal`、
  `transcript_page_up`、`transcript_page_down`，以及供 `composer` 使用的
  `submit`、`queue`、`toggle_shortcuts` 回退。
- `chat`：`interrupt_turn`、`edit_queued_message`。
- `composer`：`submit`、`queue`、`enter_shell_mode`、`previous_completion`、
  `toggle_shortcuts`、`history_search_previous`、`history_search_next`。
- `editor`：`delete_line`、`delete_backward`、`delete_forward`、
  `delete_word_backward`、四向移动、`insert_newline`、
  行首/行尾、单词左右移动、`delete_word_forward`、`delete_to_line_end`、`yank`。
- `pager`：上下滚动、整页/半页滚动、首尾跳转与关闭动作。
- `list`：确认、toggle、alternate、上下/左右/翻页/首尾移动、查询删除与取消动作。
- `approval`：详情展开、当前项确认、上下移动及各类正式审批 decision 动作。

`Ctrl+C`、`Ctrl+D`、补全取消、Shell 模式取消和菜单中断等安全生命周期入口固定，不提供
配置字段；它们仍显示在只读快捷键页中。

Ctrl+Z 不属于可配置编辑动作：Unix 上由终端 adapter 在 UI 分派前接管，挂起当前进程组并在
`fg` 后恢复 raw mode 与画面；不支持 POSIX job control 的平台会消费该按键而不修改草稿。

空草稿首次按 `Ctrl+C` 会开启两秒退出确认；只有紧接着再次按 `Ctrl+C` 才退出。任意其他
按键、提交动作或确认超时都会撤销该状态。

`scrollback_reflow_line_limit` 限制终端尺寸变化时从稳定记录中重新输出的逻辑行数，
默认是 `10000`，值必须是正整数。项目级配置不能覆盖 TUI 配置。
`raw_output_mode` 决定启动时主 transcript 使用 rich 还是 raw 投影；默认关闭。主界面按
`Alt+R` 可临时切换且不插入提示，`/raw [on|off]` 会切换并显示结果。完整记录页只负责阅读和
历史回溯，不维护第二套 raw、搜索或导出状态。

空输入时连续按两次 `Esc` 可以直接选择最近的用户消息；在完整记录中使用
`Esc/Left` 向前选择、`Right` 向后选择，按 `Enter` 从选中消息前创建分支并恢复输入。
主输入框使用 `Ctrl+J`、`Ctrl+M`、`Shift+Enter` 或 `Alt+Enter` 插入换行；
`Ctrl+O` 直接复制最近一次完整 assistant 回复，不修改当前草稿。

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
- `/review [instructions]`：审查当前 Git 工作区、相对基础分支的改动或指定提交
- `/agent`：查看和管理当前会话的子 Agent 线程
- `/listen [start|stop|status]`：管理远端请求监听器；省略动作时打开操作菜单
- `/mailbox`：查看远端请求摘要，运行、删除、展开消息或切换当前会话的 Auto-run
- `/diff`：查看当前 Git 工作区差异（包含未跟踪且未被忽略的文件）
- `/copy`：从最近一次助手回复中选择整体、围栏代码或引用并复制
- `/export [path]`：把完整本地会话记录导出为 Markdown；省略路径时选择复制到剪贴板或编辑文件名，已存在文件不会被覆盖
- `/raw [on|off]`：切换主 transcript 的 raw/rich 投影；省略参数时反转当前模式
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
model_context_window = 128000
model_auto_compact_token_limit = 90000
api_key = "..."
base_url = ""
```

`model_context_window` 和 `model_auto_compact_token_limit` 的单位是 token；上面的数字是配置示例，
应按实际模型与接入服务的容量填写，也可在 `/preferences` 的 Provider 编辑页设置。配置随每次
聊天、Review、队列任务和手动压缩请求发送；已提交 Turn 使用提交时解析的窗口和阈值。

窗口留空时，服务端只能使用同一 Provider、模型和 Base URL 的已配置容量；没有匹配容量时
请求会报错，需补填窗口。服务端已知容量会限制客户端声明的窗口。阈值留空时优先使用匹配模型
的服务端阈值，否则取有效窗口的 90% 与扣除最大输出预算后的输入容量中较小值；显式阈值超过
可用输入容量会被拒绝。自动压缩由服务端根据当前请求的 token 预算执行，固定轮数和条目数
不再触发压缩。

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

输入 `$` 后，按 `Enter` 或 `Tab` 把选中的 Skill 写入草稿，这一步不会发送消息。
已选 Skill 按整体编辑：左右键跨过整个 token，退格先删除末尾空格，再次退格删除包含 `$`
的整个 Skill；`Delete` 从 token 前方整体删除。手工输入但尚未确认的查询仍可逐字编辑。
删除后重新输入 `$` 可以再次选择 Skill；草稿中的多个已选 Skill 各自保持独立范围。

## `/review`
- 裸 `/review` 打开 `Select a review preset` 菜单，可选择相对基础分支、未提交改动、指定提交或自定义审查指令。
- 基础分支和提交使用可搜索子菜单；`Esc` 返回上一级，选择成功后关闭整组 Review 菜单。
- `/review <instructions>` 直接使用去除首尾空白后的自定义指令，不打开预设菜单；自定义菜单支持多行输入，空白内容不会提交。
- 目标选定后会先冻结 Git 目标和工作区快照，再持久化本地 Review Command；快照无效、目标消失、内容超限或缺少必要代码上下文时不会创建远端 Turn。
- Review 运行期间普通输入属于下一轮，不作为 steer 注入审查；中断后仍等待服务端 `turn.completed` 权威终态。
- 进程恢复只 attach/replay 已登记的 Review；若退出发生在首次网络操作前，则以原请求身份和冻结快照安全重派。

## `/listen` 与 `/mailbox`
- `/listen`：打开监听器菜单；`/listen start` 启动并等待 ready，`/listen stop` 停止传输，
  `/listen status` 只显示连接状态和待处理消息数。
- `/listen start` 最多等待 30 秒进入 ready；超时会停止本次监听并输出失败状态。
- `/mailbox`：打开远端请求收件箱。每条消息可选择立即运行、删除或查看详情；摘要菜单还可以切换当前会话的 Auto-run。
- 断线期间 Listener 会清除 ready，Mailbox Auto-run 会等待新连接重新 ready 后再继续。

## `/copy`
- `/copy`：打开复制选择器；第一项为整体回复，其后按源码顺序列出围栏代码和顶层引用
- `Ctrl+O`：不打开选择器，直接复制整体回复；换行键与 Codex 一致，为
  `Ctrl+J`、`Ctrl+M`、`Shift+Enter` 和 `Alt+Enter`
- 一轮中如果先输出 assistant 文本、再调用工具、再继续输出 assistant 文本，复制内容只取最后一次 assistant 输出
- commentary 和 Thinking 不成为复制快照；只有已完成的 `final_answer` 或未声明 phase
  的兼容文本 Item 会替换最近回复，恢复会话后从 Transcript 重建同一快照
- 代码块和引用保留可复制 Markdown 源内容；整体回复按 Codex 的可见 Markdown
  规则统一换行并移除行尾空白，不包含终端颜色、工具输出、Sources footer 或耗时 footer
- 流式期间打开选择器会冻结当时的回复快照；选择器关闭前，后续输入继续留在输入屏障后
- 如果还没有可复制回复，会提示 `No agent response to copy`
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
- 手动压缩按 `context.compaction.started/completed/failed` 确认进度和结果；接口不返回摘要正文。连接结束但未收到终态时不会显示成功，也不会自动重提压缩请求。
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

`/mcp` 打开服务列表，选择服务后进入 `start / force / stop / restart / status` 五动作菜单，默认选中 `status`。
二级菜单按 Esc 返回并保留原服务和滚动位置；确认动作后关闭菜单组，结果提交到正文。
空配置只显示关闭提示；配置损坏时仍列出已持有的连接，允许查看状态和停止。

直接输入 `/mcp <action>` 作用于全部服务。菜单只选择单个服务，没有 `All servers` 行；即使配置键叫 `all`，也仍是单服务目标。
未知动作和额外参数（例如 `/mcp stop extra`）在本地报错，不执行操作或发送给模型。

| 动作 | 行为 |
|------|------|
| `start` | 补启动目标中 `enabled=true` 且尚未连接的服务，保留已有连接，包括临时启动的禁用服务。 |
| `force` | 补启动目标中所有尚未连接的配置服务，包括 `enabled=false` 的；不重启已有连接、不修改配置。 |
| `stop` | 断开目标连接。HTTP/SSE 远端服务继续运行；stdio 随连接释放关闭对应子进程。 |
| `restart` | 校验完整配置后断开目标，仅重建其中 `enabled=true` 的服务；配置错误不拆除已有连接。 |
| `status` | 只读本地快照，分别显示连接状态、配置启用状态、传输、工具及过滤数，不进行网络探测。 |

状态输出沿用命令行、`🔌 MCP Tools` 标题和服务/字段圆点缩进；配置 enabled 显示绿色、disabled 显示红色，连接状态独立列出。
菜单中的编号前缀保持正常亮度，选中项保留强调色与粗体；长状态和工具名随窗口宽度换行。
操作结果沿用共享的树形缩进：正常详情使用正文色，busy 使用提示色，失败使用红色；批量结果按各服务的操作结论分别着色。

临时启用的禁用服务显示 `disabled (temporary connection)`；连接停止、重建、切换工作区或退出时结束临时启用。
配置删除但连接仍持有时显示 `removed from config`，仍可停止或查看；重新启动需要恢复配置。

连接成功不要求服务一定提供工具：未声明 tools 能力、返回空目录或全部工具被过滤，都可以保持有效连接。
工具发现失败或已观察到的传输断线会撤下对应服务的工具，不再把失败当作零工具成功；外部工具调用不会因此自动重放。

根 Turn、子代理、Subscription、Review 和 MCP Hook 在整个工具使用范围内持有连接引用。
被占用时，交互 stop/restart 显示带目标范围的 `busy`；全量动作在拆除任何连接前检查全部目标。
补启动可以与已有使用范围并存，新服务的工具只进入后续目录。退出和工作区切换会等待既有使用范围释放资源。
新增 required 服务启动失败时，仅回收本批新建连接；全量 restart 已明确拆除旧连接，其重建批次失败不会恢复旧连接。
启动进度继续使用既有活动展示，进行态与最终结果带上服务名或 `all services`，每次操作只提交一个最终结果块。
只有完成批次判定的连接才向后续消费者发布工具。活动轮次中可执行全量 start/force 和只读 status；裸菜单、stop/restart 等轮次结束后执行。

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
