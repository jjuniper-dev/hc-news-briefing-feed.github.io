#!/usr/bin/env python3
"""Basic accessibility lint for key static pages."""

from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = [
    ROOT / "index.html",
    ROOT / "intelligence-editor.html",
    ROOT / "status-site" / "intelligence.html",
    ROOT / "status-site" / "pptx-builder.html",
    ROOT / "status-site" / "backlog.html",
]


class AccessibilityParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.has_title = False
        self.title_text = ""
        self.capture_title = False
        self.html_lang = ""
        self.images_missing_alt = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag_name = tag.lower()
        attr_map = {k.lower(): (v or "") for k, v in attrs}
        if tag_name == "html":
            self.html_lang = attr_map.get("lang", "").strip()
        elif tag_name == "title":
            self.has_title = True
            self.capture_title = True
        elif tag_name == "img" and "alt" not in attr_map:
            self.images_missing_alt += 1

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self.capture_title = False

    def handle_data(self, data: str) -> None:
        if self.capture_title:
            self.title_text += data


errors: list[str] = []

for page in PAGES:
    if not page.exists():
        errors.append(f"Missing page for accessibility check: {page.relative_to(ROOT)}")
        continue

    parser = AccessibilityParser()
    parser.feed(page.read_text(encoding="utf-8"))

    if not parser.html_lang:
        errors.append(f"{page.relative_to(ROOT)}: missing <html lang=...>")
    if not parser.has_title or not parser.title_text.strip():
        errors.append(f"{page.relative_to(ROOT)}: missing non-empty <title>")
    if parser.images_missing_alt > 0:
        errors.append(
            f"{page.relative_to(ROOT)}: {parser.images_missing_alt} <img> tag(s) missing alt attribute"
        )

if errors:
    print("Accessibility checks failed:")
    for err in errors:
        print(f"- {err}")
    raise SystemExit(1)

print("Accessibility checks passed.")
