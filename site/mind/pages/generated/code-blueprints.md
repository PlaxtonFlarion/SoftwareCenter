# 蓝本实战样例

README 只保留入口层信息；如果你要看一份蓝本到底应该写到什么粒度，直接看这里。

这页只做两件事：
- 给出贴近现有工具能力的蓝本规格样例
- 用接近真实环境的接口写法表达步骤，接口地址可用 example 占位

这页不做的事：
- 不重复解释所有协议字段
- 不把样例写成底层执行 AST
- 不写工具根本不支持的能力

## 接口占位约定

样例里的接口按真实请求结构写，但域名和部分业务值可以用 example 占位。

- HTTP 基地址建议写成 https://api.example.com
- WebSocket 基地址建议写成 wss://ws.example.com
- 文档重点是请求结构、断言、提取和步骤依赖，不是要求你真的连这个地址
- 如果你有真实环境，只需要把 env 里的 example 值替换掉

## 写蓝本的基本规则

- 该写目标时，直接写目标。
- 该写参数时，只写真正决定行为的参数。
- 该写断言时，直接写通过条件。
- 该写提取时，直接写提取路径和变量名。
- 不要把“接口成功了”“页面应该没问题”这种空话当样例。

## 蓝本样例 1：登录接口成功后，再确认首页已经真的起来

蓝本名：api_login_then_ui_verify

``````
```cfg
global_rule: |
  接口断言、页面等待条件和留证动作都必须明确，不接受空描述。
```

# name: api_login_then_ui_verify
前置变量：
- base_url = {{ env.base_url }}
- username = {{ env.username }}
- password = {{ env.password }}
- package = com.example.app
- activity = .MainActivity

接口约定：
- base_url 可写为 https://api.example.com
- 登录接口使用 POST /api/login
- 首页准备检查使用 GET /api/home/ready?package={{ package }}
- 成功时返回 token，供后续首页确认复用

执行链：
- 发送 POST {{ base_url }}/api/login
- 请求头包含 Content-Type: application/json
- 请求体带 username 和 password
- 断言 response.status == 200
- 断言 response.body_json.ok == true
- 断言 response.body_json.data.token 为非空字符串
- 提取 token = response.body_json.data.token
- 发送 GET {{ base_url }}/api/home/ready?package={{ package }}
- 请求头包含 Authorization: Bearer {{ token }}
- 断言 response.status == 200
- 断言 response.body_json.data.ready == true
- 断言 response.body_json.data.title == 首页
- 将应用拉起到前台
- 目标包名为 {{ package }}
- 目标 Activity 为 {{ activity }}
- 最长等待 15 秒
- 轮询间隔 0.5 秒
- 页面同时满足存在文本 首页 和资源 id com.example.app:id/bottom_nav
- 截当前页面

通过标准：
- 登录接口断言全部通过
- 首页准备接口断言全部通过
- 首页标题可见
- 底部导航栏可见
- 截图成功
``````

为什么值得写成蓝本：
- 登录成功不等于首页真的起来
- 这里只有把接口确认、前台收敛和页面等待串起来，验收才完整

## 蓝本样例 2：签名接口不是一句“先签名再请求”，要把签名串写清楚

蓝本名：signed_request_regression

``````
```cfg
global_rule: |
  签名串来源、摘要算法和签名落点都必须可回放。
```

# name: signed_request_regression
前置变量：
- base_url = {{ env.base_url }}
- app_id = {{ env.app_id }}
- app_secret = {{ env.app_secret }}
- order_id = {{ env.order_id }}
- amount = {{ env.amount }}
- ts = {{ now_s() }}
- nonce = {{ nonce(16) }}

接口约定：
- base_url 可写为 https://api.example.com
- 支付接口使用 POST /api/secure/pay
- 服务端校验 X-App-Id、X-Timestamp、X-Nonce、X-Sign 和请求体中的 order_id、amount
- app_id、app_secret、order_id、amount 都可用 example 值占位

执行链：
- 先准备待签名字段 app_id、ts、nonce、order_id、amount
- 使用 security_sign_text 生成 query-like 签名原文
- 原文形态应为 app_id={{ app_id }}&ts={{ ts }}&nonce={{ nonce }}&order_id={{ order_id }}&amount={{ amount }}
- 再使用 security_digest(kind="hmac_sha256") 基于上面的原文计算签名
- 输出格式使用 hex
- 发送 POST {{ base_url }}/api/secure/pay
- 请求头包含 Content-Type: application/json
- 请求头包含 X-App-Id: {{ app_id }}
- 请求头包含 X-Timestamp: {{ ts }}
- 请求头包含 X-Nonce: {{ nonce }}
- 请求头包含 X-Sign: {{ sign }}
- 请求体包含 order_id 和 amount
- 断言 response.status == 200
- 断言 response.body_json.code == 0
- 断言 response.body_json.data.status == PAID
- 提取 pay_status = response.body_json.data.status
- 提取 trace_id = response.body_json.data.trace_id

通过标准：
- 签名串成功生成
- 摘要成功计算
- 支付接口断言全部通过
``````

为什么值得写成蓝本：
- 现有工具支持拼签名串和算签名，但它们是两步，不是一句模糊的自动签名
- 如果不把签名原文写清楚，读者不知道现有能力到底能不能覆盖

## 蓝本样例 3：WebSocket 触发任务后，再用 HTTP 轮询状态

蓝本名：ws_trigger_http_poll_and_capture

``````
```cfg
global_rule: |
  先确认触发消息被接受，再确认轮询最终收敛，最后补证据。
```

# name: ws_trigger_http_poll_and_capture
前置变量：
- ws_url = {{ env.ws_url }}
- base_url = {{ env.base_url }}
- job_id = {{ env.job_id }}
- package = com.example.app

接口约定：
- ws_url 可写为 wss://ws.example.com
- WebSocket 地址使用 /ws/task
- HTTP 轮询地址使用 GET /api/job/status?id={{ job_id }}
- 任务触发后，状态通常会从 PROCESSING 收敛到 DONE

执行链：
- 连接 {{ ws_url }}/ws/task
- 发送一次 JSON 消息，内容包含 action = start_job 和 job_id = {{ job_id }}
- 断言首条响应消息存在
- 断言 response.messages.0.body_json.ok == true
- 轮询 GET {{ base_url }}/api/job/status?id={{ job_id }}
- 请求方法为 GET
- 轮询超时 20 秒
- 轮询间隔 1 秒
- 停止条件为 response.status == 200 且 response.body_json.data.status == DONE
- 提取 job_status = response.body_json.data.status
- 提取 result_id = response.body_json.data.result_id
- 把 {{ package }} 拉到前台
- 截图

通过标准：
- WebSocket 响应确认成功
- 轮询在超时前进入 DONE
- 截图成功
``````

为什么值得写成蓝本：
- 这里不是单一协议能力，而是 WS 触发、HTTP 轮询和设备留证的组合

## 蓝本样例 4：接口、截图、logcat 三段证据要放在同一条链里

蓝本名：api_device_evidence_chain

``````
```cfg
global_rule: |
  证据链必须同时覆盖接口结果、页面留证和运行日志。
```

# name: api_device_evidence_chain
前置变量：
- base_url = {{ env.base_url }}
- token = {{ env.token }}
- order_id = {{ env.order_id }}
- package = com.example.app

接口约定：
- base_url 可写为 https://api.example.com
- 订单详情接口使用 GET /api/order/detail?id={{ order_id }}
- Authorization 使用 Bearer {{ token }}
- order_id、token 都可用 example 值占位，但返回结构要能支撑断言和提取

执行链：
- 发送 GET {{ base_url }}/api/order/detail?id={{ order_id }}
- 请求头包含 Authorization: Bearer {{ token }}
- 断言 response.status == 200
- 断言 response.body_json.ok == true
- 断言 response.body_json.data.status == SUCCESS
- 提取 order_status = response.body_json.data.status
- 提取 order_amount = response.body_json.data.amount
- 将 {{ package }} 拉到前台
- 截图
- 导出一次过滤后的 logcat
- 关键字包含 crash、anr、fatal
- 日志级别从 W 开始

通过标准：
- 接口断言全部通过
- 截图成功
- logcat 导出成功
``````

为什么值得写成蓝本：
- 如果接口、截图、日志分开跑，最后只能人工拼证据

## 蓝本样例 5：录屏结束后，从录屏结果继续拆帧

蓝本名：record_then_extract_then_report

``````
```cfg
global_rule: |
  前一步产物必须被下一步直接消费，不要把媒体链路写成神秘黑盒。
```

# name: record_then_extract_then_report
前置变量：
- base_url = {{ env.base_url }}
- package = com.example.app

接口约定：
- base_url 可写为 https://api.example.com
- 报告回执接口使用 POST /api/media/report
- 请求体至少包含 video_id、frame_count 和 report_type

执行链：
- 启动一次 scrcpy 录屏会话
- fps = 30
- silence = true
- 完成目标交互后关闭录屏会话
- 断言录屏会话成功开始
- 断言录屏会话成功关闭
- 断言返回结果里存在可用视频附件
- 基于录屏结果继续提取关键帧
- 最多保留 6 张关键帧
- 如果只是想抽某个固定时间点的图，改用单帧截图更合适
- 基于这段录屏生成帧级分析报告
- 发送 POST {{ base_url }}/api/media/report
- 请求体包含 video_id、frame_count、report_type = frame-analysis
- 断言 response.status == 200
- 断言 response.body_json.ok == true
- 提取 report_id = response.body_json.data.report_id

通过标准：
- 录屏成功
- 关键帧提取成功
- 报告生成成功
- 报告回执接口断言通过
``````

为什么值得写成蓝本：
- 现有能力支持录制和拆帧，但它们不是一个工具，需要蓝本把前后依赖写出来
- 这里不需要写死文件夹，重点是后一步吃前一步的结果

## 蓝本样例 6：重复执行登录首页链，观察稳定性

蓝本名：regression_login_home

``````
```cfg
repeat: 3
attempts: 2
stop_on_fail: true
global_rule: |
  每轮都必须同时保留接口结果、首页状态和日志快照。
```

# name: regression_login_home
前置变量：
- base_url = {{ env.base_url }}
- username = {{ env.username }}
- password = {{ env.password }}
- package = com.example.app

接口约定：
- base_url 可写为 https://api.example.com
- 登录接口使用 POST /api/login
- 首页准备检查使用 GET /api/home/ready?package={{ package }}
- 用户名、密码可用 example 值占位，但返回结构要稳定支持回归断言

每轮动作：
- 重置应用状态
- 发送 POST {{ base_url }}/api/login
- 请求体带 username 和 password
- 确认 response.status == 200
- 确认 response.body_json.ok == true
- 确认 response.body_json.data.token 非空
- 提取 token = response.body_json.data.token
- 发送 GET {{ base_url }}/api/home/ready?package={{ package }}
- 请求头包含 Authorization: Bearer {{ token }}
- 确认 response.status == 200
- 确认 response.body_json.data.ready == true
- 将 {{ package }} 拉到前台
- 等待首页出现 首页 标题和底部导航栏
- 截图
- 导出一次 logcat 快照

整轮通过标准：
- 接口断言全部通过
- 首页成功出现
- 截图成功
- 日志导出成功
``````

为什么值得写成蓝本：
- 这里重点不是登录本身，而是重复执行、失败重试和统一留证

## 蓝本样例 7：什么时候不需要写蓝本

下面这些场景通常不值得单独写蓝本：
- 只做一次接口请求
- 只截一次图
- 只拉一次 logcat
- 只做一次摘要或签名计算

这些动作直接调工具更清楚。

只有当你开始需要下面这些能力时，蓝本才真正有价值：
- 步骤之间有依赖
- 要跨多个工具域
- 要统一规则、重试或重复
- 要系统性留证

## 常见误区

- 只写一句“先登录，再看页面”
这不够。接口地址、请求体、断言和页面条件都应该写清。

- 只写一句“先签名，再发请求”
这不够。签名串怎么拼、摘要怎么算、签名放到哪里，都应该写清。

- 把录制和拆帧写成一个神秘动作
现有能力是先录制，再关闭，再基于录屏结果处理，不是一个万能工具。

- 把所有细节都写成参数清单
也不对。只有真正决定行为的参数才需要写，普通动作直接自然语言描述即可。

## 相关文档

- [星图协议深入说明](cli-code.md)
- [接口实战教学](api-playbook.md)
- [安全工具实战](security-playbook.md)
- [设备域实战](device-playbook.md)
- [多媒体链路实战教学](media-playbook.md)
- [文档索引](README.md)
