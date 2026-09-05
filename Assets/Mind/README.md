# 🚀 Mind :: 代理思维

![Mind](https://raw.githubusercontent.com/PlaxtonFlarion/SoftwareCenter/main/Assets/MindSource/app_readme.png)

**Mind 智能任务中枢**

**工具编排｜过程可观测 · 会话可恢复 · 能力可扩展**

**[Releases](https://github.com/PlaxtonFlarion/SoftwareCenter/releases) · [Assets](https://github.com/PlaxtonFlarion/SoftwareCenter/tree/main/Assets/Mind) · [Framix](https://github.com/PlaxtonFlarion/SoftwareCenter/tree/main/Assets/Framix) · [Memrix](https://github.com/PlaxtonFlarion/SoftwareCenter/tree/main/Assets/Memrix)**

---

**阅读导航**

- 第一次使用：先看 [快速开始](#quick-start) → [模型配置](#model-config) → [执行入口](#execution)
- 接入外部工具：看 [工具来源](#tool-sources) 和 [外接 MCP](#external-mcp)
- 开发或维护项目：先看[系统架构](ARCHITECTURE_SYSTEM.md)，再看[客户端架构](ARCHITECTURE.md)和[正文目录](docs/README.md)

**专题跳转**

- CLI 与交互：[命令行参考](docs/cli-usage.md) · [交互模式](docs/interactive-mode.md)
- MCP 与订阅：[MCP Server](docs/mcp-server.md) · [订阅模式](docs/agent-mode.md)
- 工程能力：[原生 coding](docs/playbook.nativecoding.md) · [设备与 UI](docs/playbook.device.md) · [多媒体](docs/playbook.media.md)
- 稳定性与维护：[性能实战](docs/playbook.performance.md) · [Hooks](docs/hooks.md) · [维护者指南](docs/maintainer-guide.md)

---

## 🏆 项目简介

**Mind** 是面向工程交付的终端代理运行时。它通过 CLI、交互 TUI、stdio MCP 和订阅入口接收任务，组合模型、原生工具与外部 MCP 完成执行，并保留结构化过程、会话和结果。

- **可组合**：按当前会话组合 native tools、外部 MCP 和可选 Helix
- **可观测**：统一投影模型等待、工具调用、审批、重试和终态
- **可恢复**：会话、运行事件和关键执行事实按职责持久化
- **可扩展**：通过明确的工具契约、权限策略和组合边界接入能力

Mind 默认不依赖 Helix。设备控制、协议验证、媒体处理和性能采样等 Helix 能力，需要显式接入对应运行组件。

<a id="quick-start"></a>
## ⭐️ 快速开始

### 安装入口

可以从正式发布渠道安装；使用 npm 时执行 `npm install -g @craftline/mind`。安装后确认命令可用：

```shell
mind --version
mind --help
```

源码调试使用 Python 3.11，并从仓库根目录运行：

```shell
python -m pip install -r requirements.txt
python mind.py --help
```

### 最小上手

```shell
mind exec "概述当前项目的核心能力、边界和主要入口"
mind
mind doctor
mind agent listen
```

首次运行前需要配置一个可用的模型 Provider。需要设备、接口或媒体工具时，再使用 `--helix` 或交互命令 `/helix-link` 接入 Helix。

<a id="model-config"></a>
## ⭐️ 模型配置

用户配置默认位于 `~/.mind/config.toml`。`MIND_HOME` 可以覆盖配置根；运行状态默认仍写入
同一目录，也可以通过 `MIND_STATE_HOME` 单独指定 history、sessions、reports、Helix 和
本地 SQLite 的可写根目录。显式状态根不可用时启动会直接失败，不会静默回退。
下面是一个最小 Provider Profile：

```toml
model_provider = "openai-main"

[model_providers.openai-main]
name = "openai-main"
kind = "openai"
model = "<model-id>"
route = "responses"
reasoning_effort = "high"
api_key = "<api-key>"
base_url = ""
```

交互模式可使用 `/preferences` 打开配置页面，或通过 `/provider`、`/model`、`/effort` 分别调整 Provider、模型和推理强度。变更用于后续轮次，不会中途改变正在执行的请求。

<a id="tool-sources"></a>
## ⭐️ 工具来源

```text
CLI / TUI / stdio MCP / Subscription
                 |
             Mind Runtime
                 |
    native tools / external MCP / optional Helix
```

- **Native tools**：项目检查、受控命令、补丁、图片查看、计划和本地执行能力
- **External MCP**：通过用户配置接入 Playwright、数据库、知识库等第三方服务
- **Helix**：按需提供设备、协议、媒体和性能工具，不是 Mind 的启动前置条件
- **可选能力**：JavaScript REPL 和子 Agent 默认关闭，由 `[features]` 显式启用

工具可见性不等于执行授权。实际调用仍受沙箱、审批策略、工具过滤和 Effect 规则约束。

<a id="execution"></a>
## ⭐️ 执行入口

| 场景 | 命令 | 说明 |
|------|------|------|
| 持续交互 | `mind` | 进入 TUI，在同一会话内连续处理任务 |
| 单次执行 | `mind exec "..."` | 非交互执行一次任务，也可使用 `mind e` |
| 恢复会话 | `mind resume` | 通过选择器或会话 ID 恢复历史会话 |
| 会话归档 | `mind archive` / `mind unarchive` | 归档或恢复已有会话 |
| 远端订阅 | `mind agent listen` | 监听服务端下发任务 |
| 环境诊断 | `mind doctor` | 只读检查配置、MCP 和本地运行组件 |
| MCP 管理 | `mind mcp` | 管理外部 MCP 服务注册 |
| MCP 服务 | `mind mcp-server` | 通过 stdio 对外暴露 `mind_exec` |
| Helix 升级 | `mind upgrade helix` | 下载或更新 Helix 运行组件 |

完整参数、stdin、图片、模型覆盖、补全和多级帮助见[命令行使用参考](docs/cli-usage.md)。

### 沙箱与审批

- 交互模式默认使用 `workspace-write + on-request`
- 非交互执行默认使用 `read-only + never`
- 使用 `-s/--sandbox` 和 `-a/--ask-for-approval` 可覆盖本次进程配置
- 交互模式使用 `/permissions` 在 `Read Only`、`Auto` 和 `Full Access` 间切换

<a id="external-mcp"></a>
## ⭐️ 外接 MCP

外部 MCP 可以通过 `mind mcp add` 管理，也可以写入 `~/.mind/config.toml`：

```toml
[mcp_servers.playwright]
command = "npx"
args = ["-y", "@playwright/mcp@latest"]
allow = ["browser_*"]
deny = ["browser_evaluate", "browser_file_upload"]
```

- `command` 用于 stdio，`url` 用于远程 SSE 或 Streamable HTTP；同一服务只能配置一种目标
- `allow` 和 `deny` 按原始工具名进行大小写敏感匹配；修改启动期配置后需要重启 Mind

查看实时参数使用：

```shell
mind help mcp add
mind mcp list
```

需要把 Mind 自身提供给 Codex 等 MCP host 时使用：

```shell
codex mcp add mind -- mind mcp-server
```

不要在 Mind 自己的 `[mcp_servers]` 中注册 `mind mcp-server`，否则会递归启动自身。完整说明见 [Mind MCP Server](docs/mcp-server.md)。

<a id="interactive-mode"></a>
## ⭐️ 交互模式

启动 `mind` 进入交互模式。常用入口包括 `/new`、`/resume`、`/permissions`、`/preferences`、`/tools`、`/mcp`、`/helix-link` 和 `/quit`；完整 slash 命令及运行中行为见[交互模式文档](docs/interactive-mode.md)。

<a id="architecture"></a>
## ⭐️ 项目架构

```text
mind.py
  -> composition.py
      -> agent
      -> protocol
      -> infrastructure
      -> observability
  -> frontends
```

- `mind.py` 和 `composition.py` 是具体组合边界
- `agent` 持有应用用例、执行编排、端口和持久事实
- `protocol` 持有独立的线上协议 schema 与 client
- `infrastructure` 实现配置、平台、MCP、持久化和可选服务
- `frontends` 负责 CLI、TUI、stdio MCP、Subscription 和终端展示

架构文档按以下顺序阅读：

- [系统架构](ARCHITECTURE_SYSTEM.md)：Mind、AppServer 与 Fabric 的职责、Authority 和跨仓生命周期
- [客户端架构](ARCHITECTURE.md)：Mind 内部包边界、依赖方向、状态所有权和生命周期
- [架构评分卡](ARCHITECTURE_SCORECARD.md)：阶段性架构评审和成熟度记录，不定义架构事实
- [产品背景与能力生态](docs/architecture.md)：产品定位、使用场景和可选能力，不定义架构事实

<a id="build-release"></a>
## ⭐️ 构建与发布

当前发布流程覆盖 Windows 与 macOS，平台启动器位于独立的 `npm/` workspace。正式产物见 [Releases](https://github.com/PlaxtonFlarion/SoftwareCenter/releases)。

## ⭐️ 许可与支持

仓库授权文本见 [LICENSE.md](LICENSE.md)。技术合作与部署支持请联系 `AceKeppel@outlook.com`。

提交代码前请先阅读 [AGENTS.md](AGENTS.md)、[系统架构](ARCHITECTURE_SYSTEM.md)、
[客户端架构](ARCHITECTURE.md)和[维护者指南](docs/maintainer-guide.md)，并根据影响范围运行定向测试和文档校验。
