from __future__ import annotations

from pathlib import Path
import re


DOC_FILES = (
    "README.md",
    "docs/README.md",
    "docs/cli-code.md",
    "docs/api-playbook.md",
    "docs/template-playbook.md",
    "docs/security-playbook.md",
    "docs/device-playbook.md",
    "docs/interactive-mode.md",
    "docs/media-playbook.md",
    "docs/performance-playbook.md",
    "docs/architecture.md",
    "docs/maintainer-guide.md",
)

README_REWRITE_MAP = {
    "(docs/README.md)": "(docs-index.md)",
    "(docs/cli-code.md)": "(cli-code.md)",
    "(docs/api-playbook.md)": "(api-playbook.md)",
    "(docs/template-playbook.md)": "(template-playbook.md)",
    "(docs/security-playbook.md)": "(security-playbook.md)",
    "(docs/device-playbook.md)": "(device-playbook.md)",
    "(docs/interactive-mode.md)": "(interactive-mode.md)",
    "(docs/media-playbook.md)": "(media-playbook.md)",
    "(docs/performance-playbook.md)": "(performance-playbook.md)",
    "(docs/architecture.md)": "(architecture.md)",
    "(docs/maintainer-guide.md)": "(maintainer-guide.md)",
}


def resolve_roots() -> tuple[Path, Path]:
    script = Path(__file__).resolve()
    site_root = script.parents[1]
    repo_root = script.parents[3]

    assets_root = repo_root / "Assets" / "Mind"
    if assets_root.exists():
        return assets_root, site_root

    return repo_root, site_root


def rewrite_content(source_rel: str, text: str) -> str:
    if source_rel == "README.md":
        for before, after in README_REWRITE_MAP.items():
            text = text.replace(before, after)
    text = strip_heading_suffix(text)
    return text


def strip_heading_suffix(text: str) -> str:
    return re.sub(r"^(#{1,6}\s+.+?)\s+[（(][^()（）]+[)）]\s*$", r"\1", text, flags=re.MULTILINE)


def target_name(source_rel: str) -> str:
    if source_rel == "README.md":
        return "overview.md"
    if source_rel == "docs/README.md":
        return "docs-index.md"
    return Path(source_rel).name


def sync_reference_docs(source_root: Path, site_root: Path) -> None:
    target_root = site_root / "pages" / "generated"
    target_root.mkdir(parents=True, exist_ok=True)

    for old in target_root.glob("*.md"):
        old.unlink()

    for source_rel in DOC_FILES:
        source = source_root / source_rel
        if not source.exists():
            continue

        raw = source.read_text(encoding="utf-8")
        cooked = rewrite_content(source_rel, raw)
        target = target_root / target_name(source_rel)
        target.write_text(cooked, encoding="utf-8")


def main() -> None:
    source_root, site_root = resolve_roots()
    sync_reference_docs(source_root, site_root)
    print(f"synced docs from {source_root} -> {site_root / 'pages' / 'generated'}")


if __name__ == "__main__":
    main()
