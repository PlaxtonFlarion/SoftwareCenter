# 维护者指南

这份文档面向维护者和二次开发者，不面向普通使用者。  
主 README 负责上手入口；这里负责解释维护时需要同时关注的代码、文档和同步链路。

## 维护范围
- 模式边界：`chat / fast / plan`
- 工具域边界：`device / bench / common / media`
- 接口执行面：`bench.nexus`
- 星图执行链：`--code`
- 文档拆分与同步：`README.md`、`docs/*.md`、`.github/workflows/sync-to-software-center.yml`

## 系统骨架
当前文档与实现采用同一套高层心智模型：

```text
Mind (CLI / control plane)
  ↓
Helix (MCP / execution plane)
  ↓
device / bench / common / media
```

维护时需要保证三层同时一致：
- README 中的用户口径
- `docs/` 中的展开说明
- 代码与 CLI 帮助中的真实行为

## 模式边界
- `chat`：开放式流式工具闭环，工具范围最宽
- `fast`：裁剪工具集后的快速执行通道，适合接口、文本、媒体短链路
- `plan`：先生成计划，再按步骤顺序执行，并承载 `free_rule` 这类执行期规则判断能力

维护要求：
- 如果改了模式过滤逻辑，必须同步更新 README 的“运行模式”章节
- 如果改了 CLI 帮助或示例，也要确认 `README` 和 `docs/` 是否仍然对齐
- 不要在文档里承诺未实现的 REPL 指令
- 不要把 `free_rule` 和 `--code` 的 `global_rule / rule` 混写成同一个概念

## 工具域边界
- `device`：应用与系统控制、UI 操作链
- `bench`：性能、稳定性与接口执行面
- `common`：环境与基础能力
- `media`：截图、录屏、音视频处理与帧级流水线

关键约束：
- 接口能力不是独立 `api` 域，而是落在 `bench.nexus`
- 如果工具注册名、域名或能力归属变更，README 和 `docs/architecture.md`、`docs/api-playbook.md` 都要一起改

## 星图执行链
`--code` 承担批跑、循环、规则和前后置编排。

维护时要一起检查：
- README 的 `--code` 摘要
- `docs/cli-code.md`
- REPL / README 中对 `cfg.repeat`、`loop` 的引用

建议：
- 如果只是新增一个 `cfg` 字段，优先补进 `docs/cli-code.md`
- 只有当用户入口或默认用法变化时，才改 README

## 文档分层规则
- `README.md`：入口页，只保留最小上手、边界、速查和跳转
- `docs/README.md`：长文档索引，由 `website/mind/docs_manifest.json` 生成
- `docs/api-playbook.md`：接口约定与协议说明
- `docs/media-playbook.md`：媒体命令与链路
- `docs/performance-playbook.md`：性能星图与典型跑法
- `docs/interactive-mode.md`：REPL 说明
- `docs/architecture.md`：背景、云端架构、推理集群
- `website/mind/pages/`：官网展示壳与站点入口页
- `website/mind/docs_manifest.json`：官网生成层的正文清单与专题摘要
- `website/mind/CLOUDFLARE.md`：Cloudflare Pages 部署说明

维护原则：
- 用户入口变重时，优先下沉到 `docs/`
- 维护者说明不要反向塞回 README
- `website/mind/pages/generated/` 只当生成产物看，不要手改

## 文档维护约定
- 标题统一使用中文标题，不再在标题尾部追加英文副标题
- README 和 `docs/` 内部链接统一使用仓库内相对路径
- 命令行模式名称使用小写：`chat / fast / plan`
- REPL 内部状态名称使用大写：`CHAT / FAST / PLAN`
- 术语一旦在 README 中定稿，`docs/` 中应保持同一写法，不要派生近义口径
- 只要改了 `README.md`、`docs/*.md` 或 `LICENSE.md`，都应判断是否需要同步到 SoftwareCenter

### 工具文档约定
`backend/mcp_tools/` 下对模型直接暴露的工具，说明文本必须按“模型可读”和“MCP 客户端可消费”标准维护，不能把实现注释直接暴露成工具说明。

维护要求：
- 文档必须按真实能力写，不要承诺代码没有实现的行为
- 优先写“做什么 / 不做什么 / 前置条件或限制”，避免堆实现细节
- 工具说明应帮助模型判断是否该调用该工具，而不是解释内部实现过程
- 工具对外描述优先写在 `@mcp.tool(description=...)`，不要依赖函数 docstring
- 不要在 description 中重复 `domain / class / action / return` 这类内部标签；这些信息应由工具名、`meta` 和返回结构承担
- 不要在 description 中罗列完整参数清单；字段级说明应落到 `inputSchema`，优先用 `Annotated[..., Field(description=...)]` 或 Pydantic 输入模型
- 能力边界要写清：
  - 是否只下发命令
  - 是否会等待最终状态
  - 是否只看当前页面
  - 是否会自动滚动、自动点击、自动重试
- 前置条件要写清：
  - 是否依赖输入焦点
  - 是否依赖可滚动容器
  - 是否依赖系统权限、ROM 支持或输入法状态
- 不稳定或不建议依赖的能力要直接说明，不要写成默认推荐路径
- 参数默认值、可选值和实现保持一致；如果实现改了，doc block 要一起改
- 不要把“默认目录”“内部回填”“增强层自动传参”这类内部机制直接写进工具契约，除非它本身就是稳定能力边界

推荐写法：
- 第 1 句：这个工具实际执行什么动作
- 第 2 句：它不负责什么，或它的边界在哪里
- 第 3 句：它依赖什么条件，或在哪些情况下可能无效果/失败
- 句子里只点名真正影响选工具的关键参数，例如 `kind`、`saved`、`activity`
- 复杂参数多到一段 description 说不清时，优先补字段 description，不要把工具 description 写成参数手册

避免这样写：
- `D: / C: / A: / P: / R: / N:` 这类内部标签块
- “万能入口”“智能处理”“自动完成页面操作” 这类泛化表述
- 只写底层 adb 命令，不写实际能力边界
- 把内部增强层、helper、临时实现细节写成用户契约

## 同步链路
同步工作流在：
- `.github/workflows/sync-to-software-center.yml`

当前同步目标：
```text
SoftwareCenter/Assets/Mind/
  ├── README.md
  ├── LICENSE.md
  └── docs/

SoftwareCenter/site/mind/
  ├── mkdocs.yml
  ├── requirements.txt
  ├── scripts/
  └── pages/
```

维护要求：
- README 和 `docs/README.md` 必须使用仓库内相对路径，不要写本机绝对路径
- 如果新增 `docs/*.md`，要确认：
  - `website/mind/docs_manifest.json` 已补清单
  - 运行 `website/mind/scripts/sync_docs.py` 后，`docs/README.md` 已自动补索引
  - README 是否需要补入口
  - 同步后相对路径仍可达
- 如果改了 `website/mind/`，要确认同步后仍映射到 `SoftwareCenter/site/mind/`
- 如果改了正文文档结构，记得同步检查 `website/mind/docs_manifest.json`
- 同步 workflow 会先运行 `website/mind/scripts/sync_docs.py`，再复制官网壳到公共仓库

## 变更检查清单
每次涉及模式、文档或同步链路的改动，至少检查下面这些点：

1. README 的能力边界是否仍与实现一致
2. `docs/` 中对应长文档是否同步更新
3. 是否引入了绝对路径或失效相对链接
4. `sync-to-software-center.yml` 是否仍会把新增文档同步出去
5. `Docs 索引` 是否补到了新文档入口

## 适合新增深技术文档的场景
只有在下面几类情况，才值得继续加更深的技术文档：
- 新增工具注册机制或工具路由规则
- 新增模式或大改模式过滤逻辑
- 新增同步仓库、发布仓库或目录映射
- `--code` 解析和执行器出现结构性变化

否则优先保持当前文档层次，不要让入口文档重新膨胀。
