# -*- coding: utf-8 -*-
# Notes: ==== Mind™ ====

import ast
import json
import re
from dataclasses import dataclass
from pathlib import (
    Path,
    PurePosixPath,
    PureWindowsPath,
)
from urllib.parse import (
    unquote,
    urlsplit,
)

MD_LINK_RE = re.compile(r"(]\()(?P<path>[^)#?\s]+\.md)(?P<suffix>(?:#[^)]+)?)\)")
CATEGORY_ORDER = [
    "入门与入口",
    "编排与协议",
    "执行与取证",
    "性能与安全",
    "结构与维护",
]
CATEGORY_GUIDES = {
    "入门与入口": "选择终端、桌面或订阅入口，了解启动方式、会话管理和连接准备。",
    "编排与协议": "配置工具与自动化流程，组织请求参数，并核对结果和状态。",
    "执行与取证": "完成代码、设备和媒体任务，保存可复核的文件、画面或日志。",
    "性能与安全": "设计性能与稳定性检查，按服务协议处理签名、令牌和密文。",
    "结构与维护": "理解产品组成，维护文档发布，并执行平台与服务验收。",
}


@dataclass(frozen=True)
class DocEntry:
    source: str
    target: str
    label: str
    category: str = ""
    summary: str = ""
    section: str = "开发者"


def resolve_roots() -> tuple[Path, Path]:
    """定位源码仓库或公开文档包中的正文与站点目录。"""
    script = Path(__file__).resolve()
    site_root = script.parents[1]
    repo_root = script.parents[3]

    assets_root = repo_root / "Assets" / "Mind"
    if assets_root.exists():
        return assets_root, site_root

    return repo_root, site_root


def load_manifest(site_root: Path) -> list[DocEntry]:
    """读取发布清单并校验文档身份和导航分组。"""
    manifest_path = site_root / "docs_manifest.json"
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("entries"), list):
        raise ValueError("manifest entries must be a list")
    entries: list[DocEntry] = []
    for record in payload["entries"]:
        if not isinstance(record, dict):
            raise ValueError("manifest entry must be a mapping")
        fields: dict[str, str] = {}
        for name in ("source", "target", "label", "section", "category", "summary"):
            value = record.get(name, "") if name in ("category", "summary") else record.get(name)
            if not isinstance(value, str):
                raise ValueError(f"manifest field must be a string: {name}")
            fields[name] = value
        entries.append(DocEntry(**fields))
    validate_manifest(entries)
    return entries


def validate_manifest(entries: list[DocEntry]) -> None:
    """拒绝重复身份、越界路径和未知导航分组。"""
    source_seen: set[str] = set()
    target_seen: set[str] = set()

    for entry in entries:
        for path in (entry.source, entry.target):
            if (
                not path or PurePosixPath(path).is_absolute() or PureWindowsPath(path).drive
                or ".." in PurePosixPath(path).parts or "\\" in path
            ):
                raise ValueError(f"invalid manifest path: {path}")
        if Path(entry.target).name != entry.target or not entry.target.endswith(".md"):
            raise ValueError(f"invalid manifest target: {entry.target}")
        if entry.section not in ("", "使用指南", "工具与集成", "命令参考", "开发者"):
            raise ValueError(f"unknown navigation section: {entry.section}")
        if not entry.section and entry.source != "docs/README.md":
            raise ValueError(f"navigation section missing: {entry.source}")
        if not entry.label:
            raise ValueError(f"document label missing: {entry.source}")
        if entry.source in source_seen:
            raise ValueError(f"duplicate manifest source: {entry.source}")
        if entry.target in target_seen:
            raise ValueError(f"duplicate manifest target: {entry.target}")

        source_seen.add(entry.source)
        target_seen.add(entry.target)


def local_markdown_links(text: str) -> tuple[str, ...]:
    """提取正文中的本地 Markdown 链接，排除外部站点链接。"""
    paths: list[str] = []
    for match in MD_LINK_RE.finditer(text):
        path = match.group("path")
        url = urlsplit(path)
        if not url.scheme and not url.netloc:
            paths.append(unquote(url.path))
    return tuple(paths)


def validate_publication(source_root: Path, entries: list[DocEntry]) -> tuple[str, ...]:
    """在生成前校验正文清单完整性及本地文档链接的发布目标。"""
    errors: list[str] = []
    sources = {(source_root / entry.source).resolve() for entry in entries}
    for document in sorted((source_root / "docs").rglob("*.md")):
        if document.is_file() and document.resolve() not in sources:
            errors.append(
                f"document missing from manifest: {document.relative_to(source_root).as_posix()}"
            )

    for entry in entries:
        source = source_root / entry.source
        if not source.is_file():
            errors.append(f"manifest source missing: {entry.source}")
            continue
        # 文档索引由清单重建，旧索引不能阻止已下线文档从生成结果中移除。
        if entry.source == "docs/README.md":
            continue
        for path in local_markdown_links(source.read_text(encoding="utf-8")):
            destination = (source.parent / path).resolve()
            if not destination.is_file():
                errors.append(f"broken source link: {entry.source} -> {path}")
            elif destination not in sources:
                errors.append(f"linked document missing from manifest: {entry.source} -> {path}")
    return tuple(errors)


def build_target_map(entries: list[DocEntry]) -> dict[str, str]:
    """建立正文源路径与发布页面路径之间的映射。"""
    return {entry.source: entry.target for entry in entries}


def build_link_map(source_rel: str, entries: list[DocEntry]) -> dict[str, str]:
    """按当前正文目录解析相邻文档的发布地址。"""
    target_map = build_target_map(entries)

    if not source_rel.startswith("docs/"):
        return {
            source: f"/generated/{Path(target).stem}/"
            for source, target in target_map.items()
            if source != source_rel
        }

    links = {
        Path(source).name: f"/generated/{Path(target).stem}/"
        for source, target in target_map.items()
        if source.startswith("docs/")
    }
    links.update({
        f"../{source}": f"/generated/{Path(target).stem}/"
        for source, target in target_map.items()
        if not source.startswith("docs/")
    })
    return links


def rewrite_links(text: str, link_map: dict[str, str]) -> str:
    """将已登记的正文链接改写为保留锚点的站点地址。"""
    if not link_map:
        return text

    def repl(match: re.Match[str]) -> str:
        """改写一个已登记的文档目标。"""
        path = match.group("path")
        suffix = match.group("suffix") or ""
        target = link_map.get(path)
        if not target:
            return match.group(0)
        return f"{match.group(1)}{target}{suffix})"

    return MD_LINK_RE.sub(repl, text)


def rewrite_content(source_rel: str, text: str, entries: list[DocEntry]) -> str:
    """保留正文和标题，只转换站点中的文档链接。"""
    return rewrite_links(text, build_link_map(source_rel, entries))


def frontmatter(entry: DocEntry) -> str:
    """生成页面标题、摘要和固定路由，避免更换渲染器改变公开地址。"""
    values = [
        "---",
        f"title: {json.dumps(entry.label, ensure_ascii=False)}",
        f"slug: generated/{Path(entry.target).stem}",
    ]
    if entry.summary:
        values.append(f"description: {json.dumps(entry.summary, ensure_ascii=False)}")
    if entry.source in ("docs/README.md", "LICENSE.md", "AGENTS.md"):
        values.append("pagefind: false")
    values.extend(["---", "", ""])
    return "\n".join(values)


def render_site_metadata(source_root: Path, site_root: Path) -> None:
    """从产品常量生成展示元数据，不导入客户端运行时。"""
    source = source_root / "metadata" / "const.py"
    tree = ast.parse(source.read_text(encoding="utf-8"))
    fields = {"APP_DESC": "name", "APP_CN": "nameZh", "APP_YEAR": "year"}
    values: dict[str, str] = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign) or not isinstance(node.value, ast.Constant):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id in fields and isinstance(node.value.value, str):
                values[fields[target.id]] = node.value.value
    if set(values) != set(fields.values()):
        raise ValueError("product display metadata is incomplete")
    target = site_root / "src" / "generated" / "product.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(values, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sync_reference_docs(source_root: Path, site_root: Path, entries: list[DocEntry]) -> None:
    """校验发布文档后重建索引及官网镜像，校验失败时保留原有产物。"""
    errors = validate_publication(source_root, entries)
    if errors:
        raise ValueError("\n".join(errors))

    render_site_metadata(source_root, site_root)
    render_docs_readme(source_root, entries)
    target_root = site_root / "src" / "content" / "docs" / "generated"
    target_root.mkdir(parents=True, exist_ok=True)

    for old in target_root.glob("*.md"):
        old.unlink()

    for entry in entries:
        source_rel = entry.source
        source = source_root / source_rel
        if not source.exists():
            raise FileNotFoundError(f"manifest source not found: {source}")

        raw = source.read_text(encoding="utf-8")
        cooked = rewrite_content(source_rel, raw, entries)
        target = target_root / entry.target
        target.write_text(frontmatter(entry) + cooked, encoding="utf-8")

    render_catalog(target_root, entries)


def group_docs_entries(entries: list[DocEntry]) -> dict[str, list[DocEntry]]:
    """按正文主题生成仓库索引和站点目录。"""
    grouped_entries: dict[str, list[DocEntry]] = {}
    for entry in entries:
        if not entry.source.startswith("docs/") or entry.source == "docs/README.md":
            continue
        grouped_entries.setdefault(entry.category or "未分组", []).append(entry)
    return grouped_entries


def render_catalog(target_root: Path, entries: list[DocEntry]) -> None:
    """生成保留既有地址的专题目录。"""
    grouped_entries = group_docs_entries(entries)
    overview = next((entry for entry in entries if entry.source == "README.md"), None)
    docs_index = next((entry for entry in entries if entry.source == "docs/README.md"), None)
    lines = [
        "# 专题目录",
        "",
        "## 先按阅读状态进入",
        "- 第一次使用：从[快速开始](/getting-started/)完成安装、模型配置和第一条任务。",
        "- 已有明确目标：按下方专题选择代码、设备、接口或媒体指南。",
        "- 查一条具体命令：打开[常用命令速查](/reference/)，再进入完整参考。",
        "",
        "## 入口页",
    ]

    if overview:
        lines.append(f"- [{overview.label}]({overview.target})")
        if overview.summary:
            lines.append(f"  {overview.summary}")
    if docs_index:
        lines.append(f"- [{docs_index.label}]({docs_index.target})")
        if docs_index.summary:
            lines.append(f"  {docs_index.summary}")

    lines.extend([
        "",
        "## 按专题继续深入",
    ])

    for category in CATEGORY_ORDER:
        entries_in_category = grouped_entries.get(category)
        if not entries_in_category:
            continue
        lines.append(f"### {category}")
        guide = CATEGORY_GUIDES.get(category)
        if guide:
            lines.append(guide)
        lines.append("")
        for entry in entries_in_category:
            lines.append(f"- [{entry.label}]({entry.target})")
            if entry.summary:
                lines.append(f"  {entry.summary}")
        lines.append("")

    for category, entries_in_category in grouped_entries.items():
        if category in CATEGORY_ORDER:
            continue
        lines.append(f"### {category}")
        lines.append("")
        for entry in entries_in_category:
            lines.append(f"- [{entry.label}]({entry.target})")
            if entry.summary:
                lines.append(f"  {entry.summary}")
        lines.append("")

    lines.extend([
        "## 阅读建议",
        "- 操作指南先说明前置条件与步骤；字段、协议和维护细节供需要时查阅。",
        "- 示例中的尖括号内容和 example.com 地址需要替换；自然语言任务说明不等同于固定工具参数。",
        "- 遇到陌生术语，可使用顶部搜索；返回完整目录时使用页脚的“文档目录”入口。",
        "",
    ])

    links = {entry.target: f"/generated/{Path(entry.target).stem}/" for entry in entries}
    entry = DocEntry("docs/README.md", "catalog.md", "专题目录")
    content = frontmatter(entry) + rewrite_links("\n".join(lines), links)
    (target_root / "catalog.md").write_text(content, encoding="utf-8")


def render_docs_readme(source_root: Path, entries: list[DocEntry]) -> None:
    """由发布清单生成使用仓库相对链接的正文索引。"""
    grouped_entries = group_docs_entries(entries)
    has_overview = any(entry.source == "README.md" for entry in entries)

    lines = [
        "# 正文目录",
        (
            "第一次使用先读[项目总览](../README.md#quick-start)；已经有明确目标时，按下方分组选择对应指南。"
            if has_overview else "按当前任务选择下方指南，先完成操作步骤，再按需查询参数与实现细节。"
        ),
        "",
        "## 按任务方向阅读",
    ]

    for category in CATEGORY_ORDER:
        entries_in_category = grouped_entries.get(category)
        if not entries_in_category:
            continue
        lines.append(f"### {category}")
        guide = CATEGORY_GUIDES.get(category)
        if guide:
            lines.append(guide)
        lines.append("")
        for entry in entries_in_category:
            lines.append(f"- [{entry.label}]({Path(entry.source).name})")
            if entry.summary:
                lines.append(f"  {entry.summary}")
        lines.append("")

    for category, entries_in_category in grouped_entries.items():
        if category in CATEGORY_ORDER:
            continue
        lines.append(f"### {category}")
        lines.append("")
        for entry in entries_in_category:
            lines.append(f"- [{entry.label}]({Path(entry.source).name})")
            if entry.summary:
                lines.append(f"  {entry.summary}")
        lines.append("")

    lines.extend([
        "## 阅读建议",
        "- 先解决当前任务，再回来看结构文档；索引页负责导航，不负责替代正文",
        "- 如果你正在补协议、模板、设备或媒体链路，优先读对应专题，再回到 README 看入口说明",
        "- 如果你在维护官网壳或同步链路，优先看 `维护者指南` 和 `背景与架构`",
        "",
    ])

    (source_root / "docs" / "README.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    """从发布清单校验并生成仓库索引和官网正文。"""
    source_root, site_root = resolve_roots()
    entries = load_manifest(site_root)
    sync_reference_docs(source_root, site_root, entries)
    print(f"synced {len(entries)} documents from {source_root}")


if __name__ == "__main__":
    main()
