# 交互模式

入口页只负责交互入口；REPL 指令、状态切换和输入约束继续看这里。
重点是讲清进入 REPL 之后能做什么、怎么切状态、哪些输入适合留在交互模式里。
`--agent` 不属于 REPL 状态；它是独立的订阅模式，另见 `订阅模式`。

## 先判断是不是这页的范围

- 你要连续试多个目标，并在同一会话里来回切 `chat / fast / plan / xtra`：看这里
- 你要查 `/help /new /resume /model /apikey /base-url /attach /reboot /shutdown /pref /tools /mcp /quit` 这些 REPL 指令，或用 `!` 临时进入本地 shell：看这里
- 你要理解 `--agent` 的订阅链路：这页不展开，直接看 `订阅模式`
- 你要理解单次命令行入口和 `--code` 批跑，不要先从交互模式文档开始
- 你只是偶尔跑一条命令，不一定需要先读这页

## 怎么读这页

- 先看“启动与提示”和“四种状态”，建立 REPL 的基本运行心智
- 再看指令索引，确认切换状态、更新模型和退出的方式
- 最后看输入约束，判断什么时候继续留在 REPL，什么时候该切回 `--code`

## 启动与提示
`mind` 进入循环后，会持续读取用户输入，并在 `CHAT / FAST / PLAN / XTRA` 四种互斥状态之间切换执行。

- 顶部 banner 会随模式变化：`Chat / Fast / Plan / Xtra`
- 每轮输入提示：`ready 输入目标或 /help`
- `mind_loop()` 会为一次会话生成 `cid / sid`，用于链路追踪与调用元数据

一句话理解：

- REPL 是连续交互入口
- 真正决定执行行为的是 `CHAT / FAST / PLAN / XTRA` 四种状态

## 指令索引
- `/help, /h`：指令索引
- `/license, /lic`：授权许可信息
- `/new`：开始新对话，重置 `cid / sid`，保留当前模式、模型和待发送附件
- `/resume`：从最近 24 小时内的本地会话游标中恢复当前模式的对话
- `/quit, /q, quit, exit`：安全退出
- `/model <name>`：持久化主模型名称
- `/apikey <key>`：持久化主模型访问凭证
- `/base-url <url>`：持久化主模型 Base URL
- `/attach <path|dir|glob>`：添加本轮待发送附件
- `/attachments`：查看当前待发送附件
- `/detach <index|path>`：移除一个待发送附件
- `/attach-clear`：清空当前待发送附件
- `/reboot`：重启本地后台服务
- `/shutdown`：退出前台并停止本地运行时
- `/pref`：打开偏好配置页
- `/tools`：查看当前可用 MCP 工具，包含外部 MCP 工具
- `/mcp`：查看外部 MCP runtime 状态
- `!`：进入本地 shell，输入 `exit` 回到 Mind REPL
- `! <cmd>`：执行一条本地 shell 命令后回到 Mind REPL
- `/chat`：切到 `CHAT`
- `/fast`：切到 `FAST`
- `/plan`：切到 `PLAN`
- `/xtra`：切到 `XTRA`

外接模式入口继续看：

- `/xtra` 配合 [Playwright 外接工具实战](playbook.playwright.md)
- `/xtra` 配合 [DBHub 外接工具实战](playbook.dbhub.md)
- `/xtra` 配合 [原生 coding 链路](playbook.nativecoding.md)

## 四种状态
| 状态     | 说明                                       | 适合场景            |
|--------|------------------------------------------|-----------------|
| `CHAT` | 对话驱动的流式工具闭环                              | 探索、问答、临场协作      |
| `FAST` | 裁剪工具集后的快速执行通道                            | 接口、文本、媒体短链路     |
| `PLAN` | 先生成计划，再按步骤顺序执行，并承载执行期规则判断 | 需要结构化步骤和更稳路径的任务 |
| `XTRA` | 外接 MCP 工具、Helix 通用工具与编码工具协作通道 | 数据库、浏览器、外部服务、原生 coding |

如果你在 `XTRA` 状态下要继续看专项用法，直接跳：

- [Playwright 外接工具实战](playbook.playwright.md)
- [DBHub 外接工具实战](playbook.dbhub.md)
- [原生 coding 链路](playbook.nativecoding.md)

补充：
- 执行期规则判断只属于 `PLAN` 执行面
- `--code` 中的 `global_rule / rule` 是星图规则层，不等同于执行期规则判断
- `XTRA` 会读取外接服务配置；外接服务需提前可访问，外接失败只进入 debug 日志
- `XTRA` 同时可调用原生 coding 工具，适合把外部服务排查与代码修改放在同一轮协作里

切换成功后，终端会输出：
- `Exchange -> Chat`
- `Exchange -> Fast`
- `Exchange -> Plan`
- `Exchange -> Xtra`

## `/model` 指令
示例：
```text
/model gpt-4o-mini
```

当输入无效或缺失时，会打印候选列表并提示：
```text
model invalid: /model <...>
```

保存成功后，本轮循环后续调用都会使用新的 `model`，并写入本地偏好存储。

## `/new` 指令
- `/new`：开始一个新的模型对话，并为后续请求生成新的 `cid / sid`
- 该指令不会发送给模型，也不会重启本地后台服务
- 当前 `CHAT / FAST / PLAN / XTRA` 状态、模型配置、API key 和待发送附件都会保留
- 适合在同一个 REPL 里结束上一段上下文、开启独立问题时使用

## `/resume` 指令
- `/resume`：打开最近 24 小时内的本地会话游标列表，并把当前会话恢复到选中的 `cid / sid`
- 恢复列表会按当前模式过滤；例如当前是 `XTRA`，只展示 `xtra` 的历史游标
- 本地只保存恢复所需的 `cid / sid`、标题、模式、工作区和过期时间；完整对话内容仍以服务端历史为准
- 菜单中使用 `↑/↓` 滚动，`PgUp/PgDn` 跳转，`Enter` 选择，`q` 取消
- 适合重启 REPL 后接回某一段对话；如果要开启新上下文，继续使用 `/new`

## `/apikey` 指令
当输入无效或缺失时，会打印格式提示，例如：
- `sk-...`
- `gsk_...`
- `ds-...`
- `<token>`

并输出：
```text
apikey invalid: /apikey <...>
```

保存成功后，本轮循环后续调用都会使用新的 `apikey`，并写入本地偏好存储。终端只回显密钥尾部。

## `/base-url` 指令
示例：
```text
/base-url https://api.example.com/v1
```

当输入无效或缺失时，会打印格式提示：
```text
base-url invalid: /base-url <...>
```

保存成功后，本轮循环后续调用都会使用新的 `base_url`，并写入本地偏好存储。

## 附件指令
- `/attach <path|dir|glob>`：把本地文件加入当前待发送附件列表
- `/attachments`：查看当前已挂载但尚未发送的附件
- `/detach <index|path>`：按序号或路径移除单个附件
- `/attach-clear`：清空当前待发送附件

约定：
- 当前允许挂载任意普通文件；图片会保留 `image` 分类，其它文件按 `file` 处理
- 目录会批量挂载当前层文件；递归请使用通配符，例如 `./docs/**/*.md`
- `CHAT / FAST / XTRA` 会在发送前自动上传附件
- `PLAN` 当前不支持附件；如有待发送附件，需要先切回 `CHAT / FAST / XTRA` 或清空
- 一轮消息发送后，待发送附件会自动清空，避免串到下一轮

## `/license`
- `/license` 或 `/lic`：展示授权许可信息页

## `/reboot`
- `/reboot`：重启本地后台服务，并在恢复可用后继续停留在 REPL
- 该指令是本地控制命令，不会发送给模型，也不会作为 MCP 工具调用
- 适合本地后台服务长时间运行后不可用、连接异常或需要主动恢复执行面时使用

## `/shutdown`
- `/shutdown`：退出前台 Mind，并停止本地运行时
- 该指令会在退出清理阶段释放本地运行时监听端口
- 普通 `/quit`、`/q`、`quit`、`exit` 和 `Ctrl+C` 仍只退出前台，不主动停止本地运行时

## `/pref`
- `/pref`：打开偏好配置页
- 该指令不会发送给模型
- 页面保存后，REPL 后续轮次会按偏好刷新 TTL 读取最新配置

## `/tools`
- `/tools`：列出当前 REPL 模式下可见的 MCP 工具
- 输出会按外部 MCP 服务或本地 `domain/class` 分组
- 外部 MCP 工具会优先显示，并标出服务别名和 transport
- 该指令只做诊断，不会调用任何工具，也不会发送给模型

## `/mcp`
- `/mcp`：查看外部 MCP runtime 状态
- 输出包含已解析的外部 MCP server 配置、当前 runtime 是否启动、已连接外部工具数量
- 该指令只看外部 MCP 生命周期状态，不建立新的模型会话

## Shell escape
- `!`：拉起当前平台默认 shell。Windows 优先 `pwsh` / `powershell`，类 Unix 优先 `$SHELL`，缺省回退到 `bash` / `sh`。
- `! <cmd>`：用默认 shell 执行一条命令，命令结束后自动回到 REPL。
- 子 shell 内输入 `exit` 返回 Mind REPL。
- 该能力是本地 REPL 快捷入口，不会发送给模型，也不会作为 MCP 工具调用。

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
