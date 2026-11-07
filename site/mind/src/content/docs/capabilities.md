---
title: 选择运行方式
description: 持续对话、单次执行、远端订阅，或接入 MCP host：按你的工作方式选择入口。
---

不同入口使用同一套代理能力，区别在于如何提交任务、观察结果和管理生命周期。

| 你想做什么 | 选择入口 | 开始之前 |
| --- | --- | --- |
| 边讨论边修改项目 | [持续对话](#持续对话) | 在项目目录启动，准备好模型配置 |
| 执行一个明确任务或接入脚本 | [单次执行](#执行一条任务) | 明确任务目标与本次执行权限 |
| 长时间等待远端下发任务 | [订阅模式](#订阅远端任务) | 确认服务连接与订阅配置 |
| 从支持 MCP 的应用发起任务 | [MCP 服务](#接入-mcp-host) | 在 host 中配置 stdio 服务 |

## 持续对话

```bash
mind
```

适合探索项目、反复修改和持续调试。可以管理会话、调整模型、审批工具动作，详细操作见[交互模式](/generated/interactive-mode/)。

## 执行一条任务

```bash
mind exec "检查当前项目，并说明建议先运行哪些验证"
```

适合目标明确的任务和脚本调用。图片、标准输入、模型选项与结果处理见[命令行参考](/generated/cli-usage/)。

默认使用只读沙箱且不弹出审批。需要写入项目时，在启动前明确配置沙箱与审批策略。

## 订阅远端任务

```bash
mind agent listen
```

适合持续监听并执行远端下发的任务。连接、会话恢复与退出边界见[订阅模式](/generated/agent-mode/)。

## 接入 MCP host

```bash
mind mcp-server
```

将 Mind 作为 stdio MCP server 提供给支持 MCP 的 host。配置、工具协议和生命周期见 [MCP Server](/generated/mcp-server/)。

## 选择执行能力

运行入口与工具能力可以分别选择。编码能力来自原生工具；设备、接口、媒体等 Helix 能力需要显式接入对应运行组件。

| 任务 | 指南 |
| --- | --- |
| 搜索、修改、验证代码 | [原生 coding 链路](/generated/playbook.nativecoding/) |
| 调用已有外部服务 | [外部 MCP 管理](/generated/cli-usage/#外部-mcp-管理) |
| 处理接口、提取与断言 | [接口实战](/generated/playbook.api/) |
| 操作设备或原生桌面 | [设备域实战](/generated/playbook.device/)、[桌面 Sidecar](/generated/desktop-sidecar/) |
| 抽帧、转码与音频处理 | [多媒体链路](/generated/playbook.media/) |
| 性能分析与稳定性验证 | [性能实战](/generated/playbook.performance/)、[Monkey 扰动](/generated/playbook.monkey/) |
