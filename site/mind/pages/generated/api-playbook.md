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
- 单请求优先写 `request = {...}`
- 批量任务把共享配置写进 `env = {...}`，逐项差异写进 `items[].request`
- 提取结果统一落在 `extract = {...}`
- 验收规则统一落在 `asserts = [...]`
- 需要批次级默认行为时，用 `cfg / global_rule / global_prefix / global_suffix`

### 最新星图接口约定
- 单请求蓝本统一使用：`request`、`template_vars`
- 批量蓝本统一使用：`env`、`items`、`template_vars`、`concurrency`、`fail_fast`
- 不再使用旧的单体 `payload = {...}` 形式，也不再使用 `options.fail_fast` / `vars`
- MCP 工具边界：
  - 单请求：`nexus_http_request` / `nexus_sse_request` / `nexus_ws_request` / `nexus_graphql_request` / `nexus_tcp_request` / `nexus_udp_request` / `nexus_smtp_request` / `nexus_imap_request` / `nexus_ftp_request`
  - 批量请求：`nexus_http_batch` / `nexus_sse_batch` / `nexus_ws_batch` / `nexus_graphql_batch` / `nexus_tcp_batch` / `nexus_udp_batch` / `nexus_smtp_batch` / `nexus_imap_batch` / `nexus_ftp_batch`
  - 预执行：`nexus_render_request` / `nexus_validate_request` / `nexus_render_batch` / `nexus_validate_batch`

### 内部职责边界
- `ExtractService`：只负责路径提取、过滤与后处理
- `AssertionService`：只负责断言比较运算
- `CheckService`：负责 `extract + asserts` 的检查编排与结果收尾
- `PackBuilder`：只负责构造统一返回包，不再承载检查逻辑

### Nexus 字段模板
- `request` 始终传协议原生字段，不把协议参数抬到工具顶层
- `extract` / `asserts` 作用于最终 `pack.data`
- `http / graphql` 常见提取路径：`response.status`、`response.body_json`、`response.media`
- `tcp`：`response.body_text`、`response.messages`、`response.remote`、`response.body_hex`
- `udp`：`response.body_text`、`response.remote`、`response.body_hex`
- `smtp`：`response.action`、`response.ehlo`、`response.noop`、`response.send`、`response.attachments`
- `imap`：`response.login`、`response.select`、`response.search`、`response.fetch`、`response.parsed_messages`、`response.media`
- `ftp`：`response.welcome`、`response.list`、`response.download_binary`、`response.upload_text`、`response.upload_binary`、`response.media`

## 模板 Helper
- 当前模板层已支持轻量 helper，可直接在 `request`、`env`、`items[].request`、`template_vars` 中使用 `{{ ... }}`
- 适合迁入模板层的是轻量、纯函数、无副作用的数据准备逻辑
- `JWT / RSA / AES / HMAC / 签名串` 这类确定性安全逻辑仍建议留在专用安全工具中

已支持的 helper：
- 标识与时间：`now_s()`、`now_ms()`、`now_iso()`、`format_ts(ts)`、`offset_ts(ts, ...)`、`uuid4()`、`nonce(n)`
- 取值与回退：`pick(obj, "a.b.0", default)`、`coalesce(a, b, c)`
- 编解码：`b64encode(v)`、`b64decode(v)`、`hex_encode(v)`、`hex_decode(v)`、`json_dumps(v)`、`json_loads(v)`
- URL 与结构：`urlencode(obj)`、`urldecode(text)`、`dict_merge(a, b)`、`sort_keys(obj)`、`canonical_query(obj)`
- 压缩：`gzip_encode(v)`、`gzip_decode(v)`、`zlib_encode(v)`、`zlib_decode(v)`

示例：
```text
request = {
    "url": "/api/{{ tenant }}/profile",
    "headers": {
        "Authorization": "Bearer {{ token }}",
        "X-Req-Id": "{{ uuid4() }}",
        "X-Ts": "{{ now_s() }}"
    }
}
```

## 协议选择
- `HTTP`：普通接口验证、鉴权、分页、上下文透传
- `SSE`：流式事件消费、增量输出验收
- `WebSocket`：会话态交互、事件回包校验
- `GraphQL`：查询与变更、字段级断言
- `TCP / UDP`：原始报文链路
- `SMTP / IMAP / FTP`：收发件、附件、文件传输

## 高阶蓝本
- 安全场景可组合 `JWT / RSA / nonce / timestamp / signature`
- 批量场景优先复用同一份 `env` 和模板变量，避免把共享字段复制进每个 step
- 结果回放不必写进文档；重点保留蓝本结构、提取字段和通过条件

## 本地 Mock 约定
- 文档不再内嵌 mock 服务代码
- 如果需要本地 mock，按协议边界自行实现最小服务即可
- 服务只要能覆盖请求字段、返回结构和验收条件即可，不必复刻文档历史样例
