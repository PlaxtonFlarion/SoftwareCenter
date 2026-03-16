# 交互模式详解

README 只保留交互式运行的入口说明；需要完整 REPL 指令、状态切换和输入约束时，直接看这里。

## 启动与提示
`mind` 进入循环后，会持续读取用户输入，并在 `CHAT / FAST / PLAN` 三种互斥状态之间切换执行。

- 顶部 banner 会随模式变化：`Chat / Fast / Plan`
- 每轮输入提示：`ready 输入目标或 /help`
- `mind_loop()` 会为一次会话生成 `cid / sid`，用于链路追踪与调用元数据

## 指令索引
- `/help, /h`：指令索引
- `/license, /lic`：授权许可信息
- `/subscription, /sub`：订阅与授权状态
- `/quit, /q, quit, exit`：安全退出
- `/model <name>`：切换推理引擎
- `/apikey <key>`：更新访问凭证
- `/chat`：切到 `CHAT`
- `/fast`：切到 `FAST`
- `/plan`：切到 `PLAN`

## 三种状态
| 状态     | 说明                                       | 适合场景            |
|--------|------------------------------------------|-----------------|
| `CHAT` | 对话驱动的流式工具闭环                              | 探索、问答、临场协作      |
| `FAST` | 裁剪工具集后的快速执行通道                            | 接口、文本、媒体短链路     |
| `PLAN` | 先生成计划，再按步骤顺序执行，并承载 `free_rule` 这类执行期规则判断 | 需要结构化步骤和更稳路径的任务 |

补充：
- `free_rule` 只属于 `PLAN` 执行面
- `--code` 中的 `global_rule / rule` 是蓝本规则层，不等同于 `free_rule`

切换成功后，终端会输出：
- `Exchange -> Chat`
- `Exchange -> Fast`
- `Exchange -> Plan`

## `/model` 指令
示例：
```text
/model gpt-4o-mini
```

当输入无效或缺失时，会打印候选列表并提示：
```text
model invalid: /model <...>
```

切换成功后，本轮循环后续调用都会使用新的 `model`。

## `/apikey` 指令
当输入无效或缺失时，会打印格式提示，例如：
- `sk-...`
- `gsk_...`
- `ds-...`
- `<token>`

并输出：
```text
apikey invalid: /apikey <...>
```

切换成功后，本轮循环后续调用都会使用新的 `apikey`。

## `/license` 与 `/subscription`
- `/license` 或 `/lic`：展示授权许可信息页
- `/subscription` 或 `/sub`：读取本地 License 文件并执行校验流程

适合快速确认当前机器的授权是否有效。

## 退出
任意时刻输入以下任一指令即可退出：
```text
/quit
/q
quit
exit
```

## 输入约束
- REPL 当前支持单行和多行输入
- 多行输入适合临时探索、长提示和分段目标描述
- 需要批跑、重复执行或多任务编排时，优先使用 `--code` 配合 `cfg.repeat / loop`
