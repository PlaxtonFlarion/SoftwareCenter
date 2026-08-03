# Hooks 配置

Hooks 统一写入配置层的 `config.toml`。用户配置位于
`~/.mind/config.toml`，可信项目也可以在 `.mind/config.toml` 中追加项目级
Hooks；不读取 `hooks.json`。

## 信任与启用状态

当前配置层接入 user、profile、project 和 CLI Hook，这些普通来源默认状态都是
`untrusted`，不会执行；项目配置被加载不等于其中的 Hook 自动可信。普通 Hook
必须先审核并信任当前内容。managed 和 plugin 是预留来源，当前配置解析层不负责
发现或加载这两类 Hook；未来由受控入口注入的 managed Hook 自动可信并始终启用。

信任和启用状态保存在用户 `config.toml`，不使用独立的 `hook-trust.json`：

```toml
[hooks.state."<hook-key>"]
enabled = false
trusted_hash = "sha256:<64 hex>"
```

`trusted_hash` 由 Hook 管理界面写入。用户配置和当前进程的 CLI override 可以提供
Hook state；profile 或 project 配置中的 state 不能为自身授权。`enabled`
与信任相互独立，因此受信任的 Hook 可以单独禁用，内容改变后重新信任也会保留
原有禁用状态。

信任状态有四种：

- `managed`：预留给受控入口注入的配置，始终启用并执行，用户不能修改其状态。
- `trusted`：当前内容摘要与 `trusted_hash` 相同；仅在 `enabled=true` 时执行。
- `modified`：保存过信任摘要，但当前内容已经变化，不执行。
- `untrusted`：没有保存当前 Hook 的信任摘要，不执行。

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
| `timeout` | integer | `600` | 超时秒数；`SessionEnd` 默认 `1`，超过 `3` 时钳制为 `3` 并警告 |
| `async` | boolean | `false` | 当前不支持异步命令；非 `SessionEnd` 事件会跳过并警告，`SessionEnd` 仍同步执行 |
| `additionalContextLimit` | integer | `2500` | 附加上下文近似 token 上限，`0` 不限制 |

MatcherGroup 使用 `matcher` 和 `hooks`，命令处理器使用上表字段。未知字段会被忽略
并记录 discovery warning，不会使整个配置加载失败。

Hook discovery 按匹配组和处理器分别容错：非法 matcher 只跳过当前匹配组；空命令、
字段类型错误、不支持的 handler type 或非 `SessionEnd` 的异步处理器只跳过当前
处理器，其他合法 Hook 继续加载。`type = "prompt"` 和 `type = "agent"` 可以被
解析，但当前不执行，并产生明确的“不支持” warning。warning 会写入 Hook 观察
日志，并显示在 `/hooks` 汇总界面。

Matcher 规则与工具名称：

- 未填写、空字符串和 `*` 匹配全部。
- 非法正则会产生 warning 并跳过当前 MatcherGroup。
- `UserPromptSubmit` 和 `Stop` 当前不支持 matcher，配置的 matcher 会被忽略。
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
`transcript_path` 指向当前执行实际写入的会话记录；子执行主体使用独立记录文件，
`SubagentStop.agent_transcript_path` 指向同一子执行记录。

会话记录位于应用主目录下的
`sessions/YYYY/MM/DD/session-<session_id>.jsonl`。日期取自会话标识中的创建时间；
同一会话始终解析到同一路径，根执行主体和每个子执行主体各自使用独立文件。
进程级终端展示记录仍位于 `reports`，不再作为 `transcript_path`。

文件采用本产品定义的追加式 JSONL，每行都是一个完整事件对象：

```json
{
  "timestamp": "2026-08-01T10:20:30.123Z",
  "event": "message.created",
  "session_id": "sid_...",
  "turn_id": "...",
  "actor": "user",
  "payload": {"content": "hello"}
}
```

固定字段为 `timestamp`、`event`、`session_id`、`turn_id`、`actor` 和 `payload`，
不包含 `version` 或 `schema_version`。当前事件包括 `session.started`、
`session.ended`、`turn.started`、`turn.completed`、`turn.failed`、
`turn.interrupted`、`message.created`、`message.updated`、`tool.started`、
`tool.completed`、`tool.failed`、`context.compacted` 和
`context.compaction.failed`。恢复已有会话时继续追加到原文件，并以新的
`session.started` 标记本地生命周期重新进入。

该路径和生命周期语义用于 Hook 集成，但文件内容是本产品契约，不承诺兼容
Codex 内部 rollout/transcript 格式。依赖 Codex 内部记录结构的 Hook 需要适配上述
JSONL 事件；只依赖路径存在、逐行 JSON 或生命周期顺序的 Hook 可以直接使用。

退出码 `0` 表示正常完成。只有 `PreToolUse`、`PermissionRequest`、
`PostToolUse`、`UserPromptSubmit`、`Stop` 和 `SubagentStop` 可以用退出码 `2`
表达业务阻断，而且原因必须写入 stderr；其他事件的退出码 `2` 与其余非零
退出码一样表示运行失败。
普通 stdout 只有 `SessionStart`、`UserPromptSubmit` 和 `SubagentStart` 会作为
上下文；`Stop` 与 `SubagentStop` 必须返回 JSON，其余事件的普通 stdout 会忽略。
以 `{` 或 `[` 开头但不能解析为协议对象的 stdout 会作为无效 JSON 报错，而不
会降级为普通文本。
命令超时、启动失败、非零退出、非法 JSON 或输出协议校验失败只会把本次 Hook
标记为失败，主操作继续执行。只有有效控制输出或上述受支持事件的退出码 `2`
可以表达业务阻断。
结构化输出中的 `systemMessage` 会记录为 Hook warning，不会注入模型请求；需要
提供模型可见内容时使用受支持事件的 `additionalContext`。
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
多个并发 Hook 都返回 `updatedInput` 时，采用最后完成 Hook 的完整对象，不逐字段
合并。
多个 Hook 同时阻断时，使用配置顺序中第一个有效阻断原因。
阻断结果中的有效 `additionalContext` 仍会随工具或审批结果传给模型，不会因为
拒绝执行而丢失。
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

`PostToolUse` 只在工具成功完成时执行；工具返回失败、执行异常或取消时均不执行。
它的控制和模型反馈语义彼此独立：

- `continue: false` 把该 Hook 标记为停止；`reason` 优先作为模型反馈，没有有效
  `reason` 时使用 `stopReason` 或固定反馈。它不回滚已经完成的工具执行。
- 顶层 `decision: "block"` 拒绝工具结果而不是工具执行，并把必填的 `reason`
  作为失败结果反馈给模型。
- `hookSpecificOutput.additionalContext` 作为独立上下文注入，不承担结果替换。
- 应用扩展字段 `replacementResult` 显式替换模型可见结果，不修改原始执行值；
  `block` 优先于结果替换，没有 `block` 时显式替换优先于停止反馈。

多个停止或阻断反馈按 Hook 顺序合并。上游保留字段 `updatedMCPToolOutput` 当前不
执行替换，返回非空值会使 Hook 运行失败。`PostCompact` 只接受通用输出字段，
不接受 `hookSpecificOutput`。

`SessionStart` 返回 `continue: false` 时会停止当前轮次启动，不再执行
`UserPromptSubmit` 或模型请求；同一批结果中的 `additionalContext` 会保留给
下一轮。压缩成功后会立即分发一次 `SessionStart(source="compact")`，其中的
`additionalContext` 排入压缩后的下一轮，`continue: false` 会把压缩后的继续
状态标记为已阻止。`UserPromptSubmit` 阻断当前轮次时也会保留同批结果中的
`additionalContext`。多个 `Stop` Hook 中任意一个返回
`continue: false` 时停止结果优先；只有没有停止结果时，才会聚合
`decision: "block"` 的原因并创建续跑 Prompt。
