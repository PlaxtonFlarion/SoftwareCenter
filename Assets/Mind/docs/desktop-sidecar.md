# 原生桌面 Sidecar

Sidecar 是由 Mind 启动和关闭的独立桌面进程，用来枚举窗口、观察界面、截图和发送鼠标键盘输入。普通用户通过 `computer` 工具使用它；开发者才需要关心构建命令与私有进程协议。

| 你要做什么 | 从哪里开始 |
| --- | --- |
| 让 Mind 观察或操作本机桌面 | [在 Mind 中启用](#在-mind-中启用)，无需先安装开发 SDK |
| 在 JavaScript 中组织多步操作 | [JS 用法与 skill 指引](#js-用法与-skill-指引) |
| 修改或验证 Windows 原生实现 | [构建与验证](#构建与验证) |
| 核对 macOS 支持范围和系统授权 | [macOS](#macos) |
| 接入或排查进程通信 | [私有 IPC v1](#私有-ipc-v1) |

桌面观察端口由 `agent/ports/desktop.py` 定义，进程传输由
`infrastructure/sidecars/desktop/` 实现。Windows 使用独立 C# 进程，macOS 使用独立 Swift 进程。
两种平台均提供窗口枚举、界面观察、截图和输入；Windows 的观察与截图分别使用 UI Automation 和 Windows.Graphics.Capture，macOS 使用系统辅助功能与 ScreenCaptureKit，具体差异见文末平台章节。Mind 通过单一 `computer` 工具调用，JS 使用现有 REPL 嵌套调用。
`computer` 与 `js_repl` 默认开启，仍按本次操作的权限规则审批。

TUI 将相邻 `computer` 调用合并为一个两行区块：操作期间显示 `Using computer` 和当前动作，
调用间隙在同一位置提示正在核对结果；只有前方指示符播放动画，标题与正文不做扫色。
人工审批期间指示符暂停。助手正文、其他工具或回合终态到来时，区块原位收束为
`Used computer`，显示调用数量及失败或未确认数量。该标题不表示应用中的任务目标已达成。
默认摘要隐藏输入文本、窗口引用和控件树，完整参数、审批与结果保留在 `Ctrl+T` 完整记录中；
恢复历史时同样合并为静态摘要。中断不把尚未收到结果的调用标为成功。

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

源码与打包版统一在首次获准调用 `computer` 时获取 CUA 清单并下载自包含运行库。
默认启动路径为 `%USERPROFILE%\.mind\runtimes\cua\win-x64\<version>-<hash前16位>\desktop-sidecar.exe`。
显式设置 `MIND_STATE_HOME` 时，`runtimes` 位于该状态根；不依赖当前工作目录或仓库中的 publish。
主 wheel、源码分发和 `build.py` 不再包含原生运行库，用户不需要 SDK 或本地构建。

首次安装展示 CUA 下载进度，安装总时限为 900 秒（包含清单、锁等待、下载与校验），单次网络
读取超时为 30 秒；安装不计入原生 IPC 请求超时。归档大小、SHA-256、解压路径和完整运行库
通过校验后才原子发布，临时 ZIP 随后删除。取消时等待解压线程结束再清理，进程崩溃留下的
暂存目录在下一次持锁安装时回收。跨进程 OS 文件锁阻止重复安装与半成品启动。

同一 Mind 进程固定已校验的版本。新进程查询新版本，旧版本保留供活动会话使用，不自动删除。
离线时可复用最后一次完整安装；401/403/404、非法清单或缓存损坏不回退。如果提示缓存损坏，
先退出使用 CUA 的所有 Mind 进程，只删除错误中指明的版本目录，再启动 Mind 自动重新下载；
不要在其他会话使用运行库时删除目录。macOS 与 Windows 使用各自的平台包和发布身份。

原生开发仍使用 `sidecars/cua_windows/publish` 作为上传输入，原生定向测试可直接调用该目录。
Windows 发布命令在 AppServer 仓库执行：`python test.py --service cua --station win32 --version <版本> --project-root <ProxyMind目录>`。
ZIP 与 Helix 共用 bucket 和 `toolkit-store/Mind/Windows/` 前缀，文件名包含版本和摘要，
但两者有独立清单项。上传成功后提交清单并部署 AppServer，新 Mind 进程才能选到新版本。
上传脚本复用服务端 R2 环境凭据，不在源码保存凭据，不上传 PDB、bin/obj 或临时 ZIP。
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
`host.tool` 成功返回的对象没有顶层 `ok`，工具失败会抛异常；不要用 `result.ok` 判断成败。
坐标以截图左上角为原点，必须满足 `0 <= x < image.width`、`0 <= y < image.height`；
`bounds.x/y` 是窗口在屏幕上的位置，不应叠加到传入的截图坐标。
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

指针按目标窗口的逻辑短边温和适配，绘制比例限定在原始设计的 37.8%–44.8%；主体高约
15–18 DIP，透明承载窗口约 54–65 DIP，包含柔影和波纹空间。预览按显示器范围适配。
目标物理尺寸先按指针所在显示器的 DPI 换算，系统显示缩放只应用一次；热点、柔影和
点击光圈使用相同比例，切换目标尺寸后重新定位，保持实际点击点不偏移。
移动仅改变该窗口的物理位置，不更新全屏蓝光画布；位置按实际经过时间计算，停帧后不会补播
积压的位置。蓝光保持静态，避免全屏透明层持续重绘拖慢移动。进入退出淡出时立即停止指针移动
和新波纹调度；窗口关闭由 WPF 应用生命周期统一处理，退出后再报告剩余窗口数量。
退出诊断 `frameTiming` 提供调度间隔的样本数、均值、P95、P99、最大值和超过 34 毫秒的次数；
排除启动首秒与退出淡出。这些数值不等同于显示器呈现帧率，也不测量真实输入延迟。

此独立预览不会生成真实输入，允许被捕获以便视觉验收。`computer` 的操作覆盖层复用同一
蓝光和指针绘制，按系统指针位置移动，并使用 `WDA_EXCLUDEFROMCAPTURE` 排除捕获。
真实输入的中间位置由 WPF 渲染回调采样，不再让每个鼠标事件同步等待 UI 线程；只在移动终点
与点击反馈前同步实际位置。不会排队补播过时坐标，也不会让视觉指针先于真实鼠标到达目标。
每个原生会话复用一对蓝光和指针窗口；操作结束立即隐藏、解除渲染回调并移除点击动画时钟，
会话关闭时销毁。下次显示前重新定位，避免旧位置闪现；隐藏窗口不持续驱动动画。
覆盖层不激活。真实输入期间，sidecar 启动独立的 system cursor manager 子进程，把 Windows
系统光标方案替换为透明光标，同时在目标输入线程隐藏原生光标；操作终止、sidecar 崩溃或
父进程退出都会恢复原有光标方案和显示计数，避免出现两个鼠标或遗留隐形光标；
窗口位置或 DPI 在操作中变化时先同步柔光边界，再停止输入，不追赶旧观察绑定的移动目标。
覆盖层仅在真实输入期间显示，枚举、截图与模型思考期间不显示；输入前校验失败也不会显示。
短暂点击的视觉反馈可能仅持续数百毫秒；可在专用窗口执行 1200 毫秒移动来观察指针和蓝光。
原生测试 `test_glow_preview.py` 验证预览窗口显示、前台保持、
穿透样式、小窗口尺寸、指针移动与蓝光位置独立、自动关闭及非法时长。
实际点击穿透、多屏、高 DPI 与截图排除仍需独立验收。

完整模型链路可在 Windows 交互桌面运行：

```powershell
dotnet build tests/fixtures/cua_windows/Fixture.csproj --configuration Release
python -m tests.manual.cua_visual_acceptance --directory .cache/cua-visual-acceptance
```

证据目录必须不存在；先构建原生测试夹具。该脚本通过操作系统 PTY 启动实际 `mind.py`，使用
当前模型配置和独立运行状态，由模型调用 `computer` 完成移动、点击及中文输入。采样器只读
专用窗口的计数、文字和覆盖层状态。通过条件包括 12 次成功移动、无工具失败、计数和中文输入
正确、出现两层覆盖窗口且会话退出后全部销毁。采样记录不等于显示器呈现帧率，主观流畅度仍需现场观察。

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

原生实现位于 `sidecars/cua_macos`，最低 macOS 14.2，仅支持 ARM64。
构建基线为 Xcode 26.3 / Swift 6.2.4；运行成品使用系统框架，不需要 Swift 或 .NET SDK。
Intel、Rosetta 下的 x64 Python 和低于 14.2 的系统明确返回 `unsupported_platform`。
单一 `computer` 工具、审批、JS 嵌套调用和 Harness 会话生命周期保持共用。

在仓库根目录构建开发包与测试夹具：

```sh
source venv/bin/activate
swift test --package-path sidecars/cua_macos --scratch-path .cache/cua-macos-swift --disable-sandbox
python sidecars/cua_macos/build.py --version 0.1.0
swift build --package-path tests/fixtures/cua_macos --scratch-path .cache/cua-macos-fixture --configuration release --disable-sandbox
python -m pytest tests/infrastructure/sidecars/desktop/test_macos_native.py --cua-native -q -rs
```

构建目录不可覆盖；同版本重新构建使用显式 `--output <新目录>`。测试默认使用
`sidecars/cua_macos/publish/0.1.0/runtime/DesktopSidecar.app/Contents/MacOS/desktop-sidecar`，
其他产物通过 `--cua-macos-executable <绝对路径>` 指定。未授权 GUI 测试会明确跳过；
协议、父进程退出、输入租约、背压与真实 bundle 安装测试无需代替系统授权。
GUI 验收只操作专用测试窗口，执行时停止手动输入。

bundle identity 固定为 `com.axionixlabs.desktop-sidecar`。默认 `--identity -` 生成 ad-hoc
开发包，不能当作已公证发布包；重编译改变 cdhash，不能承诺 TCC 权限随开发版升级保留。
正式发布使用同一 Developer ID 团队、bundle identity 和 helper 入口：

```sh
python sidecars/cua_macos/build.py --version 1.0.0 \
  --identity 'Developer ID Application: <持有人> (<TEAMID>)' \
  --notary-profile '<现有钥匙串 profile>'
```

脚本执行 hardened runtime 签名、notarytool 提交、staple、Gatekeeper 校验，成功后才发布新目录。
`artifact.json` 记录完整文件清单、版本、架构、签名身份、公证状态和归档 SHA-256；
`runtime/` 只包含 app bundle，ZIP 不带 SDK、构建缓存或测试夹具。
ad-hoc 包可以通过下载清单分发用于验证，仍不代表 Developer ID 签名、公证或跨机器运行验收已完成。

生产工厂查询现有 `service=cua, station=darwin, arch=arm64` 契约，安装到
`~/.mind/runtimes/cua/macos-arm64/<version>-<hash前16位>/DesktopSidecar.app/Contents/MacOS/desktop-sidecar`。
显式状态根、下载时限、跨进程安装锁、离线复用、损坏拒绝和活动会话固定版本与 Windows 相同。
解压后只给固定 Mach-O 入口恢复 0755，完整校验签名后原子发布；不会删除隔离属性或绕过 Gatekeeper。
在 AppServer 仓库执行 `python test.py --service cua --station darwin --version <版本> --project-root <ProxyMind目录>`，
读取 `sidecars/cua_macos/publish/<版本>/artifact.json` 并校验其 ZIP，原样上传至
`toolkit-store/Mind/MacOS/`，随后提交并部署清单。上传可在 Windows 执行，不重签名、不重压缩；
公证状态按构建元数据写入发布说明。Mac 与 Windows 的版本、摘要及发布时间分别保存，互不覆盖。
生产工厂只采用服务端清单选中的包，不会直接读取仓库 publish 或回退到另一平台资产。

首次系统授权可显式运行开发包入口 `--request-permissions`，按 macOS 提示打开
“系统设置 → 隐私与安全性”中的辅助功能、屏幕与系统音频录制、输入监控。
普通握手只做预检，不主动弹窗。系统验证由用户完成，不修改 TCC 数据库。
授权后关闭旧会话、reset 并重新握手；`captureSupported` 与 `inputSupported` 分别报告，
输入还要求事件投递和监控可用。宿主审批不替代 TCC；权限实际归属必须用当前启动链路验证，
不能仅凭设置开关推断成功。撤销或升级后同样需要重新验证。
从 IDE 或终端直接启动的进程可能由 macOS 归属给宿主：本机 TCC 日志显示 PyCharm
为 responsible process，单独授权 sidecar 不生效，需要用户为 PyCharm 授权。
若系统要求重启宿主，先保存工作再重启；不能通过更换启动归属或私有 entitlement 绕过授权。

AX 窗口以 PID、进程启动时间、AX 身份和 CGWindowID 联合识别；无法唯一匹配的窗口不猜测。
树限制 256 节点、8 层和软时间预算；AX 单次消息有超时。窗口/显示器/Space/权限修订、
几何及可见性在观察前后核对；移动再移回仍会使旧观察失效。捕获使用 ScreenCaptureKit
单窗口过滤，排除独立覆盖层、鼠标和阴影。PNG 超过 1 MiB 时尝试 JPEG；超过像素预算时
等比例缩小，返回真实宽高。截图不在原生观察缓存中保留。

AX 和 CGEvent 使用左上原点逻辑屏幕点；AppKit 使用按主屏顶部转换的坐标。
截图坐标依据本次图片宽高映射到本次窗口边界，支持负坐标计算；不能直接乘 `displayScale`。
`WIN` 在 macOS 映射为 Command，`ALT` 映射为 Option，`CTRL` 为 Control；字母键对应 ANSI
物理键位，F21–F24 明确拒绝。Unicode 文本逐标量提交，不使用剪贴板，最多 2048 个 UTF-16 单元。

输入前及分段执行中检查焦点、遮挡、最新观察和桌面状态。外部输入由事件 tap 触发锁停；
用户明确允许后才 reset。已知非控制台、锁屏、Secure Input 和系统安全面板会拒绝输入；
屏幕共享、远程会话等完整矩阵仍需实机确认。独立守护与 sidecar 使用同一签名入口，
登记按下状态后才提交事件；EOF、父进程异常退出时释放按键、鼠标和光标隐藏计数。
操作级租约位于 `/tmp/com.axionixlabs.desktop-sidecar-input-<uid>.lock`，冲突不重试桌面动作。
每个原生请求最多 25 秒，stdout 写入最多 5 秒；退出或 EOF 后无法清理的系统调用由独立时钟终止，
宿主仍保留 30 秒请求时限和关闭回收。协议错误、取消及未知结果均不可重放。

AppKit 复用一对点击穿透、不抢焦点的蓝光和小指针窗口，CADisplayLink 采样真实系统指针。
进入/退出动画期间不调度新移动；失败立即隐藏，空闲停止回调，会话结束销毁窗口。
可运行入口 `--preview 5` 查看不生成输入、自动退出且允许捕获的预览。
预览退出测试不等于人工视觉或实际呈现帧率验收；Retina、多屏、捕获排除和 P95/P99
呈现耗时仍需分别保留实机验收记录。
