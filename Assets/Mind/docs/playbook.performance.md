# 性能实战

这页聚焦视觉真值、资源趋势、稳定性扰动和典型跑法。

## 先判断是不是这页的范围

- 你要看 E2E、ASR 首字上屏、VAD 尾字上屏、tokens/s 这类视觉真值结果：看这里
- 你要看 Android 内存、流畅度、趋势和回归：看这里
- 你要做随机扰动并保留异常日志：看这里
- 你只是想确认怎么启动，先回入口页，不必先读完整性能文档

## 怎么读这页

- 想看端到端体验：先看 `E2E / ASR / VAD / tokens/s`
- 想看资源趋势：再看 `Android 内存基线 / 内存泄漏 / 流畅度`
- 想做稳定性扰动：最后看 `Android 扰动`

一句话理解：

- Framix 更偏视觉真值和阶段报告
- Memrix 更偏指标采样和趋势分析
- 扰动能力更偏稳定性扰动和异常发现

## 能力速览

| 类型 | 入口 |
|------|------|
| 视觉真值 | Framix 帧分析与阶段报告 |
| 指标采样 | Memrix 内存 / 流畅度 / 趋势对比 |
| 稳定性扰动 | 随机扰动 + logcat 异常留痕 |
| 典型跑法 | `mind exec --mode chat "..." --helix` |

## E2E 耗时、ASR 首字上屏、VAD 尾字上屏、流式 tokens/s

```text
mind exec --mode chat "录制完整交互流程并生成 Framix 阶段报告，关注 E2E、ASR 首字上屏、VAD 尾字上屏和流式 tokens/s" --helix
```

核心目标是先保留真实交互视频，再做视觉真值分析，最后把阶段结果沉淀成报告。

## Android 内存基线

```text
mind exec --mode chat "围绕首页进入路径重复采样 10 轮，输出 Java Heap、Native Heap 和 PSS 的分层内存基线报告" --helix
```

基线关注稳定路径的趋势，不以单次采样数字作为结论。

## Android 内存泄漏

```text
mind exec --mode chat "重复执行首页到详情页再返回首页的路径，观察多轮后内存是否持续抬升并输出报告" --helix
```

泄漏判断关注重复进入退出后的趋势变化。

## Android 流畅度

```text
mind exec --mode chat "执行首页列表滚动路径并生成流畅度报告，观察 FPS、掉帧和卡顿趋势" --helix
```

流畅度验收关注完整图形路径，不只判断单次点击是否成功。

## Android 扰动

```text
mind exec --mode chat "对 com.example.app 执行 5000 个随机事件，节流 200ms，保留核心导航键并检查崩溃、ANR 和异常日志" --helix
```

同类目标也可以用英文或日文描述，执行语义保持一致。需要持续回归时，应由外部脚本或调度系统固定输入、次数和验收条件。

## 相关文档

- [Monkey 扰动](playbook.monkey.md)
- [设备与 UI 实战](playbook.device.md)
- [正文目录](README.md)
