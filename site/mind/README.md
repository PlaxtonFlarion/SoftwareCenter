# 官网壳说明

这个目录用于承载 `Mind` 的官网展示壳，不直接替代主仓库文档。

职责边界：
- `README.md` 与 `docs/*.md` 仍然是文档事实源
- `website/mind/docs_manifest.json` 负责定义哪些正文需要进入官网生成层，以及官网专题目录摘要
- `docs/README.md` 也由同一份文档清单生成，不再单独手写维护目录
- `website/mind/pages/` 负责官网入口、导航与站点配置
- 同步到 `SoftwareCenter` 后，预期映射到 `site/mind/`
- 工具能力说明与维护约定以 `docs/maintainer-guide.md` 为准，官网壳不单独发明第二套口径

当前状态：
- 已建立站点目录骨架
- 已补首页、快速开始、能力概览和参考文档入口
- 已补 `requirements.txt` 与 `scripts/sync_docs.py`
- 正文镜像页会生成到 `pages/generated/`
- `mkdocs.yml` 只保留入口导航，不再重复手写整套正文目录

建议的本地预览方式：
```bash
cd website/mind
pip install -r requirements.txt
python scripts/sync_docs.py
mkdocs serve
```

维护提示：
- 如果改了 `README.md` 或 `docs/*.md`，先把正文文档改对，再运行 `python scripts/sync_docs.py`
- 如果新增或下线正文文档，先改 `website/mind/docs_manifest.json`
- 如果改了工具说明，尤其是 `backend/mcp_tools/automator/` 下的 doc block，记得同步检查官网生成页的描述是否仍然准确
- 工具说明应按“做什么 / 不做什么 / 前置条件或限制”维护，避免官网和源码出现两套不同口径

部署到 Cloudflare Pages 时，直接参考：
- `CLOUDFLARE.md`
