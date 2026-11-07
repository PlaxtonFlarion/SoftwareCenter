# 多媒体链路

本页按任务整理截图、抽帧、转码和音轨处理。先区分已有文件的加工与设备录制：本地文件可以由原生命令工具调用已安装的媒体程序处理；录屏、本机试听等 Helix 能力需要显式连接。

**运行示例前**

- 把输入文件放在项目的 `media/` 目录，或将示例路径替换成实际可访问的路径。
- 本地 FFmpeg 路径需要 `ffmpeg`、`ffprobe` 可用；安装 Mind 不代表这两个程序一定存在。可先用 `ffmpeg -version` 和 `ffprobe -version` 检查。
- 生成文件的单次任务使用 `-s workspace-write`，输出到工作区的新文件，便于保留原始材料。
- 使用 Helix 时以 `/tools` 的实际目录为准；`app` 过滤器并不保证所有转码能力都存在。录屏与音频工具可通过 `mind --helix` 接入。

## 先判断是不是这页的范围

适用于已有录屏或音视频文件的加工与取证。操作应用、点击控件、发起录屏的设备流程见[设备与 UI 实战](playbook.device.md)；解释画面中的阶段耗时见[性能实战](playbook.performance.md)。

## 怎么读这页
- 只想取证图片：先看截图、抽帧、关键帧和场景变化抽帧
- 只想改视频文件：再看裁剪、缩放、转码、拼接、换容器和去音轨
- 只想处理音轨：再看抽取音轨、替换音轨、音频转换和本机试听
- 想做完整证据链：最后看组合链路

一句话理解：

- 媒体工具负责处理文件和生成证据
- 它们不负责解释内容，也不负责替代设备或接口域

## 能力覆盖
| 类型 | 入口 |
|------|------|
| 取证画面 | 截图、抽帧、关键帧、场景变化抽帧 |
| 视频文件处理 | 裁剪、缩放、转码、拼接、换容器、去音轨 |
| 音轨处理 | 抽取音轨、替换音轨、音频转换、本机试听 |
| 组合链路 | 多步串联的媒体预处理与证据链任务 |

边界约定：
- 这些工具做的是媒体文件处理，不做内容理解
- 抽帧工具负责生成图片，不负责判断“哪一帧最重要”
- 视频处理工具负责改文件，不负责分析页面业务语义
- 音频试听是本机播放，不是把声音推送到设备
- 录屏会话控制属于长会话能力，不是单次文件处理

## 常见命令

### 单帧截图
```text
mind exec -s workspace-write "从 media/demo.mp4 的第 3.5 秒抽取一张截图，保存到 outputs/frame.png，并返回文件路径"
```

### 图片序列
```text
mind exec -s workspace-write "把 media/demo.mp4 从第 0 秒开始按 2fps 导出图片序列到 outputs/frames，并返回输出目录"
```

### 关键帧提取
```text
mind exec -s workspace-write "从 media/demo.mp4 提取编码关键帧，最多保留 8 张，保存到 outputs/keyframes"
```

### 场景变化抽帧
```text
mind exec -s workspace-write "从 media/demo.mp4 按场景变化抽帧，阈值 0.35，最多保留 10 张，保存到 outputs/scenes"
```

### 视频裁剪
```text
mind exec -s workspace-write "把 media/demo.mp4 从第 12 秒裁到第 25 秒，保存为 outputs/clip.mp4"
```

### 视频缩放
```text
mind exec -s workspace-write "把 media/demo.mp4 缩放到宽 720，高度等比，保存为 outputs/scaled.mp4"
```

### 视频转码
```text
mind exec -s workspace-write "把 media/demo.mov 转成 30fps、libx264 编码的 outputs/converted.mp4，并核对输出信息"
```

### 视频拼接
```text
mind exec -s workspace-write "根据 media/list.txt 中的文件顺序拼接视频，先检查格式是否兼容，再输出 outputs/joined.mp4"
```

### 仅换容器
```text
mind exec -s workspace-write "把 media/demo.mkv 重新封装为 outputs/remuxed.mp4，不重编码；若编码不兼容则说明原因"
```

### 去音轨
```text
mind exec -s workspace-write "把 media/demo.mp4 去掉音轨，输出 outputs/silent.mp4"
```

### 视频信息探测
```text
mind exec "探测 media/demo.mp4，列出时长、分辨率、视频编码和音轨信息"
```

### 音轨抽取
```text
mind exec -s workspace-write "从 media/demo.mp4 提取音轨为 outputs/audio.mp3，并返回输出文件"
```

### 替换音轨
```text
mind exec -s workspace-write "用 media/new_audio.m4a 替换 media/demo.mp4 的音轨，输出 outputs/replaced.mp4，说明音画时长处理方式"
```

### 音频格式转换
```text
mind exec -s workspace-write "把 media/demo.wav 转成 16000Hz 单声道的 outputs/converted.mp3，并核对输出信息"
```

### 音频试听
```text
mind --helix
```

连接后，在对话中输入“播放 `media/demo.mp3`，音量 0.8”。先确认文件路径可访问，实际播放由已连接的音频工具完成。

## 组合链路

### 录屏问题片段精简回放
```text
mind exec -s workspace-write "先探测 media/demo.mp4，将第 15 秒到第 28 秒裁剪到 outputs/clip.mp4，再提取最多 6 张编码关键帧到 outputs/evidence"
```

### 视觉证据链预处理
```text
mind exec -s workspace-write "把 media/demo.mp4 先缩放到宽 720，再按场景变化抽帧，将最多 10 张结果图保存到 outputs/evidence"
```

### 音频分离与验证
```text
mind exec -s workspace-write "从 media/demo.mp4 提取音轨为 outputs/audio.wav，再转成 16000Hz 单声道 MP3，核对输出时长与采样率"
```

## 最佳实践
- 先探测视频信息，再决定裁剪、抽帧、转码路径
- 报告配图优先用关键帧或场景帧，不要默认把全量帧都塞回结果
- 长视频优先先裁剪，再抽帧或转码
- 只改容器时优先只换封装，不重编码
- 涉及音轨处理时，最后接一次本机试听做验收

完成后至少核对输出文件是否存在、时长和格式是否符合目标，并打开代表性画面或音频片段。编码关键帧是视频压缩结构中的帧，不一定是业务上最重要的画面；命令返回成功也不代表内容已经符合预期。

## 相关文档

- [正文目录](README.md)
