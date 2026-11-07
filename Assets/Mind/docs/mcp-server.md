# Mind MCP Server

`mind mcp-server` 通过标准输入输出运行 MCP 服务，供 Codex 或其他 MCP host 调用 Mind agent。stdout 只承载 MCP JSON-RPC；启动错误和协议日志写入 stderr。

这里的 **host** 指发起调用的应用；Mind 是被它启动和调用的服务。若你的目标是让 Mind 调用别人的工具，应看[外部 MCP 管理](cli-usage.md#外部-mcp-管理)，两种连接方向不同。

**开始之前**：确认 `mind --help` 可运行、模型已配置，且 host 可以找到 `mind` 可执行文件。先按[通用配置](#通用配置)注册服务，再从 host 调用 `mind_exec`；单独在终端启动服务只会等待协议输入，不会出现普通聊天界面。

## 工具

服务提供一个工具：`mind_exec`。

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `prompt` | `string` | 必填 | 本次任务内容。 |
| `sandbox_mode` | `read-only \| workspace-write \| danger-full-access \| null` | 配置值或 `read-only` | 沙箱边界。 |
| `approval_policy` | `untrusted \| on-request \| never \| null` | 配置值或 `never` | 工具审批策略。 |
| `working_directory` | `string \| null` | MCP 进程工作目录 | 可选的任务工作目录，必须已经存在。 |
| `timeout_sec` | `number \| null` | `900` | 整次请求的超时秒数，包含等待串行调用锁的时间；传 `null` 可关闭服务端超时。 |
| `session_id` | `string \| null` | `null` | 传入先前返回的会话标识，在同一工作目录续接对话。 |

返回值包含 `status`、`assistant_text`、`usage`、`error`、`exit_code` 和 `session_id`。不传 `session_id` 时开始独立对话；需要继续时，把上次返回的 `session_id` 原样传入。会话游标只保存 24 小时，并且只能在创建它的工作目录恢复。

首次调用的最小参数示例：

```json
{
  "prompt": "概述当前项目的目录结构和主要入口",
  "sandbox_mode": "read-only",
  "approval_policy": "never"
}
```

先确认返回 `status`，再读取 `assistant_text`；失败时检查 `error` 和 `exit_code`。继续对话需要同时保留 `session_id` 与对应工作目录。需要修改文件时，应在调用前明确选择写入权限，不能依赖只读调用自动升级。

同一服务进程内的调用会串行执行，避免共享 workspace、conversation 和工具运行时发生竞争。MCP host 发送标准 `notifications/cancelled` 后，取消会沿当前 `mind_exec` 协程传播到底层模型和工具调用，并释放串行调用锁。服务端超时会取消同一条执行链，返回 `status=failed` 和超时原因；客户端主动取消时按照 MCP 规范不再返回重复结果。

## Codex 配置

打包安装：

```powershell
codex mcp add mind -- mind mcp-server
codex mcp get mind --json
```

源码模式：

```powershell
codex mcp add mind -- python "<REPO_ROOT>/mind.py" mcp-server
```

将 `<REPO_ROOT>` 替换为本机仓库的绝对路径，并使用已安装项目依赖的 Python。第一个 `--` 由 Codex 解析，表示后续内容是 stdio server 的启动命令。它不是 `mind` 的参数。

## 通用配置

使用 JSON 配置的 MCP host 可以采用以下结构：

```json
{
  "mcpServers": {
    "mind": {
      "command": "mind",
      "args": ["mcp-server"]
    }
  }
}
```

源码模式把 `command` 改为 Python 可执行文件，并把 `mind.py` 的绝对路径放在 `args` 第一项。

## 生命周期

服务启动时会：

1. 解析源码或打包入口的 `schematic/supports` 路径。
2. 读取 `~/.mind/config.toml`。
3. 接入 Mind native tools 和已启用的外部 MCP。
4. 等待 MCP host 调用 `mind_exec`，并处理请求取消、超时和可选会话续接。

MCP host 断开后，服务会关闭外部 MCP、native coding runtime 和运行报告。服务不会自动启动 Helix，也不提供远程 HTTP transport。

不要在 Mind 自己的 `~/.mind/config.toml` 的 `[mcp_servers]` 中配置 `mind mcp-server`。Mind 服务启动时会读取这些外部服务，把自身放进去会形成递归子进程。

**常见问题**

| 现象 | 检查方向 |
| --- | --- |
| host 无法启动服务 | 检查 `command` 是否可被该应用找到；必要时使用可执行文件的绝对路径 |
| 能发现工具，但任务失败 | 核对模型配置、工作目录、网络与返回的 `error` |
| 续接会话失败 | 确认 ID 未过期，且工作目录与创建会话时一致 |
| JSON-RPC 解析失败 | 检查启动脚本是否向 stdout 输出了欢迎语或调试信息 |
