# 星图协议

`--code` 用于装载一个或多个批量执行星图，并按选定协议执行。
重点是回答两件事：什么时候值得写星图，以及一份星图的最小结构应该怎么组织。

当前本地入口除了文件路径，也支持：

- `--code -`：从标准输入读取星图
- `--code inline:...`：直接执行内联星图文本
- `--code https://...`：从 URL 拉取星图文本

## 先判断要不要写星图

- 只是临时跑一条任务：先用入口页里的基础写法，不必先写 `--code`
- 需要把多条任务批量执行、重试、筛选、加前后置和规则：再进入星图
- 需要把多步动作整理成可回放、可复用、可回归的执行链：再进入星图

一句话判断：

- 工具：做一次动作
- 星图：把多次动作组织成一条批跑执行链

## 怎么读这页

- 先看“支持的 `cfg` 字段”和“文件格式”，建立最小结构感
- 再看“前后置层级”和“规则层级”，只建立最小心智，不在这页穷举执行语义
- 最后按需要跳到 `星图深入说明` 或 `星图样例`

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

最小心智模型：

- `cfg`：整份星图的批次控制和默认行为
- `---`：任务块分隔符
- `# name / # prefix / # suffix / # rule`：当前任务块的局部覆盖信息

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

如果你要继续看：
- 更细的执行顺序、覆盖优先级和批跑控制语义：直接看 `星图深入说明`
- 真正贴近业务的跨域写法：直接看 `星图样例`

## 规则层级
- `global_rule`：整份批跑文件的默认规则文本
- `rule`：当前任务专属规则文本

覆盖关系：
- `rule` 存在时覆盖 `global_rule`

边界说明：
- 这里的 `global_rule / rule` 属于 `--code` 的星图规则层
- 它们不等同于 `plan` 执行面中的执行期规则判断
- 需要继续理解这两者在运行时怎么分工，直接看 `星图深入说明`

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

## 深入阅读怎么选
- 你要继续看覆盖优先级、执行顺序、`repeat / pattern / attempts / stop_on_fail`：看 [星图深入说明](cli-code-advanced.md)
- 你要继续看真实任务到底该写到什么粒度：看 [星图样例](code-blueprints.md)
- 你要继续看协议字段、提取和断言边界：看 [接口实战](playbook.api.md)

## 最小星图示例
``````
```cfg
item_prefix: |
  本任务块开始前，先确认目标服务已启动，且测试环境可用。
```

# name: api_login_then_ui_verify
前置变量：
- `base_url = {{ env.base_url }}`
- `username = {{ env.username }}`
- `password = {{ env.password }}`

发送登录请求到 `{{ base_url }}/api/login`。
请求方法为 `POST`。
请求体使用：
{
  "username": "{{ username }}",
  "password": "{{ password }}"
}

断言：
- `response.status == 200`
- `response.body_json.ok == true`

提取：
- `token = response.body_json.data.token`
`````` 

这里故意只保留一个最小规格样例。
这一页的重点是星图层级、前后置和规则怎么组织；真正完整的星图粒度，直接看 [星图实战样例](code-blueprints.md)。

## 接口星图到底是什么意思

`--code` 里的星图，不是“再造一套协议参数”，而是把多步工具调用写成一份可批跑、可回放、可加规则的执行脚本。

如果你只想发一次请求：
- 直接用 `nexus_http_request`
- 或直接在 `chat / fast` 里自然语言发起

如果你要做下面这些事，才值得写星图：
- 一次批跑里串多步请求
- 前一步结果要进入后一步
- 需要统一前后置、统一规则、统一留证
- 需要按 `repeat / attempts / stop_on_fail` 跑回归

一句话理解：
- 工具：做一次动作
- 星图：把多次动作编排成一条可执行链

## 复杂接口星图怎么读

复杂星图不要写成“先做这个，再做那个”这种空描述。

至少要写清这几件事：

- 请求发到哪里
- 方法是什么
- 关键请求头或请求体是什么
- 断言什么才算通过
- 提取什么变量给后一步继续用
- 页面或媒体动作的成功条件是什么

如果你要看完整规格样例，直接看 [星图实战样例](code-blueprints.md)。  
如果你要看更深的执行语义，直接看 [星图深入说明](cli-code-advanced.md)。  
如果你要看 `request / env / items / extract / asserts` 的真实字段边界，直接看 [接口实战](playbook.api.md)。
