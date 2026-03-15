# 快速开始

如果你只想先跑起来，先按下面顺序看：

1. 先选模式：`chat / fast / plan`
2. 再跑一个最小示例
3. 需要深入时再跳到参考文档

## 先怎么选模式

- `chat`：适合探索、问答、临时任务
- `fast`：适合接口、媒体、短链路处理
- `plan`：适合巡检、固定流程和回归任务

## 最小示例

### `chat`

```bash
mind --chat "请用工程视角概述当前系统的核心能力、边界与典型使用场景"
```

### `fast`

```bash
mind --fast "对 path/to/video.mp4 进行关键帧抽取，并返回可用证据"
```

### `plan`

```bash
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

- 想看模式和工具边界：去 [能力概览](capabilities.md)
- 想看批跑与回归：去 [参考文档](reference.md) 里的星图协议
- 想看完整专题文档：去 [参考文档](reference.md)
