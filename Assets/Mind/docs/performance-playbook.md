# 性能实战教学

README 只保留性能能力边界和入口说明；需要完整蓝本样例与典型跑法时，直接看这里。

## 阅读顺序
- 想看端到端体验：先看 `E2E / ASR / VAD / tokens/s`
- 想看资源趋势：再看 `Android 内存基线 / 内存泄漏 / 流畅度`
- 想做稳定性扰动：最后看 `Android Monkey`

## 能力速览
| 类型 | 入口 |
|------|------|
| 视觉真值 | Framix 帧分析与阶段报告 |
| 指标采样 | Memrix 内存 / 流畅度 / 趋势对比 |
| 稳定性扰动 | Monkey + logcat 异常留痕 |
| 典型跑法 | `mind --plan --code ...` 或 `mind --chat "..."` |

下面几个 `cfg` 蓝本示例默认都用同一条命令运行：
```bash
mind --plan --code example.md
```

## E2E 耗时、ASR 首字上屏、VAD 尾字上屏、流式 tokens/s
``````
```cfg
attempts: 3
stop_on_fail: false

loop_suffix: |
  生成视频帧阶段报告
  
round_suffix: |
  Framix 分析视频帧
  
global_prefix: |
  开始录屏
  
global_suffix: |
  结束录屏
>>>
```

# name: performance-001
  打开APP首页，等待输入框出现，点击输入框，输入"你好"，点击发送，等待回复完成，执行5次
---
``````

## Android 内存基线
``````
```cfg
repeat: 10

loop_suffix: |
  生成分层内存测试报告

round_prefix: |
  开始采集内存
  
round_suffix: |
  结束采集内存
```

# name: performance-001
  打开APP首页，等待输入框出现，点击输入框，输入"你好"，点击发送
---
``````

## Android 内存泄漏
``````
```cfg
loop_suffix: |
  生成内存测试报告

round_prefix: |
  开始采集内存
  
round_suffix: |
  结束采集内存
```

# name: performance-001
  打开APP首页，等待输入框出现，点击输入框，输入"你好"，点击发送，执行10次
---
``````

## Android 流畅度
``````
```cfg
loop_suffix: |
  生成流畅度测试报告

round_prefix: |
  开始采集流畅度
  
round_suffix: |
  结束采集流畅度
```

# name: performance-001
  打开APP首页，等待输入框出现，点击输入框，输入"你好"，点击发送，执行5次
---
``````

## Android Monkey
```text
mind --chat "对 com.example.app 做一次 Monkey 随机事件注入测试，固定 seed 为 42，事件间隔 150 毫秒，触摸事件占 65%，滑动事件占 20%，导航事件占 10%，总事件数 10000。测试前先清理 logcat，测试过程中持续采集日志，并按异常关键词降噪保留关键 tail，最后输出执行结果和日志证据。"
```

说明：
- 同类目标也可以用英文或日文描述，执行语义保持一致
- 如果更偏批跑回归，建议把 Monkey 任务写入 `--code` 蓝本统一管理
