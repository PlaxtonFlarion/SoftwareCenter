# 参考文档

官网壳只负责入口和导航，完整正文仍然来自同步后的文档源。

!!! note "阅读建议"
    先从“项目总览”或“文档索引”进入；只有在已经明确目标时，再直接跳到具体专题页。

## 怎么读

- 先看“项目总览”，确认整体入口和模式边界
- 再按专题跳到接口、媒体、性能或交互模式
- 只有维护或二次开发时再看维护者指南

## 文档导航
- [项目总览](../generated/overview/)  
  第一次进入项目时先读这一页，快速扫入口、模式边界和 CLI 主路径。
- [文档索引](../generated/docs-index/)  
  已经知道要找什么时，从这里按专题跳文档最快。
- [星图协议](../generated/cli-code/)  
  适合看批跑、回归、前后置、循环和蓝本规则层。
- [接口实战](../generated/api-playbook/)  
  适合看 HTTP、SSE、WebSocket、GraphQL 与其它协议场景。
- [交互模式](../generated/interactive-mode/)  
  适合看 REPL 指令、状态切换和输入约束。
- [多媒体链路](../generated/media-playbook/)  
  适合看关键帧、场景帧、音轨、裁剪、转码和拼接。
- [性能实战](../generated/performance-playbook/)  
  适合看 Memrix、Framix、Monkey 相关跑法与样例。
- [背景与架构](../generated/architecture/)  
  适合看系统分层、模型矩阵和工程摘要。
- [维护者指南](../generated/maintainer-guide/)  
  适合在维护文档、官网壳和同步链路时阅读。

## 生成方式

- 站点参考文档由 `scripts/sync_docs.py` 从正文文档源生成
- 私有仓库下，正文文档源是仓库根目录的 `README.md` 与 `docs/*.md`
- 同步到 `SoftwareCenter` 后，正文文档源变成 `Assets/Mind/README.md` 与 `Assets/Mind/docs/*.md`
