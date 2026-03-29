# 参考文档

官网壳只负责入口和导航，完整正文仍然来自同步后的文档源。

!!! note "阅读建议"
    先从“项目总览”或“文档索引”进入；只有在已经明确目标时，再直接跳到具体专题页。

## 怎么读

- 先看“项目总览”，确认整体入口和模式边界
- 再看“文档索引”，按专题找到对应正文
- 只有当你要看字段、协议或执行结构时，再进入协议型文档
- 只有维护或二次开发时再看维护者指南
- 官网侧边栏只保留入口页，不再重复把整套正文列一遍

## CLI 速查

- `mind --hello`  
  会拉起后台管理中心面板，统一管理 `primary / secondary` 模型槽位、日志与服务状态。
- `mind --chat "..."`  
  适合探索、问答和临时任务。
- `mind --fast "..."`  
  适合接口、媒体和短链路处理。
- `mind --plan "..."`  
  适合巡检、固定流程和回归任务。

如果你要看完整填写示例、环境变量和常见问题，直接跳到 [快速开始](../getting-started/)。

## 星图结构速读

如果你在看 `--code`，可以先把它拆成两部分：

- 包裹结构：谁包谁
- 覆盖关系：默认值和单任务覆盖值怎么选

真正的包裹结构是：

```text
整次批跑
└─ 每一轮
   └─ 每个任务块
      └─ 当前任务正文
```

字段归属：

1. 最外层：整次批跑
   - `loop_prefix / loop_suffix`
2. 第二层：每一轮
   - `round_prefix / round_suffix`
3. 第三层：每个任务块
   - `item_prefix / item_suffix`
4. 第四层：当前任务正文
   - `message`

覆盖关系：

- `prefix` 覆盖 `global_prefix`
- `suffix` 覆盖 `global_suffix`
- `rule` 覆盖 `global_rule`

也就是说：
- `global_prefix / prefix` 是同一位置的默认值和覆盖值
- `global_suffix / suffix` 是同一位置的默认值和覆盖值
- `global_rule / rule` 是同一位置的默认值和覆盖值

执行控制层：
- `repeat / pattern / attempts / stop_on_fail`

## 文档入口
- [项目总览](../generated/overview/)  
  第一次进入项目时先读这一页，快速扫入口、模式边界和 CLI 主路径。
- [文档索引](../generated/docs-index/)  
  这页是完整正文目录；所有专题页统一从这里继续跳转，不再由官网壳重复维护第二份目录。
- [专题目录](../generated/catalog/)  
  这页由文档清单自动生成，保留官网侧需要的专题导览摘要，但不再手写维护。
- [快速开始](../getting-started/)  
  只关心安装、模式选择和最小命令时，先看这里。

## 生成方式

- 参考文档清单由 `website/mind/docs_manifest.json` 统一维护
- 官网专题目录页会由 `scripts/sync_docs.py` 按清单自动生成
- 站点参考文档由 `scripts/sync_docs.py` 从正文文档源生成
- 私有仓库下，正文文档源是仓库根目录的 `README.md` 与 `docs/*.md`
- 同步到 `SoftwareCenter` 后，正文文档源变成 `Assets/Mind/README.md` 与 `Assets/Mind/docs/*.md`
