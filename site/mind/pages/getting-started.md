# 快速开始

如果你只想先跑起来，先按下面顺序看：

1. 先激活：`--apply`
2. 再配置：`--pref`
3. 再选模式：`chat / fast / plan`
4. 最后跑一个最小示例

## 激活与配置

```bash
mind --apply YOUR_LICENSE_CODE
mind --pref
```

`--apply` 用于写入激活码并申请本地授权文件。  
`--pref` 用于配置默认模型参数，至少建议填写：

- `api`
- `model`
- `apikey`
- `base_url`（可选）

当前推荐填写方式：

```json
{
  "api": "OpenAI",
  "model": "gpt-4o-mini",
  "apikey": "sk-...",
  "base_url": ""
}
```

```json
{
  "api": "Groq",
  "model": "llama-3.3-70b-versatile",
  "apikey": "gsk_...",
  "base_url": ""
}
```

如果你走代理、中转或兼容网关，也可以填写：

```json
{
  "api": "OpenAI",
  "model": "gpt-4o-mini",
  "apikey": "sk-...",
  "base_url": "https://your-proxy.example.com/v1"
}
```

如果你是从 [Software Center](https://github.com/PlaxtonFlarion/SoftwareCenter) 进入，建议先阅读 Software 首页内置 `README`，其中包含授权、环境变量、激活与基础使用说明。

## 推荐终端与环境变量

- Windows：推荐 `Windows Terminal`
- macOS：推荐 `iTerm2` 或系统 `Terminal`
- Windows 与 macOS 都建议优先使用环境变量管理密钥和运行环境
- 不推荐默认配置系统代理或挂 VPN；只有明确需要兼容网关时，再单独配置 `base_url`

```bash
# macOS / zsh
export OPENAI_API_KEY="YOUR_API_KEY"
```

```powershell
# Windows PowerShell
$env:OPENAI_API_KEY="YOUR_API_KEY"
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

### 1. 开着抓包工具时一直 timeout？

- 先关闭抓包工具再试
- 某些抓包工具会影响 CLI 长连接、SSE 或流式响应
- 如果同时开着 VPN 或本地代理，也一并先关闭

### 2. 开着 VPN / 代理时不稳定？

- 不推荐在 VPN 场景下使用 Mind
- 如果开着 VPN、本地代理或抓包工具，先全部关闭
- 先在直连网络下验证；只有明确需要兼容网关时，再配置 `base_url`

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
