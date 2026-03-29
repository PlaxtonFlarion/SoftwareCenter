# 能力概览

这页只回答三件事：

- 三种模式分别适合什么任务
- 四个工具域分别负责什么边界
- 当前目标应该继续跳去哪一类正文

<div class="mind-panel-grid mind-panel-grid-tight">
  <div class="mind-panel mind-panel-accent">
    <span class="mind-kicker">判断顺序</span>
    <h3>先看任务形态，再看工具域</h3>
    <p>模式解决的是“怎么执行”，工具域解决的是“由谁执行”。把这两件事分开看，选路径会更稳。</p>
  </div>
  <div class="mind-panel">
    <span class="mind-kicker">不要混淆</span>
    <ul class="mind-mini-list">
      <li><code>chat / fast / plan</code> 是执行模式</li>
      <li><code>device / bench / common / media</code> 是工具域</li>
      <li><code>global_rule / rule</code> 是星图规则层，不等于 <code>free_rule</code></li>
    </ul>
  </div>
</div>

## 先按这条顺序判断

<div class="mind-step-grid">
  <div class="mind-step-card">
    <span class="mind-step-index">目标</span>
    <h3>先判断是不是探索题</h3>
    <p>如果你还在问“能不能做、该怎么做”，先不要急着追求最短或最稳，优先选 <code>chat</code>。</p>
  </div>
  <div class="mind-step-card">
    <span class="mind-step-index">路径</span>
    <h3>再判断是不是短链路</h3>
    <p>如果任务更像接口、媒体、文本或文件处理，且目标明确，优先收敛到 <code>fast</code>。</p>
  </div>
  <div class="mind-step-card">
    <span class="mind-step-index">执行</span>
    <h3>需要稳步骤时改走 plan</h3>
    <p>巡检、回归、固定流程和可读步骤优先级更高时，再选 <code>plan</code>。</p>
  </div>
  <div class="mind-step-card">
    <span class="mind-step-index">正文</span>
    <h3>最后再找工具域正文</h3>
    <p>模式定完之后，再去看对应的设备、协议、性能或媒体专题，不要反过来硬套。</p>
  </div>
</div>

## 三种模式怎么判断

<div class="mind-route-grid">
  <div class="mind-route-card">
    <span class="mind-route-meta">chat</span>
    <h3>边想边做</h3>
    <p>最开放，适合探索、问答、诊断和混合型任务。模型可持续发起工具调用，不要求先把步骤完全定死。</p>
  </div>
  <div class="mind-route-card">
    <span class="mind-route-meta">fast</span>
    <h3>短链路收束</h3>
    <p>工具更窄，适合接口、媒体和文本处理。目标是尽快把短路径任务做完，而不是保留最大探索空间。</p>
  </div>
  <div class="mind-route-card">
    <span class="mind-route-meta">plan</span>
    <h3>稳路径执行</h3>
    <p>先列步骤，再按序执行，适合巡检、固定流程和回归。更看重步骤可读性和执行过程可复盘。</p>
  </div>
</div>

## 模式边界

<div class="mind-card-grid">
  <div class="mind-card">
    <h3>chat</h3>
    <p>执行协议：流式对话，模型可持续发起工具调用。</p>
    <ul class="mind-mini-list">
      <li>工具边界最宽，只排除少量特殊工具</li>
      <li>更适合先把问题问清、边做边收敛</li>
      <li>不主打固定步骤的稳定表达</li>
    </ul>
  </div>
  <div class="mind-card">
    <h3>fast</h3>
    <p>执行协议：流式对话，和 <code>chat</code> 同类闭环，但工具面更收敛。</p>
    <ul class="mind-mini-list">
      <li>排除设备域、部分 inspect、screen、Framix/Memrix</li>
      <li>更适合接口、媒体、文本和短链路任务</li>
      <li>不主打设备/UI 或重型性能链路</li>
    </ul>
  </div>
  <div class="mind-card">
    <h3>plan</h3>
    <p>执行协议：先出计划，再顺序执行步骤。</p>
    <ul class="mind-mini-list">
      <li>独立计划执行面，保留计划内循环</li>
      <li>排除 <code>security</code>、<code>bench.nexus</code> 与 <code>loop_steps</code></li>
      <li>更适合巡检、回归和固定流程</li>
    </ul>
  </div>
</div>

## 四个工具域负责什么

<div class="mind-card-grid">
  <div class="mind-card">
    <h3>device</h3>
    <p>应用与系统控制、UI 操作链、设备动作，以及端侧执行收束。</p>
  </div>
  <div class="mind-card">
    <h3>bench</h3>
    <p>性能、稳定性与接口执行面。协议能力实际落在 <code>bench.nexus</code>。</p>
  </div>
  <div class="mind-card">
    <h3>common</h3>
    <p>运行时观测、环境声明、规则承接和基础能力。</p>
  </div>
  <div class="mind-card">
    <h3>media</h3>
    <p>截图、录屏、音视频处理、抽帧、转码与帧级流水线。</p>
  </div>
</div>

<div class="mind-command-note">
  <strong>补充：</strong>接口能力不是独立 <code>api</code> 域，而是落在 <code>bench.nexus</code>；<code>free_rule</code> 属于 <code>plan</code> 执行期能力；<code>global_rule / rule</code> 属于 <code>--code</code> 的星图规则层。
</div>

## 常见误判

<div class="mind-panel-grid mind-panel-grid-tight">
  <div class="mind-panel">
    <span class="mind-kicker">误判一</span>
    <h3><code>fast</code> 不是轻量版 <code>chat</code></h3>
    <p>它不是“少一点能力的通用模式”，而是专门为短链路任务收窄过的执行面，不适合拿来做设备/UI 执行。</p>
  </div>
  <div class="mind-panel">
    <span class="mind-kicker">误判二</span>
    <h3><code>plan</code> 也不是全能模式</h3>
    <p>它强调步骤稳定和顺序执行，不等于所有工具都会开放；某些安全、接口和循环能力本来就不在这条执行面里。</p>
  </div>
  <div class="mind-panel">
    <span class="mind-kicker">误判三</span>
    <h3>接口能力不等于独立工具域</h3>
    <p>HTTP、SSE、WebSocket、GraphQL 等能力主要落在 <code>bench.nexus</code>，不是单独的 <code>api</code> 分类。</p>
  </div>
</div>

## 常见能力落点

<div class="mind-panel-grid mind-panel-grid-tight">
  <div class="mind-panel">
    <span class="mind-kicker">设备控制</span>
    <p>启动应用、切换页面、点击输入、滚动、系统开关和执行留证。</p>
  </div>
  <div class="mind-panel">
    <span class="mind-kicker">接口验证</span>
    <p>HTTP、SSE、WebSocket、GraphQL、Socket、邮件和文件协议。</p>
  </div>
  <div class="mind-panel">
    <span class="mind-kicker">性能链路</span>
    <p>Memrix 内存/流畅度、Framix 帧级诊断与视觉证据。</p>
  </div>
  <div class="mind-panel">
    <span class="mind-kicker">媒体链路</span>
    <p>关键帧、场景帧、音轨、裁剪、转码、拼接和证据输出。</p>
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
    <p>如果你已经知道要走设备、协议、星图、多媒体或性能哪条链路，从这里继续。</p>
    <span class="mind-card-arrow">去专题入口 →</span>
  </a>
</div>
