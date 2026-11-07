---
title: 常用命令速查
description: 按目标查找命令，区分终端入口、对话内操作与任务执行中的快捷键。
---

`mind …` 命令在系统终端中执行；以 `/` 开头的命令在交互对话中输入。完整参数见[命令行使用参考](/generated/cli-usage/)，对话操作见[交互模式](/generated/interactive-mode/)。

<nav class="reading-path" aria-label="命令分类"><a href="#终端命令">终端命令</a><a href="#对话内操作">对话内操作</a><a href="#常用快捷键">快捷键</a></nav>

## 终端命令

| 命令 | 用途 |
| --- | --- |
| `mind` | 开始持续对话 |
| `mind exec "任务"` | 执行单次任务 |
| `mind resume` | 恢复已有会话 |
| `mind doctor` | 只读检查本地环境 |
| `mind agent listen` | 监听远端任务 |
| `mind mcp-server` | 启动 stdio MCP 服务 |
| `mind --help` | 查看命令帮助 |

## 对话内操作

| 目标 | 命令 |
| --- | --- |
| 新建或恢复对话 | `/new`、`/resume` |
| 归档或分叉会话 | `/archive`、`/fork` |
| 选择 Provider、模型与推理强度 | `/provider`、`/model`、`/effort` |
| 管理本地配置 | `/preferences` |
| 调整审批权限 | `/permissions` |
| 检查外部工具连接 | `/mcp`、`/tools` |
| 查看 Hook 与技能 | `/hooks`、`/skills` |

`/new` 只是开始新对话；`/archive` 管理会话归档；`/delete` 永久删除当前会话及其子会话，使用前需要确认范围。不要把清空当前上下文、归档和删除当作同一种操作。

## 常用快捷键

以下是主输入区的默认行为；打开菜单、补全或审批时，按键优先作用于当前界面。

| 按键 | 空闲时 | 任务执行时 |
| --- | --- | --- |
| <kbd>Enter</kbd> | 提交输入 | 尝试向当前任务补充输入 |
| <kbd>Tab</kbd> | 提交普通文本 | 将输入排到下一轮 |
| <kbd>Ctrl+C</kbd> | 先清空草稿，空草稿时退出 | 先清空草稿，空草稿时请求中断 |
| <kbd>Ctrl+D</kbd> | 空草稿时退出本地 | 空草稿时退出本地观察 |
| <kbd>Shift+Enter</kbd> | 插入换行 | 插入换行 |

请求中断后，客户端仍需等待远端确认；退出本地观察不会替远端任务声明结束。完整的 Esc、排队与输入恢复行为见[交互模式](/generated/interactive-mode/)。

## 工具与开发参考

- [Hooks 配置](/generated/hooks/)：生命周期事件、信任与执行边界。
- [MCP Server](/generated/mcp-server/)：host 配置、工具协议与生命周期。
- [模板能力](/generated/playbook.template/)：表达式、变量与签名前置材料。
- [系统架构](/generated/system-architecture/)：Mind、AppServer 与 Fabric 的职责与集成边界。
- [正文目录](/generated/docs-index/)：所有专题的完整索引。
