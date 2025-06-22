#!/usr/bin/env python3

import feedparser
import re
from datetime import datetime, timedelta
from http.client import RemoteDisconnected

# --- CONFIG ---
DAYS_BACK = 3
CUT_OFF = datetime.now() - timedelta(days=DAYS_BACK)

GROUPED_FEEDS = {
    "Weather": [
        "https://weather.gc.ca/rss/city/on-131_e.xml"
    ],
    "Canadian CBC": [
        "https://rss.cbc.ca/lineup/canada.xml"
    ],
    "Canadian CTV": [
        "https://www.ctvnews.ca/rss/ctvnews-ca-top-stories-public-rss-1.2170494"
    ],
    "U.S.": [
        "https://feeds.npr.org/1001/rss.xml"
    ],
    "International": [
        "https://feeds.reuters.com/Reuters/worldNews",
        "https://feeds.bbci.co.uk/news/world/rss.xml"
    ],
    "Public Health": [
        "https://www.canada.ca/etc/+/health/public-health-updates.rss"
    ],
    "AI & Emerging Tech": [
        "https://feeds.arstechnica.com/arstechnica/technology-policy"
    ],
    "Cybersecurity & Privacy": [
        "https://krebsonsecurity.com/feed/"
    ],
    "Enterprise Architecture & IT Governance": [
        "https://www.opengroup.org/news/rss/news-release.xml"
    ],
    "Geomatics": [
        "https://example.com/geomatics-feed.xml"
    ]
}


def safe_parse(url):
    try:
        feed = feedparser.parse(url)
        if getattr(feed, 'bozo', False):
            print(f"Warning: malformed feed at {url}, bozo_exception={feed.get('bozo_exception')}")
        return feed
    except RemoteDisconnected:
        print(f"Warning: disconnected from {url}")
        return feedparser.FeedParserDict(entries=[])
    except Exception as e:
        print(f"Warning: failed to parse {url}: {e}")
        return feedparser.FeedParserDict(entries=[])


def get_first_entries(key, count=2):
    # Try each URL until we get entries
    for url in GROUPED_FEEDS[key]:
        feed = safe_parse(url)
        if feed.entries:
            return feed.entries[:count]
    print(f"Warning: no entries found for {key}")
    return []


def strip_tags(html: str) -> str:
    return re.sub(r'<[^>]+>', '', html or '')


def get_weather_summary():
    feed = safe_parse(GROUPED_FEEDS["Weather"][0])
    if not feed.entries:
        return "Ottawa Weather data unavailable."
    tonight = tomorrow = None
    for e in feed.entries[:5]:
        title = strip_tags(e.title or "")
        if "Tonight" in title:
            tonight = title
        if "Tomorrow" in title or "High" in title:
            tomorrow = title
        if tonight and tomorrow:
            break
    tonight = tonight or strip_tags(feed.entries[0].title)
    tomorrow = tomorrow or (strip_tags(feed.entries[1].title) if len(feed.entries) > 1 else "")
    header = f"Ottawa Weather – {datetime.now():%B %d, %Y}"
    lines = [header, f"• Tonight: {tonight}"]
    if tomorrow:
        lines.append(f"• Tomorrow: {tomorrow}")
    return "\n".join(lines)


def collect_briefing():
    parts = []

    # 1. Weather
    parts.append(get_weather_summary())
    parts.append("")

    # 2. Canadian Headlines
    parts.append(f"Canadian Headlines – {datetime.now():%B %d, %Y}")
    for label, key in [("CBC", "Canadian CBC"), ("CTV", "Canadian CTV")]:
        entries = get_first_entries(key, count=2)
        for e in entries:
            date = ""
            if 'published_parsed' in e:
                date = datetime(*e.published_parsed[:6]).strftime("%b %d")
            parts.append(f"• {label}: {e.title.strip()} ({date})")
    parts.append("")

    # 3. U.S. Top Stories
    parts.append("U.S. Top Stories")
    for e in get_first_entries("U.S.", count=2):
        parts.append(f"• {e.title.strip()}")
    parts.append("")

    # 4. International Top Stories
    parts.append("International Top Stories")
    for e in get_first_entries("International", count=2):
        parts.append(f"• {e.title.strip()}")
    parts.append("")

    # 5. Special Sections
    for section in ["Public Health", "AI & Emerging Tech", "Cybersecurity & Privacy",
                    "Enterprise Architecture & IT Governance", "Geomatics"]:
        entries = get_first_entries(section, count=1)
        if entries:
            parts.append(section)
            parts.append(f"• {entries[0].title.strip()}")
            parts.append("")

    parts.append("— End of briefing —")
    return "\n".join(parts)


if __name__ == "__main__":
    try:
        briefing = collect_briefing()
        with open("latest.txt", "w", encoding="utf-8") as f:
            f.write(briefing)
        print("latest.txt updated successfully.")
    except Exception as e:
        msg = f"⚠️ ERROR in briefing generation: {type(e).__name__}: {e}"
        print(msg)
        with open("latest.txt", "w", encoding="utf-8") as f:
            f.write("⚠️ Daily briefing failed to generate.\n")
            f.write(msg + "\n")
        exit(0)
```  

This version tries each feed URL until it finds entries, adds fallback BBC for international, and logs warnings if none found. Copy it into `generate_latest.py` and rerun—your Canadian and International sections should now always populate correctly.