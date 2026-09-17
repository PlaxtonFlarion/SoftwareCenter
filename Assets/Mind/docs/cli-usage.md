# 命令行使用参考

> 权威参考：本页维护全部 CLI 命令、选项和组合规则。README 与官网入口页只保留摘要和跳转链接。

这份文档说明当前 CLI 的入口、选项组合和参数边界。交互模式中的 `/` 指令见[交互模式](interactive-mode.md)。

## 基本结构

```text
mind [OPTIONS] [PROMPT]
mind [OPTIONS] <COMMAND> [ARGS]
```

- 不带子命令时进入交互模式，可附带一条初始提示词。
- 单次非交互任务使用 `mind exec`，也可以使用短别名 `mind e`。
- 使用 `mind <command> --help` 查看某个命令的实时参数；例如 `mind exec --help`。
- 使用 `mind help <command...>` 也可以查看多级命令帮助；例如 `mind help mcp add`。

当前命令如下：

| 命令 | 用途 |
|------|------|
| `mind` | 进入交互模式 |
| `mind exec` / `mind e` | 执行一次非交互任务 |
| `mind resume` | 恢复已有交互会话 |
| `mind archive` | 按会话 ID 或标题归档会话 |
| `mind unarchive` | 按会话 ID 或标题恢复归档会话 |
| `mind agent` | 远端任务订阅命令组（当前子命令为 `listen`） |
| `mind agent listen` | 监听远端下发任务 |
| `mind upgrade` | 运行组件升级命令组（当前子命令为 `helix`） |
| `mind upgrade helix` | 下载或更新 Helix 运行组件 |
| `mind doctor` | 只读诊断本地运行环境 |
| `mind mcp` | 外部 MCP 服务命令组 |
| `mind mcp list/get/add/remove/enable/disable/login/logout/help` | 管理外部 MCP 服务注册与本地 OAuth 凭据 |
| `mind mcp-server` | 通过 stdio 暴露 MCP 服务 |
| `mind completion` | 生成 shell 补全脚本 |
| `mind help [COMMAND...]` | 查看根命令或多级子命令帮助 |

## 进程级选项

配置、沙箱和审批选项都是进程级选项，可以写在子命令之前或之后：

```powershell
mind -p work exec "检查当前项目"
mind exec "检查当前项目" -p work
mind exec "检查当前项目" -c 'model_providers.openai-main.reasoning_effort="high"'
```

| 选项 | 说明 |
|------|------|
| `-c, --config <key=value>` | 按点路径临时覆盖配置；值优先按 TOML 解析，可重复传入 |
| `-p, --profile <PROFILE>` | 在基础配置之上叠加 `~/.mind/<name>.config.toml` |
| `-C, --cd <DIR>` | 为交互、resume、exec 或 agent listen 指定本次工作目录；目录必须存在 |
| `-s, --sandbox <MODE>` | 选择 `read-only`、`workspace-write` 或 `danger-full-access` |
| `-a, --ask-for-approval <POLICY>` | 选择 `untrusted`、`on-request` 或 `never` |
| `-V, --version` | 输出版本号 |
| `-h, --help` | 输出帮助 |

`-c` 只覆盖本次进程。包含数组、字符串或特殊字符的值应按当前 shell 的规则加引号。

本地 JavaScript REPL 和子 Agent 能力由 `config.toml` 的启动期开关控制：

```toml
[features]
js_repl = false
subagents = false
```

将对应值改为 `true` 才会启用能力。

关闭 `js_repl` 会同时移除 `js_repl` 和 `js_repl_reset`；关闭 `subagents`
会停止注册全部 Agent 协作工具，并禁止创建或控制子 Agent。`[agents]` 仅保留
`max_concurrent_threads_per_session`、`max_depth`、`default_fork_turns` 和
`max_fork_context_chars` 等运行参数。修改这些能力开关后需要重新启动进程。

## 交互模式

```powershell
mind
mind "先检查当前项目结构"
mind -m gpt-5.5 "先检查当前项目结构"
mind -i .\screen.png "分析这张截图"
mind -H api "检查接口"
```

根命令支持：

| 选项 | 说明 |
|------|------|
| `-m, --model <MODEL>` | 为本次运行覆盖主模型 |
| `-i, --image <FILE>` | 添加初始图片；可重复，也可用逗号分隔多个路径 |
| `-H, --helix [PROFILE]` | 接入 Helix；省略 profile 时使用 `app`，也可选择 `api` |

`-m` 是本次运行的临时覆盖，不会写入持久配置。需要在交互会话中持久修改模型时，使用 `/model` 或 `/preferences`。

## 单次执行

```powershell
mind exec [OPTIONS] [PROMPT]
mind e [OPTIONS] [PROMPT]
```

常用示例：

```powershell
# 非交互运行默认使用 read-only 和 never
mind exec "检查当前项目并给出结论"

# 选择沙箱、审批策略和本次模型
mind exec -s workspace-write -a on-request -m gpt-5.5 "修复测试失败"

# 输出 newline-delimited JSON 事件
mind exec --json "检查当前项目"

# 本次运行启动或复用 Helix；省略 profile 时使用 app
mind exec --helix "检查设备状态"

# 接入 Helix 并使用 api 工具过滤器
mind exec --helix api "检查接口状态"
```

`exec` 选项：

| 选项 | 说明 |
|------|------|
| `--json` | 输出 JSONL 事件流 |
| `--dangerously-bypass-hook-trust` | 本次执行跳过已启用 Hook 的当前内容信任检查 |
| `-H, --helix [PROFILE]` | 启动或复用本地 Helix；profile 可选 `app` 或 `api`，默认 `app` |
| `-i, --image <FILE>` | 添加图片附件 |
| `-m, --model <MODEL>` | 临时覆盖本次请求使用的主模型 |

### 图片组合

图片选项可以写在 `exec` 前，也可以写在 `exec` 的 prompt 前后：

```powershell
mind -i .\overview.png exec "分析图片"
mind exec -i .\overview.png "分析图片"
mind exec "分析图片" -i .\overview.png
```

多张图片可以重复传入选项，也可以使用逗号分隔：

```powershell
mind exec "比较两张图片" -i .\before.png -i .\after.png
mind exec "比较两张图片" --image ".\before.png,.\after.png"
```

根命令和 `exec` 子命令都提供图片时，会按命令行顺序合并，不会互相覆盖：

```powershell
mind -i .\overview.png exec -i .\detail.png "结合全图和细节图分析"
```

路径包含空格或其他特殊字符时应加引号：

```powershell
mind exec "这是什么图" --image "C:\Users\Administrator\Downloads\公司文档\18891368635813248.png"
```

### 模型组合

模型可以放在根命令或 `exec` 子命令：

```powershell
mind -m gpt-5.5 exec "检查当前项目"
mind exec "检查当前项目" -m gpt-5.5
```

两处都传入时，离具体命令更近的 `exec --model` 优先。模型覆盖只作用于本次执行，不写入 `config.toml`。

### 标准输入组合

显式 prompt 可以和管道输入同时使用。管道内容会作为 `<stdin>...</stdin>` 上下文附加到 prompt：

```powershell
Get-Content .\build.log | mind exec "总结失败原因"
git diff | mind exec "审查这些改动"
```

使用 `-` 可以明确要求从标准输入读取完整 prompt；省略 prompt 时，非交互标准输入也会被读取：

```powershell
Get-Content .\task.txt | mind exec -
Get-Content .\task.txt | mind exec
```

## 恢复会话

```powershell
mind resume
mind resume --last
mind resume <SESSION_ID> "继续检查剩余问题"
mind resume --helix api
```

| 选项 | 说明 |
|------|------|
| `--last` | 不打开选择器，直接恢复最近会话 |
| `--all` | 显示所有工作目录的会话 |
| `--include-non-interactive` | 同时显示由非交互命令创建的会话 |
| `-i, --image <FILE>` | 为恢复后的首条消息添加图片 |
| `-m, --model <MODEL>` | 临时覆盖恢复会话使用的主模型 |
| `-H, --helix [PROFILE]` | 恢复时接入 Helix；省略 profile 时使用 `app` |

根命令上的 `-i/--image` 和 `-m/--model` 同样会传播给 `resume`；子命令模型优先，图片按顺序合并。

当历史会话的工作目录与活动目录不同，CLI 恢复及应用内 `/resume` 都显示四项选择：
使用会话目录、使用当前目录、始终使用会话目录、始终使用当前目录。默认选中会话目录；
Enter 确认，数字直接选择，Esc 使用会话目录，Ctrl+C/Ctrl+D 退出。
菜单使用透明背景，选中项使用终端主题的强调色，无彩色模式保留箭头与加粗；长路径随窗口宽度换行。
底部提示跟随实际确认键绑定。活动目录与启动目录不同时，“始终使用当前目录”会显示
将采用的启动目录，避免与单次“使用当前目录”混淆。

“始终”保存用户配置 `tui.resume_cwd = "session"` 或 `"current"`，不保存固定目录。
单次 Current 使用活动目录，记忆 Current 使用本次启动目录。显式 `-C/--cd` 优先于记忆策略：

```powershell
mind resume <SESSION_ID> --cd D:\Projects\Current
mind -c 'tui.resume_cwd="session"' resume --last --all
```

未配置策略且历史没有目录元数据时沿用活动目录；明确使用 Session 却缺少元数据时报告错误。
目标目录必须存在，目标项目配置按其信任状态重新解析，Profile 和 CLI 覆盖继续生效。
选择相同活动会话时保持当前画面与草稿。未完成的冻结 Turn 和旧子代理必须在其原目录继续，
不能套用另一工作区的工具；报错会显示所需目录。
工作区切换会重新加载项目 Skills 和外部 MCP。stdio MCP 未指定 `cwd` 时使用活动工作区；
相对 `cwd` 相对于活动工作区解析，带路径的相对 `command` 相对于该 MCP 目录解析。

指定会话 ID 时按 ID 查找，不按当前工作区或会话来源过滤。普通选择器默认显示当前工作区，
可以切换到 All 查看其他工作区；`--all` 直接以 All 打开。`--last` 默认只查当前工作区，
与 `--all` 一起使用时查找所有工作区的最近会话。

## 会话归档

```powershell
mind archive <SESSION_ID_OR_TITLE>
mind unarchive <SESSION_ID_OR_TITLE>
```

`archive` 将匹配到的会话标记为 archived，`unarchive` 将其恢复为 active。目标可以是会话 ID，
也可以是精确的历史标题；两个命令都只执行一次状态变更后退出，不启动交互会话。

## 外部 MCP 管理

### 查询和启停

```powershell
mind mcp list
mind mcp list --json
mind mcp get playwright
mind mcp get playwright --json
mind mcp enable playwright
mind mcp disable playwright
mind mcp remove playwright
mind mcp help
mind mcp help add
```

### 添加远端服务

```powershell
mind mcp add dbhub --url https://example.com/mcp
mind mcp add dbhub --url https://example.com/mcp `
  --bearer-token-env-var DBHUB_TOKEN `
  --env-http-header "X-Tenant=DBHUB_TENANT" `
  --required
```

远端服务可以重复使用 `--header`、`--env-http-header`、`--allow` 和 `--deny`。`--startup-timeout-sec` 控制启动和工具发现超时，`--tool-timeout-sec` 控制工具调用超时。

`mcp add` 的选项边界如下：

| 选项 | 适用服务 | 说明 |
|------|----------|------|
| `--url <URL>` | 远端 | 注册 streamable HTTP MCP 服务 |
| `--bearer-token-env-var <ENV_VAR>` | 远端 | 从环境变量读取 bearer token |
| `--header <KEY=VALUE>` | 远端 | 添加 HTTP header，可重复 |
| `--env-http-header <HEADER=ENV_VAR>` | 远端 | 从环境变量读取 HTTP header，可重复 |
| `--env <KEY=VALUE>` | stdio | 设置子进程环境变量，可重复 |
| `--cwd <DIR>` | stdio | 设置子进程工作目录 |
| `--disabled` | 两者 | 注册但不在启动时启用 |
| `--required` | 两者 | 初始化失败时让启动失败 |
| `--allow/--deny <PATTERN>` | 两者 | 按工具名或 glob 过滤，可重复 |
| `--approval-mode <MODE>` | 两者 | 设置 `auto`、`prompt`、`writes` 或 `approve` 工具审批模式 |
| `--startup-timeout-sec <SECONDS>` | 两者 | 启动和工具发现超时 |
| `--tool-timeout-sec <SECONDS>` | 两者 | 工具请求超时 |

### OAuth 浏览器登录

```powershell
mind mcp add sentry --url "<SENTRY_MCP_URL>"
mind mcp login sentry
mind mcp login sentry --scopes "org:read,project:write" --timeout-sec 180
mind mcp logout sentry
```

`login` 使用原始配置键，适用于支持 OAuth 的 Streamable HTTP 服务。配置了
`bearer_token_env_var` 或任意大小写的 `Authorization` header 时，登录会报告配置冲突，
即使对应环境变量尚未设置。登录不会改写服务注册。服务和授权端点要求 HTTPS；本机
HTTP MCP 可使用本机 HTTP 授权端点。

命令先显示授权地址，再打开系统浏览器；打开失败时可手动访问已显示的地址。
回调只监听 `127.0.0.1`，默认使用系统分配的端口。凭据成功保存到系统凭据库后才报告
登录成功；拒绝、超时、取消或保存失败均不报告成功，失败后可查询本地状态再重试。
Windows 使用 Credential Manager，
macOS 使用 Keychain，Linux 使用 Secret Service；不可用时显式失败，不回退明文文件。

可选配置示例：

```toml
[mcp_servers.sentry.oauth]
scopes = ["org:read", "project:write"]
login_timeout_sec = 300
# 预注册公共客户端需要同时提供固定回调端口：
# client_id = "your-public-client-id"
# callback_port = 12608
# 或使用服务端支持的 HTTPS 客户端元数据文档，与 client_id 互斥：
# client_metadata_url = "https://your-domain.example/oauth/client.json"
```

没有指定客户端身份时使用服务端声明的动态注册端点；只支持无需 client secret 的公共
客户端。`--scopes` 使用逗号分隔；未指定时依次选择配置、Bearer challenge、资源元数据、
授权服务器元数据中的范围。`scopes = []` 或 `--scopes ""` 明确请求空范围。显式范围不足
或服务端返回不同范围会报错。`--timeout-sec` 覆盖配置，并限制发现、浏览器等待、交换和
保存的总时长；HTTP 单次等待另有 20 秒上限。

`mcp list/get`、`/mcp status` 和 `/tools` 使用同一认证状态契约；JSON 顶层字段为
`authorization`，配置中的 `config.oauth` 仍是登录选项。`Auth` 区分 `unknown`、
`unsupported`（stdio/SSE 的 OAuth）、`header`、`bearer`、`oauth`、`anonymous`、
`not_logged_in`、`reauthorization_required` 和 `unavailable`。
`Credentials (local)` 单独展示本地事实：`missing` 无记录、`registered` 仅注册客户端、
`stored` 已保存、`expired` 已到期、`unavailable` 存储故障、`refresh_uncertain` 刷新提交不确定，
或 `reauthorization_required` 需要重新授权。空记录本身不能证明匿名服务需要登录。
`Last auth request` / JSON `verification` 的 `accepted`、`rejected` 只描述现有连接最后观察到的
请求，不代表实时探测。CLI 只查本地，因此总是 `unverified`；凭据版本改变也会撤销旧认证结论。
状态查询不联网、不刷新令牌、不打开浏览器；`/tools` 同样显示零工具和失败服务及恢复提示。
需要登录时提示原始注册名称；显式 Header/Bearer 被拒绝时提示检查其配置，不引导 OAuth 登录。
`refresh_uncertain` 和 `reauthorization_required` 需要重新运行 `mcp login`。
`logout` 幂等删除当前目标的本地凭据，不移除配置，也不声称撤销服务端授权。
退出码：成功为 `0`，登录或存储失败为 `1`，参数错误为 `2`，用户取消为 `130`。

登录后启动或重启对应 MCP 服务，运行时会恢复凭据，过期时在发送请求前自动刷新。
刷新使用登录时验证并保存的授权服务器端点；多个进程共享凭据锁，轮换成功后立即保存。
单次刷新交换最多等待 5 秒；结果不确定时停止使用旧 refresh token，要求重新登录。
运行时只使用已批准的范围，不覆盖 CLI 登录时的 `--scopes` 选择，也不自动扩大授权。

每个新请求都会检查最新凭据版本。另一个进程重新登录后，活动连接采用新凭据；退出登录
后，使用过旧凭据的连接在下一个请求边界停止使用它，已发出的远端请求继续按原生命周期
收束。401、403 和认证重定向会使服务失败并撤下工具目录；不会自动重放工具调用或打开
浏览器。`/mcp status` 展示独立的授权错误；重新登录后可通过 `/mcp` 菜单重启对应服务。
工具审批仍按既有权限策略执行。

首版支持 Streamable HTTP、授权码与 PKCE S256、公共客户端动态注册、客户端元数据文档和
预注册公共客户端；是否可用取决于服务端声明的能力。不支持 stdio/SSE 的 OAuth、client
secret、设备码登录，也不读取 Codex 或其他客户端保存的登录凭据。

| 现象 | 处理方式 |
| --- | --- |
| `missing` / `registered` / `login_required` | 执行 `mind mcp login <name>`，然后重启对应 MCP 服务。匿名服务无需登录。 |
| `expired` | 本地记录已到期；运行时有 refresh token 时自动刷新，无可用刷新授权时重新登录。 |
| `insufficient_scope` / `reauthorization_required` / `refresh_uncertain` | 确认服务要求的范围，显式重新登录；成功后重启失败的服务。 |
| `configuration_conflict` | 检查显式 Bearer/Header 与 OAuth 的选择，以及公共客户端和回调端口配置。 |
| `storage_unavailable` / `unavailable` | 检查当前用户的系统凭据库及状态目录访问；Linux 还需可用的用户 D-Bus 会话和已解锁的 Secret Service。 |
| `storage_busy` | 等待其他进程的登录、刷新或退出事务结束后重试。 |
| `storage_corrupt` | 对原注册执行 logout 清理后重新登录；不要手工删除活动索引或锁文件。 |

凭据按配置根、状态根、原始注册名和完整 URL 隔离；改变任一项都不会借用旧登录。
更名、改 URL 或删除注册前，先对原注册执行 logout。浏览器回调要求运行 CLI 的机器能接收
本机端口连接；远程终端不能把另一台机器的 `127.0.0.1` 当成本机回调。
平台支持与实际验收结果分开记录，操作步骤和记录模板见 [OAuth 验收指南](mcp-oauth-acceptance.md)。

### 添加 stdio 服务

stdio 子进程命令必须放在 `--` 之后：

```powershell
mind mcp add playwright -- npx -y @playwright/mcp@latest
mind mcp add local-tools --env "TOKEN=value" --cwd "D:\tools" -- python server.py
```

`--` 会结束 Mind 自身的选项解析，后面的参数全部原样传给子进程。因此子进程自己的 `--model`、`--image` 等参数不会被 Mind 消费：

```powershell
mind mcp add demo -- server --model child-model
```

远端 URL 与 stdio 命令不能同时使用。`--env` 和 `--cwd` 只用于 stdio 服务；HTTP header 和 bearer token 选项只用于远端服务。

stdio 服务必须使用非交互启动命令，例如 `npx -y @playwright/mcp`；`-y` 跳过 npm 安装确认，
首次安装或升级下载仍可能超过默认的 30 秒启动时限。启动超时会提示在 `config.toml` 中调整
对应服务的 `startup_timeout_sec`，并提供可复制的配置示例。预检超时则提示检查命令、工作目录
或网络地址。

子进程 stderr 按服务记录为 `external_mcp.stdio.stderr` 事件，写入本次运行的
`mind.debug.log`，不直接输出到交互终端。诊断会隐藏 URL 凭据和常见 token/password 字段；
超过 4096 字节的单行只记录省略标记。连接关闭时读取任务随 owner 回收，并记录剩余的有界尾部。

stdio 协议 stdout 的单帧上限为 8 MiB（不含换行符），在 JSON 解码前检查；持续不换行的输出
也受此限制。超限、无效 JSON-RPC 或不完整尾帧会关闭该连接。默认使用 UTF-8，其他编码须与
ASCII 换行兼容；UTF-16 等编码会在启动子进程前被拒绝。

### 外部工具审批与传输边界

外部 MCP 的 `approval-mode` 只控制模型发起的工具效果：`prompt` 每次询问，`writes` 对不是明确
只读的工具询问，`auto` 根据 MCP annotations 判断且在信息不足时询问，`approve` 明确跳过逐次
询问。全局 `approval_policy=never` 遇到仍需询问的 MCP 工具时直接拒绝，不会静默执行。

连接用户配置的 STDIO、SSE 或 Streamable HTTP 服务属于显式配置的传输信任边界，建立连接不会
生成网络审批卡，也不会把 MCP tool grant 当成网络 grant。HTTP client 不读取环境代理配置；
远端 bearer token 和动态 header 应优先通过 `--bearer-token-env-var` / `--env-http-header` 注入。
列表、状态和传输错误会隐藏凭据，运行时关闭时会终止连接 owner 并清空工具与会话引用。

HTTP/SSE 自动重定向只接受同源地址（协议、主机和端口一致），最多跟随 10 次。
明文 HTTP 主机名的跳转只允许 `localhost`；IP 地址可用于本地或专用网络服务。
OAuth 连接禁止自动重定向。跨源地址请直接修正服务 URL，客户端不会向新来源转发参数或认证头。

Streamable HTTP 初始化遇到临时连接、读写或网络超时错误，以及 HTTP 408/429/500/502/503/504，
最多尝试三次，重试前分别等待 250 毫秒和 1 秒。每次先关闭旧连接再建立新连接，所有尝试、
等待和后续目录读取共用 `startup_timeout_sec`。认证、证书及协议错误不重试；stdio、SSE、
工具目录失败和工具调用不进入该握手重试流程。取消或总期限到达后停止尝试并释放资源。

工具目录会读取全部分页，并在完成后统一发布；最多接受 100 页、2048 个工具，单个游标
最多 64 KiB。循环游标、重复工具名、规范化后的重名、超限或后续页失败都会使本次连接失败，避免暴露
不完整目录。所有分页共用该服务的 `startup_timeout_sec`，不为每一页重新计算启动期限。

## 其他命令

`doctor` 会检查全部内置命令行工具；在 macOS 上还会报告缺失执行位或仍携带
`com.apple.quarantine` 的工具，但不会实际启动这些程序。

```powershell
# 只读诊断；JSON 形式适合脚本消费
mind doctor
mind doctor --json

# 监听远端下发任务，需要 Helix app 时添加 --helix
mind agent listen
mind agent listen --helix

# 使用 Helix api 工具过滤器
mind agent listen --helix api

# 更新 Helix 运行组件
mind upgrade helix

# 通过 stdio 向 MCP host 暴露服务
mind mcp-server

# 生成补全脚本
mind completion powershell
mind completion bash
mind completion zsh
mind completion fish
mind completion elvish

# 查看根命令或多级子命令帮助
mind help
mind help mcp add
```

`mind mcp-server` 的 host 配置和生命周期见 [MCP Server](mcp-server.md)，`agent listen` 的恢复链路见[订阅模式](agent-mode.md)。

## 组合规则速查

- `-c/--config` 和 `-p/--profile` 是进程级选项，可以跨命令层级提取。
- 根命令的图片和模型会传播给 `exec` 与 `resume`。
- 图片会合并；具体子命令上的模型会覆盖根模型。
- 不传 `--helix` 时不连接 Helix；传入但省略 profile 时使用 `app`。
- `exec` 的显式 prompt 可以和非交互 stdin 同时使用。
- `mcp add ... -- <COMMAND>` 中 `--` 之后的参数只属于 stdio 子进程。
- 遇到组合疑问时，以 `mind --help` 和 `mind <command> --help` 的当前输出为准。
