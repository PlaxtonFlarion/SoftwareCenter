# 🚀 Mind :: 代理思维

![Mind](https://raw.githubusercontent.com/PlaxtonFlarion/SoftwareCenter/main/Assets/MindSource/app_readme.png)

**本地智能代理执行框架**｜MCP 工具编排｜可观测 · 可回放 · 可扩展  
[Releases](https://github.com/PlaxtonFlarion/SoftwareCenter/releases) ·
[SoftwareCenter Assets](https://github.com/PlaxtonFlarion/SoftwareCenter/tree/main/Assets/Mind) ·
[Memrix](https://github.com/PlaxtonFlarion/SoftwareCenter/tree/main/Assets/Memrix) ·
[Framix](https://github.com/PlaxtonFlarion/SoftwareCenter/tree/main/Assets/Framix)

---

## 🏆 项目简介

**Mind** 把「一句话意图」拆成可执行步骤，并自动编排调用 **MCP 工具**：  
完成设备控制、数据采集、媒体处理、脚本编排等任务。

它既像一个可扩展的 **CLI Agent**，又像一个可插拔的 **自动化执行引擎**：  
轻量启动、链路可观测、结果可复现、过程可沉淀。

- **可组合**：Prompt / Resource / Tool 统一调度，工具即积木  
- **可复现**：同样输入得到同样流程与结果（可追踪、可回放）  
- **可扩展**：新增能力只需注册工具，无需改核心逻辑  

> 项目代号：Mind｜中文名：代理思维｜定位：本地智能代理执行框架

---

## 设计原则

- **开发背景**：传统自动化脚本与 RPA 在多工具协作、动态上下文与长期任务上存在断层，执行链路难以复用与回放。  
- **执行优先**：以工具调用为核心链路，确保任务可落地、可回放。  
- **约束优先**：`chat/fast` 模式遵循 `tool_call → tool_result` 闭环协议，`plan` 模式为单向链路执行。  
- **本地优先**：关键决策与执行留在端侧，降低时延与不确定性。  
- **工程优先**：授权、配置、可观测与回收机制齐备。  

与传统自动化对比：

- **传统自动化**：脚本/流程固定、可复用性弱，跨系统编排成本高，遇到变化容易失效。  
- **Mind**：以工具协议与编排为核心，支持动态路由与上下文管理，并保留可回放、可追踪的执行证据链。  

---

## 系统形态与分层

Mind 面向工程交付，采用 **命令行作为唯一控制入口**，强调“可执行、可观测、可回放”。  
系统以 **控制面 / 执行面分层**组织能力，保持运行路径清晰、响应链路稳定：

- **控制面（Mind CLI）**：指令解析、会话编排、模型调度、任务路由、模式分流与结果聚合。  
- **执行面（Helix · 内嵌）**：工具注册与发现、调用生命周期管理、能力域隔离、运行态监测与证据链落盘。  

---

## 快速开始

```
# 对话
mind --chat "你好，介绍一下系统能力"

# 性能
mind --fast "开始录屏，打开App，等待3秒，返回桌面，结束录屏，执行5次"

# 编排（确定性自动化）
mind --plan "打开设置，等待 2 秒，然后截图"
```

---

## 运行架构

```
┌────────────┐
│  Mind      │
│  (CLI)     │
└─────┬──────┘
      │
      │ 内部调用
      ▼
┌────────────┐
│  Helix     │
│  (MCP)     │
└─────┬──────┘
      │
      ▼
Tools: automator / bench / common / media
```

执行闭环：

```
模型流输出
   ↓
tool_call
   ↓
Mind 调度
   ↓
执行层处理
   ↓
增强链处理
   ↓
tool_result 回填
   ↓
模型继续生成
```

协议与传输：

- **协议**：MCP 工具协议
- **传输**：streamable-http
- **鉴权**：Bearer Token

---

## 核心职责
- 指令解析与任务路由
- 会话状态与上下文管理
- 模型流式调度与响应编排
- 工具链路组织、执行与生命周期管理
- 能力域隔离与运行态监测
- 模式分流（对话 / 编排 / 性能）

---

## 2. 技术栈与依赖

**品牌宣言**：代理思维不是聊天机器人，而是一套具备执行力的智能系统。  
我们以“本地执行 + 云端增强”为核心架构，追求可控、可靠、可扩展的工程级交付标准。

客户端（Mind CLI）：

| 分类   | 组件                      |
|------|-------------------------|
| 语言   | Python 3.11             |
| 代理协议 | MCP (`mcp`)             |
| 传输   | httpx / streamable-http |
| 日志   | loguru + rich           |
| 多媒体  | pygame, pillow, imageio |
| 构建   | Nuitka                  |

服务端（Helix + AppServerX）：

| 分类   | 组件                        |
|------|---------------------------|
| 服务模块 | FastAPI + Uvicorn         |
| 网关   | Cloudflare                |
| 缓存   | Redis                     |
| 数据库  | Supabase Postgres         |
| 检索   | Embedding / Rerank / 向量索引 |
| 推理   | GPU 容器化推理集群               |
| 观测   | Metrics / Tracing / Logs  |
| 可靠性  | 灰度发布 / 金丝雀路由              |

---

## 项目特性概览
- 单入口 CLI 交付，运行路径确定、行为可控。
- 工具执行层内嵌，低延迟本地调用。
- 工具域标准化组织（automator / media / bench / common）。
- 增强执行链融合（RAG、多模态、自愈机制）。
- 授权与配置闭环，支持企业级交付与治理。

---

## 自动化与能力体系

能力按工具域注册与组合：

- `automator`：系统/应用/UI 自动化
- `bench`：性能基准与指标采样
- `common`：运行信息与环境检查
- `media`：截图、录屏、音频与 FFmpeg 管线

- **应用与系统控制**：应用启动/切换、系统信息读取、按键事件注入。
- **界面交互**：UI 定位、点击、输入、滚动与交互链路编排。
- **文件与数据处理**：文件系统操作、资源调度与运行态数据整理。
- **媒体能力**：截图采集、音视频处理、帧级流水线。
- **性能与稳定性**：指标采样、资源监控、长时间稳定性探测。

典型场景：

- 自动化巡检
- 设备操作
- 媒体处理流水线

---

## 三种运行模式

Mind 提供三种互斥运行模式：

| 模式       | 说明   |
|----------|------|
| `--chat` | 对话模式 |
| `--fast` | 性能模式 |
| `--plan` | 编排模式 |

### 对话模式（chat）

```
mind --chat "你好，介绍一下系统能力"
```

定位：流式对话驱动模式。

特征：

- token-by-token 流式输出
- 多轮上下文保持
- 动态工具触发

### 性能模式（fast）

```
mind --fast "开始录屏，打开App，等待3秒，返回桌面，结束录屏，执行5次"
```

定位：纯性能执行模式。

特征：

- 不调用 automator 域能力
- 仅使用自研性能工具体系
- 偏向高吞吐与低延迟执行路径

性能模式包含：

- 自研性能工具接口层
- 指标采样
- 资源监控
- 压测链路
- 稳定性探测

适用于：

- 性能压测
- 长时间运行测试
- 资源消耗对比
- 指标基准评估

### 编排模式（plan）

```
mind --plan "打开App，等待3秒，返回桌面"
```

定位：确定性自动化编排模式。

特征：

- 输出结构化行动序列
- 强工具链路组织
- 可复现执行路径
- 强调步骤拆解与顺序控制
- 单向执行链路

执行抽象：

```
意图识别
   ↓
任务拆解
   ↓
生成有序工具计划
   ↓
顺序执行
```

适用于：

- 自动化巡检
- 批量流程执行
- 设备操作链路
- 可复现工作流

---

## 循环模式

除了 `mind --chat | --fast | --plan` 的一次性命令模式外，Mind 还支持 **循环交互模式**（REPL）。  
该模式下会持续读取用户输入，并在 **CHAT / FAST / PLAN** 三种互斥状态之间切换执行。

### 启动与提示

进入循环后，终端会显示当前模式与正在使用的 `<model>`：

- 顶部 banner 会随模式变化：Chat / Fast / Plan
- 每轮输入提示：`ready 输入目标或 /help`

> `mind_loop()` 会为一次会话生成 `cid/sid` 并贯穿本轮交互，用于链路追踪与调用元数据。

### 指令索引

在任意模式下输入 `/help` 可查看指令索引：

- `/help, /h`：指令索引（用法/示例/约定）
- `/license, /lic`：授权许可（License/特性）
- `/subscription, /sub`：订阅信息（授权状态/到期）
- `/quit, /q, quit, exit`：安全退出（断开会话）
- `/model <name>`：引擎切换（选择推理内核）
- `/apikey <key>`：凭证更新（替换访问密钥 / Token）
- `/again N <goal>`：复现回放（目标 × N 次）**仅在 PLAN 模式生效**
- `/chat`：切换到对话模式（CHAT）
- `/fast`：切换到性能模式（FAST）
- `/plan`：切换到编排模式（PLAN）

### 三种互斥运行状态（交互态）

循环模式内部有一个状态机：`CHAT` / `FAST` / `PLAN`，同一时刻只会处于其中一个状态。

| 状态   | 说明           | 选择指令    |
|------|--------------|---------|
| CHAT | 对话驱动（流式，多轮）  | `/chat` |
| FAST | 性能执行（高吞吐路径）  | `/fast` |
| PLAN | 编排执行（确定性步骤链） | `/plan` |

切换时会输出类似：

- `Exchange → Chat`
- `Exchange → Fast`
- `Exchange → Plan`

### `/again` 循环复现（仅 PLAN）

`/again` 只在 **PLAN** 状态下生效，用于把一个目标重复执行 N 次（用于复现、回放、稳定性验证）：

```
/plan
/again 5 打开App，等待3秒，返回桌面
```

行为语义：

- 仅当 **tag == PLAN** 且命中 `/again N <goal>` 时生效
- 实际发送给执行器的 message 会被改写为：`<goal>，循环 N 次`
- 如果不在 PLAN 状态输入 `/again ...`，会被当作普通文本目标处理（不会进入循环语义）

### `/model` 引擎切换（带候选提示）
/model gpt-4o-mini

当输入无效或缺失时，会打印候选列表（示例）：

- `llama-3.3-70b-versatile`
- `openai/gpt-oss-120b`
- `gpt-4o-mini`
- `deepseek-chat`

并输出形如：`model invalid: /model <...>` 的错误提示。

> 切换成功后，本轮循环后续调用均使用新的 `model`。

### `/apikey` 凭证更新（带格式提示）
当输入无效或缺失时，会打印可接受的格式提示（示例）：

- `sk-...   (API Key)`
- `gsk_...  (API Key)`
- `ds-...   (API Key)`
- `<token>  (Pure token)`

并输出形如：`apikey invalid: /apikey <...>` 的错误提示。

> 切换成功后，本轮循环后续调用均使用新的 `apikey`。

### `/license` 与 `/subscription`

- `/license`（或 `/lic`）：展示授权许可信息页（License/特性）
- `/subscription`（或 `/sub`）：读取本地 License 文件并执行校验流程（授权状态 / 到期信息）

> `/subscription` 会调用本地授权验证（例如 `authorize.verify_license(<lic_file>)`），适合快速确认当前机器的授权是否有效。

### 退出

任意时刻输入以下任一指令即可安全退出循环：
```
/quit
/q
quit
exit
```

---

## 命令行兼容参数

Mind 提供两项“兼容参数”用于增强 **报告归档命名空间** 与 **调试可观测性**。

### `--gravity <tag>`：引力协议（Gravity Protocol）

为本次运行设置 **引力标签（gravity tag）**，用于确定日志/报告的 **落盘根目录命名空间**：

- 同一 `tag` 的多次运行会被聚合到同一命名空间（便于按项目/版本/场景归档）
- 适用于：回归批次、灰度组、特性分支、实验编号、设备分组等

示例：

```
# 将本次执行的日志/报告归档到同一 gravity 命名空间
mind --plan "打开设置，等待2秒，然后截图" --gravity TEST_202602

# 性能批次归档（同标签可聚合多轮压测产物）
mind --fast "开始录屏...结束录屏，执行5次" --gravity Perfermance_Baseline_v1
```

### `--reflection`：反射协议（Reflection Protocol）

开启 详细调试视角，输出运行轨迹与关键决策信息（用于定位“为什么这么做”）：
- 打印：关键分支选择、执行路径、路由与决策依据（更丰富的 trace / debug 视角）
- 适用于：PoC 调试、工具链问题定位、计划偏航分析、线上回归异常复盘

```
# 开启详细运行轨迹输出（建议与 plan 联用）
mind --plan "打开App，等待3秒，返回桌面" --reflection

# 性能模式下查看采样/链路细节（用于异常定位）
mind --fast "开始录屏...结束录屏，执行5次" --gravity Perf_v3 --reflection
```

建议：--reflection 会增加输出量，默认关闭；仅在需要追踪决策与链路细节时开启。

---

## 异步调用示例（Python / Java）

通过自然语言描述自动化步骤，异步调用 `mind --plan`：

```
import asyncio


async def run_plan(text: str) -> str:
    proc = await asyncio.subprocess_exec(
        "mind", "--plan", text,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    out, err = await proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(err.decode("utf-8", errors="ignore"))
    return out.decode("utf-8", errors="ignore")


async def main() -> None:
    plan = "打开设置，等待 2 秒，然后截图"
    result = await run_plan(plan)
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
```

```
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.CompletableFuture;

public class MindAsyncPlan {
    public static CompletableFuture<String> runPlan(String text) {
        return CompletableFuture.supplyAsync(() -> {
            try {
                Process process = new ProcessBuilder("mind", "--plan", text).start();
                String out = readAll(process.getInputStream());
                String err = readAll(process.getErrorStream());
                int code = process.waitFor();
                if (code != 0) {
                    throw new RuntimeException(err);
                }
                return out;
            } catch (Exception e) {
                throw new RuntimeException(e);
            }
        });
    }

    private static String readAll(InputStream in) throws Exception {
        ByteArrayOutputStream buffer = new ByteArrayOutputStream();
        byte[] data = new byte[4096];
        int n;
        while ((n = in.read(data)) != -1) {
            buffer.write(data, 0, n);
        }
        return buffer.toString(StandardCharsets.UTF_8);
    }

    public static void main(String[] args) {
        runPlan("打开设置，等待 2 秒，然后截图")
            .thenAccept(System.out::println);
    }
}
```

---

## 自研性能工具接口层

**Memrix-记忆星核，接口层：**

- 面向 Android 性能数据采集
- 覆盖内存、流畅度、IO 等关键指标
- 与性能模式联动的指标流入口

**Framix-画帧秀，接口层：**

- 基于视觉的端到端耗时测试
- 端侧链路采集与时序对齐
- 关键路径耗时评估与结果输出

---

## 服务结构说明

服务端采用分层架构，围绕可扩展性、可观测性与稳定性设计，支持按需接入多类基础设施能力。

**执行层（Helix）：**

- MCP 工具服务与执行闭环
- 健康检查与运行态监测
- 低延迟本地调用通道

**云端层（AppServerX）：**

- **控制与编排**：模型/工具元数据中心，远程配置与策略下发
- **检索与增强**：多路召回、Rerank、RAG 与向量检索协同
- **安全与网关**：Cloudflare、WAF、零信任访问控制、API 速率限制
- **缓存与队列**：Redis、消息队列、延迟任务调度
- **数据层**：Supabase Postgres、对象存储、冷热数据分层
- **观测体系**：Metrics / Tracing / Logs 统一可观测与告警
- **模型基础设施**：模型注册、版本路由、灰度/金丝雀发布
- **GPU 容器推理**：统一推理入口、弹性扩缩容、多模型并行与版本切换
- **测试中台**：自动化流程验证、性能基准回归与稳定性测试

**默认接口（本地）：**

- MCP：`http://127.0.0.1:3333/helix/mcp`
- Health：`/healthz`
- Ready：`/ready`
- Idle：`/idle`

Helix 为独立子进程，由 Mind 拉起；无 idle 达 30 分钟自动触发关闭。  
空闲计时由服务侧 idle 计时器维护，请求/工具调用会刷新计时；触发关闭时执行资源回收与会话清理。

---

## 云端层推理与测试中台架构

AppServerX 在云端层将推理能力与测试中台打通，形成统一的编排、执行与回归闭环：

- 统一入口与鉴权：流量入口、配额与租户隔离
- 路由与排队：模型路由、任务队列、优先级控制
- GPU 容器推理：弹性扩缩容、多模型并行与版本切换
- 测试中台：流程编排、批量执行、指标采样与报告生成
- 可观测与回归：全链路监控、异常归因、基准回归追踪

参考架构：

```
请求入口
   ↓
统一鉴权与网关
   ↓
路由与排队
   ↓
GPU 推理容器集群
   ↓
指标采集与报告
   ↓
回归追踪与告警
```

---

## 构建发布

![LOGO](https://raw.githubusercontent.com/PlaxtonFlarion/SoftwareCenter/main/Assets/MindSource/app_compile.png)

- 支持 **macOS** 与 **Windows** 平台安装包发布

**发布地址：** [https://github.com/PlaxtonFlarion/SoftwareCenter/releases](https://github.com/PlaxtonFlarion/SoftwareCenter/releases)

---

## 合作支持

如需技术合作、定制能力或企业级部署支持，请通过邮箱联系作者。

作者邮箱：`AceKeppel@outlook.com`

---

## 许可说明

当前仓库包含 `GPL-3.0` 授权文本（见 `LICENSE.md`）。  
如发布产物或常量中存在其他授权声明，请以 `LICENSE.md` 为准。
