# Mind 文档中心

正式地址：<https://www.appserverx.com/>。

站点使用 Astro + Starlight，构建为静态 HTML，在 Cloudflare Pages 发布。
产品说明和使用文档位于本站；AppServer 的 `/docs` 是独立的 API 参考入口。

## 内容与职责

- 根目录架构文件及 `docs/` 是正文事实源；官网不维护第二份正文。
- `docs_manifest.json` 登记全部正文的发布目标、标题、摘要和导航分组。
- `scripts/sync_docs.py` 生成仓库索引、`src/content/docs/generated/` 和产品展示元数据。
- `src/content/docs/` 下的手写入口页只组织安装路径、运行方式和常用命令。
- `src/components/` 与 `src/styles/docs.css` 负责展示；产品名称与年份来自 `metadata/const.py`。
- 所有正文共用标题、摘要、导航、表格与代码样式；摘要在 `docs_manifest.json` 中维护，操作细节仍以正文事实源为准。
- 阅读主题统一为“晴岚映雪”“松风入夜”“落日熔金”“星河入梦”，定义位于 `src/reading-themes.ts`。`ThemeProvider` 在首次绘制前恢复浏览器偏好，`ThemeControl` 持有选择交互与持久化；明暗模式同时用于代码高亮。
- 主题只对正文区域做 200ms 透明度交叠，导航和主题入口不参与快照，动画播放期间保持可操作。正文快照内不叠加逐元素颜色过渡；连续选择撤销旧动画及未提交选择，结束或移除组件后释放临时样式。减少动态效果或不支持 View Transition 时直接应用主题。
- `scripts/check_site.py` 校验最终 HTML 的本地资源、文件链接、章节锚点、语言和 canonical。

既有 `generated/<文档名>/` 地址保持稳定。正文保留中文锚点，同时保留旧站已发布的 ASCII 章节书签。
新增页面必须登记清单中的 `section`，按“使用指南、工具与集成、命令参考、开发者”分组；快速开始是独立入口。

## 开发与验收

在仓库虚拟环境中使用 Python，并安装 `.node-version` 指定的 Node.js。

```bash
python website/mind/scripts/check_docs.py
python -m pytest tests/website -q
cd website/mind
npm ci
npm run build
npx playwright install chromium
npm test
```

`npm run build` 依次执行正文同步、Astro 类型检查、静态构建、Pagefind 索引和 HTML 校验。
发布构建使用 `astro build --force` 全量生成正文，确保代码高亮等渲染配置变更后，页面不会引用旧缓存中的资源文件。
浏览器测试覆盖全部发布页面的响应式布局，以及桌面和手机的深浅主题、中文与命令搜索、键盘焦点、导航、书签、行宽与 WCAG 检查。
主题检查包含四套配色、跨页面记忆、首次访问时的系统外观选择及减少动态效果；搜索关闭后将焦点交还给打开它的控件。
搜索在打开时立即初始化，提供加载与失败提示；代码块在静态 HTML 中即支持键盘访问，两者均不依赖浏览器空闲回调。
本机已有 Chrome 时，可在启动测试前设置 `DOCS_BROWSER_CHANNEL=chrome`。

```bash
npm run dev
npm run preview -- --host 127.0.0.1 --port 4321
```

开发服务用于修改页面；全文搜索必须在 `npm run build` 后通过 preview 验证。

## 发布

GitHub Actions 校验通过后，将正文和站点源码同步到 SoftwareCenter；不复制依赖、缓存和构建产物。
公开仓库无需应用运行时依赖，Python 同步脚本仅使用标准库。完整部署设置见 [Cloudflare Pages](CLOUDFLARE.md)。
