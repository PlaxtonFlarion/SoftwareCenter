<div class="mind-hero">
  <h1>Mind</h1>
  <p>面向工程交付的命令行代理执行框架。</p>
  <p><strong>Mind</strong> 面向工程交付场景，把自然语言目标拆成可执行步骤，并编排调用 MCP 工具完成设备控制、接口验证、性能采样、媒体处理和批跑回归。</p>
  <div class="mind-pill-row">
    <span class="mind-pill">CLI Agent</span>
    <span class="mind-pill">MCP Tooling</span>
    <span class="mind-pill">Observability</span>
    <span class="mind-pill">Replayable</span>
    <span class="mind-pill">Batch Blueprint</span>
  </div>
  <div class="mind-cta-row">
    <a class="mind-cta mind-cta-primary" href="getting-started.md">立即开始</a>
    <a class="mind-cta mind-cta-secondary" href="reference.md">查看文档</a>
  </div>
</div>

!!! note "核心定位"
    `Mind` 的重点不是“回答问题”，而是把自然语言目标变成可执行、可观测、可复盘的任务链。

## 快速入口

- 立刻上手：[快速开始](getting-started.md)
- 看能力边界：[能力概览](capabilities.md)
- 进完整文档：[参考文档](reference.md)
- 看公共仓库：[SoftwareCenter](https://github.com/PlaxtonFlarion/SoftwareCenter)

## 一眼上手

```bash
mind --chat "概述当前系统的核心能力与边界"
mind --fast "对 path/to/video.mp4 提取关键帧并返回证据"
mind --plan "打开系统设置，稳定等待 2 秒后返回桌面"
```

## 核心能力卡片

<div class="mind-card-grid">
  <div class="mind-card">
    <h3>设备与 UI</h3>
    <p>启动应用、切换页面、点击、输入、滚动、系统控制与证据留存。</p>
  </div>
  <div class="mind-card">
    <h3>接口与协议</h3>
    <p>HTTP、SSE、WebSocket、GraphQL、Socket、邮件与文件协议验证。</p>
  </div>
  <div class="mind-card">
    <h3>性能与稳定性</h3>
    <p>Memrix / Framix 采样、Monkey 扰动、日志与视觉证据汇总。</p>
  </div>
  <div class="mind-card">
    <h3>媒体与回归</h3>
    <p>关键帧、场景帧、音轨、裁剪、转码，以及 `--code` 蓝本批跑。</p>
  </div>
</div>

## 适合什么场景

- 设备与 UI 自动化：启动、切换、点击、输入、滚动、系统控制
- 接口与协议验证：HTTP、SSE、WebSocket、GraphQL、Socket、邮件与文件协议
- 性能与稳定性：Memrix / Framix 采样、Monkey 扰动、证据沉淀
- 媒体链路处理：关键帧、场景帧、音轨、裁剪、转码、拼接
- 批跑与回归：`--code` 蓝本、前后置、循环与规则文本

## 为什么用 Mind

- 可执行：重点不是“回答”，而是“落地完成任务”
- 可观测：执行链路、日志、报告和证据可回看
- 可复用：能力按工具域注册，批跑按蓝本组织
- 可扩展：新增工具通常不需要改核心执行框架

## 三种运行模式

| 模式 | 说明 | 更适合 |
|------|------|--------|
| `chat` | 开放式流式工具闭环 | 探索、问答、临时任务 |
| `fast` | 裁剪工具集后的快速执行通道 | 接口、媒体、短链路任务 |
| `plan` | 先生成计划，再按步骤顺序执行 | 巡检、固定流程、回归任务 |

!!! tip "怎么选"
    发散探索先用 `chat`，短链路处理优先 `fast`，需要步骤稳定和结果可复盘时用 `plan`。

## 三条常用命令

### 探索

```bash
mind --chat "请用工程视角概述当前系统的核心能力、边界与典型使用场景"
```

### 短链路处理

```bash
mind --fast "对 path/to/video.mp4 进行关键帧抽取，并返回可用证据"
```

### 结构化执行

```bash
mind --plan "打开系统设置，稳定等待 2 秒后返回桌面"
```

## 入口建议

- 想立刻上手：看 [快速开始](getting-started.md)
- 想看能力边界：看 [能力概览](capabilities.md)
- 想看完整文档：看 [参考文档](reference.md)

## 典型任务

- 用 `chat` 做临时探索、问答和混合型任务
- 用 `fast` 做接口、媒体和短链路处理
- 用 `plan` 做巡检、固定流程和回归执行

## 想继续深入

- 模式和工具边界：看 [能力概览](capabilities.md)
- 完整文档树：看 [参考文档](reference.md)
- 正文事实源：看 `Assets/Mind/README.md` 与 `Assets/Mind/docs/*.md`
