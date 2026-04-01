# 模板能力

主 README 只负责入口；`bench.nexus` 模板 helper、能力边界和签名前置写法继续看这里。
重点是划清模板层、安全层和协议层的边界，知道哪些数据准备该放模板里。

## 先判断是不是这页的范围

- 你要在 `request / env / template_vars / items[]` 里准备动态值：看这里
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
- `request / env / template_vars / items[]` 里怎么用模板

## 设计定位

`backend/nexus/domain/template.py` 现在不是一个“纯字符串替换器”，而是一个轻量的数据准备层。

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
- `items[]`

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
- batch 只有一份全局 `template_vars`；如果每个 item 都有独立值，必须直接写进各自的 `items[]`

SSE batch 特别注意：

- 不要把每条 case 的 `user_input` 放进全局 `template_vars`
- 不要依赖 `{{user_input}}` 在 batch 中按 item 自动替换
- 不要把每条 case 的 `current_time` 放进 `env.json`
- 这类 case 级字段应在提交前先展开成字面值，再写入 `items[].json`
- `env` 和 `items` 必须传原生结构化对象，不要传字符串化 JSON
- `concurrency` 和 `fail_fast` 应按预期行为显式传值，不要在校验失败后通过省略字段回退默认值
- `render / validate / execute` 现在共享同一套 `env + request` 物化语义；不要再假设预执行和执行期会看到不同请求

## Helper 分类

### 1. 标识与时间

- `now_s()`
- `now_ms()`
- `now_iso()`
- `format_ts(ts, fmt="%Y-%m-%dT%H:%M:%SZ")`
- `offset_ts(ts=None, seconds=0, minutes=0, hours=0, days=0, out="iso")`
- `uuid4()`
- `nonce(length=16, alphabet=None)`

适合：

- 请求时间戳
- 重放防护 nonce
- trace / correlation id

### 2. 取值与回退

- `pick(obj, "a.b.0", default=None)`
- `coalesce(a, b, c, ...)`

适合：

- 从 `template_vars / env / request` 里兜底取值
- 做多级 fallback

示例：

```text
{{ coalesce(pick(template_vars, "token"), pick(env, "token"), "default-token") }}
```

### 3. 编解码

- `b64encode(v)`
- `b64decode(v, as_text=True)`
- `hex_encode(v)`
- `hex_decode(v, as_text=True)`
- `json_dumps(v, ensure_ascii=False, sort_keys=False)`
- `json_loads(v)`

适合：

- Authorization 基础拼接
- payload 稳定序列化
- 把模板变量转成中间字符串

### 4. URL 与结构

- `urlencode(obj)`
- `urldecode(text)`
- `dict_merge(a, b, c, ...)`
- `sort_keys(obj)`
- `canonical_query(obj)`

适合：

- query 规范化
- 生成签名前的 canonical query
- 合并默认头和请求头

示例：

```text
{{ canonical_query(dict_merge(env.query_defaults, request.params)) }}
```

### 5. 压缩与二进制转换

- `gzip_encode(v, ...)`
- `gzip_decode(v, ...)`
- `zlib_encode(v, ...)`
- `zlib_decode(v, ...)`

适合：

- 需要对请求体做轻量压缩预处理时
- 兼容特定接口的压缩输入格式

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

- 你在写 `bench.nexus` 星图
- 你要做 query / body / header 的模板化构造
- 你要准备签名前置材料
- 你想知道模板层和 `security_*` 的边界

## 相关文档

- [接口实战](playbook.api.md)
- [文档索引](docs-index.md)
- [星图协议](cli-code.md)
- [星图深入说明](cli-code-advanced.md)
