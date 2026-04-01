# 能力概览

这页只回答这些问题：

- 你当前更适合走命令行、交互式、蓝图协议，还是订阅
- 这几种使用方式分别适合什么任务
- 确认入口之后，下一步应该继续看哪一页

<div class="mind-panel-grid mind-panel-grid-tight">
  <div class="mind-panel mind-panel-accent">
    <span class="mind-kicker">判断顺序</span>
    <h3>先看怎么用，再看具体能力</h3>
    <p>先判断你当前需要的是一次性执行、持续交互、批跑编排，还是远端下发，再进入对应正文。不要一开始就陷进细节页。</p>
  </div>
  <div class="mind-panel">
    <span class="mind-kicker">不要混淆</span>
    <ul class="mind-mini-list">
      <li>命令行适合一次性任务和脚本执行</li>
      <li>交互式适合持续对话、边问边跑</li>
      <li>蓝图协议适合批跑、前后置和回归</li>
      <li>订阅适合本地等待远端下发任务</li>
    </ul>
  </div>
</div>

## 先按这条顺序判断

<div class="mind-step-grid">
  <div class="mind-step-card">
    <span class="mind-step-index">入口</span>
    <h3>先判断是不是一次性任务</h3>
    <p>如果你已经知道要做什么，只想立刻执行一条任务，先走命令行模式，不必先进入交互循环。</p>
  </div>
  <div class="mind-step-card">
    <span class="mind-step-index">互动</span>
    <h3>需要边问边试时进入交互式</h3>
    <p>如果你还在确认能力边界、做法和路径，交互式更合适，可以持续对话和反复调整。</p>
  </div>
  <div class="mind-step-card">
    <span class="mind-step-index">批量</span>
    <h3>需要批跑和规则时改走蓝图协议</h3>
    <p>如果你要把多条任务组织成可回放、可复用、可回归的执行蓝本，就不要再堆命令行，直接走 <code>--code</code>。</p>
  </div>
  <div class="mind-step-card">
    <span class="mind-step-index">下发</span>
    <h3>需要远端调度时走订阅</h3>
    <p>如果任务不是你在本地主动发起，而是等待服务端下发，就直接进入 <code>--agent</code>。</p>
  </div>
</div>

## 命令行模式

<div class="mind-card-grid">
  <div class="mind-card">
    <h3>适合什么</h3>
    <ul class="mind-mini-list">
      <li>一次性任务</li>
      <li>脚本执行和 CI</li>
      <li>已经知道目标，只差执行</li>
    </ul>
  </div>
  <div class="mind-card">
    <h3>典型写法</h3>
    <p><code>mind --chat "..."</code>、<code>mind --fast "..."</code>、<code>mind --plan "..."</code></p>
  </div>
  <div class="mind-card">
    <h3>继续看哪里</h3>
    <p>先去 <a href="./getting-started/">快速开始</a>，再根据任务类型跳到设备、协议、多媒体或性能正文。</p>
  </div>
</div>

## 交互式模式

<div class="mind-card-grid">
  <div class="mind-card">
    <h3>适合什么</h3>
    <ul class="mind-mini-list">
      <li>持续对话</li>
      <li>边问边跑</li>
      <li>反复试探能力边界</li>
    </ul>
  </div>
  <div class="mind-card">
    <h3>典型写法</h3>
    <p>直接执行 <code>mind</code> 进入 REPL，再在交互中持续推进当前任务。</p>
  </div>
  <div class="mind-card">
    <h3>继续看哪里</h3>
    <p>去 <a href="./generated/interactive-mode/">交互模式</a>，补齐 REPL 指令、输入边界和切换方式。</p>
  </div>
</div>

## 蓝图协议

<div class="mind-card-grid">
  <div class="mind-card">
    <h3>适合什么</h3>
    <ul class="mind-mini-list">
      <li>批跑</li>
      <li>前后置和规则化执行</li>
      <li>固定流程回归</li>
    </ul>
  </div>
  <div class="mind-card">
    <h3>典型写法</h3>
    <p><code>mind --chat --code api_batch.md</code> 或 <code>mind --plan --code workflow.md</code></p>
  </div>
  <div class="mind-card">
    <h3>继续看哪里</h3>
    <p>先读 <a href="./generated/cli-code/">星图协议</a>，再读 <a href="./generated/cli-code-advanced/">星图深入说明</a> 和 <a href="./generated/code-blueprints/">星图样例</a>。</p>
  </div>
</div>

## 订阅

<div class="mind-card-grid">
  <div class="mind-card">
    <h3>适合什么</h3>
    <ul class="mind-mini-list">
      <li>远端任务下发</li>
      <li>本地长链路监听</li>
      <li>恢复重连场景</li>
    </ul>
  </div>
  <div class="mind-card">
    <h3>典型写法</h3>
    <p><code>mind --agent</code></p>
  </div>
  <div class="mind-card">
    <h3>继续看哪里</h3>
    <p>去 <a href="./generated/agent-mode/">订阅模式</a>，看会话、长链路、恢复链路和排障说明。</p>
  </div>
</div>

## 常见误判

<div class="mind-panel-grid mind-panel-grid-tight">
  <div class="mind-panel">
    <span class="mind-kicker">误判一</span>
    <h3>所有事情都从交互式开始</h3>
    <p>⚠️ 不对。已经知道目标的任务，通常直接走命令行更干净。</p>
  </div>
  <div class="mind-panel">
    <span class="mind-kicker">误判二</span>
    <h3>批跑还靠一条条命令拼</h3>
    <p>⚠️ 不对。需要批跑、前后置和回归时，应尽快切到蓝图协议，不要继续堆散命令。</p>
  </div>
  <div class="mind-panel">
    <span class="mind-kicker">误判三</span>
    <h3>订阅只是另一种交互式</h3>
    <p>⚠️ 不对。订阅是独立入口，目标是等待远端下发任务，不是本地主动持续提问。</p>
  </div>
</div>

## 下一步看什么

<div class="mind-route-grid">
  <a class="mind-route-card" href="./getting-started/">
    <span class="mind-route-meta">继续</span>
    <h3>快速开始</h3>
    <p>如果你还没跑通最小命令，先去这里，不要直接钻专题正文。</p>
    <span class="mind-card-arrow">去入口页 →</span>
  </a>
  <a class="mind-route-card" href="./reference/">
    <span class="mind-route-meta">继续</span>
    <h3>参考文档</h3>
    <p>如果你已经知道下一步是设备、协议、蓝图、多媒体、性能还是订阅，从这里继续。</p>
    <span class="mind-card-arrow">去专题入口 →</span>
  </a>
</div>
