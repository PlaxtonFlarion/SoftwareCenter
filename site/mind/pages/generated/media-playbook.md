# 多媒体链路实战教学 (Media Playbook)

README 只保留多媒体能力边界和入口说明；需要完整命令样例、组合链路和蓝本任务时，直接看这里。

## 阅读顺序 (Reading Order)
- 只想抽图：先看 `snapshot / frames / keyframes / scene`
- 只想改视频：再看 `trim / scale / convert / concat / remux / mute`
- 只想处理音频：再看 `extract_audio / replace_audio / convert_audio / play`
- 想做完整证据链：最后看组合链路和蓝本任务

## 能力覆盖 (Capabilities)
| 类型 | 入口 |
|------|------|
| 抽帧取证 | `snapshot / frames / keyframes / scene` |
| 视频处理 | `trim / scale / convert / concat / remux / mute` |
| 音频处理 | `extract_audio / replace_audio / convert_audio / play` |
| 组合链路 | 多步串联的媒体预处理与证据链任务 |

## 常见命令 (Common Commands)

### 单帧截图 (Single Snapshot)
```text
mind --fast "从 /path/to/demo.mp4 的第 3.5 秒抽取一张截图，并返回证据"
```

### 图片序列 (Frame Sequence)
```text
mind --fast "把 /path/to/demo.mp4 从第 0 秒开始按 2fps 导出图片序列，并返回输出目录"
```

### 关键帧提取 (Keyframe Extraction)
```text
mind --fast "从 /path/to/demo.mp4 提取关键帧，最多返回 8 张，并输出结果证据"
```

### 场景变化抽帧 (Scene Extraction)
```text
mind --fast "从 /path/to/demo.mp4 按场景变化抽帧，阈值 0.35，最多保留 10 张"
```

### 视频裁剪 (Video Trim)
```text
mind --fast "把 /path/to/demo.mp4 从第 12 秒裁到第 25 秒，并输出 mp4 片段"
```

### 视频缩放 (Video Scale)
```text
mind --fast "把 /path/to/demo.mp4 缩放到宽 720，高度等比，并输出新视频"
```

### 视频转码 (Video Convert)
```text
mind --fast "把 /path/to/demo.mov 转成 30fps 的 mp4，编码为 libx264，并返回结果"
```

### 视频拼接 (Video Concat)
```text
mind --fast "根据 /path/to/list.txt 拼接多个视频片段，输出 mp4 文件"
```

### 仅换容器 (Remux Only)
```text
mind --fast "把 /path/to/demo.mkv 仅换容器封装成 mp4，不重编码"
```

### 去音轨 (Mute Video)
```text
mind --fast "把 /path/to/demo.mp4 去掉音轨并输出静音视频"
```

### 视频信息探测 (Video Probe)
```text
mind --fast "探测 /path/to/demo.mp4 的视频信息，并返回时长与原始探测结果"
```

### 音轨抽取 (Audio Extract)
```text
mind --fast "从 /path/to/demo.mp4 提取音轨为 mp3，并返回输出文件"
```

### 替换音轨 (Replace Audio)
```text
mind --fast "用 /path/to/new_audio.m4a 替换 /path/to/demo.mp4 的音轨，并输出 mp4"
```

### 音频格式转换 (Audio Convert)
```text
mind --fast "把 /path/to/demo.wav 转成 16000Hz 单声道 mp3，并返回结果"
```

### 音频试听 (Audio Play)
```text
mind --fast "播放 /path/to/demo.mp3，音量 0.8"
```

## 组合链路 (Composed Flows)

### 录屏问题片段精简回放 (Trimmed Replay)
```text
mind --fast "先探测 /path/to/demo.mp4，再把第 15 秒到第 28 秒裁出来，然后从裁剪结果中提取关键帧，最多保留 6 张"
```

### 视觉证据链预处理 (Visual Evidence Preprocessing)
```text
mind --fast "把 /path/to/demo.mp4 先缩放到宽 720，再按场景变化抽帧，最多返回 10 张结果图"
```

### 音频分离与验证 (Audio Split and Verify)
```text
mind --fast "从 /path/to/demo.mp4 提取音轨为 wav，再转成 16000Hz 单声道 mp3，最后播放结果文件"
```

## 最佳实践 (Best Practices)
- 先 `probe`，再决定裁剪、抽帧、转码路径
- 报告配图优先用关键帧或场景帧
- 长视频优先 `trim` 再 `extract`
- 只改容器时优先 `remux`
- 涉及音轨处理时，最后接一次 `audio_play` 做验收

## 星图蓝本任务 (Blueprint Task)
只有当你要把探测、裁剪、抽帧、抽音轨、试听串成一条完整媒体证据链时，才需要写完整蓝本。单个媒体动作直接参考上面的单项命令即可。
