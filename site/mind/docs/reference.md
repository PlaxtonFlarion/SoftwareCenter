# 参考文档

官网壳只负责入口和导航，完整正文仍然来自同步后的文档源。

## 生成方式

- 站点参考文档由 `scripts/sync_docs.py` 从正文文档源生成
- 私有仓库下，正文文档源是仓库根目录的 `README.md` 与 `docs/*.md`
- 同步到 `SoftwareCenter` 后，正文文档源变成 `Assets/Mind/README.md` 与 `Assets/Mind/docs/*.md`

## 站内入口

- [项目总览](reference/overview.md)
- [文档索引](reference/docs-index.md)
- [星图协议](reference/cli-code.md)
- [接口实战](reference/api-playbook.md)
- [交互模式](reference/interactive-mode.md)
- [多媒体链路](reference/media-playbook.md)
- [性能实战](reference/performance-playbook.md)
- [背景与架构](reference/architecture.md)
- [维护者指南](reference/maintainer-guide.md)

## 当前官网壳职责

- 提供首页、快速开始、能力概览和文档入口
- 不复制维护完整正文
- HTML 构建时应先运行 `scripts/sync_docs.py`
