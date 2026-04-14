# 星图深入说明

星图协议页负责回答“星图是什么、怎么起步写”；这页只负责更深一层的执行语义。  
重点是讲清覆盖优先级、执行顺序、批跑控制和常见误写，不再重复入门字段表。

## 先判断是不是这页的范围

- 你已经知道 `--code` 的基本格式，但不确定前后置到底谁包谁、谁覆盖谁：看这里
- 你要理解 `repeat / pattern / attempts / stop_on_fail` 的执行语义：看这里
- 你要区分 `global_rule / rule` 和计划执行时的规则判断：看这里
- 你只是第一次接触星图：先看 `星图协议`
- 你想照着真实任务样例写：先看 `星图样例`

## 怎么读这页

- 先看“分层心智”和“执行顺序”，建立谁在外层、谁在内层
- 再看“覆盖关系”和“批跑控制”，理解默认值与局部覆盖怎么生效
- 最后看“多文件装载”和“常见误写”，避免把星图写成一堆看起来对、执行时却不稳的文本

## 分层心智
先把一份星图拆成四层：

```text
整次批跑
└─ 每一轮
   └─ 每个任务块
      └─ 当前任务正文
```

字段归属：

1. 整次批跑
   - `loop_prefix`
   - `loop_suffix`
2. 每一轮
   - `round_prefix`
   - `round_suffix`
3. 每个任务块
   - `item_prefix`
   - `item_suffix`
4. 当前任务正文
   - `message`
   - `global_prefix / global_suffix`
   - `prefix / suffix`
   - `global_rule / rule`

关键判断：
- `loop_* / round_* / item_*` 是结构层
- `global_* / prefix / suffix / rule` 是正文层默认值与覆盖值
- 不要把它们都理解成“多加一层包裹”；有些是层级，有些是同位覆盖

## 执行顺序
单条任务真正展开后，执行顺序更接近：

1. `loop_prefix`
2. `round_prefix`
3. `item_prefix`
4. `global_prefix` 或 `prefix`
5. 当前任务正文
6. `global_suffix` 或 `suffix`
7. 当前任务规则：`global_rule` 或 `rule`
8. `item_suffix`
9. `round_suffix`
10. `loop_suffix`

可以把它理解成：

```text
[loop_prefix]

  [round_prefix]

    [item_prefix]

      [global_prefix 或 prefix]
      message
      [global_suffix 或 suffix]
      [global_rule 或 rule]

    [item_suffix]

  [round_suffix]

[loop_suffix]
```

边界要点：
- `item_prefix / item_suffix` 是“任务块外层 hook”，每条任务块执行一次
- `global_prefix / global_suffix` 是每条正文的默认前后置，不是更外层 hook
- `rule` 不包裹正文，它是当前任务的规则文本覆盖位

## 覆盖关系
真正存在“二选一覆盖”的只有三组：

- `prefix` 覆盖 `global_prefix`
- `suffix` 覆盖 `global_suffix`
- `rule` 覆盖 `global_rule`

可直接记成：

```text
prefix = 当前任务 prefix 或 global_prefix
suffix = 当前任务 suffix 或 global_suffix
rule   = 当前任务 rule   或 global_rule
```

这意味着：
- `item_prefix` 不会覆盖 `global_prefix`
- `round_prefix` 不会覆盖 `item_prefix`
- `loop_prefix` 也不是默认值，它就是最外层结构

## 批跑控制语义
`cfg` 里的控制字段不是“文档装饰”，而是直接决定批跑行为。

### `repeat`
- 定义整份星图要跑多少轮
- 它作用在“整次批跑”层，不是单条任务层
- 一般和 `round_prefix / round_suffix` 一起理解更清楚

### `pattern`
- 用来筛选要执行的任务块
- 常见场景是配合 `# name:` 做正则筛选
- 它解决的是“哪些任务参与本轮”，不是“任务执行顺序”

### `attempts`
- 定义单条任务失败后的重试次数预算
- 它不是整份批跑失败后整包重跑
- 适合处理临时抖动、偶发接口失败或前台收敛抖动

### `stop_on_fail`
- `true`：一旦达到失败判定，尽快停止后续执行
- `false`：当前任务失败后，继续后面的任务
- 它影响的是批跑收束策略，不改变单条任务内部步骤结构

一句话判断：
- `repeat` 决定跑几轮
- `pattern` 决定跑哪些
- `attempts` 决定单条失败后怎么补救
- `stop_on_fail` 决定失败后整包是否继续

## `global_rule / rule` 和执行期规则判断的边界
这是最容易混写的地方。

- `global_rule / rule`：属于 `--code` 的星图规则层
- 执行期规则判断：属于 `plan` 执行面

不要混淆成同一种东西：
- 星图规则层关注的是“当前任务块应该按什么规则验收、约束或留证”
- 计划执行时的规则判断关注的是“计划执行时如何做规则判断”

所以：
- 改星图结构时，优先看 `global_rule / rule`
- 改 `plan` 执行行为时，不要反向改成星图规则文案

## 多文件装载心智
当你执行：

```text
mind --chat --code a.md b.md c.md
```

更稳的理解不是“把三份文件拼成一份超级星图”，而是：

- 一次命令装载多份星图输入
- 每份文件各自保留自己的 `cfg` 和任务块结构
- 主模式仍然只有一个：`chat`、`fast` 或 `plan`
- `--code` 负责把这些星图交给显式选定的主模式执行

补充约束：
- `--code` 不能脱离 `--chat / --fast / --plan` 单独出现

因此：
- 主模式决定执行协议
- 每份星图决定自己的批跑结构
- 多文件装载解决的是“同一轮命令下跑多份蓝本”，不是“字段跨文件自动继承”

## 常见误写

### 把所有前后置都当成一类 hook
⚠️ 不对。

- `loop_* / round_* / item_*` 是结构层 hook
- `global_prefix / global_suffix` 是正文默认值
- `prefix / suffix` 是正文局部覆盖

### 以为 `global_prefix` 会包住整个任务块
⚠️ 不对。

它只作用于正文层，不替代 `item_prefix / item_suffix`。

### 以为 `attempts` 会把整份星图整包重跑
⚠️ 不对。

它更接近单条任务的失败重试预算。

### 把 `pattern` 当执行顺序控制
⚠️ 不对。

它负责筛选，不负责改写任务天然顺序。

### 把 `global_rule / rule` 写成计划执行时的规则判断
⚠️ 不对。

这会把星图规则层和执行面规则层混成一层，后续维护会非常乱。

## 阅读路径建议
- 第一次写星图：先回 `星图协议`
- 需要复杂执行语义：继续读这页
- 需要真实跨域写法：再去 `星图样例`
- 需要协议字段边界：配合 `接口实战` 一起读
