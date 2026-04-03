# 星图源抽象设计

这份文档面向维护者和实现者，目标是把当前 `--code` 从“本机文件路径入口”升级成“统一源抽象入口”，同时兼容 CLI、本地 REPL、`/mind` 任务提交接口和 `agent` 长链路下发。

重点不是重新发明一套星图语法，而是解决下面这个结构性问题：

- CLI 当前把 `--code` 绑定为本机文件路径
- `agent` 的输入入口列表目前也天然依赖“消息里如何表达星图源”
- 外部服务如果想通过 `/mind` 或 WS 下发星图任务，需要和客户端约定统一的消息级星图源语义

一句话目标：

- 把 `code` 从“路径模式”改成“源码/蓝本源模式”

## 先判断这页的范围

- 你只想知道 `--code` 现在怎么写：先看 [星图协议](cli-code.md)
- 你只想知道执行顺序、覆盖优先级和 `cfg` 行为：先看 [星图深入说明](cli-code-advanced.md)
- 你要改 `--code` 的输入模型、让外部调用不再依赖 agent 本机文件：看这里
- 你要把 `/mind` 与 `agent` 的 `mind.forward` 串起来，并支持输入入口列表：看这里

## 当前问题

当前实现里，`--code` 的本体是“路径列表”。

入口约束：

- CLI 参数定义在 [mind_core/parser.py](../mind_core/parser.py)
- 批跑入口当前接收 `list[str]`
- 路径解析在 [mind_app/modes/batch.py](../mind_app/modes/batch.py)
- 真实执行前会先检查 `Path.exists()`
- 随后直接 `read_text()`

这带来四类问题：

### 1. 外部调用无法稳定引用 agent 本机路径

- 外部系统通常只知道“要执行哪份星图”
- 它不应知道 agent 部署在哪台机器、哪个目录、文件是否已同步
- 让调用方直接传 `/Users/.../api_batch.md` 或 `C:\\...\\api_batch.md` 是错误耦合

### 2. 输入入口列表的协议语义不清

- 当前更像“请在本地打开一个 pack 文件执行”
- 这不是任务内容本身
- 这只是内容定位方式的一种

### 3. CLI、HTTP、WS 三条入口没有统一输入模型

- CLI 用本机文件路径
- `/mind` 更适合传任务内容
- `agent ws` 需要的是稳定、可恢复、可追踪的执行源

### 4. 安全与审计边界不够清楚

- 本机路径天然带来目录穿透、越权读取和部署差异
- URL、附件、内联文本又需要鉴权、缓存、超时和来源标识

## 设计目标

### 核心目标

- `--code` 不再以“文件路径”作为唯一输入语义
- 所有入口统一落到同一种 `CodeSource` 模型
- `Pack.pack_parse()` 继续只消费文本，不感知来源差异
- `agent` 的输入入口列表可以执行内联文本、URL 或服务端制品

### 兼容目标

- 现有 `mind --chat --code a.md b.md` 保持可用
- 现有星图文本语法不变
- 现有批跑执行顺序、重试、前后置、规则逻辑不变
- 现有 `agent` 的任务下发主协议不推翻，只扩展输入语义

### 非目标

- 不重写星图 DSL
- 不把 `code` 和 `plan` 合并
- 不在第一阶段引入远端制品上传中心的完整实现
- 不要求所有来源都必须持久缓存

## 总体方案

把 `--code` 的输入统一抽象为 `CodeSource`，所有入口先解析成 `CodeSource` 列表，再执行。

统一流程：

```text
CLI / REPL / HTTP / WS
  ↓
resolve_code_sources(...)
  ↓
list[CodeSourceResolved]
  ↓
Pack.pack_parse(text)
  ↓
batch runtime
```

这里的关键变化是：

- 以前的批跑入口是“收路径，再读文件”
- 以后是“收来源，再解成文本”

## 源模型

建议引入三层模型。

### 1. `CodeSourceRef`

表示调用方声明的“源引用”，还没有真正取回内容。

建议字段：

```python
class CodeSourceRef(BaseModel):
    kind: Literal["file", "stdin", "inline", "url", "artifact"]
    name: str | None = None
    path: str | None = None
    content: str | None = None
    url: str | None = None
    artifact_id: str | None = None
    headers: dict[str, str] | None = None
    auth: dict[str, Any] | None = None
    timeout_sec: float | None = None
    cache_ttl_sec: int | None = None
    metadata: dict[str, Any] | None = None
```

### 2. `CodeSourceResolved`

表示已经可执行的源内容。

建议字段：

```python
class CodeSourceResolved(BaseModel):
    kind: Literal["file", "stdin", "inline", "url", "artifact"]
    name: str
    content: str
    source_id: str
    identity: str
    cache_hit: bool = False
    fetched_at_ms: int | None = None
    content_sha256: str
    content_bytes: int
    display_origin: str
    trace: dict[str, Any] = Field(default_factory=dict)
```

### 3. `CodeSourcePolicy`

表示一次调用的解析策略，而不是单个源自身的属性。

建议字段：

```python
class CodeSourcePolicy(BaseModel):
    allow_file: bool = True
    allow_stdin: bool = True
    allow_inline: bool = True
    allow_url: bool = False
    allow_artifact: bool = False
    url_timeout_sec: float = 15.0
    max_content_bytes: int = 2_000_000
    max_source_count: int = 20
    enable_cache: bool = True
    default_cache_ttl_sec: int = 300
    allowed_url_schemes: list[str] = ["https"]
    allowed_url_hosts: list[str] = []
    redact_query_in_logs: bool = True
```

## 支持的来源类型

### `file`

面向本地 CLI 兼容。

- 输入：`path`
- 解析：读取本地文件
- 用途：继续支持 `mind --code a.md`
- 风险：仅适合本机入口，不适合外部协议主路径

### `stdin`

面向 shell 管道和动态拼装。

- 输入：`-` 或明确 `kind=stdin`
- 解析：从标准输入读取
- 用途：`cat case.md | mind --plan --code -`

### `inline`

面向 HTTP / WS / SDK 的最小可用路径。

- 输入：`content`
- 解析：直接执行文本
- 用途：最适合 `/mind`
- 优点：不依赖本机路径

### `url`

面向集中托管星图。

- 输入：`url`
- 解析：拉取远端文本
- 用途：跨环境复用、CI 调度、集中回归
- 风险：需要鉴权、缓存、超时、白名单

### `artifact`

面向平台内部对象存储或附件中心。

- 输入：`artifact_id`
- 解析：通过平台侧制品服务获取内容
- 用途：服务端统一控权限与版本
- 说明：可以晚于 `inline/url` 实现

## 新的调用面

### CLI

保留现有：

```bash
mind --chat --code a.md b.md
```

建议新增：

```bash
mind --chat --code -
mind --chat --code inline:...
mind --chat --code https://example.com/a.md
```

第一阶段也可以不新增额外参数，而是先让 `--code` 支持：

- 普通路径
- `-`
- `inline:...`
- `https://...`

但长期更推荐显式参数，因为：

- 解析规则更稳定
- shell 转义更可控
- 错误提示更清晰

### `/mind`

对外不要传本机路径，应该传输入入口列表：

```json
{
  "target": {
    "agent_id": "mind-prod-01"
  },
  "task": {
    "kind": "code",
    "profile": [
      "inline:# name: smoke\n检查登录接口..."
    ]
  },
  "execution": {
    "mode": "plan"
  }
}
```

或：

```json
{
  "task": {
    "kind": "code",
    "profile": [
      "https://example.com/packs/login-smoke.md"
    ]
  }
}
```

### `agent ws`

现有 `mind.forward` 不应推翻，只扩展输入语义：

- 文本输入与输入入口列表可以并存
- 文本输入优先，输入入口列表次之
- 输入入口列表直接承载 `mind_pack(...)` 的来源数组

## `mind.forward` 扩展建议

当前订阅端主要依赖：

- 消息类型
- 任务与会话关联标识
- 任务调用标识
- 执行模式
- 输入入口列表
- 文本输入

建议扩展为：

```json
{
  "type": "mind.forward",
  "session_id": "sess_xxx",
  "message_id": "msg_xxx",
  "cid": "cid_xxx",
  "sid": "sid_xxx",
  "seq": 12,
  "payload": {
    "call_id": "call_xxx",
    "mode": "plan",
    "profile": [
      "inline:# name: smoke\n检查登录接口..."
    ],
    "message": null
  }
}
```

兼容顺序建议：

1. 文本输入非空时，按普通单次请求执行
2. 文本输入为空且输入入口列表非空时，按批跑入口执行
3. 两者都为空时，按协议错误处理

## 批跑执行器改造

### 当前状态

当前批跑执行器的关键签名更接近：

- `mind.mind_pack(code: list[str], mode: ...)`
- `_resolve_code_paths(code: list[str]) -> list[Path]`
- `_run_pack_file(file_path: Path, ...)`

### 目标状态

建议改成：

- `mind.mind_pack(sources: list[CodeSourceRef] | list[str], mode: ...)`
- `resolve_code_sources(...) -> list[CodeSourceResolved]`
- `_run_pack_source(source: CodeSourceResolved, ...)`

执行器层的关键变化：

- 运行日志不再只打印 `file=...`
- 应打印 `origin=... kind=... source_id=...`
- 事件上报中保留来源标识，方便回放和审计

## 缓存策略

完整版设计里必须把缓存明确下来，否则 URL 和 artifact 会把执行链路拉得很抖。

### 缓存目标

- 降低重复拉取 URL 的开销
- 让一次批跑中的多轮重复执行可以复用相同内容
- 允许恢复链路中再次执行同一 `source` 时快速命中

### 缓存键

建议缓存键使用规范化来源标识，而不是原始输入字符串。

示例：

- `file`: `file:/abs/path/to/a.md`
- `url`: `url:https://example.com/packs/a.md`
- `artifact`: `artifact:pack_123`
- `inline`: `inline:sha256:<content_sha256>`
- `stdin`: `stdin:sha256:<content_sha256>`

### 缓存值

- `content`
- `content_sha256`
- `fetched_at_ms`
- `expires_at_ms`
- `etag` 可选
- `last_modified` 可选
- `source_headers` 可选

### 缓存范围

建议分两级：

- 进程内内存缓存
- 可选磁盘缓存

第一阶段只做进程内缓存即可。

磁盘缓存可后续落到：

- `src_total_place/cache/code_sources/`

### TTL 建议

- `inline` 和 `stdin` 不需要缓存复拉，但可以保留 hash
- `file` 默认不缓存跨进程内容，只缓存本次运行已读文本
- `url` 默认 `300s`
- `artifact` 默认 `300s`

### 失效策略

- 超过 TTL 即失效
- URL 如果拿到 `etag/last-modified`，可以尝试条件请求
- `file` 在同一次运行内可以按 `mtime + size` 做轻量校验

## 超时策略

不同来源必须有不同超时边界。

### 解析超时

- `file`: 2 秒
- `stdin`: 跟随整体命令执行，不单独设网络超时
- `inline`: 不需要额外超时
- `url`: 默认 15 秒
- `artifact`: 默认 15 秒

### 批次超时

如果一轮任务里加载多个 `source`，建议：

- 单源超时独立计算
- 总超时由调用方或上层 `execution.timeout_sec` 控制

### 错误语义

建议把超时错误显式区分为：

- `source_timeout`
- `source_auth_failed`
- `source_not_found`
- `source_too_large`
- `source_unsupported`

## URL 鉴权设计

URL 一旦放开，必须明确鉴权模型。

### 支持方式

- 静态 header
- Bearer token
- Basic auth
- 签名 URL

### 请求模型建议

```json
{
  "kind": "url",
  "url": "https://example.com/packs/a.md",
  "auth": {
    "type": "bearer",
    "token": "xxx"
  },
  "headers": {
    "X-Pack-Version": "2026-04-01"
  }
}
```

### 安全约束

- 默认只允许 `https`
- 默认不打印敏感 query 和鉴权头
- 默认限制 host 白名单
- 默认限制最大响应体大小
- 默认限制重定向次数

### 不建议的做法

- 不要允许任意 `http://`
- 不要把完整 header 或 token 直接写入日志
- 不要把 URL 拉取实现成无限制转发器

## 来源标识设计

来源标识是完整版里必须补的能力，否则排查和审计会失真。

### 目标

- 同一份星图从哪里来，要能看出来
- 同一内容被重复执行，要能去重和对账
- 断线恢复、重放和日志回放时，要能定位原始来源

### 建议字段

- `source_id`
- `identity`
- `display_origin`
- `content_sha256`
- `resolved_kind`

示例：

```text
source_id=file:/tmp/a.md
identity=sha256:abc123...
display_origin=file:/tmp/a.md
```

```text
source_id=url:https://packs.example.com/a.md
identity=sha256:def456...
display_origin=url:https://packs.example.com/a.md
```

### 日志建议

批跑开始事件里附带：

- `source_id`
- `kind`
- `cache_hit`
- `content_sha256`
- `content_bytes`

不要打印：

- 完整 token
- 完整敏感 query
- 过长内联文本正文

## 兼容与迁移

建议分三阶段迁移。

### 阶段 1

把批跑执行器从“吃路径”改成“吃来源文本”。

- 引入 `CodeSourceRef`
- 让 CLI 继续只传路径
- 内部先转成 `kind=file`
- `_run_pack_file` 改成 `_run_pack_source`

### 阶段 2

增加 `stdin` 和 `inline`。

- CLI 支持 `--code -`
- 支持 `--code inline:...`
- `agent ws` 支持输入入口列表

### 阶段 3

增加 `url`、缓存、鉴权和可选 `artifact`。

- `/mind` 支持输入入口列表
- `agent ws` 支持 URL 形式的输入入口
- 增加缓存、超时、来源标识和审计字段

## 失败处理策略

### 单源失败

建议默认：

- 该 `source` 对应批次失败
- 若 `stop_on_fail=true` 则整个 pack 执行立即停止

### 多源批跑

如果一次提交带多个来源：

- 每个来源各自产生一组 `batch.start/batch.done`
- 来源间顺序应与输入顺序一致

### 错误可观测性

最终错误中至少包含：

- `kind`
- `origin`
- `source_id`
- `error_code`
- `human_message`

## 测试设计

完整版里必须加回归测试，否则很容易把老的 `--code path` 弄坏。

### 单元测试

建议覆盖：

- `file` 正常读取
- `file` 不存在
- `stdin` 正常读取
- `inline` 正常读取
- `url` 正常拉取
- `url` 超时
- `url` 401/403
- `url` 404
- `url` 超大响应体
- `inline` 与 `stdin` 的 hash 生成
- 缓存命中与失效

### 协议测试

建议覆盖：

- `mind.forward` 仅带文本输入
- `mind.forward` 仅带输入入口列表
- 文本输入与输入入口列表同时存在时按文本输入优先

### 批跑回归测试

建议覆盖：

- `mind --chat --code a.md`
- `mind --plan --code a.md b.md`
- `cat a.md | mind --plan --code -`
- `mind --chat --code inline:...`

### 恢复链路测试

建议覆盖：

- `agent` 收到任务下发消息
- `mind.received` 正常回发
- 断线后 `resume`
- `replay.batch` 中重复任务消息不会重复执行

## 实现切分建议

### 任务 1

新增源模型与解析器。

- 新建 `mind_app/modes/code_sources.py` 或同等模块
- 提供 `resolve_code_sources()`
- 先支持 `file`

### 任务 2

批跑执行器改造。

- `mind_pack()` 改为吃来源
- `_run_pack_source()` 替换 `_run_pack_file()`

### 任务 3

CLI 增加 `stdin/inline`。

- 先做不涉及网络的来源
- 保证本地功能闭环

### 任务 4

`agent ws` 使用“文本输入优先，输入入口列表次之”
- 优先级清晰

### 任务 5

URL、缓存、鉴权、超时和来源标识。

- 独立实现
- 独立测试
- 不和基础执行器重构混在一次提交里

## 建议的目录变更

如果按当前仓库结构实现，建议新增：

```text
mind_app/modes/code_sources.py
mind_app/modes/code_cache.py
tests/test_code_sources.py
tests/test_agent_code_source_protocol.py
tests/test_batch_code_sources.py
```

如果暂时没有统一测试目录，也至少补同模块级测试或最小自验证脚本。

## 最终结论

这轮改造不该被理解为“让外部也能传本机路径”，而应该被理解为：

- 统一 `code` 的输入语义
- 让 `CLI / HTTP / WS` 都基于同一个源抽象
- 把本机文件路径降级为一种兼容来源

建议最终稳定口径：

- `path` 是实现细节，不是外部协议主语义
- 输入入口列表才是 `code` 的正式输入模型
- `inline` 是外部调用默认推荐路径
- `url` 和 `artifact` 是平台化扩展路径
- `file` 只作为 CLI 兼容入口保留
