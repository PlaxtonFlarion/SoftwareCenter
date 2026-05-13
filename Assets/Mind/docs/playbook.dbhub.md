# DBHub 外接工具实战

这一页讲的是：在 `--xtra` 模式下，怎么把数据库当成一个“可搜索、可查询、可控风险”的外部协作面来用。

重点不是记底层导出了哪些工具名，而是搞清楚：

1. 什么时候先搜对象，什么时候直接查数据
2. 什么时候该放开自由 SQL，什么时候应该只开放固定查询
3. SQL Server 场景下，怎样把风险收紧到工程可接受范围

## 先判断是不是这页的范围

- 你要在 `mind --xtra` 里查表、查字段、跑只读 SQL、做数据库排查：看这里
- 你要的是浏览器自动化：去看 [Playwright 外接工具实战](playbook.playwright.md)
- 你要的是 HTTP/SSE/WS/GraphQL 协议调试：去看 [接口实战](playbook.api.md)

## 连接配置

最常见的 HTTP 方式：

```json
{
  "mcpServers": {
    "dbhub-sqlserver": {
      "url": "http://localhost:8080/mcp",
      "timeout_sec": 30,
      "sse_read_timeout_sec": 300
    }
  }
}
```

最小示例：

```bash
mind --xtra "查询 users 表最近 20 条记录"
```

## 使用心智模型

数据库协作最稳的做法通常是两段式：

1. 先理解库里有什么
2. 再决定怎么查

所以工程上最常见的顺序是：

`搜索对象 -> 明确表和列 -> 执行只读查询 -> 汇总结果 -> 必要时固化成固定查询`

如果你对库很熟，也可以直接进查询；但对陌生库，先搜索对象几乎总是更稳。

## 能力总览

DBHub 这类数据库外接能力，给人看的核心不是工具名，而是 3 类能力。

### 1. 搜索数据库对象

适合：

- 不知道表名
- 想先找 schema
- 想先找列
- 想先看存储过程、函数、索引

典型自然语言：

- `搜索名字里包含 user 的表`
- `在 dbo 下搜索和 order 相关的列`
- `列出 sales schema 里的主要表`

### 2. 执行 SQL 查询

适合：

- 查明细
- 查聚合
- 做线上只读诊断
- 看执行计划或查询行为

典型自然语言：

- `查 dbo.users 最近 20 条记录`
- `统计 orders 表今天的订单数和支付成功数`
- `查询最近 20 条失败订单，返回订单号、失败原因和创建时间`

### 3. 固定化业务查询

适合：

- 生产环境固定报表
- 需要稳定参数校验
- 需要限制查询形状
- 不希望模型自由拼 SQL

典型自然语言：

- `调用 get_active_users，返回最多 20 条活跃用户`
- `调用 find_order_by_id，查询指定订单详情`

## 常见工作流

### 先探索再查询

适合：库不熟、表结构不清楚。

```bash
mind --xtra "先搜索和 invoice 相关的表和列，再帮我查最近 10 张发票"
```

### 直接只读查询

适合：表和字段都明确。

```bash
mind --xtra "查询 dbo.users 中 status='active' 的前 50 条记录"
```

### 先搜索再生成查询

适合：业务知道目标，但不确定表结构。

```bash
mind --xtra "先搜索和 customer 相关的表和列，再生成一条只读 SQL，查询最近 30 天新增客户"
```

### 用固定查询收生产风险

适合：生产环境固定报表、稳定诊断。

```bash
mind --xtra "调用 get_active_users，返回最多 20 条活跃用户"
```

## SQL Server 场景建议

对 `dbhub-sqlserver` 这类场景，我建议默认采取这套收口策略：

1. 先开放对象搜索
2. 再决定是否开放自由 SQL
3. 一旦开放查询，优先只读
4. 再给结果行数上限

原因很直接：

- SQL Server 常见库 schema 多、历史表多、行数大
- 模型在陌生库里最容易犯的错不是语法错，而是查错表、查太大
- 先搜索对象再查询，稳定性和可控性都更高

## 什么时候别让模型自由写 SQL

下面几类场景，建议直接走固定查询，而不是让模型自由拼：

- 生产环境固定报表
- 核心订单、支付、账务类查询
- 有明确参数约束的业务查询
- 复杂联表、复杂权限边界
- 重复复用的高频查询

固定查询的价值在于：

- 给模型一个稳定能力名
- 给参数一个稳定类型
- 把风险留在配置层，而不是留给模型即时生成

## 配置策略建议

### 只开放对象搜索

适合：生产库风险高，只允许探索结构。

```toml
[[sources]]
id = "production"
dsn = "sqlserver://..."

[[tools]]
name = "search_objects"
source = "production"
```

### 开放只读查询 + 行数限制

适合：线上排障，但不允许写入，也不允许大结果集。

```toml
[[sources]]
id = "production"
dsn = "sqlserver://..."

[[tools]]
name = "execute_sql"
source = "production"
readonly = true
max_rows = 100

[[tools]]
name = "search_objects"
source = "production"
```

## 工程建议

- 对陌生库，优先先搜对象
- 对生产库，默认只读并限制行数
- 对高风险查询，优先做固定查询，不要放任自由 SQL
- 返回结果时，最好让模型补一句“查询意图 + 风险说明 + 结果摘要”

## 实现映射（维护参考）

这一节只给维护者或需要核对底层实现的人看，正常使用不需要记。

### 对象搜索

- `search_objects`

### SQL 查询

- `execute_sql`

### 固定业务查询

- 自定义工具名由你在 `dbhub.toml` 里定义

补充：

- DBHub 的最终导出名会受 source id 影响
- 在 Mind 里显示时，还会再被包到外接 MCP 命名空间里
- 这些名称属于实现细节，不建议写进面向使用者的主体说明

## 参考来源

- DBHub 官方工具总览：`dbhub.ai/tools/overview`
- DBHub `execute_sql` 文档：`dbhub.ai/tools/execute-sql`
- DBHub `search_objects` 文档：`dbhub.ai/tools/search-objects`

