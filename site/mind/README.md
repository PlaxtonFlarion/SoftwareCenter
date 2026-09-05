# 官网壳说明

这个目录用于承载 `Mind` 的官网展示壳，不直接替代主仓库文档。

职责边界：
- `ARCHITECTURE_SYSTEM.md` 是 Mind、AppServer 与 Fabric 的系统级架构权威
- `ARCHITECTURE.md` 是 ProxyMind 客户端内部架构权威，并受系统架构约束
- `ARCHITECTURE_SCORECARD.md` 是阶段性评审材料，不定义架构事实
- `README.md` 与 `docs/*.md` 负责入口、解释与教学，不反向定义架构事实
- 命令事实源固定为 `docs/cli-usage.md` 和 `docs/interactive-mode.md`；README 与官网入口页只保留摘要
- `website/mind/docs_manifest.json` 负责定义哪些正文需要进入官网生成层，以及官网专题目录摘要
- `docs/README.md` 也由同一份文档清单生成，不再单独手写维护目录
- `website/mind/pages/` 负责官网入口、导航与站点配置
- 同步到 `SoftwareCenter` 后，预期映射到 `site/mind/`
- 工具能力说明与维护约定以 `docs/maintainer-guide.md` 为准，官网壳不单独发明第二套口径

当前状态：
- 已建立站点目录骨架
- 已补首页、快速开始、能力概览和参考文档入口
- 已补 `requirements.txt` 与 `scripts/sync_docs.py`
- 已补 `scripts/check_docs.py`，校验实际命令注册表、文档覆盖和生成页内部链接
- 正文镜像页会生成到 `pages/generated/`
- `mkdocs.yml` 只保留入口导航，不再重复手写整套正文目录

建议的本地预览方式：
```bash
cd website/mind
pip install -r requirements.txt
python scripts/check_docs.py
python scripts/sync_docs.py
python scripts/check_docs.py --generated
mkdocs serve
```

维护提示：
- 如果改了两份架构权威、架构评分卡、`README.md` 或 `docs/*.md`，先把源文档改对，再运行 `python scripts/sync_docs.py`
- 如果改了 CLI 或 TUI 命令注册，先更新对应权威命令文档，再运行 `python scripts/check_docs.py`
- 如果新增或下线正文文档，先改 `website/mind/docs_manifest.json`
- 如果改了工具说明，尤其是 `backend/mcp_tools/automator/` 下的 doc block，记得同步检查官网生成页的描述是否仍然准确
- 工具说明应按“做什么 / 不做什么 / 前置条件或限制”维护，避免官网和源码出现两套不同口径

部署到 Cloudflare Pages 时，直接参考：
- `CLOUDFLARE.md`
