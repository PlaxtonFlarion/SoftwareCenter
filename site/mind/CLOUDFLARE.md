# Cloudflare Pages 部署说明

这份说明对应当前的 `A` 方案：
- 私有仓库维护正文与官网壳
- GitHub Actions 同步到公共仓库 `SoftwareCenter`
- Cloudflare Pages 直接从公共仓库构建站点

## 目录约定

公共仓库中的目标结构：

```text
SoftwareCenter/
├── Assets/
│   └── Mind/
│       ├── README.md
│       └── docs/
└── site/
    └── mind/
        ├── mkdocs.yml
        ├── requirements.txt
        ├── scripts/
        └── pages/
```

说明：
- `Assets/Mind/` 是文档事实源
- `site/mind/` 是官网展示壳
- Cloudflare Pages 应该指向 `site/mind/`

## 前置条件

在 Cloudflare Pages 接入之前，先确认：

1. 私有仓库中的同步 workflow 已跑通
2. 公共仓库中已经存在：
   - `Assets/Mind/README.md`
   - `Assets/Mind/docs/*.md`
   - `site/mind/mkdocs.yml`
   - `site/mind/docs_manifest.json`
   - `site/mind/requirements.txt`
   - `site/mind/scripts/sync_docs.py`

## Cloudflare Pages 配置

在 Cloudflare Pages 新建项目时，使用下面这组参数：

- Repository：`PlaxtonFlarion/SoftwareCenter`
- Production branch：`main`
- Root directory：`site/mind`
- Build command：

```bash
pip install -r requirements.txt && python scripts/sync_docs.py && mkdocs build
```

- Build output directory：

```text
site
```

## 构建逻辑

Cloudflare Pages 的构建过程分三步：

1. 安装 `MkDocs` 相关依赖
2. 运行 `scripts/sync_docs.py`
   - 从 `Assets/Mind/README.md`
   - 以及 `Assets/Mind/docs/*.md`
   - 按 `site/mind/docs_manifest.json` 的清单
   - 生成 `site/mind/pages/generated/*.md`
3. 运行 `mkdocs build`
   - 输出静态 HTML 到 `site/`

## 本地预览

如果要在本地先看站点效果：

```bash
cd website/mind
pip install -r requirements.txt
python scripts/sync_docs.py
mkdocs serve
```

默认访问：

```text
http://127.0.0.1:8000
```

## 首次上线顺序

建议按这个顺序做：

1. 在私有仓库完成正文和官网壳修改
2. 手动运行 `sync_docs_bundle`
3. 到公共仓库确认：
   - `Assets/Mind/` 已更新
   - `site/mind/` 已更新
4. 在 Cloudflare Pages 中配置：
   - repo
   - root directory
   - build command
   - output directory
5. 先用 `*.pages.dev` 域名验证
6. 确认无误后再绑定自定义域名

## 常见检查点

- 如果首页更新了但参考文档没更新：
  - 检查 `scripts/sync_docs.py` 是否已运行
- 如果站点能构建但正文链接不对：
  - 检查正文链接是否仍是仓库内相对路径
- 如果 Cloudflare 构建失败：
  - 先检查 `requirements.txt`
  - 再检查 `mkdocs.yml`
  - 最后检查 `scripts/sync_docs.py` 是否能在公共仓库目录下运行

## 当前边界

这份官网壳当前负责：
- 首页
- 快速开始
- 能力概览
- 参考文档入口

它不负责：
- 复制维护完整正文
- 改写 `Assets/Mind` 的事实源文档
