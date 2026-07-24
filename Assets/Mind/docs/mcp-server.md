# Mind MCP Server

`mind mcp-server` 通过标准输入输出运行 MCP 服务，供 Codex 或其他 MCP host 调用 Mind agent。stdout 只承载 MCP JSON-RPC；启动错误和协议日志写入 stderr。

## 工具

服务提供一个工具：`mind_exec`。

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `prompt` | `string` | 必填 | 本次任务内容。 |
| `mode` | `chat \| fast \| xtra` | `xtra` | Mind 运行模式。 |
| `access_mode` | `safe \| full` | `safe` | 工具访问模式。 |
| `working_directory` | `string \| null` | MCP 进程工作目录 | 可选的任务工作目录，必须已经存在。 |

返回值包含 `status`、`assistant_text`、`usage`、`error` 和 `exit_code`。每次调用开始独立对话；同一服务进程内的调用会串行执行，避免共享 workspace、conversation 和工具运行时发生竞争。

## Codex 配置

打包安装：

```powershell
codex mcp add mind -- mind mcp-server
codex mcp get mind --json
```

源码模式：

```powershell
codex mcp add mind -- python D:\PycharmProjects\ProxyMind\mind.py mcp-server
```

第一个 `--` 由 Codex 解析，表示后续内容是 stdio server 的启动命令。它不是 `mind` 的参数。

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
4. 等待 MCP host 调用 `mind_exec`。

MCP host 断开后，服务会关闭外部 MCP、native coding runtime 和运行报告。服务不会自动启动 Helix；第一阶段也不提供远程 HTTP transport。

不要在 Mind 自己的 `~/.mind/mcp_servers.json` 中配置 `mind mcp-server`。该文件由 Mind 服务启动时读取，把自身放进去会形成递归子进程。
