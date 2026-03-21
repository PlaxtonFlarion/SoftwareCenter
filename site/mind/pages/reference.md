# 参考文档

官网壳只负责入口和导航，完整正文仍然来自同步后的文档源。

!!! note "阅读建议"
    先从“项目总览”或“文档索引”进入；只有在已经明确目标时，再直接跳到具体专题页。

## 怎么读

- 先看“项目总览”，确认整体入口和模式边界
- 再看“文档索引”，按专题找到对应正文
- 只有当你要看字段、协议或执行结构时，再进入协议型文档
- 只有维护或二次开发时再看维护者指南

## CLI 速查

- `mind --apply YOUR_LICENSE_CODE`  
  用于写入激活码并申请本地授权文件。
- `mind --pref`  
  会拉起本地偏好设置前端页，用于配置 `primary / secondary` 两个模型槽位。
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

## 文档导航
- [项目总览](../generated/overview/)  
  第一次进入项目时先读这一页，快速扫入口、模式边界和 CLI 主路径。
- [文档索引](../generated/docs-index/)  
  已经知道要找什么时，从这里按专题跳文档最快。
- [星图协议](../generated/cli-code/)  
  适合看 `--code` 的字段、层级、前后置和规则结构。
- [星图样例](../generated/code-blueprints/)  
  适合看 `--code` 的高层自然语言样例，以及什么时候该写星图。
- [接口实战](../generated/api-playbook/)  
  适合看 `bench.nexus` 的协议边界、提取、断言和批量请求。
- [模板能力](../generated/template-playbook/)  
  适合看 `bench.nexus` 模板 helper、签名前置材料和模板层边界。
- [安全工具](../generated/security-playbook/)  
  适合看 `security_*` 的摘要、JWT、RSA、AES 和安全层边界。
- [设备域实战](../generated/device-playbook/)  
  适合看设备能力分层、稳定执行建议和自然语言任务写法。
- [Monkey 扰动](../generated/monkey-playbook/)  
  适合看 `device.monkey.injection` 的全部参数、执行流程和返回结构。
- [交互模式](../generated/interactive-mode/)  
  适合看 REPL 指令、状态切换和输入约束。
- [多媒体链路](../generated/media-playbook/)  
  适合看媒体能力边界、自然语言任务写法和证据链思路。
- [性能实战](../generated/performance-playbook/)  
  适合看 Memrix、Framix、Monkey 相关场景和回归写法。
- [背景与架构](../generated/architecture/)  
  适合看系统分层、模型矩阵和工程摘要。
- [维护者指南](../generated/maintainer-guide/)  
  适合在维护文档、官网壳和同步链路时阅读。

## 生成方式

- 站点参考文档由 `scripts/sync_docs.py` 从正文文档源生成
- 私有仓库下，正文文档源是仓库根目录的 `README.md` 与 `docs/*.md`
- 同步到 `SoftwareCenter` 后，正文文档源变成 `Assets/Mind/README.md` 与 `Assets/Mind/docs/*.md`
