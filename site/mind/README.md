# 官网壳说明 (Website Shell)

这个目录用于承载 `Mind` 的官网展示壳，不直接替代主仓库文档。

职责边界：
- `README.md` 与 `docs/*.md` 仍然是文档事实源
- `website/mind/` 负责官网入口、导航与站点配置
- 同步到 `SoftwareCenter` 后，预期映射到 `site/mind/`

当前状态：
- 已建立站点目录骨架
- 已补首页、快速开始、能力概览和参考文档入口
- 已补 `requirements.txt` 与 `scripts/sync_docs.py`

建议的本地预览方式：
```bash
cd website/mind
pip install -r requirements.txt
python scripts/sync_docs.py
mkdocs serve
```

部署到 Cloudflare Pages 时，直接参考：
- `CLOUDFLARE.md`
