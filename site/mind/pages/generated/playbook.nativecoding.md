# 原生 coding 链路

这页讲的是：Mind 内置的原生 coding 工具链如何完成搜索、阅读、修改、执行命令和汇总结果。

重点不是背工具清单，而是形成一条稳定的工程闭环：

```text
定位文件 -> 读取窗口 -> 修改文件 -> 执行验证 -> 查看 diff -> 汇总结果
```

## 先判断是不是这页的范围

- 你要用 `workspace_search / workspace_read_file / workspace_apply_patch / shell_exec / git_diff` 做可见的编码闭环：看这里
- 你要写批跑任务或多条自然语言用例：先看 [星图协议](cli-code.md)

## 使用心智模型

原生 coding 链路是“模型调用 Mind 暴露的受控工具，一步步完成编码任务”。
它可在 `chat`、`fast` 和 `xtra` 流式模式下使用；当编码任务需要同时接入外部 MCP 服务时，优先切到 `xtra`。

```text
模型
  -> workspace_search / workspace_read_file / native_parallel_read
  -> workspace_apply_patch / workspace_write_file
  -> shell_exec
  -> git_status / git_diff / change_summary
  -> 最终回复
```

它的核心优势是可见、可审计、可插入审批。每一步都会进入工具 trace，失败也会返回结构化 reason 和 recommended next step。

## 工具分层

### 1. 定位

- `workspace_root`：确认当前原生 coding 工作区根目录
- `workspace_list_file`：按目录列出文件
- `workspace_search`：统一搜索入口，覆盖文件名、文本、正则和符号模式
- `native_parallel_read`：并行读取多个候选文件或行窗口

推荐搜索策略：

- 先用文件名或关键词缩小范围
- 再按错误文本、函数名、调用点多轮搜索
- 搜到候选后只读相关行窗口
- 多个候选文件用 `native_parallel_read` 并行读取

### 2. 阅读

- `workspace_read_file`：读取文件或指定行窗口

建议：

- 大文件不要一次读完整文件
- 搜索结果给出行号时，优先读取附近窗口
- byte 或 line 截断后，按 next step 继续读下一窗口

### 3. 修改

- `workspace_apply_patch`：精确 old/new 文本替换
- `workspace_apply_unified_patch`：标准 unified diff patch
- `workspace_write_file`：新建或整体覆盖文本文件
- `workspace_copy_file` / `workspace_move_file` / `workspace_delete_file`：文件级操作

建议：

- 小范围局部改动优先 `workspace_apply_patch`
- 多处或跨文件 diff 优先 `workspace_apply_unified_patch`
- 小文件整体重写可用 `workspace_write_file`
- 不要用 `shell_exec` 的 echo、tee、sed、重定向来改文件

### 4. 执行

- `shell_exec`：执行本地命令

当前执行层会做命令审计和 runtime resolution：

- Python / Node / Java / Go 等常见运行时会先解析真实可执行文件
- 版本类命令可走较轻的 metadata audit
- 测试类命令保留更完整的文件审计
- 缺失 runtime 时返回明确的诊断和建议

建议：

- 验证命令优先用项目现有测试命令
- 如果是打包环境，避免假设 `python` 一定是真 Python；看返回里的 runtime 诊断
- destructive 命令必须走审批，不要绕过文件工具

### 5. 收束

- `git_status`：查看工作区状态
- `git_diff`：查看 tracked diff
- `change_summary`：汇总当前状态、diff、未跟踪文件、冲突、截断风险和工作区阻断项

建议：

- 修改后先跑最小验证
- 再看 `git_status` 和 `git_diff`
- 最终回复应说明改了什么、执行过什么验证、当前工作区还有什么风险或未覆盖项

## 推荐闭环

一条稳定的原生 coding 回合通常是：

1. `workspace_search` 找文件或符号
2. `workspace_read_file` 读取相关窗口
3. `workspace_apply_patch` 或 `workspace_apply_unified_patch` 修改
4. `shell_exec` 运行测试或最小验证
5. `git_diff` / `change_summary` 汇总
6. 回复用户结果和验证情况

## 常见失败与处理

### patch 失败

常见原因：

- old text 和当前文件不完全一致
- unified diff 缺少文件头
- hunk 行数不匹配
- 上下文不唯一或上下文已变化
- patch 带了 UI 行号

处理方式：

- 先重新 `workspace_read_file` 读取当前窗口
- 小范围改动重新生成精确 old/new patch
- 多文件改动使用严格 unified diff
- 失败 reason 已返回时，按 `suggested_next_action` 调整

### 命令执行失败

常见原因：

- runtime 缺失
- 当前 cwd 不对
- 打包环境命令名被 shim 包装
- 测试命令需要依赖或网络

处理方式：

- 先看 `shell_exec` 返回的 `exit_code / stdout / stderr / runtime`
- runtime 缺失时不要反复执行同一命令
- 需要云端 sandbox 时只在支持的语言和策略下切换

## 使用建议

- 需要可见、可控、可审计的编码闭环时，走原生 coding
- 在调试 patch engine、shell runtime、tool trace、synthetic tool call 时，必须走原生 coding
