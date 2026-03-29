# 快速开始

如果你只想尽快把 Mind 跑起来，不需要先把所有专题正文看完。  
按这条路径走就够了：先确认环境，再选模式，最后发一条最小命令。

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
    <span class="mind-step-index">模式</span>
    <h3>按任务选择模式</h3>
    <p>探索走 <code>chat</code>，短链路走 <code>fast</code>，固定流程和回归走 <code>plan</code>。</p>
  </div>
  <div class="mind-step-card">
    <span class="mind-step-index">命令</span>
    <h3>发送最小命令</h3>
    <p>先跑通一条最小任务，再进入设备、协议、多媒体或星图专题。</p>
  </div>
</div>

<div class="mind-command-note">
  <strong>一条最短路径：</strong><code>mind --hello</code> → 选 <code>chat / fast / plan</code> → 发一条最小命令。先确认链路可用，再去读更长的专题正文。
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

## 模式怎么选

<div class="mind-panel-grid mind-panel-grid-tight">
  <div class="mind-panel mind-panel-accent">
    <span class="mind-kicker">chat</span>
    <h3>先确认能力边界</h3>
    <p>适合探索、问答、诊断和混合型任务。模型可边想边做，工具边界最宽。</p>
  </div>
  <div class="mind-panel">
    <span class="mind-kicker">fast</span>
    <h3>先跑短链路任务</h3>
    <p>适合接口、媒体和文本处理。工具集更窄，执行路径更干净。</p>
  </div>
  <div class="mind-panel">
    <span class="mind-kicker">plan</span>
    <h3>先拿稳路径</h3>
    <p>适合巡检、固定流程和回归。先生成计划，再按序执行。</p>
  </div>
</div>

## 最小命令

### 先用 `chat` 确认整体边界

```bash
mind --chat "请用工程视角概述当前系统的核心能力、边界与典型使用场景"
```

### 再用 `fast` 跑一个短任务

```bash
mind --fast "对 path/to/video.mp4 进行关键帧抽取，并返回可用证据"
```

### 需要稳路径时切到 `plan`

```bash
mind --plan "打开系统设置，稳定等待 2 秒后返回桌面"
```

## 交互式运行

如果你想连续试多个目标，直接进 REPL 更顺手：

```bash
mind
```

进入 REPL 后可随时切换：

```text
/chat
/fast
/plan
```

<div class="mind-command-note">
  <strong>理解边界：</strong>REPL 只是交互入口，真正决定执行行为的是 `chat / fast / plan` 三种模式。
</div>

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
    <p>继续确认三种模式和四个工具域各自承担什么，不承担什么。</p>
    <span class="mind-card-arrow">查看边界 →</span>
  </a>
  <a class="mind-route-card" href="./reference/">
    <span class="mind-route-meta">Next</span>
    <h3>参考文档</h3>
    <p>准备继续读设备、协议、多媒体、性能或星图专题时，从这里进入。</p>
    <span class="mind-card-arrow">查看专题 →</span>
  </a>
</div>
