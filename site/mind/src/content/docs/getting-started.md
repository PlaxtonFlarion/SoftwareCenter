---
title: 快速开始
description: 安装 Mind CLI，检查环境，配置模型并完成第一条任务。
---

在 Windows 或 macOS 终端安装 CLI，完成配置后即可开始对话。

## 安装 CLI

准备好 Node.js 与 npm，然后运行：

```bash
npm install -g @craftline/mind
```

安装器会按系统下载对应运行时。Windows 推荐使用 Windows Terminal；macOS 可使用系统终端或 iTerm2。

## 检查安装

```bash
mind --help
mind doctor
```

`mind doctor` 只读检查本地配置、外部 MCP 配置和运行组件，不会启动服务或访问网络。

如果提示找不到 `mind`，重新打开终端，再确认 npm 全局可执行文件目录已加入 `PATH`。
通过安装包使用时，检查安装目录下的 `MindEngine` 是否在 `PATH` 中。

## 配置模型

启动交互界面：

```bash
mind
```

输入 `/preferences` 打开本地配置，填写当前 Provider 的模型、API key 和 Base URL。
已有配置时，可用 `/model` 选择模型，用 `/effort` 调整推理强度。

配置保存在本地 `config.toml`。完整配置与权限说明见[交互模式](/generated/interactive-mode/)。

## 完成第一条任务

在项目目录打开终端，输入一个明确的目标：

```bash
mind exec "概述当前项目的目录结构和主要入口"
```

也可以直接运行 `mind`，在对话中持续补充要求。需要结束当前上下文时，用 `/new` 开始新对话；用 `/resume` 恢复已有会话。

:::note[中断与退出]
任务执行时，Ctrl+C 请求中断；空闲且输入为空时，单次 Ctrl+C 退出。
菜单或审批打开时，Ctrl+C 优先取消当前界面操作。空输入下的 Ctrl+D 可直接退出本地。
:::

## 按需连接工具

原生 coding 工具可以直接使用。外部 MCP 服务需先配置并启用，见 [MCP 管理](/generated/cli-usage/#外部-mcp-管理)。

需要 Helix 执行能力时，显式接入：

```bash
mind --helix
mind --helix api
```

`--helix` 默认使用 `app` 工具过滤器；`--helix api` 选择接口工具。不传该选项时不连接 Helix。

## 排查连接问题

| 现象 | 检查方向 |
| --- | --- |
| 请求超时 | 确认服务地址可达，检查网络、代理与网关是否支持长连接和流式响应。 |
| 证书校验失败 | 检查系统时间、证书信任链以及代理或抓包工具的 HTTPS 配置。 |
| 模型或鉴权失败 | 核对当前 Provider 的模型名称、密钥与 Base URL。 |
| 外部工具不可用 | 查看 `/mcp` 中的启用状态、连接状态和错误信息。 |

继续阅读[运行方式](/capabilities/)、[常用命令](/reference/)或[交互模式](/generated/interactive-mode/)。
