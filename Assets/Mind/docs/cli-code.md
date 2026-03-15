# 星图协议深入说明 (`--code` Advanced Guide)

`--code` 用于装载一个或多个批量执行蓝本，并按选定协议执行。

## 适用范围 (Scope)
- 适用于需要批次控制、前后置、全局规则、重试和筛选的批跑场景
- 如果你只是想把几条任务跑起来，README 里的基础写法已经足够

## 支持的 `cfg` 字段 (Supported `cfg` Keys)
- `repeat`
- `pattern`
- `attempts`
- `stop_on_fail`
- `loop_prefix`
- `loop_suffix`
- `round_prefix`
- `round_suffix`
- `global_prefix`
- `global_suffix`
- `global_rule`

## 文件格式 (Format)
- 顶部可包含一个 ` ```cfg ` 配置块
- `cfg` 配置块必须以独立一行 ` ```cfg ` 开始，并以独立一行 ` ``` ` 结束
- 多行字段推荐两种写法：
  - `key: |`
  - `key: <<<` ... `>>>`
- 任务块之间仍然使用 `---` 分隔
- 每个任务块顶部支持 meta 注释：`# key: value`
- 常用 meta 字段：
  - `# name:`
  - `# loop:`
  - `# prefix:`
  - `# suffix:`
  - `# rule:`

## 前后置层级 (Hook Layers)
- 批次级：`loop_prefix` / `loop_suffix`
- 轮次级：`round_prefix` / `round_suffix`
- 默认任务级：`global_prefix` / `global_suffix`
- 单条任务级：`prefix` / `suffix`

覆盖关系：
- `prefix` 覆盖 `global_prefix`
- `suffix` 覆盖 `global_suffix`

## 规则层级 (Rule Layers)
- `global_rule`：整份批跑文件的默认规则
- `rule`：当前任务专属规则

覆盖关系：
- `rule` 存在时覆盖 `global_rule`

## 最小示例 (Minimal Example)
``````
```cfg
loop_prefix: |
  [LP] 批跑开始前：环境准备（一次）
loop_suffix: |
  [LS] 批跑结束后：环境清理（一次）

round_prefix: |
  [RP] 每轮开始：统一初始化（每轮一次）
round_suffix: |
  [RS] 每轮结束：统一收尾（每轮一次）

global_prefix: |
  [GP] 每条前置：通用准备（每条一次）
global_suffix: |
  [GS] 每条后置：通用收尾（每条一次）

global_rule: <<<
【证据/断言/评分（自由文本）】
- 这里可以写截图策略、UI 断言描述、评分说明等
>>>
```

# name: case_001
# prefix:
# [P1] 仅本条前置：覆盖 global_prefix
# suffix:
# [S1] 仅本条后置：覆盖 global_suffix
# rule: <<<
# 这里写本条规则（覆盖 global_rule）
# >>>
这里是正文（自然语言目标）。
---

# name: case_002
这里是正文（未写 prefix/suffix/rule，将使用 global_prefix/global_suffix/global_rule）。
---
``````

## 长文本示例 (Long Text Example)
``````
```cfg
global_prefix: <<<
【占位符/填充字段规则（示例）】
>>>

global_suffix: <<<
【占位符/填充字段规则（示例）】
>>>

global_rule: <<<
【占位符/填充字段规则（示例）】
>>>
```
``````

## 完整蓝本示例 (Full Blueprint Example)
``````
```cfg
global_prefix: <<<
base_url = http://127.0.0.1:18080
time_out = 10
concurrency = 2
>>>
```

# name: http
请求 /http 来验证解析与 ok 判定。

request = {
    "kind": "json"
}

# rule: <<<
# PASS 条件：
# - ok == true
# - type == "http"
# - detail.response.status == 200
# - detail.response.body_json 不为空
# - detail.response.body_json.ok == true
# >>>
---

# name: sse
从 /sse 拉取前 5 条事件，并验证 event/id/data 字段齐全。

request = {
    "max_events": 5,
    "interval_ms": 20,
    "coalesce": true
}

# rule: <<<
# PASS 条件：
# - step.type == "sse"
# - step.ok == true
# - step.detail.status == 200
# - step.detail.events 长度 == 5
# >>>
---

# name: ws
连接 ws://127.0.0.1:18080/ws，依次发送 ping 与 close。

request = {
    "sends": ["ping", "close"]
}

# rule: <<<
# PASS 条件：
# - step.type == "ws"
# - step.ok == true
# - step.detail.messages 至少包含 hello 和 echo:ping
# >>>
---
``````
