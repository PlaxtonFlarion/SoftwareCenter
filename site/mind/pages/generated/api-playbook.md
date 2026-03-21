# 接口实战教学

README 只保留接口能力边界、统一约定和入口说明；需要协议样例、批量蓝本或高阶安全链路时，直接看这里。

## 阅读顺序
- 先看协议覆盖，确认当前场景是否落在 `bench.nexus`
- 再看统一约定，按同一套字段边界组织蓝本
- 最后按协议挑样例，不要把所有协议从头读到尾

## 协议覆盖
- `HTTP / SSE / WebSocket / GraphQL`
- `TCP / UDP`
- `SMTP / IMAP / FTP`
- 单请求与批量蓝本
- `render / validate / extract / asserts`

## 统一约定
- 单请求场景里，把协议原生参数写进 `request`
- 批量场景里，把共享默认值写进 `env`，逐项差异写进 `items[].request`
- 提取结果统一放在 `extract`
- 验收规则统一放在 `asserts`
- 需要批次级默认行为时，用 `cfg / global_rule / global_prefix / global_suffix`

再强调一次边界：
- `render`：只做模板展开和默认值合并，不执行协议请求
- `validate`：只做模板展开和基础字段校验，不执行协议请求
- `*_request`：执行单个协议请求
- `*_batch`：执行一组同协议请求

### 最新星图接口约定
- 单请求蓝本统一使用：`request`、`template_vars`
- 批量蓝本统一使用：`env`、`items`、`template_vars`、`concurrency`、`fail_fast`
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
- `request` 始终承载协议原生字段，不把 `url / host / headers / body / query` 这类协议参数抬到工具顶层
- `env` 只在批量任务里出现，用作共享默认值；`items[].request` 会覆盖同名字段
- `extract` 和 `asserts` 都作用于最终结果包中的 `data`
- 如果你只想确认模板展开结果，用 `render`
- 如果你想先检查必填字段和请求结构，用 `validate`
- 如果你要真实发请求，才用 `*_request` 或 `*_batch`

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
- 如果你要系统看 helper 分类、组合写法和模板层边界，直接看 [模板能力实战](template-playbook.md)
- 如果你要看 `security_digest / security_jwt / security_crypto / security_aes` 的能力边界，直接看 [安全工具实战](security-playbook.md)

已支持的 helper：
- 标识与时间：`now_s()`、`now_ms()`、`now_iso()`、`format_ts(ts)`、`offset_ts(ts, ...)`、`uuid4()`、`nonce(n)`
- 取值与回退：`pick(obj, "a.b.0", default)`、`coalesce(a, b, c)`
- 编解码：`b64encode(v)`、`b64decode(v)`、`hex_encode(v)`、`hex_decode(v)`、`json_dumps(v)`、`json_loads(v)`
- URL 与结构：`urlencode(obj)`、`urldecode(text)`、`dict_merge(a, b)`、`sort_keys(obj)`、`canonical_query(obj)`
- 压缩：`gzip_encode(v)`、`gzip_decode(v)`、`zlib_encode(v)`、`zlib_decode(v)`

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

它们在蓝本里是独立块：
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

如果你要系统看签名、JWT、RSA、AES 的工具能力，继续看 [安全工具实战](security-playbook.md)。

## 协议选择
- `HTTP`：普通接口验证、鉴权、分页和 JSON 接口回归
- `SSE`：流式事件消费和事件序列验收
- `WebSocket`：一次性建连、发送、接收和消息断言
- `GraphQL`：query / mutation 的单次或批量调用
- `TCP / UDP`：低层原始报文链路校验，不负责高级协议语义
- `SMTP / IMAP / FTP`：邮件与文件传输链路的协议级验证

## 高阶蓝本
- 安全场景可组合 `JWT / RSA / nonce / timestamp / signature`
- 批量场景优先复用同一份 `env` 和模板变量，避免把共享字段复制进每个 step
- 结果回放不必写进文档；重点保留蓝本意图、提取字段和通过条件

如果你要把接口工具真正写进 `--code`，推荐先看 [星图协议深入说明](cli-code.md) 里的“复杂接口蓝本怎么读”。
那里重点讲的是蓝本如何编排步骤，不是再重复协议字段表。

## 本地 Mock 约定
- 文档不再内嵌 mock 服务代码
- 如果需要本地 mock，按协议边界自行实现最小服务即可
- 服务只要能覆盖请求字段、返回结构和验收条件即可，不必复刻文档历史样例
