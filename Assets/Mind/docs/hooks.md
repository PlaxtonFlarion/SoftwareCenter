# Hooks 配置

Hooks 统一写入配置层的 `config.toml`。用户配置位于
`~/.mind/config.toml`，可信项目也可以在 `.mind/config.toml` 中追加项目级
Hooks；不读取 `hooks.json`。

每个事件包含多个 MatcherGroup，每组使用一个可选的 `matcher`，并按声明顺序
包含多个命令处理器：

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

Matcher 规则与工具名称：

- 未填写、空字符串和 `*` 匹配全部。
- 不含正则控制字符的单值按全等匹配，例如 `Bash` 不会匹配 `BashOutput`。
- 仅由字面候选组成的 `|` 表达式按候选集合匹配，例如 `Edit|Write`。
- 只有出现其他正则控制字符时才按正则匹配。
- 工具 Hook 同时匹配本地 canonical 名称和固定兼容别名：`shell_command`、
  `exec_command`、`write_stdin` 对应 `Bash`，`apply_patch` 对应 `Edit`、
  `Write`，`spawn_agent` 对应 `Agent`；同一处理器只执行一次。

命令从 stdin 接收一个符合事件 schema 的 JSON 对象。公共字段使用 Codex
canonical 名称：`session_id`、`transcript_path`、`cwd`、`hook_event_name` 和
`model`；按事件补充 `turn_id`、`permission_mode`、Agent 字段或工具字段。
工具事件使用 `tool_name`、`tool_use_id`、`tool_input`，后置事件使用
`tool_response`。Shell 工具的输入名称为 `Bash`，补丁工具的输入名称为
`apply_patch`。Shell 与补丁工具都把可执行文本放在 `tool_input.command`；补丁
Hook 返回的 `updatedInput.command` 会转换回本地 `patch` 参数。

退出码 `0` 表示正常完成。只有 `PreToolUse`、`PermissionRequest`、
`PostToolUse`、`UserPromptSubmit`、`Stop` 和 `SubagentStop` 可以用退出码 `2`
表达业务阻断，而且原因必须写入 stderr；其他事件的退出码 `2` 与其余非零
退出码一样表示运行失败。
普通 stdout 只有 `SessionStart`、`UserPromptSubmit` 和 `SubagentStart` 会作为
上下文；`Stop` 与 `SubagentStop` 必须返回 JSON，其余事件的普通 stdout 会忽略。
以 `{` 或 `[` 开头但不能解析为协议对象的 stdout 会作为无效 JSON 报错，而不
会降级为普通文本。
过大的输出或附加上下文会写入会话临时文件，并在会话结束时清理。

`PreToolUse` 使用嵌套控制输出：

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow",
    "updatedInput": {"command": "echo rewritten"}
  }
}
```

`permissionDecision: "allow"` 只有同时返回 `updatedInput` 时才受支持；
`permissionDecision: "deny"` 必须包含非空 `permissionDecisionReason`。
`permissionDecision: "ask"`、顶层 `decision: "approve"` 以及该事件的
`continue: false`、`stopReason`、`suppressOutput: true` 会使当前 Hook 运行失败。

`PermissionRequest` 的决定必须使用嵌套结构。多个 Hook 中 deny 优先；没有
决定时继续走普通审批：

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PermissionRequest",
    "decision": {
      "behavior": "deny",
      "message": "Blocked by repository policy."
    }
  }
}
```

`deny` 未提供非空 `message` 时使用固定默认原因。`updatedInput`、
`updatedPermissions` 和 `interrupt: true` 是保留字段，当前返回这些值会使 Hook
运行失败；`continue: false`、`stopReason` 和 `suppressOutput: true` 同样不受
支持。

`PostToolUse` 使用顶层 `decision: "block"`、`reason` 和嵌套的
`hookSpecificOutput.additionalContext`。结果替换仍通过应用扩展字段
`replacementResult` 完成；上游保留字段 `updatedMCPToolOutput` 当前不执行替换，
返回非空值会使 Hook 运行失败。`PostCompact` 只接受通用输出字段，不接受
`hookSpecificOutput`。
