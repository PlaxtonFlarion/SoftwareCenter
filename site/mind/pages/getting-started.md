# 快速开始

如果你只想尽快把 Mind 跑起来，不需要先把所有专题正文看完。  
按这条路径走就够了：先确认环境，再发一条最小命令，最后再决定是否进入交互式、外接协作或订阅。

<div class="mind-step-grid">
  <div class="mind-step-card">
    <span class="mind-step-index">入口</span>
    <h3>确认命令入口</h3>
    <p>先用 <code>mind --help</code> 确认 CLI 可用；需要 Helix MCP 时再显式加 <code>--helix</code>。</p>
  </div>
  <div class="mind-step-card">
    <span class="mind-step-index">环境</span>
    <h3>安装 CLI 并准备终端</h3>
    <p>优先用 npm 全局安装；如果使用安装包，再把 Mind/MindEngine 目录加入 PATH。</p>
  </div>
  <div class="mind-step-card">
    <span class="mind-step-index">路径</span>
    <h3>先跑通，再决定怎么继续</h3>
    <p>先确认一条最小命令能跑通；后面是进入交互循环、外接协作，还是订阅远端任务，再按需要继续分流。</p>
  </div>
  <div class="mind-step-card">
    <span class="mind-step-index">命令</span>
    <h3>发送最小命令</h3>
    <p>先跑通一条最小任务，再进入设备、协议或多媒体专题。</p>
  </div>
</div>

<div class="mind-command-note">
  <strong>一条最短路径：</strong><code>npm install -g @craftline/mind</code> → <code>mind --help</code> → 发一条最小命令。
</div>

## 安装 Mind CLI

推荐使用 npm 全局安装，Windows 和 macOS 使用同一条命令：

```bash
npm install -g @craftline/mind
```

安装完成后验证命令入口：

```bash
mind --help
mind doctor
```

`mind doctor` 会只读检查本地配置、外部 MCP 配置、Helix 运行组件和 Mind coding 工具；它不会创建文件、启动服务或访问网络。需要交给脚本处理时使用 `mind doctor --json`。

需要把 Mind 接入 Codex 等 MCP host 时，使用 `mind mcp-server` 作为 stdio server 启动命令。

`@craftline/mind` 是主入口包，安装时会按当前系统拉取对应运行时包：

- Windows：`@craftline/mind-win32`
- macOS：`@craftline/mind-darwin`

如果安装后提示找不到 `mind` 命令，先关闭并重新打开终端；仍不可用时，再检查 npm 全局 bin 目录是否已经加入 `PATH`。

## 先确认命令入口

<div class="mind-command-note">
  <strong>第一件事：</strong>不要一开始就堆长命令。先确认 CLI 参数正常显示，再跑最小命令。
</div>

```bash
mind --help
```

默认执行链路使用原生工具和已启用的外接 MCP。需要进入 Helix 执行面时，可以在启动时显式接入：

```bash
mind --helix
mind --helix api
```

只写 `--helix` 时默认选择 `app` 工具过滤器；可显式传入 `api`。不传 `--helix` 时不连接 Helix。

进入 REPL 后可以使用全部 slash 命令。下面是入口速查，完整行为说明见[交互模式](../generated/interactive-mode/)：

| 命令 | 作用 |
|------|------|
| `/new [title]`、`/resume` | 新建会话或恢复最近会话 |
| `/archive`、`/fork` | 归档当前会话并退出，或复制当前上下文为新分支 |
| `/permissions` | 切换 `Read Only`、`Auto`、`Full Access` 权限预设 |
| `/provider`、`/model <model-id>`、`/effort`、`/preferences` | 选择 Provider、模型、推理强度和本地配置 |
| `/compact`、`/tools`、`/diff`、`/copy` | 压缩上下文、查看工具、查看补丁或复制回复 |
| `/hooks`、`/agent`、`/skills` | 管理生命周期 Hooks、子 Agent 和 Skills |
| `/listen [start, stop, status]`、`/mailbox` | 管理远端监听器和待处理消息 |
| `/ps`、`/stop` | 查看或停止后台终端 |
| `/mcp [start, force, stop, restart, status]` | 管理外部 MCP 连接 |
| `/helix-link`、`/helix-mode`、`/helix-unlink`、`/helix-home`、`/helix-stop` | 接入、筛选、移除或停止 Helix |
| `/shutdown`、`/quit`、`/q`、`quit`、`exit` | 停止本地 runtime 并退出，或仅退出前台 |

`/helix-mode` 和 `/helix-home` 发现 Helix runtime asset 缺失时会先显示确认菜单；确认后只下载，完成后需要重新打开应用，再通过 `--helix` 或 `/helix-link` 接入，不会在当前命令中启动服务。

如果你是从 [Software Center](https://github.com/PlaxtonFlarion/SoftwareCenter) 进入，建议先阅读 Software 首页内置 `README`，其中包含环境变量、后台管理中心与基础使用说明。

## 准备终端与环境变量

如果通过 `npm install -g @craftline/mind` 安装，通常不需要手动配置 `Mind/MindEngine` 路径。下面的 PATH 配置主要用于 Software Center 或安装包方式。

<div class="mind-panel-grid mind-panel-grid-tight">
  <div class="mind-panel">
    <span class="mind-kicker">终端建议</span>
    <ul class="mind-mini-list">
      <li>Windows：推荐 `Windows Terminal`</li>
      <li>macOS：推荐 `iTerm2`；系统 `Terminal` 不显示窗口进度状态</li>
      <li>其他终端默认不显示窗口进度状态</li>
      <li>npm 全局安装后，优先重新打开终端验证 `mind --help`</li>
    </ul>
  </div>
  <div class="mind-panel">
    <span class="mind-kicker">链路建议</span>
    <ul class="mind-mini-list">
      <li>不推荐默认挂 VPN 或系统代理</li>
      <li>只有明确要兼容网关时，再单独配置 `base_url`</li>
      <li>先保证直连可用，再谈代理兼容</li>
    </ul>
  </div>
</div>

macOS：

```bash
echo 'export PATH="/Applications/Mind/MindEngine:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

Windows：

```powershell
[Environment]::SetEnvironmentVariable(
  "Path",
  [Environment]::GetEnvironmentVariable("Path", "User") + ";C:\Program Files\Mind\MindEngine",
  "User"
)

$env:Path += ";C:\Program Files\Mind\MindEngine"
```

## CLI 命令速查

| 命令 | 作用 |
|------|------|
| `mind` | 进入交互模式 |
| `mind exec` / `mind e` | 执行一次非交互任务 |
| `mind resume` | 恢复交互会话 |
| `mind archive` / `mind unarchive` | 归档或恢复会话 |
| `mind agent` / `mind agent listen` | 远端订阅命令组和监听入口 |
| `mind upgrade` / `mind upgrade helix` | 运行组件升级命令组和 Helix 更新入口 |
| `mind doctor` | 只读诊断本地环境 |
| `mind mcp` | 外部 MCP 服务命令组 |
| `mind mcp list/get/add/remove/enable/disable/help` | 管理外部 MCP 注册 |
| `mind mcp-server` | 通过 stdio 暴露 MCP 服务 |
| `mind completion` | 生成 shell 补全脚本 |
| `mind help [COMMAND...]` | 查看命令帮助 |

进程级 `-c/--config`、`-p/--profile`、`-s/--sandbox`、`-a/--ask-for-approval` 可以放在根命令或子命令层级；完整选项组合见[命令行使用参考](../generated/cli-usage/)。

## 最小命令

完整的选项位置、图片与模型组合、stdin、会话恢复和 MCP 管理示例见[命令行使用参考](../generated/cli-usage/)。

### 先跑一条最小命令

```bash
mind exec "请用工程视角概述当前系统的核心能力、边界与典型使用场景"
```

### 需要持续交互时进入 REPL

```bash
mind
```

### 需要外接工具协作时使用 `exec`

```bash
mind exec "Open DBHub and query the users table"
```

外接 MCP 服务需提前可访问；如果同一轮还要搜索、修改或验证代码，也可以继续使用原生 coding 链路。

### 需要等待远端任务时用 `agent listen`

```bash
mind agent listen
```

## 交互式运行

如果你想连续试多个目标，直接进 REPL 更顺手：

```bash
mind
```

进入 REPL 后可继续输入目标：

```text
概述当前系统的核心能力与边界
对 path/to/video.mp4 做关键帧抽取，并输出证据
打开系统设置，稳定等待 2 秒后返回桌面
查询外接数据库里的 users 表
```

需要结束上一段上下文但继续留在 REPL 时，输入 `/new` 开始新对话；当前模型配置和待发送附件会保留。

如果要接回最近 24 小时内的旧会话，输入 `/resume` 打开恢复菜单。恢复列表会按当前工作区和会话来源筛选；菜单中用 `↑/↓` 滚动、`Enter` 选择、`q` 取消。

### 在 REPL 中调整模型

- 输入 `/model <model-id>` 可以只修改主模型 ID，例如 `/model gpt-5-codex`。
- 输入 `/effort` 可以用二级菜单选择推理强度：`low / medium / high / xhigh`。
- `/model <model-id>` 会写入本地 `config.toml` 的顶层 `model`；`/effort` 会写入顶层 `model_reasoning_effort`；当前正在进行的一轮不会中途切换，下一轮请求会读取新配置。
- 输入 `/preferences` 打开本地配置页面，适合同时维护模型名、API key、Base URL、route 和服务域名。

## 常见问题

### 已经联网，但一直 timeout？

- 这类问题优先归到网络链路问题，先关闭 VPN、本地代理和系统代理
- 某些 VPN 或代理会中断 CLI 长连接、SSE 或流式响应，表现为一直 `timeout`
- 先在直连网络下验证；只有明确需要兼容网关时，再配置 `base_url`

### 出现 SSL 证书错误？

- 这类问题优先归到证书链被改写，常见原因是抓包工具做了 HTTPS 中间人代理
- 先关闭抓包工具后再试；如果仍然开启证书注入，也会继续报这个错误
- `timeout` 和证书校验失败是两类问题：前者偏链路中断，后者偏 TLS 证书被替换或无法被系统信任

### 配置、环境变量和服务状态说明在哪里？

- [Software Center](https://github.com/PlaxtonFlarion/SoftwareCenter) 内置 `README`
- 当前页面
- 模型和密钥配置改为维护本地 `config.toml`
- REPL 中可用 `/model <model-id>` 快速更新主模型 ID，也可用 `/preferences` 打开配置页面

## 下一步看什么

<div class="mind-route-grid">
  <a class="mind-route-card" href="../generated/cli-usage/">
    <span class="mind-route-meta">Next</span>
    <h3>命令行使用参考</h3>
    <p>继续查 exec、resume、归档、订阅、图片、模型、stdin、MCP、帮助与补全命令的组合方式。</p>
    <span class="mind-card-arrow">查看命令 →</span>
  </a>
  <a class="mind-route-card" href="../capabilities/">
    <span class="mind-route-meta">Next</span>
    <h3>能力概览</h3>
    <p>继续确认不同执行模式和主要能力各自承担什么，不承担什么。</p>
    <span class="mind-card-arrow">查看边界 →</span>
  </a>
  <a class="mind-route-card" href="../reference/">
    <span class="mind-route-meta">Next</span>
    <h3>参考文档</h3>
    <p>准备继续读设备、协议、多媒体或性能专题时，从这里进入。</p>
    <span class="mind-card-arrow">查看专题 →</span>
  </a>
</div>
