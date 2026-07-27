# 命令行使用参考

这份文档说明当前 CLI 的入口、选项组合和参数边界。交互模式中的 `/` 指令见[交互模式](interactive-mode.md)，星图批跑的输入格式见[星图协议](cli-code.md)。

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
| `mind batch` | 执行一个或多个星图 source |
| `mind agent listen` | 监听远端下发任务 |
| `mind helix upgrade` | 下载或更新 Helix 运行组件 |
| `mind doctor` | 只读诊断本地运行环境 |
| `mind mcp ...` | 管理外部 MCP 服务注册 |
| `mind mcp-server` | 通过 stdio 暴露 MCP 服务 |
| `mind completion` | 生成 shell 补全脚本 |

## 进程级选项

配置、沙箱和审批选项都是进程级选项，可以写在子命令之前或之后：

```powershell
mind -p work exec "检查当前项目"
mind exec "检查当前项目" -p work
mind exec "检查当前项目" -c 'model_reasoning_effort="high"'
```

| 选项 | 说明 |
|------|------|
| `-c, --config <key=value>` | 按点路径临时覆盖配置；值优先按 TOML 解析，可重复传入 |
| `-p, --profile <PROFILE>` | 在基础配置之上叠加 `~/.mind/<name>.config.toml` |
| `-s, --sandbox <MODE>` | 选择 `read-only`、`workspace-write` 或 `danger-full-access` |
| `-a, --ask-for-approval <POLICY>` | 选择 `untrusted`、`on-request` 或 `never` |
| `-V, --version` | 输出版本号 |
| `-h, --help` | 输出帮助 |

`-c` 只覆盖本次进程。包含数组、字符串或特殊字符的值应按当前 shell 的规则加引号。

## 交互模式

```powershell
mind
mind "先检查当前项目结构"
mind -m gpt-5.5 "先检查当前项目结构"
mind -i .\screen.png "分析这张截图"
```

根命令支持：

| 选项 | 说明 |
|------|------|
| `-m, --model <MODEL>` | 为本次运行覆盖主模型 |
| `-i, --image <FILE>` | 添加初始图片；可重复，也可用逗号分隔多个路径 |

`-m` 是本次运行的临时覆盖，不会写入持久配置。需要在交互会话中持久修改模型时，使用 `/model` 或 `/preferences`。

## 单次执行

```powershell
mind exec [OPTIONS] [PROMPT]
mind e [OPTIONS] [PROMPT]
```

常用示例：

```powershell
# 非交互运行默认使用 xtra、read-only 和 never
mind exec "检查当前项目并给出结论"

# 选择模式、沙箱、审批策略和本次模型
mind exec --mode xtra -s workspace-write -a on-request -m gpt-5.5 "修复测试失败"

# 输出 newline-delimited JSON 事件
mind exec --json "检查当前项目"

# 本次运行启动或复用 Helix，并挂载其 MCP 工具
mind exec --helix "检查设备状态"
```

`exec` 选项：

| 选项 | 说明 |
|------|------|
| `--mode <chat|fast|xtra>` | 选择执行模式，默认 `xtra` |
| `--json` | 输出 JSONL 事件流 |
| `--helix` | 启动或复用本地 Helix，并接入其 MCP 工具 |
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
```

| 选项 | 说明 |
|------|------|
| `--last` | 不打开选择器，直接恢复最近会话 |
| `--all` | 显示所有工作目录的会话 |
| `--include-non-interactive` | 同时显示由非交互命令创建的会话 |
| `-i, --image <FILE>` | 为恢复后的首条消息添加图片 |
| `-m, --model <MODEL>` | 临时覆盖恢复会话使用的主模型 |

根命令上的 `-i/--image` 和 `-m/--model` 同样会传播给 `resume`；子命令模型优先，图片按顺序合并。

## 批量执行

```powershell
mind batch --mode chat .\api_batch.md
mind batch --mode xtra .\first.md .\second.md -s danger-full-access -a never
Get-Content .\task.md | mind batch --mode chat -
mind batch --mode fast "inline: 在这里写星图内容"
mind batch --mode chat https://example.com/task.md
```

`SOURCE` 支持本地文件、`-`、`inline:` 内容和 URL，并且可以一次传入多个 source。`--mode` 必填；未覆盖时非交互运行使用 `read-only + never`；需要 Helix MCP 工具时添加 `--helix`。

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

## 其他命令

```powershell
# 只读诊断；JSON 形式适合脚本消费
mind doctor
mind doctor --json

# 监听远端下发任务，需要 Helix 时添加 --helix
mind agent listen
mind agent listen --helix

# 更新 Helix 运行组件
mind helix upgrade

# 通过 stdio 向 MCP host 暴露服务
mind mcp-server

# 生成补全脚本
mind completion powershell
mind completion bash
mind completion zsh
mind completion fish
mind completion elvish
```

`mind mcp-server` 的 host 配置和生命周期见 [MCP Server](mcp-server.md)，`agent listen` 的恢复链路见[订阅模式](agent-mode.md)。

## 组合规则速查

- `-c/--config` 和 `-p/--profile` 是进程级选项，可以跨命令层级提取。
- 根命令的图片和模型会传播给 `exec` 与 `resume`。
- 图片会合并；具体子命令上的模型会覆盖根模型。
- `exec` 的显式 prompt 可以和非交互 stdin 同时使用。
- `mcp add ... -- <COMMAND>` 中 `--` 之后的参数只属于 stdio 子进程。
- 遇到组合疑问时，以 `mind --help` 和 `mind <command> --help` 的当前输出为准。
