# 模板能力

这页聚焦模板 helper、能力边界和签名前置数据准备。

## 先判断是不是这页的范围

- 你要在 `request / env / template_vars / items[].request` 里准备动态值：看这里
- 你要做时间戳、nonce、query 规范化、轻量编码转换：看这里
- 你要做摘要、JWT、RSA、AES、HMAC 等确定性安全计算：优先去安全工具文档
- 你只是想确认协议字段该怎么写：先回接口文档，不必先把模板文档读完

## 怎么读这页

- 先看“设计定位”，确认模板层到底承接什么，不承接什么
- 再看“能放在哪些位置”和 helper 分类，判断动态值应该写在哪里
- 最后看组合写法和模板层与安全工具的分工，不要一开始就往模板层堆所有逻辑

## 这页解决什么问题

- 模板层到底能做什么
- 哪些逻辑适合放模板里
- 哪些逻辑应该交给 `security_*`
- `request / env / template_vars / items[].request` 里怎么用模板

## 设计定位

当前模板能力已经不是一个“纯字符串替换器”，而是一个轻量的数据准备层。

它适合做：

- 时间戳、随机值、请求 ID、nonce
- JSON / Base64 / Hex / URL 编解码
- query 拼装、字典排序、稳定 query 串生成
- 轻量 request/env 物化与合并
- 在模板里做纯函数、无副作用的数据准备

它不适合做：

- 复杂业务流程判断
- 带外部副作用的操作
- 重型安全实现的替代品

一句话理解：

- 模板层负责准备材料
- 安全层负责做确定性计算

## 能放在哪些位置

模板表达式 `{{ ... }}` 可以放在：

- `request`
- `env`
- `template_vars`
- `items[].request`

常见使用方式：

```text
request = {
  "url": "/api/{{ tenant }}/profile",
  "headers": {
    "X-Request-Id": "{{ uuid4() }}",
    "X-Timestamp": "{{ now_s() }}"
  }
}
```

- 这层只负责把动态值准备好，不负责描述完整请求结构
- batch 只有一份全局 `template_vars`；如果每个 item 都有独立值，必须直接写进各自的 `items[].request`

SSE batch 特别注意：

- 不要把每条 case 的 `user_input` 放进全局 `template_vars`
- 不要依赖 `{{user_input}}` 在 batch 中按 item 自动替换
- 不要把每条 case 的 `current_time` 放进 `env.json`
- 这类 case 级字段应在提交前先展开成字面值，再写入 `items[].request.json`
- `env` 和 `items` 必须传原生结构化对象，不要传字符串化 JSON
- `concurrency` 和 `fail_fast` 应按预期行为显式传值，不要在校验失败后通过省略字段回退默认值
- `render / validate / execute` 现在共享同一套 `env + request` 物化语义；不要再假设预执行和执行期会看到不同请求

## Helper 分类

### 1. 标识与时间

- `now_s()`
  返回当前 Unix 秒级时间戳。适合请求头时间、轻量时间字段、简单时序标记。
- `now_ms()`
  返回当前 Unix 毫秒级时间戳。适合请求体时间、事件打点、需要更细粒度时间的字段。
- `now_iso()`
  返回当前 ISO 8601 时间字符串。适合可读时间字段、日志时间、要求 ISO 格式的接口。
- `format_ts(ts, fmt="%Y-%m-%dT%H:%M:%SZ")`
  把已有时间戳格式化成指定字符串格式。适合把上游时间值转成接口要求的时间文本。
- `offset_ts(ts=None, seconds=0, minutes=0, hours=0, days=0, out="iso")`
  基于当前时间或指定时间做偏移，并按目标格式输出。适合生成过期时间、未来时间、窗口起止时间。
- `uuid4()`
  生成随机 UUID。适合请求 ID、trace ID、幂等键、关联标识。
- `nonce(length=16, alphabet=None)`
  生成指定长度的随机字符串。适合防重放 nonce、临时随机参数、一次性标识。

### 2. 取值与回退

- `pick(obj, "a.b.0", default=None)`
  按路径从对象中安全取值，取不到时回退到默认值。适合从 `template_vars / env / request` 中读取嵌套字段。
- `coalesce(a, b, c, ...)`
  返回第一个非空值。适合多来源 fallback，例如优先业务值，缺失时回退到环境值或默认值。

示例：

```text
{{ coalesce(pick(template_vars, "token"), pick(env, "token"), "default-token") }}
```

### 3. 编解码

- `b64encode(v)`
  把值编码成 Base64。适合基础认证、二进制转文本、接口要求 Base64 载荷的场景。
- `b64decode(v, as_text=True)`
  把 Base64 文本解码回原值。适合服务端返回 Base64 内容后先还原再参与后续拼装。
- `hex_encode(v)`
  把值编码成十六进制。适合原始字节、协议字段要求 hex 文本、签名前的中间值表达。
- `hex_decode(v, as_text=True)`
  把十六进制文本解码回原值。适合服务端返回 hex 内容后继续参与模板计算。
- `json_dumps(v, ensure_ascii=False, sort_keys=False)`
  把对象序列化成 JSON 字符串。适合接口字段要求字符串化 JSON，而不是原生对象时使用。
- `json_loads(v)`
  把 JSON 字符串解析成对象。适合上游给的是 JSON 文本，但当前模板逻辑需要读取内部字段时使用。

### 4. URL 与结构

- `urlencode(obj)`
  把对象编码成 URL query 字符串。适合拼查询串、表单串、回调参数。
- `urldecode(text)`
  把 URL 编码文本解码回可读内容。适合先还原已有 query 或编码参数再继续处理。
- `dict_merge(a, b, c, ...)`
  合并多个对象，后者覆盖前者。适合构造 headers、params、variables 等共享默认值叠加场景。
- `sort_keys(obj)`
  按 key 排序对象。适合生成稳定结构，便于签名前预处理或做稳定比较。
- `canonical_query(obj)`
  把对象转成稳定排序的 query 字符串。适合签名前 query 归一化、稳定 URL 参数生成。

示例：

```text
{{ canonical_query(dict_merge(env.query_defaults, request.params)) }}
```

### 5. 压缩与二进制转换

- `gzip_encode(v, ...)`
  用 gzip 压缩值。适合服务端要求 gzip 输入，或要模拟压缩请求体的场景。
- `gzip_decode(v, ...)`
  解 gzip 内容。适合服务端返回 gzip 文本或上游给的是压缩内容时先恢复原值。
- `zlib_encode(v, ...)`
  用 zlib 压缩值。适合协议明确要求 zlib 编码时使用。
- `zlib_decode(v, ...)`
  解 zlib 内容。适合继续处理 zlib 压缩后的响应或中间值。

## 常见组合写法

### 生成时间戳与请求 ID

```text
{
  "headers": {
    "X-Req-Id": "{{ uuid4() }}",
    "X-Ts": "{{ now_ms() }}"
  }
}
```

### 稳定 query 串

```text
{{ canonical_query(request.params or {}) }}
```

### 合并公共头

```text
{{ dict_merge(env.headers or {}, request.headers or {}) }}
```

### 生成 Basic 认证原文

```text
{{ b64encode(coalesce(env.username, '') + ':' + coalesce(env.password, '')) }}
```

## 模板层与安全工具怎么分工

推荐分工：

- 模板层：准备输入材料
- `security_*`：负责摘要、HMAC、JWT、RSA、AES 这类确定性安全能力

例如 HMAC 场景：

1. 模板层生成 canonical query / body string / timestamp
2. `security_digest` 计算 `hmac_sha256`
3. 把签名结果回填到请求头

所以：

- query 排序、JSON 稳定序列化：放模板层
- `hmac_sha256 / jwt / rsa_sign`：放 `security_*`

## 为什么不建议继续把所有能力塞进模板层

`template.py` 现在已经偏大而全。

继续往里塞 helper 会带来这些问题：

- 责任边界模糊
- 文档和可发现性下降
- 用户不知道该在模板层还是安全层处理

新增 helper 的标准应该尽量收紧：

- 纯函数
- 无副作用
- 明显属于“请求前的数据准备”
- 不重复实现 `security_*`

## 什么时候优先看这页

- 你在写协议与校验类星图
- 你要做 query / body / header 的模板化构造
- 你要准备签名前置材料
- 你想知道模板层和 `security_*` 的边界

## 相关文档

- [接口实战](playbook.api.md)
- [正文目录](docs-index.md)
- [星图协议](cli-code.md)
- [星图深入说明](cli-code-advanced.md)
