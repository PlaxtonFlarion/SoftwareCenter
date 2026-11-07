---
title: 常用命令速查
description: 快速查找会话、模型、权限和工具连接相关的常用命令。
---

这里提供常用入口。完整参数和组合规则见[命令行使用参考](/generated/cli-usage/)，slash 命令的完整行为见[交互模式](/generated/interactive-mode/)。

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
| 配置模型与推理强度 | `/model`、`/effort` |
| 管理本地配置 | `/preferences` |
| 调整审批权限 | `/permissions` |
| 检查外部工具连接 | `/mcp`、`/tools` |
| 查看 Hook 与技能 | `/hooks`、`/skills` |

## 工具与开发参考

- [Hooks 配置](/generated/hooks/)：生命周期事件、信任与执行边界。
- [MCP Server](/generated/mcp-server/)：host 配置、工具协议与生命周期。
- [模板能力](/generated/playbook.template/)：表达式、变量与签名前置材料。
- [系统架构](/generated/system-architecture/)：Mind、AppServer 与 Fabric 的职责与集成边界。
- [正文目录](/generated/docs-index/)：所有专题的完整索引。
