# -*- coding: utf-8 -*-
# Notes: ==== Mind™ ====

import re
import json
from pathlib import Path
from dataclasses import dataclass

MD_LINK_RE = re.compile(r"(]\()(?P<path>[^)#?\s]+\.md)(?P<suffix>(?:#[^)]+)?)\)")


@dataclass(frozen=True)
class DocEntry:
    source: str
    target: str
    label: str
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


def render_catalog(target_root: Path, entries: list[DocEntry]) -> None:
    lines = [
        "# 专题目录",
        "",
        "这页由 `website/mind/docs_manifest.json` 自动生成，用来承接官网侧的专题导览。",
        "如果你只是想按专题找正文，从这里继续跳转即可。",
        "",
        "## 文档列表",
    ]

    for entry in entries:
        lines.append(f"- [{entry.label}]({entry.target})  ")
        if entry.summary:
            lines.append(f"  {entry.summary}")

    lines.append("")
    (target_root / "catalog.md").write_text("\n".join(lines), encoding="utf-8")


def render_docs_readme(source_root: Path, entries: list[DocEntry]) -> None:
    docs_entries = [
        entry
        for entry in entries
        if entry.source.startswith("docs/") and entry.source != "docs/README.md"
    ]

    lines = [
        "# 文档索引",
        "",
        "这里收纳从主 README 拆出的长文档。主 README 只保留上手入口、能力边界和最小速查。",
        "这页由 `website/mind/docs_manifest.json` 自动生成；如果新增、下线或调整专题顺序，应优先修改文档清单。",
        "",
        "## 使用说明",
        "- 先看主 README，确认怎么启动、怎么选模式、怎么跑最小示例",
        "- 需要某一块的完整说明时，再跳到对应文档",
        "",
        "## 文档目录",
    ]

    for entry in docs_entries:
        lines.append(f"- [{entry.label}]({Path(entry.source).name})  ")
        if entry.summary:
            lines.append(f"  {entry.summary}")

    lines.append("")
    (source_root / "docs" / "README.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    source_root, site_root = resolve_roots()
    entries = load_manifest(site_root)
    render_docs_readme(source_root, entries)
    sync_reference_docs(source_root, site_root, entries)
    print(f"synced docs from {source_root} -> {site_root / 'pages' / 'generated'}")


if __name__ == "__main__":
    main()
