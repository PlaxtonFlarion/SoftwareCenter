# 设备域实战

README 只保留入口层信息；如果你需要系统理解 `device` 域的能力边界、工具分层和稳定执行建议，直接看这里。

## 这页解决什么问题

- `device` 域到底能做什么
- `app / ui / info / system / keyevent / monkey / file / tool` 分别负责什么
- 哪些动作应该用系统级工具，哪些应该用 UI 工具
- 多设备执行、前台收敛、自愈和等待应该怎么理解

## 设计定位

`device` 是端侧执行域，代码入口在：

- `backend/mcp_tools/automator/ctl_app.py`
- `backend/mcp_tools/automator/ctl_ui.py`
- `backend/mcp_tools/automator/ctl_info.py`
- `backend/mcp_tools/automator/ctl_system.py`
- `backend/mcp_tools/automator/ctl_keyevent.py`
- `backend/mcp_tools/automator/ctl_monkey.py`
- `backend/mcp_tools/automator/ctl_file.py`
- `backend/mcp_tools/automator/ctl_zest.py`

它的重点不是“回答页面上有什么”，而是“真的对设备做动作，并把结果按设备回收”。

## 执行模型

大多数 `device` 工具都走同一套广播模型：

- 默认对当前在线设备列表广播执行
- `matrix` 可按 `serial -> args` 做逐设备覆盖
- 多设备场景下返回的是 per-device 结果，不是单一设备结果

这意味着：

- 你不写 `matrix`，通常就是对所有在线设备一起执行
- 你写了 `matrix`，可以对不同设备传不同参数
- 多设备 pull、截图、logcat 这类能力会避免本地文件冲突

## 工具分层

### 1. `tool`

当前主要入口：

- `refresh`

作用：

- 刷新可用设备列表
- 在执行前更新 adb 在线状态
- 返回在线设备数量和 serial 列表

适合：

- 执行前做设备就绪检查
- 多设备批跑前先收敛可用性

### 2. `app`

当前能力：

- `app_deep_link`
- `app_start`
- `app_stop`
- `app_install`
- `app_uninstall`
- `app_clear`
- `app_foreground`

特点：

- 直接以包名、Activity、Deep Link 驱动应用生命周期
- `app_foreground` 不是简单 start，它会做前台收敛
- 安装、卸载、清数据这些动作都属于状态级操作，不该混进 UI 点击链里

适合：

- 启动应用
- 强制停止并重启
- 清数据重置状态
- 通过 Deep Link 直接跳转页面

建议：

- 需要确保应用真的到前台时，优先用 `app_foreground`
- 需要重置应用状态时，用 `app_clear` 或 `app_stop`

### 3. `ui`

当前能力大致分四类：

- 滚动与手势
  - `scroll_up / scroll_down / scroll_left / scroll_right`
  - `scroll_to_top / scroll_to_bottom`
  - `scroll_into_view`
  - `swipe`
- 坐标与控件点击
  - `tap`
  - `click`
  - `double_click`
- 输入与焦点
  - `send_keys`
  - `send_keys_fallback`
  - `clear_text`
  - `current_focus`
- 页面感知与等待
  - `current_widgets`
  - `find_element`
  - `heal_element`
  - `wait_exists`
  - `wait_gone`

这里有几个关键边界：

- `tap / swipe / double_click` 是绝对坐标级动作
- `click / find_element / wait_exists` 是控件语义级动作
- `scroll_into_view` 是“滚到目标出现”为止，不是盲滚
- `heal_element` 是自愈与诊断工具，不只是简单查找

### 4. `info`

当前能力：

- `device_snapshot`
- `screenshot`
- `grep_packages`

适合：

- 拉设备快照
- 截图留证
- 检查包是否安装

这类工具偏观察，不负责状态修改。

### 5. `system`

当前能力：

- `open_notification`
- `open_settings`
- `combo_key`
- `ime_reset`
- `reboot`
- `swipe_unlock`
- `screen_on / screen_off`
- `bluetooth_on / bluetooth_off`
- `wifi_on / wifi_off`
- `data_on / data_off`

这里的核心原则很明确：

- 系统级入口不要用 `click / tap` 模拟
- 像通知栏、设置页、屏幕、电源、网络开关都应该走 `system`

适合：

- 系统级页面和开关控制
- 需要更稳、更接近系统语义的动作

### 6. `keyevent`

当前能力：

- 导航：
  - `go_home`
  - `go_back`
  - `open_recents`
  - `open_menu`
- 输入与焦点：
  - `press_enter`
  - `press_tab`
  - `press_delete`
  - `press_space`
  - `press_escape`
- 系统和媒体：
  - `press_power`
  - `press_voice_assist`
  - `volume_up / volume_down / volume_mute`
  - `media_pause / media_next / media_previous`

适合：

- 系统导航键
- 物理键语义更强的输入场景
- 不适合用点击模拟的系统入口

### 7. `file`

当前能力：

- `file_pull`
- `file_push`
- `file_remove`
- `file_logcat_dump`
- `file_logcat_clean`

适合：

- 拉取设备文件
- 推送本地文件
- 清理设备文件或 logcat
- 导出设备日志作为证据

这组能力和 `device` 执行链结合得很紧，尤其适合：

- 动作后拉日志
- 回归失败后留证
- Monkey 后看 logcat 片段

### 8. `monkey`

当前能力：

- `injection`

特点：

- 不是普通点击脚本
- 会执行 `adb shell monkey`
- 同时抓取 logcat 证据

适合：

- 稳定性扰动
- 随机事件压测
- 崩溃、ANR、异常日志探测

## 定位方式和稳定性

`ui` 当前支持的典型定位方式：

- `id`
- `desc`
- `text`
- `bbox`
- `xpath`

但要注意：

- `xpath` 在 `find_element` 这类场景并不稳定，代码里已经明确写了 Android dump 不是标准 XPath
- `match / ignore_case` 只对字符串类定位生效
- `bbox` 更偏硬坐标，适合临时兜底，不适合长期维护

更稳的优先级通常是：

1. `id`
2. `desc`
3. `text`
4. `bbox`

## 前台收敛、等待和自愈

设备域里真正提高稳定性的，不是多点几次，而是这些工具：

- `app_foreground`
  - 负责把应用真正收敛到前台
- `wait_exists / wait_gone`
  - 负责把页面变化显式等待出来
- `scroll_into_view`
  - 负责把目标滚进可见区域
- `heal_element`
  - 负责定位漂移后的诊断和自愈
- `current_focus / current_widgets`
  - 负责在动作前确认上下文

推荐思路：

1. 先确保应用或页面状态对
2. 再找控件
3. 再点击或输入
4. 再等待结果出现或消失

不要把所有问题都堆给 `click`。

## 什么时候用 `system`，什么时候用 `ui`

优先用 `system`：

- 打开通知栏
- 打开系统设置
- 屏幕开关
- Wi-Fi、蓝牙、数据开关
- 重启、解锁、组合键

优先用 `ui`：

- 页面内部控件查找
- 滚动、点击、输入
- 等待页面元素出现或消失

优先用 `keyevent`：

- Home / Back / Recents / Menu
- Enter / Tab / Delete / Space
- 音量、媒体控制

不要用 `tap` 去模拟系统栏入口，也不要用 `click` 去替代真实系统按键。

## 模式建议

- `chat`
  - 适合探索式设备操作、边看边调
- `fast`
  - 不适合重型设备域主路径，设备相关能力会更受限
- `plan`
  - 最适合固定流程、巡检、页面跳转和回归链路

如果任务是：

- 多步设备巡检
- 固定 UI 路径
- 需要前后台收敛和等待

优先考虑 `plan`。

## 常见写法建议

更稳的链路通常长这样：

1. `refresh`
2. `app_foreground`
3. `wait_exists`
4. `click` 或 `scroll_into_view`
5. `send_keys`
6. `wait_gone / wait_exists`
7. `screenshot` 或 `file_logcat_dump`

而不是：

1. 连续 `tap`
2. 猜页面已经到了
3. 再继续 `tap`

## 约束和风险

- 多设备默认广播执行，别忽略这一点
- `send_keys` 依赖输入焦点和输入法环境
- `send_keys_fallback` 对中文、emoji、特殊字符兼容性有限
- `xpath` 不适合当成长期稳定定位策略
- 坐标点击容易随分辨率、布局和状态变化漂移
- `reboot`、网络开关、安装卸载这类动作有明显副作用，别在探索场景乱用

## 和其它域的关系

- `device`
  - 负责真的操作设备
- `media`
  - 负责截图、录屏、音视频和证据加工
- `bench`
  - 负责接口、性能、稳定性与协议验证
- `--code`
  - 负责把设备动作组织成可批跑、可回归的蓝本

设备域不是孤立的，常见组合是：

- `device + media`
  - 执行后截图、录屏、抽帧
- `device + file`
  - 动作后拉日志
- `device + --code`
  - 固定流程批跑

## 什么时候优先看这页

- 你要做端侧 UI 自动化
- 你要理解 `device` 和 `media / bench` 的边界
- 你在排查为什么点击不稳、输入没生效、页面没收敛
- 你要把设备动作写进 `plan` 或 `--code`

## 相关文档

- [交互模式详解](interactive-mode.md)
- [星图协议深入说明](cli-code.md)
- [多媒体链路实战教学](media-playbook.md)
- [文档索引](README.md)
