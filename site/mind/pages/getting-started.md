# 快速开始

如果你只想先跑起来，先按下面顺序看：

1. 先激活：`--apply`
2. 再配置：`--pref`
3. 再选模式：`chat / fast / plan`
4. 最后跑一个最小示例

## 激活与配置

### 第一步：激活授权

```bash
mind --apply YOUR_LICENSE_CODE
```

`--apply` 用于写入激活码并申请本地授权文件。

### 第二步：配置模型偏好

```bash
mind --pref
```

`--pref` 会拉起本地偏好设置前端页，用于配置两个模型槽位：

- `primary`
- `secondary`

每个槽位当前包含：

- `api`：目前支持 `OpenAI` 或 `Groq`
- `type`：`Text` 或 `Multimodal`
- `model`
- `apikey`
- `base_url`（可选）

如果你是从 [Software Center](https://github.com/PlaxtonFlarion/SoftwareCenter) 进入，建议先阅读 Software 首页内置 `README`，其中包含授权、环境变量、激活与基础使用说明。

## 推荐终端与环境变量

- Windows：推荐 `Windows Terminal`
- macOS：推荐 `iTerm2` 或系统 `Terminal`
- Windows 与 macOS 都建议先把 `mind` 所在目录加入 `PATH`
- 不推荐默认配置系统代理或挂 VPN；只有明确需要兼容网关时，再单独配置 `base_url`

macOS：

```bash
# Mind 示例
echo 'export PATH="/Applications/Mind.app/Contents/MacOS:$PATH"' >> ~/.zshrc

source ~/.zshrc
```

Windows：

```powershell
# Mind 示例（默认安装目录）
[Environment]::SetEnvironmentVariable(
  "Path",
  [Environment]::GetEnvironmentVariable("Path", "User") + ";C:\Program Files\Mind",
  "User"
)

$env:Path += ";C:\Program Files\Mind"
```

## 先怎么选模式

- **chat**
  适合探索、问答、临时任务。
- **fast**
  适合接口、媒体、短链路处理。
- **plan**
  适合巡检、固定流程和回归任务。

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

## 常见问题解答

### 1. 已经联网，但一直 timeout？

- 这类问题优先归到网络链路问题，先关闭 VPN、本地代理和系统代理
- 某些 VPN 或代理会中断 CLI 长连接、SSE 或流式响应，表现为一直 `timeout`
- 先在直连网络下验证；只有明确需要兼容网关时，再配置 `base_url`

### 2. 出现 SSL 证书错误？

- 这类问题优先归到证书链被改写，常见原因是抓包工具做了 HTTPS 中间人代理
- 先关闭抓包工具后再试；如果仍然开启证书注入，也会继续报这个错误
- `timeout` 和证书校验失败是两类问题：前者偏链路中断，后者偏 TLS 证书被替换或无法被系统信任

### 3. 授权、环境变量、激活说明在哪里？

- [Software Center](https://github.com/PlaxtonFlarion/SoftwareCenter) 内置 `README`
- 当前页面
- `mind --apply <code>`
- `mind --pref`

## 下一步看什么

- [能力概览](capabilities.md)  
  适合继续看模式边界和工具域边界。
- [参考文档](reference.md)  
  适合继续看批跑、回归和完整专题文档。
