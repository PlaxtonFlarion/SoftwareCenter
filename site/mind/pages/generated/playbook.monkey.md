# Monkey 扰动

主 README 只负责入口；`device.monkey` 的参数、流程和返回结构继续看这里。
重点是看什么时候该用扰动、参数怎么调，以及哪些返回结果能直接拿来验收和排错。

## 先判断是不是这页的范围

- 你要做随机事件扰动、稳定性压测、异常发现：看这里
- 你要调 `seed / throttle_ms / touch / motion / nav / events` 这些参数：看这里
- 你要做稳定页面点击、输入和等待，不要先从 Monkey 文档开始
- 你只是想知道 device 域整体分层，先去 `playbook.device.md`

## 怎么读这页

- 先看“最小参数面”，确认当前工具真正暴露了哪些输入
- 再看参数说明，理解默认值适合什么场景、该往哪个方向调
- 最后看底层命令和结果字段，确认怎么留证、怎么复现、怎么排错

## 这页解决什么问题

- `injection` 工具到底做了什么
- 每个参数是什么意思
- 默认值适合什么场景
- 返回结果里哪些字段可以直接拿来验收或排错

一句话理解：

- Monkey 负责扰动和异常暴露
- 它不是稳定执行路径的替代品

## 工具入口

`Monkey` 当前对外暴露的是一个工具：

- `device.monkey.injection`

实现上分成工具定义层和执行层；对使用者来说，只需要记住工具入口即可，不必依赖内部目录结构。

## 最小参数面

当前完整参数如下：

```text
injection(
  package: str,
  seed: int = 42,
  throttle_ms: int = 150,
  touch: int = 65,
  motion: int = 20,
  nav: int = 10,
  events: int = 10000,
  matrix: dict[str, dict[str, Any]] | None = None
)
```

## 参数说明

### `package`

- 必填
- 指定要注入的目标包名

作用：

- Monkey 只会针对这个包执行事件注入

建议：

- 压测前先确认包已安装
- 更稳的链路里，通常先 `app_foreground` 或 `app_start`

### `seed`

- 默认 `42`

作用：

- 控制随机序列
- 相同参数和相同环境下，便于复现同一组随机事件

建议：

- 做回归时固定 `seed`
- 做探索时可以换种子扩大覆盖面

### `throttle_ms`

- 默认 `150`

作用：

- 每个 Monkey 事件之间的间隔，单位毫秒

影响：

- 值越小，注入越快，压力越大
- 值越大，节奏越慢，更接近人工交互

建议：

- 想看高压稳定性：减小 `throttle_ms`
- 想保留更多页面切换时间：增大 `throttle_ms`

### `touch`

- 默认 `65`

作用：

- `--pct-touch`
- 表示触摸事件占比

建议：

- UI 交互为主的应用可以维持较高占比

### `motion`

- 默认 `20`

作用：

- `--pct-motion`
- 表示手势/移动类事件占比

建议：

- 需要更多滚动、拖动、滑动类扰动时，可以适当调高

### `nav`

- 默认 `10`

作用：

- `--pct-nav`
- 表示导航类事件占比

建议：

- 想更多触发返回、方向、导航切换时，可以提高
- 如果只想在当前页面内做重度点击扰动，可以降低

### `events`

- 默认 `10000`

作用：

- 总注入事件数

影响：

- 值越大，测试越久
- 覆盖面更广，但也更容易引入长尾异常

建议：

- 快速冒烟：先用小一些的值
- 稳定性压测：再逐步拉高

### `matrix`

- 可选

作用：

- 多设备场景下，按 `serial -> args` 覆盖参数

适合：

- 不同设备跑不同包名
- 同一轮对不同设备使用不同 `seed / events / throttle_ms`

## 底层实际命令

当前实现会拼出类似这样的命令：

```text
adb -s <serial> shell monkey -p <package> \
  -s <seed> \
  --throttle <throttle_ms> \
  --pct-touch <touch> \
  --pct-motion <motion> \
  --pct-nav <nav> \
  --pct-appswitch 0 \
  --pct-syskeys 0 \
  --ignore-crashes \
  --ignore-timeouts \
  --ignore-security-exceptions \
  -v -v <events>
```

这里有几个重要点：

- `--pct-appswitch 0`
  - 不主动做应用切换
- `--pct-syskeys 0`
  - 不主动打系统键
- `--ignore-crashes`
- `--ignore-timeouts`
- `--ignore-security-exceptions`
  - 这些参数保证 Monkey 尽量继续跑，而不是一遇到异常就立即停

所以当前这套更偏：

- 在目标包内做稳定性扰动
- 不把系统级跳转比例开太大

## 实际执行流程

底层流程不是单纯启动 Monkey。

当前实现顺序是：

1. 清空 logcat
2. 启动 logcat 长连接
3. 等待约 `0.2s`
4. 启动 `adb shell monkey`
5. 并行读取 `logcat` 和 `monkey` 输出
6. 只保留命中关键词的 tail 和统计
7. Monkey 结束后回收 logcat 进程

## 内置关键词监测

当前会监测这几类异常：

- `crash`
- `anr`
- `oom`
- `monkey_abort`

内置匹配关键词包括但不限于：

- `FATAL EXCEPTION`
- `AndroidRuntime`
- `Fatal signal`
- `SIGSEGV`
- `SIGABRT`
- `ANR in`
- `Application Not Responding`
- `Input dispatching timed out`
- `OutOfMemoryError`
- `Failed to allocate`
- `Monkey aborted`
- `Monkey finished`
- `Events injected:`

注意：

- 只有命中这些关键词的行，才会进入 tail
- 这能降低噪音，但不等于完整 logcat 全量存档

## 返回结构

返回里最重要的是 `data` 字段，当前包含：

- `ok`
- `serial`
- `package`
- `seed`
- `throttle_ms`
- `pct.touch`
- `pct.motion`
- `pct.nav`
- `events`
- `monkey_cmd`
- `monkey_return_code`
- `start_ms`
- `end_ms`
- `duration_ms`
- `tail`
- `error`（有异常时）

这意味着你可以直接拿这些字段做：

- 时长统计
- 参数回放
- 失败排错
- 结果摘要

## 怎么理解 `ok`

当前实现里：

- 没抛 Python 层异常
- 且 `monkey_return_code` 有值

就会判成 `ok`

所以要注意：

- `ok=True` 不等于“没有 crash / ANR”
- 真正的异常痕迹，要继续看 `tail`

换句话说：

- `ok` 更接近“工具链跑完了”
- `tail` 更接近“业务稳定性证据”

## 推荐验收方式

如果你后续把 Monkey 纳入回归，建议至少看这几类字段：

- `monkey_return_code`
- `duration_ms`
- `tail`

更稳的判断方式通常是：

1. 先确认工具执行完成
2. 再检查 `tail` 里有没有 crash / ANR / OOM 证据
3. 必要时结合 `file_logcat_dump` 做额外留证

## 典型场景

### 1. 快速冒烟

特点：

- 小事件量
- 固定种子
- 先看有没有明显 crash

### 2. 稳定性压测

特点：

- 更长事件数
- 可能更小的 `throttle_ms`
- 重点看 ANR、OOM、崩溃 tail

### 3. 多设备回归

特点：

- 用 `matrix` 给不同设备传不同参数
- 统一收集 per-device 结果

## 实践建议

- 跑前先确认包名正确
- 需要复现问题时固定 `seed`
- 不要把 `ok=True` 当成“应用稳定无异常”
- 如果要深挖异常，再配合：
  - `device.file_logcat_dump`
  - `device.screenshot`
  - `media` 侧证据链

## 风险和限制

- 当前只暴露一组 Monkey 参数，不是完整 adb monkey 全参数面
- `tail` 是关键词过滤后的摘要，不是完整日志
- `--pct-appswitch` 和 `--pct-syskeys` 在当前实现里被写死为 `0`
- 结果里没有直接返回 `stats / evidence` 分类统计，当前主要暴露的是 `tail`

## 什么时候优先看这页

- 你要做稳定性扰动
- 你要把 Monkey 接入回归链
- 你在调 `seed / throttle_ms / events`
- 你想知道为什么工具显示成功，但应用其实可能已经异常

## 相关文档

- [设备域实战](playbook.device.md)
- [性能实战](playbook.performance.md)
- [星图协议](cli-code.md)
- [星图深入说明](cli-code-advanced.md)
- [文档索引](docs-index.md)
