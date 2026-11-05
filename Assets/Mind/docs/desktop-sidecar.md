# 原生桌面 Sidecar

桌面观察端口由 `agent/ports/desktop.py` 定义，进程传输由
`infrastructure/sidecars/desktop/` 实现。Windows 使用独立 C# 进程，不依赖 Codex。
现有实现提供窗口枚举、UI Automation 控件树、Windows.Graphics.Capture 截图、目标激活、
鼠标键盘输入和操作覆盖层。Mind 通过单一 `computer` 工具调用，JS 使用现有 REPL 嵌套调用。
`computer` 与 `js_repl` 默认开启，仍按本次操作的权限规则审批。
场景验收范围见根目录[迭代清单](../CUA_IMPLEMENTATION_CHECKLIST.md)，macOS 留到最后实施。

## 构建与验证

Windows 开发使用 .NET SDK 10.0.403，安装在系统位置，不放入仓库。
`sidecars/cua_windows/global.json` 固定 SDK 基线，允许同 feature band 的补丁版本。
目标框架为 `net10.0-windows10.0.19041.0`；这是 API 编译基线，不代表该系统版本已完成验收。
Windows 发布配置生成 x64 自包含目录，携带 .NET 10 Windows Desktop Runtime；运行产物不要求
安装开发 SDK。尚未在未安装 .NET 的独立 Windows 机器上完成验收。

在 `sidecars/cua_windows` 中构建：

```powershell
dotnet restore DesktopSidecar.csproj --locked-mode
dotnet publish DesktopSidecar.csproj -p:PublishProfile=Windows -p:RestoreLockedMode=true
dotnet build ../../tests/fixtures/cua_windows/Fixture.csproj --configuration Release
dotnet build ../../tests/fixtures/cua_encoding/Encoding.csproj --configuration Release
```

在仓库根目录运行：

```powershell
. ./venv/Scripts/Activate.ps1
python -m pytest tests/infrastructure/sidecars/desktop -q
python -m pytest tests/infrastructure/sidecars/desktop -q --cua-native
```

第二条测试命令要求交互式 Windows 桌面，会打开专用测试窗口并操作真实鼠标键盘，期间应停止
手动输入。它断言控件树、截图、窗口引用失效、观察过期、资源上限、按钮计数、文本与按键释放。
未传 `--cua-native` 时原生测试明确跳过。
协议与故障测试使用独立进程替身，不把替身结果作为原生平台支持的证据。

JS 接入回归运行 `python -m pytest tests/integration/test_computer_integration.py -q`，要求 Node
22.22.0 或更高版本。真实 GUI 链路位于 `test_native_reliability.py` 的
`test_js_native_observation_and_reset`，同时验证生产注册表、审批账本、Node、C# 和重置。
若执行环境阻止子进程管道或桌面访问，应在允许这些能力的测试环境运行，保留原错误证据。

## 在 Mind 中启用

源码运行时先完成上述 publish；资产必须位于
`sidecars/cua_windows/publish/desktop-sidecar.exe`，相对于应用根定位，不依赖当前工作目录。
`publish` 是可运行资产，`bin/obj` 是可重建的中间产物。发布前校验目录包含自带运行时，
`build.py` 显式复制原生资产，wheel 使用相同清单且标记为 `win_amd64`，不携带构建缓存。
日常直接运行源码时，仅需保留完整 `publish` 目录；其中程序、DLL 和自带运行库共同构成运行资产。
需要分发时再生成 wheel，验证后可以清理安装包和空 `dist`，不影响源码调用。
已安装的旧版 `mind` 不会自动使用源码改动。

在仓库根目录启动本次源码版本，无需修改全局配置：

```powershell
. ./venv/Scripts/Activate.ps1
python mind.py
```

默认开关如下；已有配置显式设为 `false` 时仍会关闭对应工具：

```toml
[features]
computer = true
js_repl = true
```

两个开关独立：`computer` 可直接调用，JS 用法需要 `js_repl`。关闭 `computer` 时不注册工具，
不探测或启动原生进程。切换开关后重启 Mind。可用查询：

> 使用 computer 枚举窗口，找到我指定的计算器窗口，读取控件树并展示截图，然后停止。

观察和输入都使用本地桌面审批，绑定当前会话、轮次和调用 ID。审批卡展示动作和参数，仅支持本次
批准、拒绝或取消；拒绝不会启动原生进程。`workspace-write` 和启用功能本身不授予桌面权限。
显式 `full-access` 预设沿用完整权限语义，不再弹出审批；受限沙箱搭配 `never` 时明确返回
`approval_required`。本地审批类别不会扩展服务端 `tool.approval` 协议。`reset` 是资源清理，不弹审批。

## JS 用法与 skill 指引

先枚举并读取结果，再选择真实窗口引用：

```javascript
var desktopWindows = await host.tool("computer", {action: "list_windows"});
console.log(desktopWindows.data);
```

确认目标后用刚取得的引用观察。下例中的 `实际窗口引用` 必须替换为枚举结果：

```javascript
var desktopObservation = await host.tool("computer", {
  action: "observe", window: "实际窗口引用", screenshot: true
});
console.log(desktopObservation.data);
await host.emitImage(desktopObservation);
```

所有本地工具的结构化元数据始终从 `result.data` 读取，与是否有图片无关。
`output` 是展示内容，有图片时为图片内容数组；不要把它当作观察对象或丢弃结果外层。
`host.emitImage(result)` 只展示显式提交的图片。禁止把 Base64 整段打印到日志。
JS 交互脚本优先用 `var` 保存结果，避免重复声明 `const/let`；辅助依赖先定义再创建调用它的函数。
坐标动作必须沿用同一份带截图观察的 `data.observation`，不要另取无图观察覆盖它。
只有 `click` 支持控件索引；`move/drag/scroll` 必须使用截图坐标。

| 动作 | 参数 | 行为 |
|---|---|---|
| `list_windows` | `action` | 枚举有界窗口列表 |
| `observe` | `action, window, screenshot` | 读取控件树，按布尔开关返回截图 |
| `validate_observation` | `action, window, observation` | 校验当前引用，不构成后续输入授权 |
| `activate` | `action, window` | 显式请求前台激活，成功后重新观察 |
| `click` | `action, window, observation, target, button, count` | target 为 `{element: index}` 或 `{x,y}`；button 为 left/right/middle，count 为 1/2 |
| `move` | `action, window, observation, target, duration_ms` | 移动到截图坐标，duration_ms 为 0–1200 |
| `drag` | `action, window, observation, start, end, duration_ms` | 窗口内左键拖拽，时长 50–1200 ms |
| `scroll` | `action, window, observation, target, delta_x, delta_y` | 每轴 -20–20 格，正值向右/上，不允许两轴同时为零 |
| `press_key` | `action, window, observation, keys` | 1–4 个不重复大写按键，例如 `["CTRL","A"]`；每次都会释放 |
| `type_text` | `action, window, observation, text` | 最多 2048 UTF-16 单元，支持中文与 emoji，不使用剪贴板 |
| `reset` | `action` | 关闭当前桌面会话并作废全部引用 |

面向模型的 skill 应要求：先枚举、确认唯一目标、观察后再决定下一步；不猜测窗口或控件引用。
窗口变化、观察过期或 `reset` 后必须重新获取引用。每次输入后重新观察并核对应用结果；
`eventsSubmitted` 仅表示系统接受的事件数，`requiresObservation` 要求重新观察。失败不自动重放。
遇到用户鼠标键盘介入立即停止，只有用户明确要求继续后才 reset，不自动解除停止状态。
普通 `console.log` 不替代
`host.emitImage()`；专用视觉预览不代表已经操作桌面。无树或截断状态须按原结果说明。

## 会话所有权

组合根注入执行与生命周期两个端口；`agent/harness/sessions/desktop.py` 按 `sid` 惰性持有原生会话，
最多 128 个条目。一个 Mind 进程内的操作共享 FIFO 锁；根会话、子代理和后台会话隔离引用。
Windows 在系统交互会话内使用命名互斥锁，跨进程冲突明确返回 `desktop_busy`，不隐式排队重试。
释放守护进程拥有该锁和有界按下记录，私有管道断开时先释放按键，再放开锁。

工作目录或权限信封变化时，下一次获准调用先关闭原生进程再创建新会话。超时、通信失败或
活动调用被取消时回收进程；等待关闭的调用被取消不会中断后台清理。队列中的已关闭会话
拒绝执行。语义错误（例如过期观察）不重建进程，也不重放动作。

`computer` 的 `reset` 只清理桌面资源，保留 JS 变量；变量里的旧引用随即失效。
`js_repl_reset` 只重置 JS 内核。会话结束、删除、子代理关闭和宿主退出均清理两类资源。
原生进程关闭失败保留所有权供后续关闭重试，不把失败记作已回收。
JS Cell 的时间预算不包含宿主工具或审批等待；这些等待由对应工具生命周期负责超时和取消。
取消最后一个审批等待者会清理审批卡，不会在 JS 已结束后继续等待孤立确认。

## 蓝光预览

Windows 原生程序提供独立视觉预览。在 `sidecars/cua_windows` 目录运行：

```powershell
dotnet run --configuration Release -- --preview-glow 45
```

各显示器边缘显示宽幅蓝色柔光，四角填满，不绘制边框线；另用独立小窗口展示冰白代理指针、
移动轨迹和波纹。窗口不取得焦点、不进入任务栏，并设置鼠标穿透。
时长参数为 1–120 秒，出现和结束时渐变；按 Esc 可提前关闭。

指针绘制比例为原始设计的 80%，小窗口约 115 × 115 DIP，包含柔影和波纹空间。
移动仅改变该窗口的物理位置，不更新全屏蓝光画布；位置按实际经过时间计算，停帧后不会补播
积压的位置。蓝光保持静态，避免全屏透明层持续重绘拖慢移动。进入退出淡出时立即停止指针移动
和新波纹调度；窗口关闭由 WPF 应用生命周期统一处理，退出后再报告剩余窗口数量。
退出诊断 `frameTiming` 提供调度间隔的样本数、均值、P95、P99、最大值和超过 34 毫秒的次数；
排除启动首秒与退出淡出。这些数值不等同于显示器呈现帧率，也不测量真实输入延迟。

此独立预览不会生成真实输入，允许被捕获以便视觉验收。`computer` 的操作覆盖层复用同一
蓝光和指针绘制，按系统指针位置移动，并使用 `WDA_EXCLUDEFROMCAPTURE` 排除捕获。
覆盖层不激活。真实输入期间，sidecar 启动独立的 system cursor manager 子进程，把 Windows
系统光标方案替换为透明光标，同时在目标输入线程隐藏原生光标；操作终止、sidecar 崩溃或
父进程退出都会恢复原有光标方案和显示计数，避免出现两个鼠标或遗留隐形光标；
窗口位置或 DPI 在操作中变化时先同步柔光边界，再停止输入，不追赶旧观察绑定的移动目标。
覆盖层仅在真实输入期间显示，枚举、截图与模型思考期间不显示；输入前校验失败也不会显示。
短暂点击的视觉反馈可能仅持续数百毫秒；可在专用窗口执行 1200 毫秒移动来观察指针和蓝光。
原生测试 `test_glow_preview.py` 验证预览窗口显示、前台保持、
穿透样式、小窗口尺寸、指针移动与蓝光位置独立、自动关闭及非法时长。
实际点击穿透、多屏、高 DPI 与截图排除仍需独立验收。

## 私有 IPC v1

每个进程对应一个桌面会话，使用 UTF-8 JSONL。启动参数为 `--parent-pid <pid>`。
stdin EOF 正常退出，半帧 EOF 或超限请求非正常退出；父进程退出后原生进程结束。
stdout 只写协议，stderr 用于有界诊断。

```json
{"v":1,"id":"unique-request-id","action":"hello","parameters":{}}
```

成功响应只含 `v`、`id`、`ok: true`、`result`；失败响应只含 `v`、`id`、`ok: false`、
`error: {code, message}`。未知、缺失、重复字段均拒绝。请求 ID 不可重复使用。

| 操作 | 参数 | 结果 |
|---|---|---|
| `hello` | `{}` | 版本、平台、支持动作、坐标单位、捕获与输入能力 |
| `list_windows` | `{}` | 不透明窗口引用、标题、进程、边界、显示缩放、最小化状态和截断标记 |
| `observe` | `{window, screenshot}` | 观察引用、采集时间、边界、控件树和可选 PNG/JPEG |
| `validate_observation` | `{window, observation}` | 当前有效时返回 `{}`，失效返回结构化错误 |
| `activate` | `{window}` | `{eventsSubmitted, requiresObservation:true}` |
| `input` | `{window, observation, operation}` | 单个具名输入操作及系统提交数量 |

握手必须声明三个观察操作；`inputSupported=true` 必须同时声明 `activate/input`。
宿主核对观察结果与握手声明的坐标单位。

请求限制 64 KiB、响应限制 32 MiB，均包含帧末换行；窗口上限 128；控件上限 256、深度上限 8；
截图上限 1600 万像素和 8 MiB 编码数据；请求身份缓存上限 10000。
原生侧先编码 PNG，超过 1 MiB 优化目标时尝试 JPEG 90/85 质量、4:4:4 色度；
优先保留原尺寸，达到质量下限仍超过 8 MiB 时才等比例缩小。1 MiB 是优化目标，
不是强制牺牲分辨率的上限。图片格式、实际宽高与观察缓存同时返回。
客户端交付前与服务端统一校验完整结果 16 MiB、普通内容 2 MiB、单图 8 MiB；
预算计入 Base64 和元数据，多图合计不得超限。错误包含位置和字节数，不记录图像正文。
不可重试交付错误停止自动恢复，保持旧轮恢复门禁；补交复用冻结结果，不重新执行桌面动作。
控件树有软时间预算，单次第三方 UIA 调用仍可能阻塞；Python 请求硬超时后终止整个进程。
stderr 输出带 `id/action/phase/code` 的结构化失败诊断，`phase` 区分 `startup`、`communication`、
`observation`、`input`、`overlay` 和 `cleanup`，不记录参数正文或图片，宿主仅保留末尾 4 KiB；
超时、取消、通信断开不自动重放动作。工具调用记录仍遵守既有会话留存规则。

Windows 原生读取器按 8 KiB 分块读取并保留未消费的数据，支持一帧跨多个分片和一次读取多帧。
UTF-8 字符在完整帧组成后解析；达到 64 KiB 的完整请求可接受，超过限制或半帧 EOF 会终止传输。
窗口枚举用临时索引复用已有引用，避免逐窗口扫描上一轮全部引用；该索引不延长引用生命周期。
专用消息线程持有 WinEvent 钩子，记录被枚举窗口的代次和窗口级事件修订；枚举索引之外的
条目被清除。会话关闭在安装钩子的线程注销钩子并结束消息循环。

观察 adapter 的并发关闭共用一个任务。普通桌面请求的硬截止时间为 30 秒，以覆盖资源管理器
首次启动后的 UIA 读取和窗口截图；超过截止时间仍按不可重放错误处理。关闭先取消正在交换的请求、拒绝尚在排队的请求，
再发送 EOF，同时分块丢弃剩余 stdout 并排空 stderr，避免满管道阻塞进程退出；
两秒内未退出则终止进程。调用方取消对 `close()` 的等待不会取消后台回收，后续 `close()`
仍等待同一回收任务。桌面请求超时必须是有限正数。

Windows 窗口边界采用物理屏幕像素，控件边界相对窗口左上角；截图宽高采用图片像素。
`displayScale` 是显示缩放，不能直接当作截图转换倍率。坐标输入按本次实际图片宽高映射到同次
窗口物理边界，必须在截图内；没有截图的观察只允许控件索引定位。混合缩放仍需实机验收。
Windows 使用窗口句柄、进程 ID、线程 ID 和事件代次校验引用，销毁或重建使旧引用失效。
观察前后检查身份、窗口状态、边界、DPI 和事件修订，变化时拒绝交付混合状态结果。
WinEvent 通知异步到达，这不是对任意句柄复用竞争的原子保证；输入路径仍须在实际执行时
重新校验目标，不能把提前调用校验当作安全锁。

原生会话保存每窗口最新一条观察，总数不超过 128；每条最多持有 256 个 UIA 控件身份与边界，
不保留图片副本。控件输入前检查 RuntimeId、位置、启用/可见状态；每次输入尝试后作废观察。
有效期从观察完成按单调时钟计 120 秒，为模型、传输和审批留出时间；
每次枚举、观察或校验时淘汰过期和离开枚举范围的条目。窗口身份、几何、事件修订仍在输入前校验；
控件输入还检查实时名称、AutomationId、RuntimeId、位置与可用性，不能仅凭未超时执行。
再次观察先作废旧记录，即使刷新失败也不能复用旧观察。错误分类如下：

| 错误 | 含义 |
|---|---|
| `stale_observation` | 观察过期、被替换、已失效或不属于本会话/窗口 |
| `stale_window` | 原生身份或窗口代次已失效，需要重新枚举 |
| `window_changed` | 边界、DPI 或窗口级事件修订发生变化，需要重新观察 |
| `window_unavailable` | 窗口隐藏、最小化、被系统隐藏或无法读取边界/DPI |
| `desktop_busy` / `input_busy` | 其他进程正在输入，或 Windows 报告按键按下；后者带虚拟键码，尚未提交输入，释放后重新观察即可，无需 reset |
| `focus_changed` / `target_obscured` | 目标失焦或点击位置被其他窗口遮挡 |
| `input_interrupted` | 已提交部分事件后停止；可能有副作用，必须观察，不可重放 |
| `user_interrupted` / `input_stopped` | 外部输入介入；用户明确允许后才能 reset 恢复 |
| `desktop_unavailable` / `input_rejected` | 交互桌面不可用或系统拒绝输入；不自动提升权限 |
| `overlay_unavailable` / `input_guard_unavailable` | 视觉覆盖层或释放守护初始化/通信失败 |

校验失败后记录失效。移动后恢复原位置仍会因事件修订变化而拒绝旧观察。
这些检查不保证应用内部内容原子不变；控件索引只对本次观察有效，不是可永久复用的对象。

最小化或隐藏窗口明确不可观察；控件树无法读取时返回 `tree.error` 和截断事实。
UIA 在无窗口的 MTA 线程执行。截图在会话内惰性创建并复用一个 D3D 设备，关闭会话时释放；
WGC 帧池、捕获会话、帧和图像资源按请求释放，并限制等待首帧的时间。
观察引用和校验成功均不提供输入授权。

## macOS

共用端口与传输支持平台能力声明和逻辑屏幕点；Swift 原生 sidecar 尚未实现。
目标采用 Accessibility、ScreenCaptureKit、Quartz CGEvent 和 AppKit 覆盖层。
Mac 用户需要授予辅助功能与屏幕录制权限；权限归属、撤销、应用升级和签名须实机验证。
开发使用 Mac 上的 Swift / Xcode 工具链，运行成品不要求 .NET SDK。
最低系统版本、arm64 / x86_64 发布目标、Retina、Spaces、Secure Input 与签名公证均须
按清单验收；Windows 协议测试不替代 Mac 原生编译和桌面测试。
