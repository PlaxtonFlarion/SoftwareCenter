# 参考文档

官网壳只负责入口和导航，完整正文仍然来自同步后的文档源。  
这页的目标不是把所有长文档再抄一遍，而是帮你更快判断“下一页该去哪”。

<div class="mind-panel-grid mind-panel-grid-tight">
  <div class="mind-panel mind-panel-accent">
    <span class="mind-kicker">先这样读</span>
    <h3>先定目标，再进正文</h3>
    <p>先用入口页确认自己是在看入门、边界、专题还是维护说明，然后再进入对应正文，不要一开始就在完整目录里盲翻。</p>
  </div>
  <div class="mind-panel">
    <span class="mind-kicker">这页不做什么</span>
    <ul class="mind-mini-list">
      <li>不重复维护整套正文目录</li>
      <li>不替代 `docs-index` 和专题正文</li>
      <li>不承诺实现中不存在的能力</li>
    </ul>
  </div>
</div>

## 先走哪条阅读路径

<div class="mind-route-grid">
  <a class="mind-route-card" href="../getting-started/">
    <span class="mind-route-meta">Path A</span>
    <h3>我还没跑起来</h3>
    <p>先看环境、管理中心、模式选择和最小命令，不要直接跳长文。</p>
    <span class="mind-card-arrow">去快速开始 →</span>
  </a>
  <a class="mind-route-card" href="../generated/overview/">
    <span class="mind-route-meta">Path B</span>
    <h3>我先想看整体入口</h3>
    <p>先扫项目总览，确认 Mind 的定位、模式边界和常见使用路径。</p>
    <span class="mind-card-arrow">去项目总览 →</span>
  </a>
  <a class="mind-route-card" href="../generated/docs-index/">
    <span class="mind-route-meta">Path C</span>
    <h3>我已经知道要找什么</h3>
    <p>直接走完整目录，按专题跳文档最快，不必先读所有入口页。</p>
    <span class="mind-card-arrow">去文档索引 →</span>
  </a>
  <a class="mind-route-card" href="../generated/catalog/">
    <span class="mind-route-meta">Path D</span>
    <h3>我想按专题浏览</h3>
    <p>看自动生成的专题目录，用摘要快速筛掉当前不需要的正文。</p>
    <span class="mind-card-arrow">去专题目录 →</span>
  </a>
</div>

## 按同一套专题分组找正文

下面这组分法和仓库内 `docs/README.md`、自动生成的 `catalog.md` 保持一致。  
如果你在 repo 内和官网之间来回切换，阅读路径不会变。

<div class="mind-card-grid mind-card-stack">
  <div class="mind-card">
    <h3>入门与入口</h3>
    <p>适合你已经会跑主命令，但想补齐 REPL 指令、状态切换和交互边界时阅读。</p>
    <ul class="mind-mini-list">
      <li><a href="../generated/interactive-mode/">交互模式</a></li>
    </ul>
  </div>
  <div class="mind-card">
    <h3>编排与协议</h3>
    <p>适合你正在处理 `--code`、批量协议、模板层和验收结构时阅读。</p>
    <ul class="mind-mini-list">
      <li><a href="../generated/cli-code/">星图协议</a></li>
      <li><a href="../generated/code-blueprints/">星图样例</a></li>
      <li><a href="../generated/playbook.api/">接口实战</a></li>
      <li><a href="../generated/playbook.template/">模板能力</a></li>
    </ul>
  </div>
  <div class="mind-card">
    <h3>执行与取证</h3>
    <p>适合你正在处理设备动作、多媒体证据链和稳定性扰动时阅读。</p>
    <ul class="mind-mini-list">
      <li><a href="../generated/playbook.device/">设备域实战</a></li>
      <li><a href="../generated/playbook.media/">多媒体链路</a></li>
      <li><a href="../generated/playbook.monkey/">Monkey 扰动</a></li>
    </ul>
  </div>
  <div class="mind-card">
    <h3>性能与安全</h3>
    <p>适合你正在做性能回归、证据留痕、签名和加解密链路时阅读。</p>
    <ul class="mind-mini-list">
      <li><a href="../generated/playbook.performance/">性能实战</a></li>
      <li><a href="../generated/playbook.security/">安全工具</a></li>
    </ul>
  </div>
  <div class="mind-card">
    <h3>结构与维护</h3>
    <p>适合你正在看系统骨架、站点壳和同步链路，或准备二次开发时阅读。</p>
    <ul class="mind-mini-list">
      <li><a href="../generated/architecture/">背景与架构</a></li>
      <li><a href="../generated/maintainer-guide/">维护者指南</a></li>
    </ul>
  </div>
</div>

## CLI 速查

<div class="mind-panel-grid mind-panel-grid-tight">
  <div class="mind-panel">
    <span class="mind-kicker">配置入口</span>
    <p><code>mind --hello</code> 会拉起后台管理中心面板，统一管理 <code>primary / secondary</code> 模型槽位、日志与服务状态。</p>
  </div>
  <div class="mind-panel">
    <span class="mind-kicker">模式速记</span>
    <ul class="mind-mini-list">
      <li><code>mind --chat "..."</code>：探索、问答、临时任务</li>
      <li><code>mind --fast "..."</code>：接口、媒体、短链路处理</li>
      <li><code>mind --plan "..."</code>：巡检、固定流程、回归</li>
    </ul>
  </div>
</div>

如果你要看完整填写示例、环境变量和常见问题，直接跳到 [快速开始](../getting-started/)。

## 星图结构速读

<div class="mind-step-grid">
  <div class="mind-step-card">
    <span class="mind-step-index">L1</span>
    <h3>整次批跑</h3>
    <p>最外层控制整轮执行，常见字段是 <code>loop_prefix / loop_suffix</code>。</p>
  </div>
  <div class="mind-step-card">
    <span class="mind-step-index">L2</span>
    <h3>每一轮</h3>
    <p>轮次级控制放在 <code>round_prefix / round_suffix</code>。</p>
  </div>
  <div class="mind-step-card">
    <span class="mind-step-index">L3</span>
    <h3>每个任务块</h3>
    <p>任务块级 hook 放在 <code>item_prefix / item_suffix</code>。</p>
  </div>
  <div class="mind-step-card">
    <span class="mind-step-index">L4</span>
    <h3>当前任务正文</h3>
    <p>正文层由 <code>message</code> 承载；默认值和覆盖值分别落在 <code>global_* / *</code>。</p>
  </div>
</div>

<div class="mind-command-note">
  <strong>覆盖关系：</strong><code>prefix</code> 覆盖 <code>global_prefix</code>，<code>suffix</code> 覆盖 <code>global_suffix</code>，<code>rule</code> 覆盖 <code>global_rule</code>。执行控制层主要看 <code>repeat / pattern / attempts / stop_on_fail</code>。
</div>

## 这套文档怎么来的

- 参考文档清单由 `website/mind/docs_manifest.json` 统一维护
- 官网专题目录页会由 `scripts/sync_docs.py` 按清单自动生成
- 站点参考文档由 `scripts/sync_docs.py` 从正文文档源生成
- 私有仓库下，正文文档源是仓库根目录的 `README.md` 与 `docs/*.md`
- 同步到 `SoftwareCenter` 后，正文文档源变成 `Assets/Mind/README.md` 与 `Assets/Mind/docs/*.md`
