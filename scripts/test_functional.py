#!/usr/bin/env python3
"""Small functional checks for static GitHub Pages content."""

from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = [
    ROOT / "index.html",
    ROOT / "intelligence-editor.html",
    ROOT / "status-site" / "intelligence.html",
    ROOT / "status-site" / "pptx-builder.html",
    ROOT / "status-site" / "backlog.html",
]


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        for key, value in attrs:
            if key.lower() == "href" and value:
                self.links.append(value.strip())


errors: list[str] = []
warnings: list[str] = []

for file_path in REQUIRED_FILES:
    if not file_path.exists():
        errors.append(f"Missing required page: {file_path.relative_to(ROOT)}")

for file_path in REQUIRED_FILES:
    if not file_path.exists():
        continue

    parser = LinkParser()
    parser.feed(file_path.read_text(encoding="utf-8"))

    for href in parser.links:
        if not href or href.startswith("#"):
            continue

        parsed = urlparse(href)
        if parsed.scheme in {"http", "https", "mailto", "tel"}:
            continue

        normalized_path = parsed.path.lstrip("/")
        target_path = (ROOT / normalized_path).resolve() if normalized_path else file_path.resolve()

        if parsed.path.startswith("/"):
            candidate = target_path
        else:
            candidate = (file_path.parent / parsed.path).resolve()

        if not candidate.exists():
            errors.append(
                f"Broken internal link in {file_path.relative_to(ROOT)}: {href}"
            )

custom_404 = ROOT / "404.html"
if not custom_404.exists():
    warnings.append("No 404.html page found; GitHub Pages fallback UX may be generic.")

for warning in warnings:
    print(f"WARN: {warning}")

if errors:
    print("Functional checks failed:")
    for err in errors:
        print(f"- {err}")
    raise SystemExit(1)

print("Functional checks passed.")
