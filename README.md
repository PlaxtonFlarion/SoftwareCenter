# Release Center

> **本仓库为发布专用仓库**  
> 本仓库用于发布软件的正式版本与授权机制相关文件，包含：
> 
> - 各平台安装包（如 `.dmg`, `.exe`, `.zip`, `.7z`, `.pkg` 等）
> - 授权说明与激活指南
> - 公共文档（`README.md`, `LICENSE.md` 等）
>
> ⚠️ 本仓库不包含源代码，源项目位于私有仓库。

---

## 🔐 使用通行证激活

软件在未激活状态下可正常启动，但**核心功能将被锁定**。用户可通过输入通行证进行激活，以解锁完整功能。

---

### **激活流程**

1. 在终端中执行激活命令并输入通行证（格式如：`XXXX-XXXX-XXXX`）
2. 系统将自动联网验证并将通行证绑定到当前设备
3. 激活成功后将在本地生成 `.lic` 文件，用于后续离线校验

```
framix --apply Framix-XXXX-XXXX-XXXX
```

```
memrix --active Memrix-XXXX-XXXX-XXXX
```

---

### **授权机制说明**

- 每个通行证最多可绑定 **3 台设备**
- 激活后会生成 `.lic` 文件，支持 **离线运行**
- 启动时系统将尝试每日联网检查授权状态
- 无需解绑设备，若授权失效可直接使用新的通行证重新激活

---

### **通行证申请方式**

请发送邮件至：

**AceKeppel@outlook.com**

请在标题中注明“通行证申请”，并附阁下的联系方式和简要说明您的用途或使用场景。

---

### **.lic 授权文件说明**

激活成功后，系统将在本地生成一个授权文件（如：`framix.lic` 或 `memrix.lic`），其内容采用 Base64 编码，并由签名保护，不可伪造或篡改。

授权结构示例（解码后的 JSON 格式）：

```
{
  "code": "XXXX-XXXX-XXXX-XXXX",
  "castle": "B6D74E7C-1A2B-4C77-9A2D-XXXXXXXXXXXX",
  "expire": "2025-12-31T23:59:59Z",
  "issued": "2025-05-01T10:21:00Z",
  "license_id": "18e9f7b5-1023-4aa7-9e45-bbd2d95d51d2"
}
```

字段说明：

- `code`：激活码（通行证）本体  
- `castle`：绑定的设备唯一标识符  
- `expire`：该激活码的有效截止时间（UTC）  
- `issued`：授权签发时间（UTC）  
- `license_id`：授权记录唯一编号（可用于后台查询与审计）

授权文件仅可由官方授权服务器签发，使用 RSA 签名机制保护。每次启动时将验证该文件合法性和有效性。

---

## ⚡️ 快速开始（Windows）

### 下载并安装

在本页面的发布资源中，下载对应软件的安装包（`.exe` 文件）并按提示完成安装。

示例：

- `Framix-windows-setup-v1.0.0.exe`
- `Memrix-windows-setup-v1.0.0.exe`

默认安装路径（可选）：

```
C:\Program Files\<软件名>\
```

---

### 添加环境变量

为支持命令行调用，建议将安装目录添加至系统环境变量 `Path`。

---

## 🛡 Windows 安全提示说明（首次运行）

首次运行 `.exe` 安装包或程序时，Windows 可能会弹出以下提示：

> **“Windows 已保护您的电脑”**  
> 来自 Microsoft Defender SmartScreen 的安全警告

这属于 Windows 的默认保护机制，对于尚未通过代码签名验证的新软件版本会弹出提示。请按以下步骤继续运行：

1. 点击提示框中的 **“更多信息”**
2. 点击 **“仍要运行”** 按钮继续安装或启动程序

> 此提示不会影响软件安全性或功能，仅在首次运行时出现一次。

建议您仅从官方发布页面下载安装程序，以确保来源可信。

## ⚡️ 快速开始（macOS）

### 安装

打开对应软件的 `.dmg` 安装包，按提示将图标拖入「应用程序」或任意目录。

示例：

- Framix → 拖入 `/Applications/Framix.app`
- Memrix → 拖入 `/Applications/Memrix.app`

---

### 添加环境变量

如需在终端中直接运行命令，可将二进制路径添加到系统 `PATH`：

```bash
# Framix 示例
echo 'export PATH="/Applications/Framix.app/Contents/MacOS:$PATH"' >> ~/.zshrc

# Memrix 示例
echo 'export PATH="/Applications/Memrix.app/Contents/MacOS:$PATH"' >> ~/.zshrc

source ~/.zshrc
```

---

### 授权启动脚本（首次运行前）

```bash
# Framix
chmod +x /Applications/Framix.app/Contents/MacOS/framix
chmod +x /Applications/Framix.app/Contents/MacOS/framix.sh

# Memrix
chmod +x /Applications/Memrix.app/Contents/MacOS/memrix
chmod +x /Applications/Memrix.app/Contents/MacOS/memrix.sh
```

---

## 🛡 macOS 安全提示说明（首次启动）

由于本应用未通过 App Store 分发，macOS 的安全机制（Gatekeeper）**可能在首次启动时弹出提示**，显示“无法验证开发者”或“已被阻止使用”。

如遇此情况，请按以下步骤操作以启用应用：

1. 打开 **系统设置** > **隐私与安全性**
2. 滚动到页面底部，找到“允许从以下位置下载的应用”部分
3. 点击“仍要打开”或“允许来自未知开发者的应用”
4. 再次双击 `.app` 图标即可正常启动

此操作仅需执行一次，后续启动不会再提示。

> 此行为是 macOS 的默认安全策略，不影响应用功能或安全性。

---

## ▶️ 命令行启动（Windows / macOS）

安装后可通过命令行直接启动软件，查看参数或执行任务。

### 通用命令格式：

```
<软件命令>           # 启动程序
<软件命令> -h        # 查看帮助
<软件命令> --help    # 查看详细参数说明
```

### 示例：

```bash
framix
framix -h
framix --help

memrix
memrix -h
memrix --help
```

---

## 🖥 系统兼容性

- **macOS**：支持 macOS 12.0 及以上版本  
  （原生兼容 Apple Silicon M1 / M2 / M3 与 Intel 芯片架构）
- **Windows**：支持 Windows 10 / 11（64 位）

---

## 🚦 当前版本状态：稳定版

本版本为正式发布版本，已通过功能验证与基础稳定性测试，适用于日常使用或集成部署。  
后续版本将持续优化性能表现与扩展能力。
