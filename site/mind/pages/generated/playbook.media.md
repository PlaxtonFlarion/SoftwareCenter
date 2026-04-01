# 多媒体链路

这页聚焦文件处理、抽帧、转码、音轨和证据链任务。

## 先判断是不是这页的范围

- 你要抽帧、截图、裁剪、缩放、转码、拼接、去音轨、抽音轨：看这里
- 你要把录屏问题片段整理成可回看的证据链：看这里
- 你要理解页面语义、接口协议或安全签名，不要先从媒体文档开始
- 你只是想先跑最小命令，先回入口页，不必先把整篇媒体文档读完

## 怎么读这页
- 只想取证图片：先看 `snapshot / frames / keyframes / scene`
- 只想改视频文件：再看 `trim / scale / convert / concat / remux / mute`
- 只想处理音轨：再看 `extract_audio / replace_audio / convert_audio / play`
- 想做完整证据链：最后看组合链路和星图任务
- 如果你要把媒体链路真正写进 `--code`，结构层先配合星图协议页，执行语义再配合星图深入说明

一句话理解：

- 媒体工具负责处理文件和生成证据
- 它们不负责解释内容，也不负责替代设备或接口域

## 能力覆盖
| 类型 | 入口 |
|------|------|
| 取证画面 | `snapshot / frames / keyframes / scene` |
| 视频文件处理 | `trim / scale / convert / concat / remux / mute` |
| 音轨处理 | `extract_audio / replace_audio / convert_audio / play` |
| 组合链路 | 多步串联的媒体预处理与证据链任务 |

边界约定：
- 这些工具做的是媒体文件处理，不做内容理解
- 抽帧工具负责生成图片，不负责判断“哪一帧最重要”
- 视频处理工具负责改文件，不负责分析页面业务语义
- `audio_play` 是本机播放，不是把声音推送到设备
- `scrcpy_*` 是长会话控制，不是单次文件处理

## 常见命令

### 单帧截图
对应工具：`ffmpeg_extract_snapshot`
```text
mind --fast "从 /path/to/demo.mp4 的第 3.5 秒抽取一张截图，并返回证据"
```

### 图片序列
对应工具：`ffmpeg_extract_frames`
```text
mind --fast "把 /path/to/demo.mp4 从第 0 秒开始按 2fps 导出图片序列，并返回输出目录"
```

### 关键帧提取
对应工具：`ffmpeg_extract_keyframes`
```text
mind --fast "从 /path/to/demo.mp4 提取关键帧，最多返回 8 张，并输出结果证据"
```

### 场景变化抽帧
对应工具：`ffmpeg_extract_scene`
```text
mind --fast "从 /path/to/demo.mp4 按场景变化抽帧，阈值 0.35，最多保留 10 张"
```

### 视频裁剪
对应工具：`ffmpeg_trim_video`
```text
mind --fast "把 /path/to/demo.mp4 从第 12 秒裁到第 25 秒，并输出 mp4 片段"
```

### 视频缩放
对应工具：`ffmpeg_scale_video`
```text
mind --fast "把 /path/to/demo.mp4 缩放到宽 720，高度等比，并输出新视频"
```

### 视频转码
对应工具：`ffmpeg_convert_video`
```text
mind --fast "把 /path/to/demo.mov 转成 30fps 的 mp4，编码为 libx264，并返回结果"
```

### 视频拼接
对应工具：`ffmpeg_concat_video`
```text
mind --fast "根据 /path/to/list.txt 拼接多个视频片段，输出 mp4 文件"
```

### 仅换容器
对应工具：`ffmpeg_remux_video`
```text
mind --fast "把 /path/to/demo.mkv 仅换容器封装成 mp4，不重编码"
```

### 去音轨
对应工具：`ffmpeg_mute_video`
```text
mind --fast "把 /path/to/demo.mp4 去掉音轨并输出静音视频"
```

### 视频信息探测
对应工具：`ffmpeg_probe_video`
```text
mind --fast "探测 /path/to/demo.mp4 的视频信息，并返回时长与原始探测结果"
```

### 音轨抽取
对应工具：`ffmpeg_extract_audio`
```text
mind --fast "从 /path/to/demo.mp4 提取音轨为 mp3，并返回输出文件"
```

### 替换音轨
对应工具：`ffmpeg_replace_audio`
```text
mind --fast "用 /path/to/new_audio.m4a 替换 /path/to/demo.mp4 的音轨，并输出 mp4"
```

### 音频格式转换
对应工具：`ffmpeg_convert_audio`
```text
mind --fast "把 /path/to/demo.wav 转成 16000Hz 单声道 mp3，并返回结果"
```

### 音频试听
对应工具：`audio_play`
```text
mind --fast "播放 /path/to/demo.mp3，音量 0.8"
```

## 组合链路

### 录屏问题片段精简回放
```text
mind --fast "先探测 /path/to/demo.mp4，再把第 15 秒到第 28 秒裁出来，然后从裁剪结果中提取关键帧，最多保留 6 张"
```

### 视觉证据链预处理
```text
mind --fast "把 /path/to/demo.mp4 先缩放到宽 720，再按场景变化抽帧，最多返回 10 张结果图"
```

### 音频分离与验证
```text
mind --fast "从 /path/to/demo.mp4 提取音轨为 wav，再转成 16000Hz 单声道 mp3，最后播放结果文件"
```

## 最佳实践
- 先 `probe`，再决定裁剪、抽帧、转码路径
- 报告配图优先用关键帧或场景帧，不要默认把全量帧都塞回结果
- 长视频优先 `trim` 再 `extract`
- 只改容器时优先 `remux`
- 涉及音轨处理时，最后接一次 `audio_play` 做验收

## 星图任务
只有当你要把探测、裁剪、抽帧、抽音轨、试听串成一条完整媒体证据链时，才需要写完整星图。单个媒体动作直接参考上面的单项命令即可。

更自然的星图写法通常长这样：

```text
mind --plan --code media.md

# name: media_evidence_chain
从 `/path/to/demo.mp4` 中裁出第 `15` 秒到第 `28` 秒的问题片段。
输出到 `./artifacts/media/demo_trim.mp4`。
从裁剪结果里提取关键帧，最多保留 `6` 张。
输出目录写到 `./artifacts/media/keyframes`。
抽出音轨到 `./artifacts/media/demo_trim.mp3`。
播放一次，确认音频结果正常。
```

这个例子真正表达的是：
- 先裁剪，再抽帧，再抽音轨，再试听
- 重点是媒体处理顺序和证据链，不是要求读者手写工具参数
- 如果只是单步动作，直接用上面的 `mind --fast "..."` 更合适

## 相关文档

- [星图协议](cli-code.md)
- [星图深入说明](cli-code-advanced.md)
- [星图样例](code-blueprints.md)
- [正文目录](docs-index.md)
