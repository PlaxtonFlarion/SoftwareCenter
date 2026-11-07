# Cloudflare Pages 部署

正式域名为 `https://www.appserverx.com`。ProxyMind 维护正文和站点源码，GitHub Actions 校验后同步到
公共仓库 `PlaxtonFlarion/SoftwareCenter`，Cloudflare Pages 从公共仓库构建静态站点。

## 项目设置

| 设置 | 值 |
| --- | --- |
| Repository | `PlaxtonFlarion/SoftwareCenter` |
| Production branch | `main` |
| Root directory | `site/mind` |
| Build command | `npm ci && npm run build` |
| Build output directory | `site` |
| Node.js | `.node-version` 指定的 `24.21.0`；如控制台设置了 `NODE_VERSION`，需与之保持一致 |
| Python | Python 3.11 或更新版本，`python` 命令可用；无需 pip 依赖 |

Pages 控制台的构建命令必须与本表一致；仓库文件不会自动修改控制台里保存的构建命令。
依赖通过 `package-lock.json` 与 `npm ci` 固定。

## 公开仓库布局

```text
SoftwareCenter/
├── Assets/Mind/
│   ├── README.md
│   ├── ARCHITECTURE_SYSTEM.md
│   ├── ARCHITECTURE.md
│   ├── ARCHITECTURE_SCORECARD.md
│   ├── AGENTS.md
│   ├── LICENSE.md
│   ├── metadata/const.py
│   └── docs/
└── site/mind/
    ├── astro.config.mjs
    ├── package.json
    ├── package-lock.json
    ├── docs_manifest.json
    ├── scripts/
    ├── public/
    └── src/
```

`scripts/sync_docs.py` 自动识别此布局，将清单内的正文转换为 Astro 内容集合，并从产品常量提取展示元数据。
`npm run build` 完成页面、搜索索引和 sitemap 后，校验实际 HTML；失效文件链接或章节锚点会令构建失败。

## 域名与入口

在 Pages 的 Custom domains 中绑定 `www.appserverx.com`，按控制台要求配置 DNS。
裸域到 `www` 的跳转使用 Cloudflare Bulk Redirects；Pages 的 `_redirects` 不支持按来源域名匹配。

| Bulk Redirect 设置 | 值 |
| --- | --- |
| Source URL | `appserverx.com/` |
| Target URL | `https://www.appserverx.com/` |
| Status | `301` |
| Preserve query string | 开启 |
| Subpath matching | 开启 |
| Preserve path suffix | 开启 |
| Include subdomains | 关闭，避免匹配 `www` 导致循环跳转 |

创建并启用引用该列表的 Bulk Redirect Rule；裸域 DNS 必须开启 Cloudflare 代理，确保请求经过规则。
若裸域仍返回 522，检查 DNS、代理状态和规则是否生效，站点源码无法代替这些账户设置。
配置方式见 [Cloudflare 域名重定向说明](https://developers.cloudflare.com/pages/how-to/www-redirect/)，
这里使用相反的跳转方向，将裸域统一到 `www`。

canonical、sitemap 和 robots.txt 均使用 `https://www.appserverx.com`。
AppServer 首页的 Mind 入口链接到官网；AppServer `/docs` 保持 API 参考职责，并提供官网入口。
公网文档不硬编码某个内网 IP 作为用户必须访问的服务地址。

## 验收与发布顺序

1. PR 检查通过：Python 发布契约、Astro 类型检查、实际构建、HTML 链接和浏览器验收。
2. 核对 Pages 的构建命令、Node.js 和两个域名设置。
3. `main` 同步完成后，在 Pages 部署预览中验证首页、正文、中文搜索与旧书签。
4. 检查正式域名、裸域跳转、静态资源和搜索索引均可访问。

构建失败时先看 Pages 日志中的具体步骤；若 `npm ci` 失败，核对 Node.js 和 lockfile；若正文生成失败，
核对 `Assets/Mind` 与清单；若 HTML 校验失败，按报出的页面、资源或锚点修复源文档。
