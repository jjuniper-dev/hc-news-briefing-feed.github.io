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
        "https://www.theglobeandmail.com/canada/toronto/feed/"
    ],
    "U.S.": [
        "https://feeds.npr.org/1001/rss.xml"
    ],
    "International": [
        "http://feeds.reuters.com/Reuters/worldNews"
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
        "https://example.com/geomatics-feed.xml"  # replace with a real Geomatics RSS
    ]
}

def safe_parse(url):
    try:
        return feedparser.parse(url)
    except RemoteDisconnected:
        print(f"Warning: disconnected from {url}")
        return feedparser.FeedParserDict(entries=[])
    except Exception as e:
        print(f"Warning: failed to parse {url}: {e}")
        return feedparser.FeedParserDict(entries=[])

def strip_tags(html: str) -> str:
    return re.sub(r'<[^>]+>', '', html or '')

def get_weather_summary():
    feed = safe_parse(GROUPED_FEEDS["Weather"][0])
    if not feed.entries:
        return "Ottawa Weather data unavailable."
    # Assume first entry = Tonight, second = Tomorrow
    tonight = strip_tags(feed.entries[0].title)
    tomorrow = strip_tags(feed.entries[1].title) if len(feed.entries) > 1 else ""
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

    # 2. Canadian Headlines (CBC + CTV)
    parts.append(f"Canadian Headlines – {datetime.now():%B %d, %Y}")
    for label, key in [("CBC", "Canadian CBC"), ("Global/CTV", "Canadian CTV")]:
        feed = safe_parse(GROUPED_FEEDS[key][0])
        for e in feed.entries[:2]:
            date = ""
            if 'published_parsed' in e:
                date = datetime(*e.published_parsed[:6]).strftime("%b %d")
            parts.append(f"• {label}: {e.title.strip()} ({date})")
    parts.append("")

    # 3. U.S. Top Stories
    parts.append("U.S. Top Stories")
    us = safe_parse(GROUPED_FEEDS["U.S."][0])
    for e in us.entries[:2]:
        parts.append(f"• {e.title.strip()}")
    parts.append("")

    # 4. International Top Stories
    parts.append("International Top Stories")
    intl = safe_parse(GROUPED_FEEDS["International"][0])
    for e in intl.entries[:2]:
        parts.append(f"• {e.title.strip()}")
    parts.append("")

    # 5. Special Sections (headline-only, one each)
    for section in ["Public Health", "AI & Emerging Tech", "Cybersecurity & Privacy",
                    "Enterprise Architecture & IT Governance", "Geomatics"]:
        feed = safe_parse(GROUPED_FEEDS[section][0])
        if feed.entries:
            parts.append(section)
            parts.append(f"• {feed.entries[0].title.strip()}")
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