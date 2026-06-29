# 原生 coding 链路

这页讲的是：Mind 内置的原生 coding 工具链如何在工作区内执行命令、应用 patch，并汇总结果。

重点不是背工具清单，而是形成一条稳定的工程闭环：

```text
shell 诊断 -> apply_patch 修改文件 -> 执行验证 -> 汇总结果
```

## 先判断是不是这页的范围

- 你要用内置编码工具做可见的搜索、阅读、修改、验证和收束闭环：看这里
- 你要写批跑任务或多条自然语言用例：先看 [星图协议](cli-code.md)

## 使用心智模型

原生 coding 链路是“模型调用 Mind 暴露的受控工具，一步步完成编码任务”。
它可在 `chat`、`fast` 和 `xtra` 流式模式下使用；当编码任务需要同时接入外部 MCP 服务时，优先切到 `xtra`。

```text
模型
  -> 用 shell 命令定位文件、符号、调用点或错误文本
  -> 必要时读取相关文件内容
  -> 使用 apply_patch 修改工作区文件
  -> 执行验证命令
  -> 汇总验证结果和剩余风险
  -> 最终回复
```

它的核心优势是可见、可审计、可插入审批。每一步都会进入工具 trace，失败也会返回结构化 reason 和 recommended next step。

## 工具分层

### 1. Shell 诊断

当前直接暴露的命令执行能力是 `shell_command`：

- 批量执行工作区内 shell 命令。
- 每项包含 `command`，可带 `cwd` 和 `timeout_sec`。
- 适合搜索、列目录、读取文件片段、运行测试、构建和脚本。
- 不应用它通过 `echo`、`tee`、`sed -i` 或重定向来创建/覆盖/局部修改文件。

当前执行环境的工作区根目录由 `exec_env.workspace.root` 提供。

推荐搜索策略：

- 先用文件名或关键词缩小范围，例如 `rg --files`、`rg`
- 再按错误文本、函数名、调用点多轮搜索
- 搜到候选后只读相关窗口，避免把大文件整段塞进上下文
- 多个只读诊断命令可以放进同一次 `shell_command.items`

### 2. 修改文件

当前直接暴露的工作区文件修改能力是 `apply_patch`：

- 支持严格 patch 语法。
- 支持多文件、多 hunk、新建/删除文件、上下文校验和按文件 SHA256 基线保护。
- patch 必须以 `*** Begin Patch` 开始，以 `*** End Patch` 结束。
- 文件段使用 `*** Add File:`、`*** Update File:`、`*** Delete File:`，重命名使用 `*** Move to:`。

建议：

- 所有代码创建、整体覆盖、局部修改和删除都使用 `apply_patch`。
- 不要把 Markdown 代码围栏、UI 行号或解释文字混进 patch。
- patch 失败后先重新读取当前文件内容，再按当前内容重建补丁。

### 3. 执行

执行仍通过 `shell_command` 完成。

当前执行层会做命令审计和 runtime resolution：

- Python / Node / Java / Go 等常见运行时会先解析真实可执行文件
- 版本类命令可走较轻的 metadata audit
- 测试类命令保留更完整的文件审计
- 缺失 runtime 时返回明确的诊断和建议

建议：

- 验证命令优先用项目现有测试命令
- 如果是打包环境，避免假设 `python` 一定是真 Python；看返回里的 runtime 诊断
- destructive 命令必须走审批，不要绕过文件工具

### 4. 收束

- 用 shell 命令查看必要状态，例如测试输出、构建结果、`git status --short` 或 `git diff --stat`。
- 汇总改动文件、验证命令、失败项和剩余风险。

建议：

- 修改后先跑最小验证
- 再按需要查看版本状态和 diff
- 最终回复应说明改了什么、执行过什么验证、当前工作区还有什么风险或未覆盖项

## 推荐闭环

一条稳定的原生 coding 回合通常是：

1. 搜索能力找文件或符号
2. 读取相关内容
3. 使用 apply_patch 修改
4. 运行测试或最小验证命令
5. 汇总验证结果、版本状态和风险
6. 回复用户结果和验证情况

## 常见失败与处理

### patch 失败

常见原因：

- old text 和当前文件不完全一致
- patch 缺少 `*** Begin Patch` / `*** End Patch`
- hunk 行数不匹配
- 上下文不唯一或上下文已变化
- patch 带了 UI 行号

处理方式：

- 先重新读取当前文件内容
- 小范围改动重新生成最小 patch
- 多文件改动使用多个文件段
- 失败 reason 已返回时，按 `suggested_next_action` 调整

### 命令执行失败

常见原因：

- runtime 缺失
- 当前 cwd 不对
- 打包环境命令名被 shim 包装
- 测试命令需要依赖或网络

处理方式：

- 先看命令执行结果返回的 `exit_code / stdout / stderr / runtime`
- runtime 缺失时不要反复执行同一命令
- 需要云端 sandbox 时只在策略层明确接管的场景下切换；不可用时返回依赖缺失和本地替代建议

## 使用建议

- 需要可见、可控、可审计的编码闭环时，走原生 coding
- 在调试 patch engine、shell runtime、tool trace、synthetic tool call 时，必须走原生 coding
