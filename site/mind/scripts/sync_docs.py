# -*- coding: utf-8 -*-
# Notes: ==== Mind™ ====

import re
import json
from pathlib import Path
from dataclasses import dataclass

MD_LINK_RE = re.compile(r"(]\()(?P<path>[^)#?\s]+\.md)(?P<suffix>(?:#[^)]+)?)\)")
CATEGORY_ORDER = [
    "入门与入口",
    "编排与协议",
    "执行与取证",
    "性能与安全",
    "结构与维护",
]
CATEGORY_GUIDES = {
    "入门与入口": "适合补齐交互入口、REPL 切换、订阅和输入约束。",
    "编排与协议": "适合处理 `--code`、协议校验、模板层和批量执行结构。",
    "执行与取证": "适合处理设备动作、多媒体证据链和端侧执行收束。",
    "性能与安全": "适合处理性能回归、稳定性诊断、签名和加解密链路。",
    "结构与维护": "适合继续读系统骨架、站点同步链路和维护约定。",
}


@dataclass(frozen=True)
class DocEntry:
    source: str
    target: str
    label: str
    category: str = ""
    summary: str = ""


def resolve_roots() -> tuple[Path, Path]:
    script = Path(__file__).resolve()
    site_root = script.parents[1]
    repo_root = script.parents[3]

    assets_root = repo_root / "Assets" / "Mind"
    if assets_root.exists():
        return assets_root, site_root

    return repo_root, site_root


def load_manifest(site_root: Path) -> list[DocEntry]:
    manifest_path = site_root / "docs_manifest.json"
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    entries = [
        DocEntry(
            source=str(entry["source"]),
            target=str(entry["target"]),
            label=str(entry["label"]),
            category=str(entry.get("category") or ""),
            summary=str(entry.get("summary") or "")
        )
        for entry in payload.get("entries", [])
    ]
    validate_manifest(entries)
    return entries


def validate_manifest(entries: list[DocEntry]) -> None:
    source_seen: set[str] = set()
    target_seen: set[str] = set()

    for entry in entries:
        if entry.source in source_seen:
            raise ValueError(f"duplicate manifest source: {entry.source}")
        if entry.target in target_seen:
            raise ValueError(f"duplicate manifest target: {entry.target}")

        source_seen.add(entry.source)
        target_seen.add(entry.target)


def build_target_map(entries: list[DocEntry]) -> dict[str, str]:
    return {entry.source: entry.target for entry in entries}


def build_link_map(source_rel: str, entries: list[DocEntry]) -> dict[str, str]:
    target_map = build_target_map(entries)

    if source_rel == "README.md":
        return {
            source: target
            for source, target in target_map.items()
            if source.startswith("docs/")
        }

    if source_rel.startswith("docs/"):
        return {
            Path(source).name: target
            for source, target in target_map.items()
            if source.startswith("docs/")
        }

    return {}


def rewrite_links(text: str, link_map: dict[str, str]) -> str:
    if not link_map:
        return text

    def repl(match: re.Match[str]) -> str:
        path = match.group("path")
        suffix = match.group("suffix") or ""
        target = link_map.get(path)
        if not target:
            return match.group(0)
        return f"{match.group(1)}{target}{suffix})"

    return MD_LINK_RE.sub(repl, text)


def rewrite_content(source_rel: str, text: str, entries: list[DocEntry]) -> str:
    text = rewrite_links(text, build_link_map(source_rel, entries))
    text = strip_heading_suffix(text)
    return text


def strip_heading_suffix(text: str) -> str:
    return re.sub(r"^(#{1,6}\s+.+?)\s+[（(][^()（）]+[)）]\s*$", r"\1", text, flags=re.MULTILINE)


def sync_reference_docs(source_root: Path, site_root: Path, entries: list[DocEntry]) -> None:
    target_root = site_root / "pages" / "generated"
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
        target.write_text(cooked, encoding="utf-8")

    render_catalog(target_root, entries)


def group_docs_entries(entries: list[DocEntry]) -> dict[str, list[DocEntry]]:
    grouped_entries: dict[str, list[DocEntry]] = {}
    for entry in entries:
        if not entry.source.startswith("docs/") or entry.source == "docs/README.md":
            continue
        grouped_entries.setdefault(entry.category or "未分组", []).append(entry)
    return grouped_entries


def render_catalog(target_root: Path, entries: list[DocEntry]) -> None:
    grouped_entries = group_docs_entries(entries)
    overview = next((entry for entry in entries if entry.source == "README.md"), None)
    docs_index = next((entry for entry in entries if entry.source == "docs/README.md"), None)
    lines = [
        "# 专题目录",
        "",
        "这页由 `website/mind/docs_manifest.json` 自动生成，用来承接官网侧的专题导览。",
        "它不重复抄写正文，而是帮你先判断现在应该读入口、边界、专题还是维护说明；分组结构与仓库内的 `docs/README.md` 保持一致。",
        "",
        "## 先按阅读状态进入",
        "- 还没跑起最小命令：先看 `项目总览`，不要一上来就翻长文",
        "- 已经知道要补哪条链路：直接跳到下面对应专题分组",
        "- 只是想确认完整目录：直接走 `文档索引`，按标题检索最快",
        "",
        "## 入口页",
    ]

    if overview:
        lines.append(f"- [{overview.label}]({overview.target})  ")
        if overview.summary:
            lines.append(f"  {overview.summary}")
    if docs_index:
        lines.append(f"- [{docs_index.label}]({docs_index.target})  ")
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
            lines.append(f"- [{entry.label}]({entry.target})  ")
            if entry.summary:
                lines.append(f"  {entry.summary}")
        lines.append("")

    for category, entries_in_category in grouped_entries.items():
        if category in CATEGORY_ORDER:
            continue
        lines.append(f"### {category}")
        lines.append("")
        for entry in entries_in_category:
            lines.append(f"- [{entry.label}]({entry.target})  ")
            if entry.summary:
                lines.append(f"  {entry.summary}")
        lines.append("")

    lines.extend([
        "## 阅读建议",
        "- 先用入口页确认任务形态，再按专题分组进入长正文，不要把专题目录当百科首页",
        "- 如果你已经知道要找什么，直接走 `文档索引` 会更快；如果还在判断方向，就先停在这里筛掉无关长文",
        "- repo 内的 `docs/README.md` 和这里是同一套清单，只是一个面向仓库阅读，一个面向官网跳转",
        "",
    ])

    (target_root / "catalog.md").write_text("\n".join(lines), encoding="utf-8")


def render_docs_readme(source_root: Path, entries: list[DocEntry]) -> None:
    grouped_entries = group_docs_entries(entries)

    lines = [
        "# 文档索引",
        "",
        "这里收纳从主 README 拆出的长文档。主 README 只保留上手入口、能力边界和最小速查，完整正文统一从这里继续跳转。",
        "这页由 `website/mind/docs_manifest.json` 自动生成；如果新增、下线、重命名或调整专题顺序，应优先修改文档清单，而不是手改索引页。",
        "",
        "## 先按阅读状态进入",
        "- 第一次进入项目：先看主 README，确认怎么启动、怎么选模式、怎么跑最小命令",
        "- 已经知道任务类型：直接按下面的专题分组跳正文，不必把所有长文都读一遍",
        "- 需要回到站点入口：官网壳负责导航和导览，`docs` 负责完整正文",
        "- 正在排查某条链路：只读和当前任务相关的专题，不要把索引页当成长文正文",
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
            lines.append(f"- [{entry.label}]({Path(entry.source).name})  ")
            if entry.summary:
                lines.append(f"  {entry.summary}")
        lines.append("")

    for category, entries_in_category in grouped_entries.items():
        if category in CATEGORY_ORDER:
            continue
        lines.append(f"### {category}")
        lines.append("")
        for entry in entries_in_category:
            lines.append(f"- [{entry.label}]({Path(entry.source).name})  ")
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
    source_root, site_root = resolve_roots()
    entries = load_manifest(site_root)
    render_docs_readme(source_root, entries)
    sync_reference_docs(source_root, site_root, entries)
    print(f"synced docs from {source_root} -> {site_root / 'pages' / 'generated'}")


if __name__ == "__main__":
    main()
