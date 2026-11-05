# CUA 实施清单与 macOS 交接说明

本文件是 Windows / macOS Computer Use 的实施清单、协议基线和交接入口。它只记录可验证的工程事实与待办，不新增架构事实。职责、依赖方向、状态所有权和生命周期以 [ARCHITECTURE.md](client-architecture.md)、[ARCHITECTURE_SYSTEM.md](system-architecture.md) 为准；稳定使用说明以 [docs/desktop-sidecar.md](desktop-sidecar.md) 为准；服务端字段以 protocol/ 和正式服务端契约为准。

更新日期：2026-11-05
当前交接目标：在保留 Windows 可运行基线的前提下，由真实 Mac 完成 Swift sidecar、TCC、Retina、多屏、签名和实机验收。

## 1. 交接结论

| 范围                         | 状态       | 结论                                                                         |
|------------------------------|------------|------------------------------------------------------------------------------|
| 共用 Mind / JS / Python 端口 | 已完成     | 继续使用单一 computer 工具、现有 js_repl、Harness 会话和审批链               |
| Windows 原生 sidecar         | 可运行基线 | C# / .NET 10 自包含 x64 产物可由 Mind 直接调用，已有真实窗口、输入和视觉证据 |
| Windows 全场景               | 部分完成   | 多屏混合 DPI、长时间压力、跨应用矩阵和若干人工视觉项仍未收口                 |
| macOS 原生 sidecar           | 未开始     | 当前没有 Mac；不得用 Windows 协议测试或未编译 Swift 源码勾选完成             |
| Windows 运行产物             | 已收口     | 当前只保留 Mind 直接调用的 publish；另一台无 SDK 真机和正式跨机分发仍待验收  |

交接时以“可运行基线”和“未完成边界”两列为准。任何仅有代码、未在真实系统执行并留下证据的项目都保持未完成。

## 2. 当前可交付物与证据

### 2.1 Windows 运行资产

- [x] Mind 入口：D:\Projects\ProxyMind\venv\Scripts\python.exe D:\Projects\ProxyMind\mind.py。
- [x] 当前默认开启 computer 与 js_repl；两者仍经既有 schema、审批和会话生命周期，不增加平台专用 MCP。
- [x] 原生资产：sidecars/cua_windows/publish/desktop-sidecar.exe 及同目录自包含运行库。
- [x] 目录只保留最终运行资产；bin、obj、wheel、空 dist、Python 缓存和 pytest 缓存已清理。
- [x] publish 当前 245 个文件，约 163 MB；SHA-256：FA0EC7224BC2D42AFEC1E3BBC2AB994921051F7FBB415548B344E9E82DF23504。
- [x] 运行不依赖 codex.exe、@oai/sky、node_repl.exe 或 Codex 缓存目录。
- [x] .NET SDK 10.0.403 已在构建机完成安装、版本和 Release 构建验收；这不等同于跨机器运行验收。
- [ ] 尚未在一台未安装 .NET SDK 的另一台 Windows 真机上启动最终 publish；该项验证的是 self-contained 分发，不是 SDK 安装。

### 2.2 已完成的 Windows 真实证据

- [x] 真实 Mind TUI 会话完成枚举、观察、1200 ms 移动、按钮计数、中文输入和最终截图核对；用户现场确认蓝光与代理指针可见。
- [x] 真实 TTY 桌面会话完成 list_windows、observe、move；每次移动均提交真实输入事件。
- [x] 专用窗口完成 7 × 8 = 56；通过 UIA 控件引用点击 7、乘、8、等于，两个显示控件均报告 56，并通过 UIA 关闭计算器。
- [x] 原生观察、输入、会话、协议、视觉预览和宿主集合完成定向回归；纯 Python 定向集合 86 passed，架构审计 139 passed、1 warning。
- [x] 目标窗口移动或几何变化时，柔光边界先同步，随后旧观察失效并停止输入。
- [x] 真实输入期间隐藏系统光标，结束路径恢复原显示计数，避免出现两个鼠标。
- [x] 覆盖层已实现点击穿透、不抢焦点、截图排除和失败清理路径；排除效果、多屏和高 DPI 仍需硬件验收。

### 2.3 Windows 尚未收口

- [ ] 多显示器、混合 DPI、负坐标、热插拔和显示器变化。
- [ ] 单屏 125% / 150% / 200% 的真实截图、控件、输入和覆盖层一致性。
- [ ] Chromium / Electron、自绘无控件树应用和提升权限目标。
- [ ] 锁屏、UAC 安全桌面、远程会话断开、焦点被抢和目标遮挡。
- [ ] 长时间输入与观察压力、真实呈现帧耗时、空闲资源和输入延迟。
- [ ] 高 DPI、窗口边缘、全屏、取消和覆盖层捕获排除的人工视觉记录。
- [ ] 未安装开发 SDK 的 Windows 真机启动；这是最终运行资产的跨机器验收，不能用本机 SDK 存在替代此项。

## 3. 固定的职责与生命周期

### 3.1 依赖方向

- Application 负责工具参数、schema、审批和结果投影。
- Harness 负责按 sid 持有桌面会话、FIFO 调度、取消、reset 和关闭。
- infrastructure.sidecars.desktop 负责平台选择、子进程、私有 IPC、帧限制和外部载荷校验。
- sidecar 只负责原生窗口、控件、截图、输入、覆盖层和资源回收；不决定用户授权，不引入线上字段。
- agent.ports.desktop 只暴露平台无关的具名值和操作；不得向上泄露 HWND、AXUIElement 或平台指针。
- 只注册一个 computer 工具；不为 click、move、type 等动作增加独立 MCP 工具。

### 3.2 会话规则

- 一个 Mind 进程内桌面输入串行执行；跨会话或跨进程冲突返回 desktop_busy，不隐式重试。
- 窗口引用只属于创建它的会话；枚举、观察、窗口事件、DPI、reset、超时或关闭都会使旧引用失效。
- 每次输入只绑定一条最新观察；输入尝试后观察作废。输入结果只表示系统接受的事件数，不表示应用业务完成。
- 过期观察、窗口变化、焦点变化、目标遮挡和权限失败均返回结构化错误；不得重放 click、text 或 drag。
- 外部鼠标键盘介入立即停止当前动作；用户明确允许后才可 reset，不自动解除停止状态。
- sidecar EOF、取消、超时、宿主退出或进程崩溃都必须释放按下的键、鼠标按钮、覆盖层和进程资源。
- 观察和校验成功不等于输入授权；工具调用仍经过既有审批与 Effect 链。

## 4. 共用 IPC v1 基线（macOS 必须对齐）

传输为 UTF-8 JSONL。stdout 只写协议，stderr 只写有界结构化诊断。父进程退出后 sidecar 必须退出；正常 stdin EOF 与半帧 EOF 必须区分。

请求形状：

    {"v":1,"id":"unique-request-id","action":"hello","parameters":{}}

成功响应只含 v、id、ok=true、result；失败响应只含 v、id、ok=false、error，其中 error 只含 code、message。未知字段、缺失字段、重复 JSON 键、重复请求 id 均拒绝。

### 4.1 操作与结果

| action               | 输入                           | 必须返回                                                                       |
|----------------------|--------------------------------|--------------------------------------------------------------------------------|
| hello                | 空参数                         | protocol、platform、actions、coordinateSpace、captureSupported、inputSupported |
| list_windows         | 空参数                         | 不透明窗口引用、标题、PID、边界、displayScale、最小化状态、truncated           |
| observe              | window、screenshot             | observation、采集时间、边界、displayScale、coordinateSpace、控件树、可选图片   |
| validate_observation | window、observation            | 空成功结果；失效时返回结构化错误                                               |
| activate             | window                         | eventsSubmitted、requiresObservation=true                                      |
| input                | window、observation、operation | 单个具名输入操作及系统提交数量                                                 |

握手必须声明 list_windows、observe、validate_observation。只有同时声明 activate 和 input，inputSupported 才能为 true。未知动作不能静默成功。

### 4.2 限制与图片

- 请求帧最多 64 KiB，响应帧最多 32 MiB，均包含末尾换行。
- 窗口最多 128 个，控件最多 256 个、深度最多 8，观察缓存最多 128 条。
- 图片最多 1600 万像素、编码数据 8 MiB；客户端交付前还受完整信封 16 MiB、普通内容 2 MiB 限制。
- 原生侧应优先保留实际尺寸；超过优化目标后再按协议选择 JPEG 或等比例缩小，并返回真实 mime、宽高和数据。
- 原生侧不缓存图片副本；控件树和错误必须返回截断或不可用事实，不得用旧截图冒充当前状态。
- stderr 每行至少包含 id、action、phase、code；phase 使用 startup、communication、observation、input、overlay、cleanup 之一；不得记录输入正文或完整敏感画面。

### 4.3 坐标与观察语义

- Windows 使用 physical_screen_pixels；macOS 使用 logical_screen_points。Mac 不得套用 Windows DPI 公式。
- 每次 observe 同时返回窗口边界、displayScale、coordinateSpace 和图片实际宽高。
- 控件边界相对窗口左上角；截图坐标必须属于同次观察的图片范围。
- macOS 必须明确逻辑点、backing scale、截图像素、窗口坐标和屏幕坐标之间的转换；禁止凭屏幕尺寸猜比例。
- 图片观察和控件观察来自同一采集时点；任一窗口几何、显示器、权限或事件代次变化都应拒绝混合状态结果。

### 4.4 错误与不可重放

macOS 错误码至少映射以下语义：stale_observation、stale_window、window_changed、window_unavailable、desktop_busy、input_busy、focus_changed、target_obscured、input_interrupted、user_interrupted、input_stopped、desktop_unavailable、input_rejected、overlay_unavailable、input_guard_unavailable。

通信错误、超时、取消和“可能已提交但响应丢失”都按不可重放处理。恢复顺序是记录错误、关闭或回收会话、重新枚举、重新观察、由模型决定是否再次操作；sidecar 和宿主不得自动重放。

## 5. macOS 实施路线

每个阶段必须提交代码、定向测试、真实 Mac 运行证据和已知限制；缺少其中任一项保持未勾选。

### M0：工具链、身份和资产布局

- [ ] 确定最低 macOS 版本、Xcode 版本、Swift 工具链、Deployment Target 和支持架构。
- [ ] 确定 bundle identity、开发签名身份、Release 签名身份和升级时保持权限身份的规则。
- [ ] 在 sidecars 下建立 macOS 原生目录；不把 Swift 依赖引入 Python 业务层。
- [ ] 定义 Mac 资产选择、缺失资产、架构不匹配和系统版本过低的明确错误。
- [ ] 用 Mac 实际路径验证 Mind 能找到 sidecar；路径不得依赖当前工作目录。

交付证据：swift --version、xcodebuild -version、Deployment Target、架构清单、bundle identity、未签名和签名产物路径。

### M1：Swift sidecar 与 IPC

- [ ] 建立与 Windows 相同的 JSONL v1 握手、请求关联、字段拒绝、帧限制和 stderr 诊断。
- [ ] 处理正常 EOF、半帧 EOF、父进程退出、取消、超时、重复 id、stdout 堵塞和 stderr 上限。
- [ ] 保证每个请求只对应一个结果；通信失败、取消和关闭不重放桌面动作。
- [ ] 用共用协议夹具验证能力声明、错误形状、图片预算、Unicode 和边界值。
- [ ] 实现有界观察缓存与会话关闭；关闭后所有窗口引用和观察引用失效。

交付证据：swift test 或 xcodebuild test 输出、协议夹具结果、进程退出码、无孤儿进程和资源采样。

### M2：窗口、控件树与截图

- [ ] 使用 Accessibility API 枚举可定位窗口，返回不透明引用、标题、PID、边界、最小化状态和显示缩放。
- [ ] 返回有界 AX 控件树；树不可用、权限不足或被截断时保留事实，不伪造完整树。
- [ ] 使用 ScreenCaptureKit 捕获目标窗口或显示区域；返回实际图片宽高、格式、坐标空间和采集时间。
- [ ] 建立窗口销毁、重建、隐藏、最小化、移动、缩放、显示器变化和权限撤销的事件修订。
- [ ] 观察期间不保存图片副本；截图资源、stream、buffer 和 Core Graphics 对象按请求释放。

API 入口核对：Accessibility 权限探测使用 AXIsProcessTrustedWithOptions；窗口和控件读取使用 AXUIElement；ScreenCaptureKit 使用 SCShareableContent、SCWindow 或 SCDisplay 及对应 stream。具体 API 版本随 M0 的最低系统版本冻结。

交付证据：专用测试应用窗口列表、AX 控件树、截图像素/尺寸断言、窗口关闭后 stale_window、权限失败错误。

### M3：输入、安全和停止

- [ ] 使用 Quartz CGEvent 实现 activate、click、move、drag、scroll、key 和有界 Unicode text。
- [ ] 每次输入绑定最新观察，执行前重新校验 AX 身份、边界、可见/启用状态、窗口焦点和权限。
- [ ] 处理逻辑屏幕点到 CGEvent 屏幕坐标的转换，包括 Retina、负坐标、多屏和显示器变化。
- [ ] 输入分段可取消；无论取消、异常、EOF、超时还是崩溃，都释放按下的键和鼠标按钮。
- [ ] 侦测外部鼠标键盘介入，立即停止并返回 user_interrupted 或 input_stopped；不与用户争抢输入。
- [ ] Secure Input、锁屏、系统安全界面、远程会话和目标失焦时明确失败，不尝试绕过系统限制。

交付证据：专用测试应用真实状态变化、按键释放检查、取消/崩溃恢复、物理干预日志和不可重放断言。

### M4：蓝光、代理指针和捕获排除

- [ ] 使用 AppKit 透明窗口和 Core Animation 绘制无边框蓝色柔光；四角填充、点击穿透、不抢焦点、不进入任务栏。
- [ ] 代理指针使用独立小窗口；真实输入期间隐藏系统光标，操作结束或失败后恢复原可见性。
- [ ] 指针位置由本地动画时钟驱动，不通过逐帧 computer 调用；进入/退出淡出时停止新移动和波纹。
- [ ] 覆盖层跟随真实输入生命周期；输入前校验失败、取消、超时和关闭都不留下窗口。
- [ ] 使用 ScreenCaptureKit 的排除配置或等效机制验证目标截图不包含覆盖层；预览模式可单独允许被捕获。
- [ ] 记录实际呈现帧耗时、P95/P99、输入延迟、空闲 CPU/内存和多显示器资源；调度间隔不能冒充呈现帧率。

交付证据：屏幕录制或逐帧截图、窗口层级、点击穿透、截图排除、光标单实例、自动退出和性能报告。

### M5：TCC、系统状态和权限恢复

- [ ] 验证 Accessibility 未授权、授权、拒绝、撤销和重新授权；明确是 Mind、sidecar 还是签名 bundle 持有权限。
- [ ] 验证 Screen Recording 未授权、授权、撤销和重新授权；截图能力与输入能力分别报告。
- [ ] 验证签名或升级后权限身份是否保持；权限变更必须使能力重新探测，不得沿用旧握手。
- [ ] 验证 Retina、混合缩放、多屏负坐标、显示器热插拔、Spaces、全屏窗口、应用失焦和窗口关闭。
- [ ] 验证 Secure Input、锁屏、系统权限面板和其他不可控桌面；返回可识别错误并停止覆盖层和输入。

权限入口核对：ScreenCaptureKit 预检/请求使用 CGPreflightScreenCaptureAccess 与 CGRequestScreenCaptureAccess；输入事件使用 CGEvent/CGEventPost；覆盖层使用 NSWindow 与 Core Animation。权限请求不能由 sidecar 静默绕过，也不能把宿主审批当作 TCC 授权。

交付证据：每种权限状态的系统设置截图、握手能力、错误码、重新授权后的新会话观察和输入结果。

### M6：构建、签名、公证与升级

- [ ] 在真实 Mac 构建 arm64；如支持 Intel，再构建 x86_64 并验证原生资产选择。
- [ ] 生成 Mind 直接调用的最终目录；删除 DerivedData、build、测试截图和临时压缩包。
- [ ] 完成 Developer ID 签名、公证、安装、首次启动、升级和卸载验证。
- [ ] 验证签名 identity、bundle path 或 helper 变化不会意外丢失 TCC 权限。
- [ ] 记录产物文件清单、架构、版本、签名摘要、公证结果和 SHA-256。

交付证据：xcodebuild archive/export、codesign、spctl、notarytool、安装/升级实测日志和最终产物哈希。

## 6. macOS 验收矩阵

| 完成 | 场景                                    | 必须留下的证据                               |
|------|-----------------------------------------|----------------------------------------------|
| [ ]  | 专用 AppKit / Swift 测试应用            | 枚举、AX 树、截图、输入、结果和关闭          |
| [ ]  | 一个系统应用                            | 真实窗口、控件、焦点、Unicode 输入和关闭     |
| [ ]  | 自绘或无控件树应用                      | 空树事实、截图坐标输入和明确失败边界         |
| [ ]  | 单屏 1x / 2x Retina                     | 逻辑点、图片像素、CGEvent 坐标和覆盖层一致   |
| [ ]  | 多屏、混合缩放、负坐标、热插拔          | 显示器变化后的新观察、转换和资源重建         |
| [ ]  | Spaces、全屏、窗口移动/缩放/最小化/关闭 | 旧观察拒绝、边界同步、无误点                 |
| [ ]  | Accessibility 未授权/撤销               | handshake 能力和结构化权限错误               |
| [ ]  | Screen Recording 未授权/撤销            | 截图失败事实，输入能力不被伪造               |
| [ ]  | Secure Input、锁屏、系统安全界面        | 停止输入、释放状态、恢复需新观察             |
| [ ]  | 物理鼠标键盘干预、停止键                | user_interrupted/input_stopped，不能自动恢复 |
| [ ]  | 取消、超时、EOF、崩溃                   | 无残留按键、覆盖层、孤儿进程或重放           |
| [ ]  | 长时间观察与输入                        | 帧耗时、资源、观察缓存和线程有界             |
| [ ]  | arm64 / x86_64、签名、公证、升级        | 资产选择、签名身份、TCC 权限和功能回归       |
| [ ]  | Windows 共用协议夹具                    | 共用测试通过，Mac 特有错误和能力差异另有断言 |

Windows 现有场景矩阵仍必须维护；Mac 通过后再更新双平台状态，不把“协议夹具通过”计为 Mac 实机通过。

## 7. 验收记录格式

每条完成项至少记录：

- 系统：macOS 版本、机型、芯片、显示器数量、缩放、Spaces/全屏状态。
- 构建：Xcode/Swift 版本、git 提交、bundle identity、签名摘要、sidecar SHA-256。
- 调用：Mind 会话 sid、computer action、窗口/观察引用是否重新获取、结果和错误码。
- 证据：测试命令及退出码、结构化日志、必要的截图或录屏、进程/窗口/资源清理结果。
- 限制：失败、跳过、人工确认和未覆盖原因；不能用“看起来正常”替代结果断言。

推荐在 Mac 上按以下顺序执行：

    1. 先运行 Swift 协议/单元测试，再运行 Python 共用协议与宿主测试。
    2. 启动正式 Mind，确认 computer 和 js_repl 均开启，使用专用测试应用完成观察。
    3. 逐阶段打开 Accessibility、Screen Recording 和输入能力，记录每次握手与错误。
    4. 完成单屏 1x/2x 后再做多屏、Spaces、全屏、锁屏和 Secure Input。
    5. 完成真实输入和视觉覆盖层后，执行取消、崩溃、升级、签名和公证验收。
    6. 最后清理构建缓存，只保留 Mind 直接调用的最终产物，并把哈希写回本文件。

## 8. 勾选与交接规则

- [ ] 表示未完成、代码未验证、环境不足、失败或仅有 mock/协议证据。
- [x] 只表示代码、定向测试和真实系统证据都齐全；同一阶段有一项未完成，阶段状态仍为未完成。
- 失败、跳过和用户未授权操作必须写清原因；不要把首次失败后的修正版结果写成首次通过。
- 不将沙箱、宿主审批、TCC、Windows 权限或网络错误混写；分别记录 Application、Harness、IPC、sidecar 和系统层证据。
- 不新增平台专用 MCP；平台差异留在 sidecar 与 adapter，能力不足必须显式返回。
- 不恢复官方 Codex runtime，不修改用户全局 PATH，不把系统 SDK、源码、缓存和调试符号放进最终运行资产。
- 每次暂停交接前更新第 1、2、5、6 节；删除已经被替代的历史流水账，保留可复核的提交、测试、产物和限制。

## 9. macOS 交接阻塞项

当前阻塞只有环境项：

- 没有可用 Mac，无法完成 Swift 编译、TCC 授权、Retina/多屏、签名、公证和真实 GUI 验收。
- Windows 仍有多屏混合 DPI、长时间压力、跨应用和若干人工视觉项；这些不应被移植阶段隐藏。
- macOS sidecar 尚未创建，因此不能承诺 Mac 的最低系统版本、bundle identity、权限归属或架构产物。
- 获得 Mac 后从 M0 开始，先冻结工具链和身份，再实现 M1–M6；每完成一个阶段立即回填验收证据。

相关文档：
- [ARCHITECTURE.md](client-architecture.md)
- [ARCHITECTURE_SYSTEM.md](system-architecture.md)
- [docs/desktop-sidecar.md](desktop-sidecar.md)
- [agent/ports/desktop.py](agent/ports/desktop.py)
- [infrastructure/sidecars/desktop/protocol.py](infrastructure/sidecars/desktop/protocol.py)
