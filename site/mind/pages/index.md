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
    <h3>先跑通，再进入对应正文</h3>
    <p>首页只给你最短入口：先完成启动，再进入能力判断和专题正文。</p>
  </div>
  <div class="mind-panel">
    <span class="mind-kicker">推荐路径</span>
    <ul class="mind-mini-list">
      <li>先去快速开始，把环境和最小命令跑通</li>
      <li>再去能力概览，判断当前该怎么进入</li>
      <li>最后去参考文档，按专题继续读正文</li>
    </ul>
  </div>
</div>

## 先从哪里进

<div class="mind-route-grid">
  <a class="mind-route-card" href="./getting-started/">
    <span class="mind-route-meta">Step 1</span>
    <h3>快速开始</h3>
    <p>适合第一次进项目。先把管理中心、环境变量和最小命令跑通。</p>
    <span class="mind-card-arrow">看启动路径 →</span>
  </a>
  <a class="mind-route-card" href="./capabilities/">
    <span class="mind-route-meta">Step 2</span>
    <h3>能力概览</h3>
    <p>适合确认当前该走命令行、交互式、蓝图协议还是订阅。</p>
    <span class="mind-card-arrow">看边界 →</span>
  </a>
  <a class="mind-route-card" href="./reference/">
    <span class="mind-route-meta">Step 3</span>
    <h3>参考文档</h3>
    <p>适合已经知道目标方向，要继续读设备、协议、星图、多媒体或性能正文时进入。</p>
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
      <li>或直接看 <a href="./generated/docs-index/">正文目录</a></li>
    </ul>
  </div>
</div>
