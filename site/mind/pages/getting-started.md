# 快速开始

如果你只想尽快把 Mind 跑起来，不需要先把所有专题正文看完。  
按这条路径走就够了：先确认环境，再发一条最小命令，最后再决定是否进入交互式、蓝图协议或订阅。

<div class="mind-step-grid">
  <div class="mind-step-card">
    <span class="mind-step-index">入口</span>
    <h3>确认后台管理中心</h3>
    <p>先用 <code>--hello</code> 打开配置面板，确认模型、日志和服务状态都可见。</p>
  </div>
  <div class="mind-step-card">
    <span class="mind-step-index">环境</span>
    <h3>准备终端与环境变量</h3>
    <p>把可执行目录加入 PATH，避免每次都手动定位安装目录。</p>
  </div>
  <div class="mind-step-card">
    <span class="mind-step-index">路径</span>
    <h3>先跑通，再决定怎么继续</h3>
    <p>先确认一条最小命令能跑通；后面是进入交互循环、批跑蓝图，还是订阅远端任务，再按需要继续分流。</p>
  </div>
  <div class="mind-step-card">
    <span class="mind-step-index">命令</span>
    <h3>发送最小命令</h3>
    <p>先跑通一条最小任务，再进入设备、协议、多媒体或星图专题。</p>
  </div>
</div>

<div class="mind-command-note">
  <strong>一条最短路径：</strong><code>mind --hello</code> → 发一条最小命令 → 再按需要进入交互式、蓝图协议或订阅。
</div>

## 先确认后台管理中心

<div class="mind-command-note">
  <strong>第一件事：</strong>不要一开始就堆长命令。先把管理中心拉起，确认主副模型槽位和本地服务状态都可见。
</div>

```bash
mind --hello
```

`--hello` 会拉起本地后台管理中心面板，统一管理：

- 主模型 / 副模型配置
- 本地运行日志
- 服务状态和基础环境

主副模型槽位为：

- `primary`
- `secondary`

每个槽位当前包含：

- `api`：目前支持 `OpenAI`
- `type`：`Text` 或 `Multimodal`
- `route`：`Responses` 或 `chat_completions`
- `model`
- `apikey`
- `base_url`（可选）

如果你是从 [Software Center](https://github.com/PlaxtonFlarion/SoftwareCenter) 进入，建议先阅读 Software 首页内置 `README`，其中包含环境变量、后台管理中心与基础使用说明。

## 准备终端与环境变量

<div class="mind-panel-grid mind-panel-grid-tight">
  <div class="mind-panel">
    <span class="mind-kicker">终端建议</span>
    <ul class="mind-mini-list">
      <li>Windows：推荐 `Windows Terminal`</li>
      <li>macOS：推荐 `iTerm2` 或系统 `Terminal`</li>
      <li>建议先把 `mind` 所在目录加入 `PATH`</li>
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
echo 'export PATH="/Applications/Mind.app/Contents/MacOS:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

Windows：

```powershell
[Environment]::SetEnvironmentVariable(
  "Path",
  [Environment]::GetEnvironmentVariable("Path", "User") + ";C:\Program Files\Mind",
  "User"
)

$env:Path += ";C:\Program Files\Mind"
```

## 最小命令

### 先跑一条最小命令

```bash
mind --chat "请用工程视角概述当前系统的核心能力、边界与典型使用场景"
```

### 需要持续交互时进入 REPL

```bash
mind
```

### 需要批跑和回归时用 `--code`

```bash
mind --chat --code api_batch.md
```

### 需要等待远端任务时用 `--agent`

```bash
mind --agent
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
```

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
- `mind --hello`

## 下一步看什么

<div class="mind-route-grid">
  <a class="mind-route-card" href="./capabilities/">
    <span class="mind-route-meta">Next</span>
    <h3>能力概览</h3>
    <p>继续确认不同执行模式和主要能力各自承担什么，不承担什么。</p>
    <span class="mind-card-arrow">查看边界 →</span>
  </a>
  <a class="mind-route-card" href="./reference/">
    <span class="mind-route-meta">Next</span>
    <h3>参考文档</h3>
    <p>准备继续读设备、协议、多媒体、性能或星图专题时，从这里进入。</p>
    <span class="mind-card-arrow">查看专题 →</span>
  </a>
</div>
