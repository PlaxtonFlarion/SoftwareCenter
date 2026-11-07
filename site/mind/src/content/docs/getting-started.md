---
title: 快速开始
description: 安装 CLI，连接一个可用的模型，在你的项目中完成第一条任务。
---

这条入门路径适用于 Windows 和 macOS。你需要 Node.js 18 或更高版本、npm，以及一个可用的模型 Provider 和 API key。

Provider 是模型服务提供方。模型名、密钥和服务地址需要互相匹配；本地安装 CLI 后，模型请求与会话服务仍需要可用的网络。

<nav class="reading-path" aria-label="入门步骤"><a href="#安装-cli">01 安装</a><a href="#配置模型">02 配置模型</a><a href="#完成第一条任务">03 开始任务</a></nav>

## 安装 CLI

在终端运行：

```bash
npm install -g @craftline/mind
```

安装器会按系统下载对应运行时。Windows 推荐使用 Windows Terminal；macOS 可使用系统终端或 iTerm2。

## 检查安装

```bash
mind --version
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

默认用户配置位于 `~/.mind/config.toml`。已有多个 Provider 时，使用 `/provider` 选择，再用 `/model` 和 `/effort` 调整后续任务。完整配置示例见[模型配置](/generated/overview/#model-config)。

配置完成后再发送第一条任务；模型名称、密钥与服务地址需要属于同一个可用的 Provider。

## 完成第一条任务

先进入你想处理的项目目录。可以让代理从只读检查开始：

```bash
mind exec "概述当前项目的目录结构和主要入口"
```

也可以直接运行 `mind`，在对话中持续补充要求。回答会帮助你确认项目入口，再决定下一步修改。用 `/new` 开始新对话，用 `/resume` 恢复已有会话。

本地恢复选择器使用最近 24 小时的会话游标，不是永久会话备份。需要保留可独立查看的结果时，可在交互模式用 `/export` 导出记录。

单次执行默认使用只读沙箱；交互模式默认允许写入工作区并按需请求审批。需要调整时，在交互模式输入 `/permissions`，详细规则见[沙箱与审批](/generated/overview/#沙箱与审批)。

:::note[中断与退出]
Ctrl+C 会先取消当前菜单或审批；主输入框有草稿时先清空草稿。输入为空时，运行中的任务会收到中断请求，空闲时则直接退出。
空输入下的 Ctrl+D 可退出本地观察；退出本地不代表远端任务已经结束。
:::

## 按需连接工具

代码搜索、命令执行和补丁等原生工具可直接使用。MCP 是连接外部工具服务的协议；添加服务后，Mind 才能发现该服务提供的工具，见 [MCP 管理](/generated/cli-usage/#外部-mcp-管理)。

需要 Helix 执行能力时，显式接入：

```bash
mind --helix
mind --helix api
```

`--helix` 默认使用 `app` 工具过滤器；`--helix api` 选择接口工具。不传该选项时不连接 Helix。

## 排查连接问题

| 现象 | 检查方向 |
| --- | --- |
| 找不到 `mind` 命令 | 重新打开终端，检查 npm 全局可执行文件目录是否在 `PATH` 中。 |
| 请求超时 | 确认服务地址可达，检查网络、代理与网关是否支持长连接和流式响应。 |
| 证书校验失败 | 检查系统时间、证书信任链以及代理或抓包工具的 HTTPS 配置。 |
| 模型或鉴权失败 | 核对当前 Provider 的模型名称、密钥与 Base URL。 |
| 外部工具不可用 | 查看 `/mcp` 中的启用状态、连接状态和错误信息。 |

## 接下来

- 想持续修改项目：阅读[交互模式](/generated/interactive-mode/)，了解输入、审批与会话恢复。
- 想从脚本或其他应用调用：查看[运行方式](/capabilities/)，选择合适的执行入口。
- 只想查一条命令：打开[常用命令速查](/reference/)。
