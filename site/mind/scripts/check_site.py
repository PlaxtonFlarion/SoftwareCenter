# -*- coding: utf-8 -*-
# Notes: ==== Mind™ ====

"""校验实际构建的 HTML、章节锚点和本地资源。"""

import argparse
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import (
    unquote,
    urlsplit,
)


class PublishedPage(HTMLParser):
    """收集单个静态页面的链接、锚点和语言，不执行脚本。"""

    def __init__(self) -> None:
        """初始化当前页面的校验输入。"""
        super().__init__(convert_charrefs=True)
        self.ids: set[str] = set()
        self.duplicates: set[str] = set()
        self.links: list[str] = []
        self.language = ""
        self.canonical = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """读取 HTML 元素的本地目标和页面元信息。"""
        attributes = dict(attrs)
        identity = attributes.get("id")
        if identity:
            if identity in self.ids:
                self.duplicates.add(identity)
            self.ids.add(identity)
        if tag == "html":
            self.language = attributes.get("lang") or ""
        if tag == "link" and attributes.get("rel") == "canonical":
            self.canonical = attributes.get("href") or ""
            return
        if tag in ("a", "link"):
            target = attributes.get("href")
        elif tag in ("script", "img", "source", "video", "audio"):
            target = attributes.get("src")
        else:
            target = None
        if target:
            self.links.append(target)


def validate_site(root: Path, *, origin: str = "https://www.appserverx.com") -> tuple[str, ...]:
    """检查构建结果中的本地链接、重复锚点和正式域名。"""
    root = root.resolve()
    pages: dict[Path, PublishedPage] = {}
    errors: list[str] = []
    for path in sorted(root.rglob("*.html")):
        page = PublishedPage()
        page.feed(path.read_text(encoding="utf-8"))
        pages[path] = page
    if root / "index.html" not in pages:
        return ("built homepage missing",)
    for path, page in pages.items():
        relative = path.relative_to(root).as_posix()
        if page.language.lower() != "zh-cn":
            errors.append(f"incorrect page language: {relative} -> {page.language}")
        if not page.canonical.startswith(origin + "/"):
            errors.append(f"incorrect canonical: {relative} -> {page.canonical}")
        for identity in sorted(page.duplicates):
            errors.append(f"duplicate anchor: {relative} -> #{identity}")
        for href in page.links:
            url = urlsplit(href)
            if (url.netloc and url.netloc != urlsplit(origin).netloc) or url.scheme not in ("", "http", "https"):
                continue
            url_path = unquote(url.path)
            if not url_path:
                target = path
            elif url_path.startswith("/"):
                target = (root / url_path.lstrip("/")).resolve()
            else:
                target = (path.parent / url_path).resolve()
            if not target.is_relative_to(root):
                errors.append(f"link outside site: {relative} -> {href}")
                continue
            if target.is_dir():
                target /= "index.html"
            if not target.is_file():
                errors.append(f"broken file link: {relative} -> {href}")
            elif url.fragment and target in pages:
                fragment = unquote(url.fragment).split(":~:text=", 1)[0]
                if fragment and fragment not in pages[target].ids:
                    errors.append(f"broken anchor: {relative} -> {href}")
    return tuple(sorted(set(errors)))


def main() -> int:
    """校验站点产物，任何失效目标均阻止发布。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", type=Path, default=Path(__file__).resolve().parents[1] / "site")
    arguments = parser.parse_args()
    errors = validate_site(arguments.site)
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        return 1
    print("built site ok: files, anchors, canonical URLs and Chinese page language")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
