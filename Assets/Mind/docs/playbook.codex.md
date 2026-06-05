# Codex 链路

这页讲的是：什么时候把编码任务交给外部 Codex CLI 执行，以及这条链路和原生 coding 工具链有什么边界差异。

重点不是记住底层工具名，而是搞清楚三件事：

1. Codex 链路适合解决什么问题
2. 一次稳定调用通常怎么走
3. 什么时候不该走 Codex，而该走原生 coding 链路

## 先判断是不是这页的范围

- 你要把一个相对完整的代码任务交给 Codex CLI 自行规划、修改和验证：看这里
- 你要逐步搜索、读窗口、打 patch、跑命令并把每一步展示在 Mind 终端：优先看 [原生 coding 链路](playbook.nativecoding.md)
- 你要写批跑星图、循环执行多个自然语言任务：先看 [星图协议](cli-code.md)
- 你只是想了解 REPL 命令和模式切换：先看 [交互模式](interactive-mode.md)

## 使用心智模型

Codex 链路是“把一整个编码目标交给外部执行面”的路径。

```text
Mind
  -> coding 工具
  -> Codex CLI
  -> 当前工作区
  -> 汇总输出
```

它适合目标已经比较完整、允许 Codex 自己组织搜索与修改步骤的场景。Mind 负责启动、等待、收集输出和最终结果；具体怎么搜文件、怎么编辑、怎么跑测试，主要由 Codex CLI 在自己的执行循环里完成。

## 适合场景

- 已经明确要改什么，但不需要 Mind 展示每个子工具调用细节
- 希望 Codex CLI 使用它自己的搜索、阅读、编辑和测试策略
- 改动涉及多个文件，但任务边界清楚
- 可以接受执行过程是一个外部编码会话，而不是 Mind 原生工具逐步展开

示例输入：

```text
用 Codex 完成这个仓库的登录态缓存修复，补测试并给出 diff 摘要。
```

或：

```text
让 Codex 检查当前分支的失败测试，定位原因并修复。
```

## 不适合场景

- 你需要 Mind 终端逐步展示 `Searched / Read / Edited / Ran / Git diff`
- 你需要严格控制每一次文件读写、patch、命令审批
- 你要验证原生 coding 工具本身的 trace、审批、patch engine 或 runtime resolution
- 你希望模型按 `workspace_search -> workspace_read_file -> workspace_apply_patch -> shell_exec` 的路径执行

这些场景优先走 [原生 coding 链路](playbook.nativecoding.md)。

## 前置条件

- 本机可执行 `codex`
- 当前工作区对 Codex CLI 可读写
- Codex CLI 自身的认证、模型和沙箱配置已就绪

如果本机没有可用的 Codex CLI，Mind 会在连接检查阶段提示缺少运行时。Windows 下如果 `codex` 是 `.cmd` shim，运行时解析层会用系统 shell 包一层，避免直接执行 shim 失败。

## 常见流程

1. 用户提出完整编码目标
2. Mind 调用 coding 链路启动 Codex CLI
3. Codex CLI 在工作区内自行搜索、修改、验证
4. Mind 持续消费 stdout/stderr
5. 进程结束后返回 exit code、输出摘要和最终状态

## 和原生 coding 的区别

| 维度 | Codex 链路 | 原生 coding 链路 |
|------|------------|------------------|
| 执行主体 | 外部 Codex CLI | Mind/Helix 暴露的原生工具 |
| 过程展示 | 以 Codex 输出为主 | 每个工具调用都有 trace |
| 文件操作 | Codex 自行决定 | `workspace_*` 工具受控执行 |
| 命令执行 | Codex 自行组织 | `shell_exec` 带审计和执行元数据 |
| 适合任务 | 边界清楚的完整编码目标 | 需要可见、可审计、可逐步控制的编码闭环 |

## 使用建议

- 任务越完整、越像“交给一个编码代理处理”，越适合 Codex 链路
- 任务越需要你观察每一步、控制每次 patch 或审批命令，越适合原生 coding
- 如果你在调试 Mind 自己的工具展示、patch engine、shell runtime 或远端 synthetic tool call，不要走 Codex 链路

