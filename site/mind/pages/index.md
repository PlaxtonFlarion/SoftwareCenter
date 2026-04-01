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
    <h3>先看入口，再看边界，最后看专题正文</h3>
    <p>首页只负责帮你确认 Mind 适不适合当前任务，不负责把所有协议、参数和执行细节一次讲完。</p>
  </div>
  <div class="mind-panel">
    <span class="mind-kicker">典型使用场景</span>
    <ul class="mind-mini-list">
      <li>打开应用、稳定等待页面、留证截图</li>
      <li>跑一条 HTTP / SSE / WebSocket 校验链</li>
      <li>对视频抽帧、转码、裁剪或拼接</li>
      <li>用 `--code` 做批跑、前后置和回归</li>
    </ul>
  </div>
</div>

## 先从哪里进

<div class="mind-route-grid">
  <a class="mind-route-card" href="./getting-started/">
    <span class="mind-route-meta">Step 1</span>
    <h3>快速开始</h3>
    <p>适合第一次进项目。先把管理中心、环境变量、模式选择和最小命令跑通。</p>
    <span class="mind-card-arrow">看启动路径 →</span>
  </a>
  <a class="mind-route-card" href="./capabilities/">
    <span class="mind-route-meta">Step 2</span>
    <h3>能力概览</h3>
    <p>适合先确认 `chat / fast / plan` 的边界、`agent` 的入口定位，以及四个工具域分别负责什么。</p>
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
  <strong>推荐顺序：</strong>先打开管理中心确认环境，再发一条最小命令，最后再决定是否切到更窄或更稳的模式。
</div>

### 先确认后台管理中心

```bash
mind --hello
```

### 再发一条最小命令

```bash
mind --chat "概述当前系统的核心能力、边界与典型使用场景"
```

### 按任务性质切模式

```bash
mind --chat "概述当前系统的核心能力与边界"
mind --fast "对 path/to/video.mp4 提取关键帧并返回证据"
mind --plan "打开系统设置，稳定等待 2 秒后返回桌面"
```

### 需要驻留监听时切到 `agent`

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
  <a class="mind-card mind-card-link" href="./generated/cli-code/">
    <h3>星图协议</h3>
    <p>先看结构层：字段、层级、文件格式和最小写法。需要覆盖优先级和执行语义时，再继续跳到星图深入说明。</p>
    <span class="mind-card-arrow">查看详情 →</span>
  </a>
</div>

## 三种模式怎么选

<div class="mind-panel-grid mind-panel-grid-tight">
  <a class="mind-panel mind-panel-link" href="./capabilities/#chat">
    <span class="mind-kicker">chat</span>
    <h3>最开放</h3>
    <p>适合探索、问答、诊断和混合型任务，模型可持续发起工具调用。</p>
  </a>
  <a class="mind-panel mind-panel-link" href="./capabilities/#fast">
    <span class="mind-kicker">fast</span>
    <h3>最短链路</h3>
    <p>适合接口、媒体和文本处理，工具集更窄，执行路径更干净。</p>
  </a>
  <a class="mind-panel mind-panel-link" href="./capabilities/#plan">
    <span class="mind-kicker">plan</span>
    <h3>最稳路径</h3>
    <p>先出结构化步骤，再顺序执行，更适合巡检、固定流程和回归任务。</p>
  </a>
</div>

<div class="mind-command-note">
  <strong>补充：</strong><code>agent</code> 是独立驻留订阅入口，不在上面三种本地主动执行模式里；需要远端任务下发和恢复重连链路时，直接看 <a href="./generated/agent-mode/">驻留与订阅模式</a>。
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
      <li>或直接看 <a href="./generated/docs-index/">文档索引</a></li>
    </ul>
  </div>
</div>
