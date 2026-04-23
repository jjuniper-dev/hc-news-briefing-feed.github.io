#!/usr/bin/env python3
"""Architecture and navigation contract checks for the static site."""

from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SITE_PAGES = [
    ROOT / "index.html",
    ROOT / "intelligence-editor.html",
    ROOT / "status-site" / "intelligence.html",
    ROOT / "status-site" / "pptx-builder.html",
    ROOT / "status-site" / "backlog.html",
]

STATUS_PAGES = [
    ROOT / "status-site" / "intelligence.html",
    ROOT / "status-site" / "pptx-builder.html",
    ROOT / "status-site" / "backlog.html",
]

REQUIRED_NAV_LABELS = [
    "Dashboard",
    "Intelligence Editor",
    "Intelligence Posts",
    "PPTX Builder",
    "Backlog",
]


class SiteParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.meta_names: dict[str, str] = {}
        self.meta_props: dict[str, str] = {}
        self.nav_links: list[tuple[str, str]] = []
        self.in_title = False
        self.title_text = ""
        self.current_href: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag_name = tag.lower()
        attr_map = {k.lower(): (v or "") for k, v in attrs}
        if tag_name == "meta":
            if "name" in attr_map:
                self.meta_names[attr_map["name"].strip().lower()] = attr_map.get(
                    "content", ""
                ).strip()
            if "property" in attr_map:
                self.meta_props[attr_map["property"].strip().lower()] = attr_map.get(
                    "content", ""
                ).strip()
        elif tag_name == "title":
            self.in_title = True
        elif tag_name == "a":
            self.current_href = attr_map.get("href", "").strip()

    def handle_endtag(self, tag: str) -> None:
        tag_name = tag.lower()
        if tag_name == "title":
            self.in_title = False
        elif tag_name == "a":
            self.current_href = None

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_text += data
        if self.current_href is not None:
            text = data.strip()
            if text:
                self.nav_links.append((text, self.current_href))


def normalize_nav_links(links: list[tuple[str, str]]) -> dict[str, str]:
    normalized: dict[str, str] = {}
    for label, href in links:
        if label in REQUIRED_NAV_LABELS and label not in normalized:
            normalized[label] = href
    return normalized


errors: list[str] = []

for page in SITE_PAGES:
    if not page.exists():
        errors.append(f"Missing required page: {page.relative_to(ROOT)}")
        continue

    parser = SiteParser()
    parser.feed(page.read_text(encoding="utf-8"))

    if not parser.title_text.strip():
        errors.append(f"{page.relative_to(ROOT)}: missing non-empty <title>")

    viewport = parser.meta_names.get("viewport", "")
    if "width=device-width" not in viewport.lower() or "initial-scale" not in viewport.lower():
        errors.append(f"{page.relative_to(ROOT)}: missing responsive viewport meta")

    for required in ("og:title", "og:description", "og:image"):
        if not parser.meta_props.get(required):
            errors.append(f"{page.relative_to(ROOT)}: missing social meta property '{required}'")
    if not parser.meta_names.get("twitter:card"):
        errors.append(f"{page.relative_to(ROOT)}: missing twitter:card meta")

for page in STATUS_PAGES:
    parser = SiteParser()
    parser.feed(page.read_text(encoding="utf-8"))
    nav = normalize_nav_links(parser.nav_links)

    missing_labels = [label for label in REQUIRED_NAV_LABELS if label not in nav]
    if missing_labels:
        errors.append(
            f"{page.relative_to(ROOT)}: missing nav labels: {', '.join(missing_labels)}"
        )

# Backlog discoverability checks
for required_source in [
    ROOT / "index.html",
    ROOT / "intelligence-editor.html",
    ROOT / "status-site" / "intelligence.html",
    ROOT / "status-site" / "pptx-builder.html",
]:
    parser = SiteParser()
    parser.feed(required_source.read_text(encoding="utf-8"))
    has_backlog_link = any("backlog.html" in href for _, href in parser.nav_links)
    if not has_backlog_link:
        errors.append(
            f"{required_source.relative_to(ROOT)}: missing link to backlog.html"
        )

if errors:
    print("Architecture checks failed:")
    for error in errors:
        print(f"- {error}")
    raise SystemExit(1)

print("Architecture checks passed.")
