#!/usr/bin/env python3

import requests
import feedparser
import re
from datetime import datetime, timedelta
from http.client import RemoteDisconnected

# --- CONFIG ---
DAYS_BACK = 5
CUT_OFF = datetime.now() - timedelta(days=DAYS_BACK)

# Grouped RSS feeds by category
GROUPED_FEEDS = {
    "Weather": [
        "https://weather.gc.ca/rss/city/on-131_e.xml"
    ],
    "International & Canadian News": [
        "http://feeds.reuters.com/Reuters/worldNews",
        "https://rss.cbc.ca/lineup/canada.xml",
        "http://feeds.bbci.co.uk/news/world/rss.xml"
    ],
    "U.S. Top Stories": [
        "https://feeds.npr.org/1001/rss.xml",
        "https://rss.cnn.com/rss/cnn_topstories.rss"
    ],
    "Artificial Intelligence & Digital Strategy": [
        "https://openai.com/blog/rss/",
        "https://feeds.arstechnica.com/arstechnica/technology-policy",
        "https://blogs.gartner.com/smarterwithgartner/feed/"
    ],
    "Public Health & Science": [
        "https://www.who.int/feeds/entity/mediacentre/news/en/rss.xml",
        "https://www.canada.ca/etc/+/health/public-health-updates.rss"
    ],
    "Government & Policy": [
        "https://www.cbc.ca/cmlink/rss-politics",
        "https://gds.blog/feed/"
    ]
}

# Utility functions

def safe_parse(url):
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return feedparser.parse(resp.content)
    except Exception:
        return feedparser.FeedParserDict(entries=[])


def strip_tags(html: str) -> str:
    return re.sub(r'<[^>]+>', '', html or '')


def get_section_items(title, urls, limit=2):
    for url in urls:
        feed = safe_parse(url)
        if feed.entries:
            items = []
            for entry in feed.entries[:limit]:
                text = strip_tags(entry.get('summary', entry.title))
                items.append((entry.title.strip(), text))
            return items
    return []

# Build briefing

def build_briefing():
    today = datetime.now()
    header = [
        f"✅ Morning News Briefing – {today:%B %d, %Y}",
        "",
        f"📅 Date: {today:%Y-%m-%d}",
        "🏷️ Tags: #briefing #ai #publichealth #digitalgov",
        "",
        "⸻",
        ""
    ]
    lines = header
    # Sections
    for section, feeds in GROUPED_FEEDS.items():
        lines.append(f"🌍 {section}") if section == "International & Canadian News" else None
        lines.append(f"🇺🇸 {section}") if section == "U.S. Top Stories" else None
        # generic icon for others
        if section not in ["International & Canadian News", "U.S. Top Stories"]:
            icon = "🧠" if "Intelligence" in section or "AI" in section else "🏥" if "Health" in section else "🧾"
            lines.append(f"{icon} {section}")
        items = get_section_items(section, feeds)
        for title, summary in items:
            lines.append(title)
            lines.append(summary)
            lines.append("")
        lines.append("⸻")
        lines.append("")
    return "\n".join(lines)

# Main

if __name__ == "__main__":
    try:
        briefing = build_briefing()
        with open("latest.txt", "w", encoding="utf-8") as f:
            f.write(briefing)
        print("latest.txt generated successfully.")
    except Exception as e:
        print(f"ERROR generating briefing: {e}")
        with open("latest.txt", "w", encoding="utf-8") as f:
            f.write(f"ERROR generating briefing: {e}\n")
        exit(0)
