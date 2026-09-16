# 外接 MCP OAuth 验收

本指南用于检查源码或安装入口，并在真实操作系统、浏览器和外接服务上验证 OAuth。
命令与支持范围以 [CLI 使用说明](cli-usage.md#oauth-浏览器登录) 为准；模拟服务测试、
运行入口检查和真实账号验收分别记录，未实际执行的项目保持“待验收”。

## 源码入口与凭据库

激活仓库虚拟环境，使用 `python mind.py` 运行。先执行 `python -m pip check` 确认依赖
完整，再执行 `python mind.py --version` 和 `python mind.py mcp login --help` 确认入口。
以下真实服务步骤中的 `mind`，源码运行时统一替换为 Python 和 `mind.py` 的绝对路径；
无需先编译或安装 npm 包。

源码运行需要 `keyring` 及当前平台的系统 adapter。Windows 使用 `pywin32-ctypes`，
macOS 使用 Keychain API，Linux 源码运行使用 `SecretStorage` 和 `jeepney`；依赖由
固定版本的 keyring 按平台声明。升级这些依赖后重新验证实际读写，不能只检查 import。

仓库提供隔离检查：它从非源码目录启动指定入口，检查 help、参数错误、服务注册、真实
系统凭据库的大记录恢复、绝对过期时间和幂等 logout。所有凭据均为本次创建的合成数据，
执行后删除；不登录真实账户，不修改默认配置。报告只包含时间、平台、版本、状态和结果。

```powershell
python -m tests.manual.mcp_oauth_entry --report "<STATE_ROOT>/reports/mcp-oauth-source.json" --command "<ABSOLUTE_PYTHON>" "<REPO_ROOT>/mind.py"
```

每次报告使用新文件名，不覆盖旧证据。报告显式记录 `entry_kind=source`，SDK 和 keyring
版本来自运行脚本的虚拟环境。未来验证安装产物时，可选 `--entry-kind installed` 并将
`--command` 改为实际可执行文件或 npm launcher；脚本环境需与构建依赖一致。源码通过
不表示安装产物通过，当前 npm 平台包覆盖 Windows、macOS，Linux 不在 npm 发行范围内。

## 真实服务准备

为验收终端设置独立的 `MIND_HOME` 和 `MIND_STATE_HOME`，并在所有参与进程中保持一致。
运行状态根下的 `reports/` 是证据目录；未设置状态根时使用配置根。不要覆盖日常配置或
复用已有注册名。连接模型所需的设置仍通过正常配置方式准备，不将密钥放入验收记录。

Windows PowerShell 示例：

```powershell
$env:MIND_HOME = "<ACCEPTANCE_ROOT>/config"
$env:MIND_STATE_HOME = "<ACCEPTANCE_ROOT>/state"
New-Item -ItemType Directory -Force "$env:MIND_STATE_HOME/reports"
mind --version
mind mcp add sentry-oauth-acceptance --url "<SENTRY_MCP_URL>"
```

macOS/Linux 终端可用 `export MIND_HOME="<ACCEPTANCE_ROOT>/config"` 和
`export MIND_STATE_HOME="<ACCEPTANCE_ROOT>/state"` 设置同样的隔离目录。
记录版本或提交、平台、源码/安装入口和 SDK 版本；URL、组织与项目仅使用脱敏别名。
按服务端支持的方式配置公共客户端；预注册方式必须匹配固定 loopback 回调端口。

## 首次登录、调用与新进程恢复

1. 执行 `mind mcp login sentry-oauth-acceptance`，在真实浏览器中选择测试账户并同意授权。
   确认回调完成且命令返回 0；不要将授权地址、回调 URL 或授权码复制到报告。
2. 执行 `mind mcp get sentry-oauth-acceptance` 和 `mind mcp list`，确认本地状态且无机密输出。
3. 启动 `mind`，用 `/mcp status` 和 `/tools` 确认服务已连接并发现工具。从实际目录选择
   一个只读调用，经现有审批路径执行并核对真实结果。只有服务实际暴露 `find_releases`
   时才使用它；参数须限定在测试账户可访问的组织/项目。
4. 完全退出进程并重新启动，再次调用同一只读工具，确认无需浏览器登录。确认验收配置
   未设置 Bearer/Header，也未借用其他客户端的凭据。

## 刷新、竞争和失败恢复

| 场景 | 操作与通过标准 |
| --- | --- |
| 实际过期刷新 | 等待真实令牌到期，或使用服务正式支持的短有效期设置；下一次调用成功，新进程仍可调用。用脱敏的本地 expires_at 前后变化或服务端刷新事件确认刷新及持久化，不能仅以调用成功证明。 |
| 多进程 | 两个进程共享验收目录，在到期边界执行只读调用，无重复登录、轮换冲突或凭据覆盖。 |
| 授权拒绝 | 在真实授权页面拒绝一次登录，确认明确失败后可以重新登录。 |
| 取消与回调 | 登录等待时 Ctrl+C，确认退出码 130、回调端口释放，下一次登录成功。 |
| 手动打开 | 在不能自动启动浏览器的终端中，手动打开该次授权地址并完成登录。 |
| 网络失败 | 暂时断网后收到明确错误，恢复网络后可重新登录或重启服务；无无限刷新。 |
| 服务端撤销 | 在测试账户中撤销授权，下一请求失败且工具目录撤下，提示重新登录；原工具调用不自动重放。 |
| 退出竞争 | 一个进程调用，另一个执行 logout；活动进程在下一请求边界不得继续使用旧凭据，旧刷新结果不得恢复已删除登录。 |
| 清理和重入 | logout 两次均安全；新进程显示未登录，重新登录可恢复。最后先 logout，再 remove，仅清理本次创建的注册和资源。 |

若服务不发放 refresh token 或无法在验收窗口内验证过期，该项保留“待验收”，并另选实际
支持刷新的 MCP 服务补验。Linux/macOS 的浏览器、系统凭据库和取消行为须在对应平台
实际执行，不能用 Windows 通过结果代替。

## 记录模板

将下表复制为 `<STATE_ROOT>/reports/mcp-oauth-acceptance-<date>-<platform>.md`。
只保留时间、平台、版本、脱敏服务身份、状态和结果；不附原始终端转储、完整 URL、Token、
secret、授权码或凭据库内容。失败后填写原因和复验结果，不覆盖原失败记录。

| 字段 | 内容 |
| --- | --- |
| 时间 / 平台 | 待填写 |
| 版本 / 提交 / SDK | 待填写 |
| 源码或安装入口 / 检查结果 | 待填写 |
| 脱敏服务身份 / 客户端注册方式 | 待填写 |
| 首次浏览器登录 / 返回码 | 待验收 |
| 工具发现 / 审批 / 只读结果 | 待验收 |
| 新进程恢复 | 待验收 |
| 实际刷新 / 持久化证据 | 待验收 |
| 多进程 / 退出竞争 | 待验收 |
| 拒绝 / Ctrl+C / 端口释放 / 手动打开 | 待验收 |
| 断网 / 撤销 / 重新登录 | 待验收 |
| logout / 重复 logout / 清理 | 待验收 |
| Windows / Linux / macOS | 分别填写；未执行保持待验收 |
| 最终结果 / 待验收项 | 待填写 |
