# 快速开始

如果你只想先跑起来，先记住三件事：

- 发散探索先用 `chat`
- 接口、媒体这类短链路任务优先 `fast`
- 固定流程、巡检和回归优先 `plan`

## 最小示例

```bash
# chat：先问系统能做什么
mind --chat "请用工程视角概述当前系统的核心能力、边界与典型使用场景"

# fast：做一个短链路媒体任务
mind --fast "对 path/to/video.mp4 进行关键帧抽取，并返回可用证据"

# plan：执行一条结构化动作链
mind --plan "打开系统设置，稳定等待 2 秒后返回桌面"
```

## 交互式运行

```bash
mind
```

进入 REPL 后可随时切换：

```text
/chat
/fast
/plan
```

## 下一步看什么

- 想看模式边界：去 [能力概览](capabilities.md)
- 想看批跑与回归：回到 `Assets/Mind/README.md` 中的 `--code`
- 想看完整长文档：去 [参考文档](reference.md)
