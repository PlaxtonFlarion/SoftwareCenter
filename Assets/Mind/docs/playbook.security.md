# 安全工具

这页聚焦签名、摘要、JWT、RSA、AES 等安全能力及其分工。

## 先判断是不是这页的范围

- 你要做摘要、HMAC、JWT、RSA、AES、签名前文本拼装：看这里
- 你要确认某个签名或密文链路该落在哪个工具：看这里
- 你只是在准备 query、header、body 的动态值：先去模板文档，不要把数据准备和安全计算混在一起
- 你要做最终接口验收：安全工具不是 `extract / asserts` 的替代品

## 怎么读这页

- 先看“设计定位”，建立模板层和安全层的边界
- 再按工具类型看 `digest / jwt / jwt_rs / crypto / aes / sign_text`
- 最后再结合你的协议场景决定是否需要回到接口文档或模板文档

## 这页解决什么问题

- 当前有哪些安全能力
- 每类能力适合做什么
- 模板层和安全工具怎么分工
- 哪些场景该用摘要、令牌、签名或加解密能力

## 设计定位

安全工具层承载的是确定性、可复用、可验证的安全能力。

它适合做：

- 摘要与 HMAC
- JWT 生成、解析、验签
- RSA 签名、验签、加解密
- AES 对称加解密
- 业务签名串和 multipart 签名前文本拼装

它不适合做：

- 请求模板渲染
- query 拼装和轻量结构转换
- 复杂业务流程判断
- 代替 `extract / asserts` 做接口最终验收

推荐边界：

- 模板层：准备输入材料
- 专用安全能力：做确定性的安全计算

一句话理解：

- 模板层负责把材料准备对
- 安全工具负责把结果算对

## 当前工具面

### 1. 摘要与 HMAC

适合：

- `md5 / sha256 / sha512`
- `hmac_sha256 / hmac_sha512`
- 需要把结果输出成 `hex / base64 / bytes`

支持的 `kind`：

- `md5`
- `sha1`
- `sha224`
- `sha256`
- `sha384`
- `sha512`
- `hmac_md5`
- `hmac_sha1`
- `hmac_sha224`
- `hmac_sha256`
- `hmac_sha384`
- `hmac_sha512`

最小输入示意：

```text
kind="hmac_sha256"
output="sign"
input_value="ts=1710000000&nonce=abc123"
secret="your-secret"
out_mode="hex"
```

适用场景：

- 接口签名串
- Webhook 签名
- 文件或文本摘要

### 2. 对称令牌

适合：

- HS256 JWT 生成
- 无验签解析
- HS256 验签

支持的 `kind`：

- `jwt_hs256`
- `jwt_decode_unverified`
- `jwt_verify_hs256`

最小输入示意：

```text
kind="jwt_hs256"
output="token"
payload={"sub": "u_1001", "role": "admin"}
secret="your-hs256-secret"
```

适用场景：

- 本地测试 JWT 颁发
- 轻量 HS256 鉴权链路
- 调试 token 载荷

### 3. 非对称令牌

适合：

- `RS256` JWT 生成与验签
- `ES256` JWT 生成与验签

支持的 `kind`：

- `jwt_rs256`
- `jwt_verify_rs256`
- `jwt_es256`
- `jwt_verify_es256`

最小输入示意：

```text
kind="jwt_verify_rs256"
output="claims"
token="{{ token }}"
public_key="{{ public_key_pem }}"
```

约束：

- RSA key 支持完整 PEM，也兼容部分裸 key 自动补齐
- EC key 需要完整 PEM

适用场景：

- 对接 OAuth / OIDC 风格公私钥链路
- 需要真实验签的接口回归

### 4. 非对称签名与加解密

适合：

- RSA 签名 / 验签
- RSA 公钥加密 / 私钥解密

支持的 `kind`：

- `rsa_sign`
- `rsa_verify`
- `rsa_encrypt`
- `rsa_decrypt`
- `rsa_encrypt_oaep_sha256`
- `rsa_decrypt_oaep_sha256`
- `rsa_sign_pss_sha256`
- `rsa_verify_pss_sha256`

最小输入示意：

```text
kind="rsa_sign_pss_sha256"
output="signature"
input_value="{{ canonical_text }}"
private_key="{{ private_key_pem }}"
```

适用场景：

- RSA 请求签名
- 平台公钥加密敏感字段
- 对接需要 PSS / OAEP 的系统

### 5. 对称加解密

适合：

- AES 加密 / 解密
- `cbc / ecb / gcm`

最小输入示意：

```text
kind="encrypt"
output="ciphertext"
input_value='{"name":"mind"}'
key="0123456789abcdef"
iv="abcdef0123456789"
mode="cbc"
out_mode="base64"
```

适用场景：

- 对称加密接口参数
- 本地验证 AES 密文结果
- 与服务端密文协议对齐

### 6. 业务签名前文本

适合：

- 生成业务签名前的确定性文本
- `key=value`、query-like、prefix/suffix 这类文本拼装

它不做：

- 摘要
- HMAC
- RSA / AES

最小输入示意：

```text
kind="query_like"
output="sign_text"
data={"ts": 1710000000, "nonce": "abc123", "uid": "u_1001"}
```

### 7. 表单签名前文本

适合：

- `multipart/form-data` 场景的签名前文本构造
- 需要把表单字段和文件元信息按确定规则拼成签名串

它不做：

- 真正的 multipart 编码
- 文件上传
- 摘要或加密

## 模板层和安全工具怎么分工

推荐做法：

1. 模板层负责准备输入材料
2. 安全工具负责计算签名、token、密文或签名前文本
3. 再把结果注入请求头、query 或 body

例如 HMAC 场景：

1. 用模板表达式生成 `timestamp / nonce / canonical_query`
2. 需要时先拼签名串，再计算 `hmac_sha256`
3. 把签名回填到 `request.headers`

例如 JWT 场景：

1. 模板层准备 claims
2. 用专用安全能力生成 token
3. 把 token 填进 `Authorization`

## 什么时候不要把逻辑塞进模板层

这些逻辑不建议继续写成模板表达式：

- `HMAC / JWT / RSA / AES`
- 业务签名串拼装规则
- 需要密钥处理的确定性安全能力
- 需要明确输入输出格式约束的加解密逻辑

原因很直接：

- 模板层已经偏大而全
- 安全逻辑需要更稳定的参数边界
- 工具返回结构更适合复用和验收

## 和 `extract / asserts` 的关系

安全工具生成的是中间结果，真正验收仍建议落到 `extract / asserts`。

例如（与 [接口实战](playbook.api.md) 一致；根对象保证整段为**合法 JSON**）：

```json
{
  "extract": {
    "status": "response.status",
    "code": "response.body_json.code"
  },
  "asserts": [
    { "path": "response.status", "op": "eq", "value": 200 },
    { "path": "response.body_json.code", "op": "eq", "value": 0 }
  ]
}
```

验签是否通过应对 **`response.body_json` 里接口实际返回的字段** 再追加断言（例如某布尔字段 `verify_ok`），避免写无法映射到路径的自然语言句。

这样结构更清晰：

- 模板层：准备值
- 安全工具：算值
- 协议执行层：发请求
- `extract / asserts`：验结果

## 什么时候优先看这页

- 你要做 HMAC / JWT / RSA / AES
- 你在写鉴权、签名或加密链路
- 你想知道模板表达式和安全工具的边界
- 你在调试 token、签名或密文格式

## 相关文档

- [模板能力](playbook.template.md)
- [接口实战](playbook.api.md)
- [正文目录](README.md)
