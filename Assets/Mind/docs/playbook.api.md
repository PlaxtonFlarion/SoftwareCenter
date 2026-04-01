# 接口实战

主 README 只负责接口入口和边界；协议样例、批量星图和高阶链路继续看这里。
重点是先判断当前任务是不是协议与校验类问题，再给出统一字段边界和协议入口。

## 先判断是不是这页的范围

- 你要发 HTTP、SSE、WebSocket、GraphQL、TCP、UDP、SMTP、IMAP、FTP 请求：看这里
- 你要先做模板展开或字段校验，再决定是否真的发请求：看这里
- 你要处理 JWT、RSA、AES、摘要和签名：优先跳到安全工具文档，不要把安全逻辑硬塞进协议层
- 你只是想确认主入口和模式边界：先回 README，不必先读完整接口文档

## 怎么读这页
- 先看协议覆盖，确认当前场景是否真的属于协议与校验这一类
- 再看统一约定和字段边界，用同一套结构组织单请求或批量请求
- 最后按协议挑样例，不要把所有协议从头读到尾
- 如果你在写 `--code`，结构层先配合 `cli-code.md`，执行语义再配合 `cli-code-advanced.md`

## 协议覆盖
- `HTTP / SSE / WebSocket / GraphQL`
- `TCP / UDP`
- `SMTP / IMAP / FTP`
- 单请求与批量星图
- `render / validate / extract / asserts`

一句话理解：

- `render / validate`：预执行
- `*_request`：执行单个请求
- `*_batch`：执行一组同协议请求

[## 统一约定
- 单请求场景里，把协议原生参数写进 `request`
- 批量场景里，把共享默认值写进 `env`，逐项差异写进 `items[].request`
- 执行前会先把 `env + 当前 item.request` 物化成最终请求；不要假设所有字段都是简单覆盖
- 提取结果统一放在 `extract`
- 验收规则统一放在 `asserts`
- 需要批次级默认行为时，用 `cfg / global_rule / global_prefix / global_suffix`]()

再强调一次边界：
- `render`：只做模板展开和默认值物化，不执行协议请求
- `validate`：只做模板展开、默认值物化和基础字段校验，不执行协议请求
- `*_request`：执行单个协议请求
- `*_batch`：执行一组同协议请求

如果你只记一条：

- 单请求的协议原生参数留在 `request`
- 批量请求的协议原生参数统一写进 `items[].request`
- 批量共享默认值留在 `env`
- 提取写 `extract`
- 验收写 `asserts`

### 最新星图接口约定
- 单请求星图统一使用：`request`、`template_vars`
- 单请求的 `render / validate` 可额外接收 `env`，用于预览或校验共享默认值，不会改变正式执行工具的输入边界
- 批量星图统一使用：`env`、`items`、`template_vars`、`concurrency`、`fail_fast`
- 不再使用旧的单体 `payload = {...}` 形式，也不再使用 `options.fail_fast` / `vars`
- MCP 工具边界：
  - 单请求：`nexus_http_request` / `nexus_sse_request` / `nexus_ws_request` / `nexus_graphql_request` / `nexus_tcp_request` / `nexus_udp_request` / `nexus_smtp_request` / `nexus_imap_request` / `nexus_ftp_request`
  - 批量请求：`nexus_http_batch` / `nexus_sse_batch` / `nexus_ws_batch` / `nexus_graphql_batch` / `nexus_tcp_batch` / `nexus_udp_batch` / `nexus_smtp_batch` / `nexus_imap_batch` / `nexus_ftp_batch`
  - 预执行：`nexus_render_request` / `nexus_validate_request` / `nexus_render_batch` / `nexus_validate_batch`

最小示意：

```text
request = {
  "method": "GET",
  "url": "/health"
}
```

```text
env = {
  "base_url": "https://api.example.com",
  "headers": {
    "Authorization": "Bearer {{ token }}"
  }
}

items = [
  {"request": {"method": "GET", "url": "/health"}},
  {"request": {"method": "GET", "url": "/profile"}}
]
```

### 内部职责边界
- `ExtractService`：只负责路径提取、过滤与后处理
- `AssertionService`：只负责断言比较运算
- `CheckService`：负责 `extract + asserts` 的检查编排与结果收尾
- `PackBuilder`：只负责构造统一返回包，不再承载检查逻辑

### Nexus 字段边界
- 单请求里，`request` 始终承载协议原生字段，不把 `url / host / headers / body / query` 这类协议参数抬到工具顶层
- 批量请求里，每个 item 都使用统一结构：协议原生字段写进 `items[].request`
- `env` 在批量工具里用于共享默认值，在单请求的 `render / validate` 里也可作为预执行默认值；执行前会先物化最终请求
- 当前默认物化语义：标量字段由当前请求覆盖，`headers / json / json_body / params / form / variables` 做对象合并，其余字段按当前请求覆盖
- `extract` 和 `asserts` 都作用于最终结果包中的 `data`
- 如果你只想确认模板展开结果，用 `render`
- 如果你想先检查必填字段和请求结构，用 `validate`
- 如果你要真实发请求，才用 `*_request` 或 `*_batch`

### SSE 批量硬性约束
- SSE 单条请求用 `nexus_sse_request`
- SSE 多条独立用例用 `nexus_sse_batch`
- `1` 条 case = `items` 中的 `1` 个独立 item，其协议字段写在 `item.request`
- 多条 `user_input` 必须展开成多个独立 `items`
- 不允许把多条 `user_input` 合并进同一个 `request`
- 不允许把 case 级字段写到 `env`
- 不允许把 case 级字段写到全局 `template_vars`
- 不允许假设 batch 会为每个 item 自动注入独立变量
- `env` 和 `items` 必须传原生结构化对象，不要传字符串化 JSON
- `concurrency` 和 `fail_fast` 需要按预期行为显式传值，不要省略后依赖默认值
- 若出现参数校验错误，必须修正字段类型或结构，不要通过删除字段绕过校验

### SSE 批量字段放置规则
- `env` 只放所有 `items` 共享且不随 case 变化的默认参数
- `items[].request` 只放当前 case 的差异字段
- `user_input` 必须写入 `items[].request.json.user_input`
- `current_time` 必须写入 `items[].request.json.current_time`
- 不要把 `current_time` 放入 `env.json`
- 不要把 `user_input` 放入 `template_vars`
- 不要依赖 `{{user_input}}` 在 batch 中按 item 自动替换
- 若使用占位符，必须在提交工具前由上层先展开成最终字面值

### SSE 批量执行规则
- `concurrency > 1` 表示并发执行多个 SSE 请求
- `fail_fast = true` 表示任一 item 失败后，尽快停止剩余未完成项
- `fail_fast = false` 表示继续执行剩余 item
- 若预期 `5` 条并发执行，就必须显式传 `concurrency: 5`，省略字段不算传对参数
- 若预期失败后继续执行剩余项，就必须显式传 `fail_fast: false`，省略字段不算传对参数
- 若后续 item 依赖前一步提取结果参与模板渲染，必须使用 `concurrency = 1`
- 若只是多条独立 `user_input` 并发压测或回放，优先使用 batch

正确示意：

```text
tool: nexus_sse_batch
args:
  concurrency: 5
  fail_fast: true
  env:
    method: POST
    url: http://10.0.80.65:8081/light1d/light/sse/generate
    timeout: 60
    headers:
      Accept: text/event-stream
      Content-Type: application/json
      Authorization: Bearer es_fuzzy_search_token_2024
    json:
      user_id: dage
      device_id: SS20250029_588C810F0842
      type: text
      language: zh
      zone: GMT+8
      sku: PD20250029
      platform: Android
      conversation_id: 0
  items:
    - request:
        json:
          user_input: 第一条 case 的原文
          current_time: 第一条 case 的毫秒时间戳
    - request:
        json:
          user_input: 第二条 case 的原文
          current_time: 第二条 case 的毫秒时间戳
```

错误示意 1：

```text
args:
  template_vars:
    user_input: xxx
  items:
    - request:
        json: {}
```

原因：
- batch 只有一份全局 `template_vars`，不能为每个 item 提供独立 `user_input`

错误示意 2：

```text
args:
  env:
    json:
      current_time: {{now_ms()}}
  items:
    - request:
        json:
          user_input: A
    - request:
        json:
          user_input: B
```

原因：
- `env` 会在批次级统一渲染，通常导致整批 item 共用同一个时间戳

错误示意 3：

```text
args:
  env: {...}
  items: [...]
```

原因：
- 如果你的目标是 `5` 条并发且失败后继续执行，就不能省略 `concurrency` 和 `fail_fast`
- 省略后会回退到工具默认值，通常等价于 `concurrency = 1`、`fail_fast = true`
- 这不算参数传递正确

错误示意 4：

```text
args:
  concurrency: "5"
  fail_fast: "false"
  env: "{...}"
  items: "[...]"
```

原因：
- `concurrency` 必须是整数
- `fail_fast` 必须是布尔值
- `env` 必须是对象
- `items` 必须是数组对象
- 参数校验失败后，应修正类型，不要删除字段绕过校验

展开规则：
- 若一组有 `5` 条 `user_input`，则展开为 `5` 个 `items`
- 使用一次 `nexus_sse_batch` 提交
- `concurrency` 设为 `5`
- `fail_fast` 按预期行为显式写出，不要省略
- 每个 item 单独写自己的 `user_input` 和 `current_time`

常见提取路径：
- `http / graphql`：`response.status`、`response.body_json`、`response.media`
- `sse`：`response.events`、`response.media`
- `ws`：`response.messages`、`response.media`
- `tcp`：`response.body_text`、`response.messages`、`response.remote`、`response.body_hex`
- `udp`：`response.body_text`、`response.remote`、`response.body_hex`
- `smtp`：`response.action`、`response.ehlo`、`response.noop`、`response.send`、`response.attachments`
- `imap`：`response.login`、`response.select`、`response.search`、`response.fetch`、`response.parsed_messages`、`response.media`
- `ftp`：`response.welcome`、`response.list`、`response.download_binary`、`response.upload_text`、`response.upload_binary`、`response.media`

## 模板 Helper
- 当前模板层已支持轻量 helper，可直接在 `request`、`env`、`items[].request`、`template_vars` 中使用 `{{ ... }}`
- 适合迁入模板层的是轻量、纯函数、无副作用的数据准备逻辑
- `JWT / RSA / AES / HMAC / 签名串` 这类确定性安全逻辑仍建议留在专用安全工具中
- 如果你要系统看 helper 分类、组合写法和模板层边界，直接看 [模板能力](playbook.template.md)
- 如果你要看 `security_digest / security_jwt / security_crypto / security_aes` 的能力边界，直接看 [安全工具](playbook.security.md)

已支持的 helper：
- `now_s()`
  返回当前 Unix 秒级时间戳。适合请求头时间、签名前的轻量时间字段、简单时序标记。
- `now_ms()`
  返回当前 Unix 毫秒级时间戳。适合请求体里的 `current_time`、事件打点、需要更细粒度时间的接口字段。
- `now_iso()`
  返回当前 ISO 8601 时间字符串。适合日志字段、可读时间、服务端要求 ISO 时间格式的场景。
- `format_ts(ts)`
  把已有时间戳格式化成标准时间字符串。适合把上游提取出来的时间值转成人类可读格式后再提交。
- `offset_ts(ts, ...)`
  在已有时间戳基础上做偏移。适合生成过期时间、延后时间、窗口起止时间等派生字段。
- `uuid4()`
  生成随机 UUID。适合请求 ID、trace ID、幂等键、一次性业务标识。
- `nonce(n)`
  生成指定长度的随机 nonce。适合轻量防重放字段、随机串参数、临时 token 片段。
- `pick(obj, "a.b.0", default)`
  从对象路径中取值，取不到时回退到默认值。适合从 `env`、提取结果或复杂对象中安全读取嵌套字段。
- `coalesce(a, b, c)`
  返回第一个非空值。适合多来源回退，例如优先业务值，缺失时回退到默认值或环境变量。
- `b64encode(v)`
  把值编码成 Base64。适合基础认证、二进制转文本、接口要求 Base64 载荷的场景。
- `b64decode(v)`
  把 Base64 文本解码回原值。适合服务端返回 Base64 内容后，在模板层先还原再继续使用。
- `hex_encode(v)`
  把值编码成十六进制。适合原始字节、签名前中间值、协议字段要求 hex 文本的场景。
- `hex_decode(v)`
  把十六进制文本解码回原值。适合服务端返回 hex 内容后做后续拼装。
- `json_dumps(v)`
  把对象序列化成 JSON 字符串。适合接口字段本身要求字符串化 JSON，而不是对象结构的场景。
- `json_loads(v)`
  把 JSON 字符串解析成对象。适合上游给的是 JSON 文本，但当前模板逻辑需要对象字段时使用。
- `urlencode(obj)`
  把对象编码成 URL query 字符串。适合拼查询串、表单串、回调参数。
- `urldecode(text)`
  解析 URL 编码文本。适合把已有 query 或编码参数还原后再继续处理。
- `dict_merge(a, b)`
  合并两个对象，通常用于构造 headers、params、variables 等结构。适合在模板层补默认值再叠加局部覆盖。
- `sort_keys(obj)`
  按 key 排序对象。适合生成稳定字典结构，便于签名前预处理或做稳定比对。
- `canonical_query(obj)`
  把对象转成稳定排序的 query 字符串。适合签名前 query 归一化、稳定串比较、可重复构造 URL 参数。
- `gzip_encode(v)`
  用 gzip 压缩值。适合服务端要求 gzip 载荷，或要模拟压缩上传的场景。
- `gzip_decode(v)`
  解 gzip 内容。适合服务端返回 gzip 文本或上游给的是压缩内容时做恢复。
- `zlib_encode(v)`
  用 zlib 压缩值。适合协议明确要求 zlib 编码的场景。
- `zlib_decode(v)`
  解 zlib 内容。适合继续处理 zlib 压缩后的响应或中间值。

示意：

```text
request = {
  "url": "/api/{{ tenant }}/profile",
  "headers": {
    "X-Request-Id": "{{ uuid4() }}",
    "X-Timestamp": "{{ now_s() }}"
  }
}
```

## 提取与验收最小样例

`extract` 和 `asserts` 的职责很简单：

- `extract`：从最终 `pack.data` 提取你关心的字段
- `asserts`：用自然语言写通过条件，例如“response.status 等于 200”

它们在星图里是独立块：
- `request` 负责协议原生参数
- `extract` 负责结果提取
- `asserts` 负责通过条件
- 不要求和 `request` 写在一起，只要语义归属清楚即可

请求示意：

```text
request = {
  "method": "GET",
  "url": "/health"
}
```

提取与断言示意：

```text
extract:
- status 取 response.status
- ok 取 response.body_json.ok
```

```text
asserts:
- response.status 等于 200
- response.body_json.ok 等于 true
```

这已经够表达断言和提取的最小结构了，后面不再重复展开长样例。

建议：

- 只提取真正需要回看的字段
- 断言优先写最终是否通过的业务条件
- 提取是“为了回看”，断言是“为了判定”

如果你要系统看签名、JWT、RSA、AES 的工具能力，继续看 [安全工具](playbook.security.md)。

## 协议选择
- `HTTP`：普通接口验证、鉴权、分页和 JSON 接口回归
- `SSE`：流式事件消费和事件序列验收
- `WebSocket`：一次性建连、发送、接收和消息断言
- `GraphQL`：query / mutation 的单次或批量调用
- `TCP / UDP`：低层原始报文链路校验，不负责高级协议语义
- `SMTP / IMAP / FTP`：邮件与文件传输链路的协议级验证

## 高阶星图
- 安全场景可组合 `JWT / RSA / nonce / timestamp / signature`
- 批量场景优先复用同一份 `env` 和模板变量，避免把共享字段复制进每个 step
- 结果回放不必写进文档；重点保留星图意图、提取字段和通过条件

如果你要把接口工具真正写进 `--code`，推荐按这个顺序读：
- 先看 [星图协议](cli-code.md)，确认星图结构、文件格式和最小层级
- 再看 [星图深入说明](cli-code-advanced.md)，确认覆盖优先级、批跑控制和常见误写

这两页讲的是星图怎么组织与执行，不是再重复协议字段表。

## 本地 Mock 约定
- 文档不再内嵌 mock 服务代码
- 如果需要本地 mock，按协议边界自行实现最小服务即可
- 服务只要能覆盖请求字段、返回结构和验收条件即可，不必复刻文档历史样例
