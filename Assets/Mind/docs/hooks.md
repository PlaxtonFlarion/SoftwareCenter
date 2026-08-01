# Hooks 配置

Hooks 统一写入配置层的 `config.toml`。用户配置位于
`~/.mind/config.toml`，可信项目也可以在 `.mind/config.toml` 中追加项目级
Hooks；不读取 `hooks.json`。

每个事件包含多个 MatcherGroup，每组使用一个可选的正则 `matcher`，并按声明
顺序包含多个命令处理器：

```toml
[[hooks.PreToolUse]]
matcher = "shell_command|apply_patch"
hooks = [
  { type = "command", command = "python scripts/check_tool.py", commandWindows = "py scripts/check_tool.py", statusMessage = "Checking tool call", timeout = 10, async = false, additionalContextLimit = 2500 },
  { type = "command", command = "python scripts/audit_tool.py", async = true },
]
```

处理器字段：

| 字段 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `type` | string | 必填 | 当前仅支持 `command` |
| `command` | string | 必填 | 默认平台执行的 shell 命令 |
| `commandWindows` | string | 无 | Windows 上覆盖 `command`；也接受 `command_windows` |
| `statusMessage` | string | 无 | 命令执行期间显示的临时状态 |
| `timeout` | integer | `600` | 超时秒数；`SessionEnd` 默认 `1` 且最大为 `3` |
| `async` | boolean | `false` | 后台执行；输出不参与当前事件控制 |
| `additionalContextLimit` | integer | `2500` | 附加上下文近似 token 上限，`0` 不限制 |

MatcherGroup 只能包含 `matcher` 和 `hooks`。处理器只能包含上表字段；旧的事件
直挂处理器结构以及 `handler`、`enabled`、`on_error` 字段会作为无效配置拒绝。

命令从 stdin 接收事件 JSON。退出码 `0` 表示正常完成，`2` 表示业务阻断，其他
非零退出码表示运行失败。stdout 可以返回 JSON 对象，也可以直接返回普通文本作为
附加上下文。过大的输出或附加上下文会写入会话临时文件，并在会话结束时清理。
