# 交互模式

入口页只负责交互入口；REPL 指令、状态切换和输入约束继续看这里。
重点是讲清进入 REPL 之后能做什么、怎么切状态、哪些输入适合留在交互模式里。
`--agent` 不属于 REPL 状态；它是独立的订阅模式，另见 `订阅模式`。

## 先判断是不是这页的范围

- 你要连续试多个目标，并在同一会话里来回切 `chat / fast / xtra`：看这里
- 你要查 `/chat /fast /xtra /new /resume /attach /detach /permissions /model /effort /preferences /compact /tools /diff /copy /ps /mcp /helix-link /helix-unlink /helix-home /helix-stop /help /license /shutdown /quit` 这些 REPL 指令：看这里
- 你要理解 `--agent` 的订阅链路：这页不展开，直接看 `订阅模式`
- 你要理解单次命令行入口和 `--code` 批跑，不要先从交互模式文档开始
- 你只是偶尔跑一条命令，不一定需要先读这页

## 怎么读这页

- 先看“启动与提示”和“三种状态”，建立 REPL 的基本运行心智
- 再看指令索引，确认切换状态、管理附件、查看工具和退出的方式
- 最后看输入约束，判断什么时候继续留在 REPL，什么时候该切回 `--code`

## 启动与提示
`mind` 进入循环后，会持续读取用户输入，并在 `CHAT / FAST / XTRA` 三种互斥状态之间切换执行。

- 顶部 banner 会随模式变化：`Chat / Fast / Xtra`
- 每轮输入提示：`ready 输入目标或 /help`
- `mind_loop()` 会为一次会话生成 `cid / sid`，用于链路追踪与调用元数据

一句话理解：

- REPL 是连续交互入口
- 真正决定执行行为的是 `CHAT / FAST / XTRA` 三种状态

## 指令索引
- `/chat`：切到 `CHAT`
- `/fast`：切到 `FAST`
- `/xtra`：切到 `XTRA`
- `/new`：开始新对话，重置 `cid / sid`，保留当前模式、模型和待发送附件
- `/resume`：从最近 24 小时内的本地会话游标中恢复当前模式的对话
- `/attach <path|dir|glob>`：添加本轮待发送附件
- `/attachments`：查看当前待发送附件
- `/detach <index|path>`：移除一个待发送附件
- `/attach-clear`：清空当前待发送附件
- `/permissions`：切换权限模式
- `/model <model-id>`：持久化主模型 ID；写入本地 `config.toml`，下一轮模型请求生效
- `/effort`：设置主模型推理强度
- `/preferences`：打开本地 Preferences 页面，用于维护模型、密钥、Base URL 和服务域名配置
- `/compact`：压缩当前对话上下文，减少后续请求携带的历史体积
- `/tools`：查看当前可用 MCP 工具，包含 Mind native、外部 MCP 和已接入 Helix MCP 工具
- `/diff`：查看本轮补丁净差异
- `/copy`：复制最近一次助手回复原文到剪贴板
- `/ps`：查看运行中的命令
- `/mcp`：管理外部 MCP 服务
- `/helix-link`：检查/下载 Helix runtime asset，启动或复用本地 Helix 服务，并接入当前会话
- `/helix-unlink`：从当前会话移除 Helix MCP，不停止本地 Helix 服务
- `/helix-home`：启动或复用本地 Helix 服务，接入当前会话，并打开首页
- `/helix-stop`：停止本地 Helix 服务
- `/help, /h`：指令索引
- `/license, /lic`：授权许可信息
- `/shutdown`：退出前台并停止本地运行时
- `/quit, /q, quit, exit`：安全退出

外接模式入口继续看：

- `/xtra` 配合 [Playwright 外接工具实战](playbook.playwright.md)
- `/xtra` 配合 [DBHub 外接工具实战](playbook.dbhub.md)
- `/xtra` 配合 [原生 coding 链路](playbook.nativecoding.md)

## 四种状态
| 状态     | 说明                                       | 适合场景            |
|--------|------------------------------------------|-----------------|
| `CHAT` | 对话驱动的流式工具闭环                              | 探索、问答、临场协作      |
| `FAST` | 裁剪工具集后的快速执行通道                            | 接口、文本、媒体短链路     |
| `CHAT` | 先生成计划，再按步骤顺序执行 | 需要结构化步骤和更稳路径的任务 |
| `XTRA` | 外接 MCP 工具、Mind native 工具与编码工具协作通道 | 数据库、浏览器、外部服务、原生 coding |

如果你在 `XTRA` 状态下要继续看专项用法，直接跳：

- [Playwright 外接工具实战](playbook.playwright.md)
- [DBHub 外接工具实战](playbook.dbhub.md)
- [原生 coding 链路](playbook.nativecoding.md)

补充：
- `--code` 中的 `global_rule / rule` 是星图文本层，会拼入任务正文，不触发独立执行链路
- `XTRA` 会读取外接服务配置；外接服务需提前可访问，外接失败只进入 debug 日志
- `CHAT / FAST` 依赖 Helix MCP 服务；切换或执行这些状态前需要先用 `/helix-link` 接入 Helix
- `XTRA` 不依赖 Helix，默认只使用 Mind native tools、原生 coding 工具和已连接 external MCP tools
- `XTRA` 同时可调用原生 coding 工具，适合把外部服务排查与代码修改放在同一轮协作里

切换成功后，终端会输出：
- `Exchange -> Chat`
- `Exchange -> Fast`
- `Exchange -> Chat`
- `Exchange -> Xtra`

## `/new` 指令
- `/new`：开始一个新的模型对话，并为后续请求生成新的 `cid / sid`
- 该指令不会发送给模型，也不会重启本地后台服务
- 当前 `CHAT / FAST / XTRA` 状态、偏好配置和待发送附件都会保留
- 适合在同一个 REPL 里结束上一段上下文、开启独立问题时使用

## `/resume` 指令
- `/resume`：打开最近 24 小时内的本地会话游标列表，并把当前会话恢复到选中的 `cid / sid`
- 恢复列表会按当前模式过滤；例如当前是 `XTRA`，只展示 `xtra` 的历史游标
- 本地只保存恢复所需的 `cid / sid`、标题、模式、工作区和过期时间；完整对话内容仍以服务端历史为准
- 菜单中使用 `↑/↓` 滚动，`PgUp/PgDn` 跳转，`Enter` 选择，`q` 取消
- 适合重启 REPL 后接回某一段对话；如果要开启新上下文，继续使用 `/new`

## `/model` 与 `/preferences`
- `/model <model-id>`：只更新主模型 ID，适合临时切换模型后继续留在 REPL 里验证
- 不带模型 ID 时会把主模型 ID 清空
- 写入目标是本地 `config.toml` 的 `[model.primary].model`
- 写入成功后会刷新当前进程中的偏好缓存；REPL 每轮请求前也会重新读取配置，所以下一轮模型请求会使用新模型
- 正在进行中的一轮不会中途切换模型；需要等下一轮输入
- `/preferences`：打开本地配置页面，适合同时维护模型名、API key、Base URL、route 和服务域名

## `/effort`
- `/effort`：打开二级菜单设置推理强度，可选 `low / medium / high / xhigh`
- 写入目标是本地 `config.toml` 的 `[model.primary].reasoning_effort`
- 写入成功后会刷新当前进程中的偏好缓存；REPL 每轮请求前也会重新读取配置，所以下一轮模型请求会使用新的推理强度
- 当前正在进行中的一轮不会中途切换推理强度；需要等下一轮输入

## `/copy`
- `/copy`：复制最近一次 `CHAT / FAST / XTRA` 成功完成的 assistant 输出原文到系统剪贴板
- 一轮中如果先输出 assistant 文本、再调用工具、再继续输出 assistant 文本，复制内容只取最后一次 assistant 输出
- 复制内容是模型返回的 Markdown 原文，不包含终端颜色、打字机动画、工具输出、Sources footer 或耗时 footer
- 如果还没有可复制回复，会提示没有 assistant message
- 该指令不会发送给模型，也不会修改对话上下文

## 附件指令
- `/attach <path|dir|glob>`：把本地文件加入当前待发送附件列表
- `/attachments`：查看当前已挂载但尚未发送的附件
- `/detach <index|path>`：按序号或路径移除单个附件
- `/attach-clear`：清空当前待发送附件

约定：
- 当前允许挂载任意普通文件；图片会保留 `image` 分类，其它文件按 `file` 处理
- 目录会批量挂载当前层文件；递归请使用通配符，例如 `./docs/**/*.md`
- `CHAT / FAST / XTRA` 会在发送前自动上传附件
- `CHAT` 当前不支持附件；如有待发送附件，需要先切回 `CHAT / FAST / XTRA` 或清空
- 一轮消息发送后，待发送附件会自动清空，避免串到下一轮

## `/license`
- `/license` 或 `/lic`：展示授权许可信息页

## Helix 指令
- `/helix-link`：检查/下载 Helix runtime asset，启动或复用本地 Helix 服务，并在后续 `/tools` 或模型请求中挂载 Helix MCP 工具
- `/helix-unlink`：只从当前会话移除 Helix MCP，不停止本地 Helix 服务；需要时可再次用 `/helix-link` 接入
- `/helix-home`：检查/下载 Helix runtime asset，启动或复用本地 Helix 服务，接入当前会话，并打开首页
- `/helix-stop`：停止 Helix 服务；Mind native tools 和已连接 external MCP tools 仍可用
- Helix runtime asset 缺失时会先显示确认菜单，取消后不会下载或启动
- `CHAT / FAST` 需要 Helix 已接入；如果用户取消下载或接入失败，应保持当前状态，不进入这些模式
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
- 需要批跑、重复执行或多任务编排时，优先使用 `--code` 配合 `cfg.repeat / loop`
