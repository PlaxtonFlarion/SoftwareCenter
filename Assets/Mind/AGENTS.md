# Agents

本文件只规定编码代理的工作方式、代码质量和验证流程。系统职责、依赖方向、状态所有权、
生命周期和稳定架构决策只以 `ARCHITECTURE.md` 为准；线上字段、端点、事件和错误只以服务端
正式契约及 `protocol/schema/`、`protocol/client/` 为准。对应目录中的局部 `AGENTS.md` 可以
补充本文件，但不能放宽更高层契约。

## 开始工作

- 修改前先阅读本文件、目标目录最近的局部 `AGENTS.md`、相关实现和测试。
- 先确认改动的职责归属、依赖方向、状态所有者和生命周期，再选择实现位置。
- 先检查 `git status --short`，保留用户已有改动；无关文件不回退、不重排、不顺手重构。
- 优先复用现有公开契约和生命周期。只有形成完整用例、明确删除条件并能移除旧路径时，才新增模块或端口。
- 同一次改造删除被替代字段、端点、语义和回退；未声明字段按不存在处理，不增加专用别名、`pop` 或兼容分支。
- 变更完成后同步受影响的稳定文档和契约测试；过程日志、迁移流水账和临时方案不写入长期文档。

## 代码约束

- 涉及新模块、端口或公开入口时，遵循 `ARCHITECTURE.md` 的依赖规则和扩展规则；本文件不重复架构定义。
- 不使用 `global`、`nonlocal`、`in locals()` 或 mixin。
- 路径、Shell、子进程、信号和文件操作默认兼容 Windows、Linux、macOS；平台差异必须隔离在职责明确的 adapter 中。

## 类型与边界

- 不使用 `typing.cast()`，也不通过别名导入 `cast`。类型不明确时修正真实契约，或用
  `isinstance`、显式的 `is None` / `is not None`、提前返回和具名局部变量完成收窄。
- 外部字典和第三方载荷先在边界校验，再转换为 `TypedDict`、dataclass 或其他具名类型。
- 跨层对象使用职责明确的 `Protocol` 或 ABC；第三方无类型交互隔离在 adapter 内，业务层只接收已验证类型。
- 类型声明必须符合真实可空性和返回值，不用 `Any`、`object`、`# type: ignore` 或宽泛的
  `# noinspection` 掩盖契约错误。

## 导入、命名与文档

- 普通 `import` 位于 `from ... import ...` 之前，每条 `import` 只导入一个模块；`typing`
  使用 `import typing`。单名称 from-import 使用单行，多名称按每行一个名称并保留尾逗号。
- 新增类、函数、方法、属性和常量按实际职责命名，不把 `Mind` 或 `mind` 扩展成新的领域语义。
- 既有品牌、包路径、稳定入口和外部契约中的 `Mind`/`mind` 保持不变；展示字符串中的产品信息、
  版本和编码使用 `metadata.const`。
- 非测试函数的 docstring 使用中文中性描述；新增 `Protocol`、ABC 或跨层契约要说明职责、生命周期和实现方约束。
- 代码注释只用于解释非显然的约束或复杂流程，不写空泛的逐行旁白。

## 测试与验证

- 使用 pytest 风格；异步测试使用 pytest 异步标记，mock 使用 `unittest.mock`。
- 先运行受影响模块的定向测试；共享配置、协议、控制器或公共契约变更再扩大范围。
- 新增功能或复杂行为变化覆盖核心成功路径和关键失败路径；小改动不机械增加低价值测试。
- 测试不直接修改进程环境，优先从上层注入派生值或依赖。
- `tests/test_package_architecture.py` 是架构边界审计，不得删除。日常迭代只运行受影响测试；
  包边界、依赖方向或发布收口变更时才运行完整审计。
- 先激活仓库虚拟环境，再使用平台无关命令：

  ```shell
  python -m pytest <targets> -q
  python -m pytest tests/test_package_architecture.py -q
  python -m compileall agent protocol frontends infrastructure observability metadata
  git diff --check
  ```

  第二条只在架构边界或发布收口时执行；普通迭代不把它作为默认门槛。

## 编辑与安全

- 搜索优先使用 `rg`；结构化数据使用解析器或项目现有 API，不做脆弱的字符串拼接。
- 手工修改使用 `apply_patch`；不使用 shell 重定向或临时脚本覆盖源码。
- 不使用 `# noinspection PyBroadException` 吞掉异常；应收窄异常类型，或通过不吞异常的生命周期清理保证状态收敛。
- 删除、覆盖、移动前确认目标范围属于用户请求；优先使用可恢复操作。禁止使用破坏性的
  `git reset --hard` 或 `git checkout --`，除非用户明确要求。
