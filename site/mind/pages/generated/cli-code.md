# 星图协议深入说明

`--code` 用于装载一个或多个批量执行蓝本，并按选定协议执行。

## 适用范围
- 适用于需要批次控制、前后置、蓝本规则层、重试和筛选的批跑场景
- 如果你只是想把几条任务跑起来，README 里的基础写法已经足够

## 支持的 `cfg` 字段
- `repeat`
- `pattern`
- `attempts`
- `stop_on_fail`
- `loop_prefix`
- `loop_suffix`
- `round_prefix`
- `round_suffix`
- `item_prefix`
- `item_suffix`
- `global_prefix`
- `global_suffix`
- `global_rule`

## 文件格式
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

## 前后置层级
- 批次级：`loop_prefix` / `loop_suffix`
- 轮次级：`round_prefix` / `round_suffix`
- 任务块级：`item_prefix` / `item_suffix`
- 默认任务正文级：`global_prefix` / `global_suffix`
- 单条任务级：`prefix` / `suffix`

覆盖关系：
- `prefix` 覆盖 `global_prefix`
- `suffix` 覆盖 `global_suffix`

执行顺序：
1. `loop_prefix`
2. `round_prefix`
3. `item_prefix`
4. `global_prefix` 或 `prefix`
5. 任务正文
6. `global_suffix` 或 `suffix`
7. `item_suffix`
8. `round_suffix`
9. `loop_suffix`

边界说明：
- `item_prefix / item_suffix` 是“任务块外层 hook”，每个任务块执行一次
- `global_prefix / global_suffix` 是“任务正文默认前后置”，会被单条任务的 `prefix / suffix` 覆盖
- 如果你只想给每条任务统一套一层准备/收尾，用 `item_prefix / item_suffix`
- 如果你想让任务正文有可被单条覆盖的默认前后置，用 `global_prefix / global_suffix`

## 规则层级
- `global_rule`：整份批跑文件的默认规则文本
- `rule`：当前任务专属规则文本

覆盖关系：
- `rule` 存在时覆盖 `global_rule`

边界说明：
- 这里的 `global_rule / rule` 属于 `--code` 的蓝本规则层
- 它们不等同于 `plan` 执行面中的 `free_rule`

## 最小示例
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

item_prefix: |
  [IP] 任务块开始前：统一包裹（每条一次）
item_suffix: |
  [IS] 任务块结束后：统一包裹（每条一次）

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

## 长文本示例
``````
```cfg
item_prefix: <<<
【任务块开始前：统一说明（示例）】
>>>

item_suffix: <<<
【任务块结束后：统一说明（示例）】
>>>

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

## 最小蓝本示例
``````
```cfg
item_prefix: |
  本任务块开始前，先确认目标服务已启动，且测试环境可用。
```

# name: http
对单个 HTTP 接口执行一次请求，并确认状态码和业务返回都正常。

# rule: <<<
# PASS 条件：
# - 请求成功
# - 返回结构符合预期
# >>>
`````` 

这里故意不展开底层结构。
这一页的重点是蓝本层级、前后置和规则怎么组织，不是把接口参数整块摊开。

## 接口蓝本到底是什么意思

`--code` 里的蓝本，不是“再造一套协议参数”，而是把多步工具调用写成一份可批跑、可回放、可加规则的执行脚本。

如果你只想发一次请求：
- 直接用 `nexus_http_request`
- 或直接在 `chat / fast` 里自然语言发起

如果你要做下面这些事，才值得写蓝本：
- 一次批跑里串多步请求
- 前一步结果要进入后一步
- 需要统一前后置、统一规则、统一留证
- 需要按 `repeat / attempts / stop_on_fail` 跑回归

一句话理解：
- 工具：做一次动作
- 蓝本：把多次动作编排成一条可执行链

## 复杂接口蓝本怎么读

复杂蓝本这里不再展开长结构。你只需要记住三点：

- 蓝本可以把多个接口步骤串起来，例如先登录拿 token，再访问 profile；或者先做签名准备，再访问受保护接口。
- 蓝本可以把不同协议串起来，例如先消费 SSE，再查详情接口；或者先用 WebSocket 触发，再用 HTTP 校验状态。
- 蓝本可以把接口和其它工具域串起来，例如接口成功后补截图；或者接口轮询完成后导出日志或留证。

如果你要看“高层自然语言蓝本该怎么写”，直接看 [蓝本实战样例](code-blueprints.md)。  
如果你要看 `request / env / items / extract / asserts` 的真实字段边界，直接看 [接口实战教学](api-playbook.md)。
