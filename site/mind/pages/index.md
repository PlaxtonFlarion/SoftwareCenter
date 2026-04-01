<div class="mind-hero">
  <div class="mind-hero-copy">
    <span class="mind-eyebrow">ENGINEERING AGENT RUNTIME</span>
    <h1>Mind 代理思维</h1>
    <p>面向工程交付，强调可观测、可复盘和可扩展。</p>
    <div class="mind-cta-row">
      <a class="mind-cta mind-cta-primary" href="./getting-started/">快速开始</a>
      <a class="mind-cta mind-cta-secondary" href="./reference/">参考文档</a>
    </div>
  </div>
</div>

<div class="mind-panel-grid mind-panel-grid-tight">
  <div class="mind-panel mind-panel-accent">
    <span class="mind-kicker">阅读路线</span>
    <h3>先判断你要怎么使用，再进入对应正文</h3>
    <p>首页先帮你判断应该走 CLI 命令行、REPL 交互式、`--code` 星图协议，还是 `--agent` 订阅模式，再进入对应正文。</p>
  </div>
  <div class="mind-panel">
    <span class="mind-kicker">典型使用场景</span>
    <ul class="mind-mini-list">
      <li>用一条 CLI 命令直接完成一次任务</li>
      <li>进入 REPL 持续交互，边问边跑</li>
      <li>用 `--code` 组织批跑、前后置和回归</li>
      <li>用 `--agent` 进入订阅，等待远端下发任务</li>
    </ul>
  </div>
</div>

## 先从哪里进

<div class="mind-route-grid">
  <a class="mind-route-card" href="./getting-started/">
    <span class="mind-route-meta">Step 1</span>
    <h3>快速开始</h3>
    <p>适合第一次进项目。先把管理中心、环境变量、最小命令和四种入口形态跑通。</p>
    <span class="mind-card-arrow">看启动路径 →</span>
  </a>
  <a class="mind-route-card" href="./capabilities/">
    <span class="mind-route-meta">Step 2</span>
    <h3>能力概览</h3>
    <p>适合先确认能力边界、主要能力分别覆盖什么，以及本地主动执行和订阅执行分别覆盖什么。</p>
    <span class="mind-card-arrow">看边界 →</span>
  </a>
  <a class="mind-route-card" href="./reference/">
    <span class="mind-route-meta">Step 3</span>
    <h3>参考文档</h3>
    <p>适合已经知道目标方向，要继续读 `设备 / 协议 / 星图 / 多媒体 / 性能` 专题正文时进入。</p>
    <span class="mind-card-arrow">看专题入口 →</span>
  </a>
</div>

## 30 秒跑通

<div class="mind-command-note">
  <strong>推荐顺序：</strong>先打开管理中心确认环境，再跑一次 CLI，接着再决定是否进入 REPL、切到 `--code`，或直接启用 `--agent`。
</div>

### 先确认后台管理中心

```bash
mind --hello
```

### 先跑一次 CLI 命令行模式

```bash
mind --chat "概述当前系统的核心能力、边界与典型使用场景"
```

### 需要持续交互时进入 REPL

```bash
mind
```

### 需要批跑和回归时用 `--code`

```bash
mind --chat --code api_batch.md
```

### 需要订阅监听时切到 `--agent`

```bash
mind --agent
```

## 你会继续用到什么

<div class="mind-card-grid">
  <a class="mind-card mind-card-link" href="./generated/playbook.device/">
    <h3>设备与 UI</h3>
    <p>应用生命周期、页面交互、滚动点击和执行留证。</p>
    <span class="mind-card-arrow">查看详情 →</span>
  </a>
  <a class="mind-card mind-card-link" href="./generated/playbook.api/">
    <h3>接口与协议</h3>
    <p>HTTP、SSE、WebSocket、GraphQL 以及批量执行结构。</p>
    <span class="mind-card-arrow">查看详情 →</span>
  </a>
  <a class="mind-card mind-card-link" href="./generated/playbook.media/">
    <h3>媒体处理</h3>
    <p>关键帧、场景帧、音轨、裁剪、转码和证据输出。</p>
    <span class="mind-card-arrow">查看详情 →</span>
  </a>
  <a class="mind-card mind-card-link" href="./generated/playbook.performance/">
    <h3>性能链路</h3>
    <p>Memrix / Framix 采样、趋势留证和回归样例。</p>
    <span class="mind-card-arrow">查看详情 →</span>
  </a>
  <a class="mind-card mind-card-link" href="./generated/playbook.security/">
    <h3>安全工具</h3>
    <p>摘要、JWT、RSA、AES 与签名前置的边界拆分。</p>
    <span class="mind-card-arrow">查看详情 →</span>
  </a>
</div>

## 使用方式

<div class="mind-panel-grid mind-panel-grid-tight">
  <a class="mind-panel mind-panel-link" href="./getting-started/">
    <span class="mind-kicker">CLI</span>
    <h3>命令行模式</h3>
    <p>适合一次性任务、脚本执行和 CI。用一条命令直接完成当前目标，最快进入执行。</p>
  </a>
  <a class="mind-panel mind-panel-link" href="./generated/interactive-mode/">
    <span class="mind-kicker">REPL</span>
    <h3>交互式模式</h3>
    <p>适合持续对话、边问边跑、反复试探能力边界。进入交互循环后，再在内部切换具体执行状态。</p>
  </a>
  <a class="mind-panel mind-panel-link" href="./generated/cli-code/">
    <span class="mind-kicker">--code</span>
    <h3>星图协议模式</h3>
    <p>适合批跑、前后置、规则化执行和回归任务。重点是把多条任务组织成可复用的执行蓝本。</p>
  </a>
  <a class="mind-panel mind-panel-link" href="./generated/agent-mode/">
    <span class="mind-kicker">--agent</span>
    <h3>订阅模式</h3>
    <p>适合本地常驻监听、远端任务下发和恢复重连链路。它是独立入口，不属于本地主动执行流程。</p>
  </a>
</div>

## 下一步

<div class="mind-panel-grid mind-panel-grid-tight">
  <div class="mind-panel">
    <span class="mind-kicker">如果你刚开始</span>
    <ul class="mind-mini-list">
      <li>先读 <a href="./getting-started/">快速开始</a></li>
      <li>再看 <a href="./capabilities/">能力概览</a></li>
    </ul>
  </div>
  <div class="mind-panel">
    <span class="mind-kicker">如果你已经知道任务类型</span>
    <ul class="mind-mini-list">
      <li>去 <a href="./reference/">参考文档</a> 按专题继续读</li>
      <li>或直接看 <a href="./generated/docs-index/">完整目录页</a></li>
    </ul>
  </div>
</div>
