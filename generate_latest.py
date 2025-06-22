#!/usr/bin/env python3

import feedparser
import re
from datetime import datetime, timedelta
from http.client import RemoteDisconnected

# --- CONFIG ---
DAYS_BACK = 5
CUT_OFF = datetime.now() - timedelta(days=DAYS_BACK)

# RSS Feeds by category (vetted, working URLs)
GROUPED_FEEDS = {
    "Weather": [
        "https://weather.gc.ca/rss/city/on-131_e.xml"
    ],
    "Canadian CBC": [
        "https://www.cbc.ca/cmlink/rss-topstories"
    ],
    "Canadian CTV": [
        "https://www.ctvnews.ca/rss/ctvnews-ca-canada-1.796439"
    ],
    "U.S.": [
        "https://feeds.npr.org/1001/rss.xml"
    ],
    "International": [
        "https://www.reuters.com/world/rss",
        "http://feeds.bbci.co.uk/news/world/rss.xml"
    ],
    "Public Health": [
        "https://www.canada.ca/etc/+/health/public-health-updates.rss"
    ],
    "AI & Emerging Tech": [
        "https://feeds.arstechnica.com/arstechnica/technology-policy",
        "https://www.technologyreview.com/feed/"
    ],
    "Cybersecurity & Privacy": [
        "https://krebsonsecurity.com/feed/"
    ],
    "Enterprise Architecture & IT Governance": [
        "https://www.opengroup.org/news/rss/news-release.xml"
    ],
    "Geomatics": [
        "https://www.geospatialworld.net/feed/"
    ]
}

# Utility functions

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

# Weather parser for Tonight/Tomorrow

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

# Build concise briefing

def collect_briefing():
    parts = []

    # 1. Weather
    parts.append(get_weather_summary())
    parts.append("")

    # 2. Canadian Headlines (CBC + CTV)
    parts.append(f"Canadian Headlines – {datetime.now():%B %d, %Y}")
    for label, key in [("CBC", "Canadian CBC"), ("CTV", "Canadian CTV")]:
        feed = safe_parse(GROUPED_FEEDS[key][0])
        if feed.entries:
            for e in feed.entries[:2]:
                date = datetime(*e.published_parsed[:6]).strftime("%b %d") if 'published_parsed' in e else ""
                parts.append(f"• {label}: {e.title.strip()} ({date})")
        else:
            parts.append(f"• {label}: (no entries)")
    parts.append("")

    # 3. U.S. Top Stories
    parts.append("U.S. Top Stories")
    feed_us = safe_parse(GROUPED_FEEDS["U.S."][0])
    for e in feed_us.entries[:2]:
        parts.append(f"• {e.title.strip()}")
    parts.append("")

    # 4. International Top Stories
    parts.append("International Top Stories")
    for url in GROUPED_FEEDS["International"]:
        feed_intl = safe_parse(url)
        if feed_intl.entries:
            for e in feed_intl.entries[:2]:
                parts.append(f"• {e.title.strip()}")
            break
    else:
        parts.append("(no entries)")
    parts.append("")

    # 5. Special Sections (headline-only)
    for section in ["Public Health", "AI & Emerging Tech", "Cybersecurity & Privacy",
                    "Enterprise Architecture & IT Governance", "Geomatics"]:
        feed = safe_parse(GROUPED_FEEDS[section][0])
        parts.append(section)
        if feed.entries:
            parts.append(f"• {feed.entries[0].title.strip()}")
        else:
            parts.append("(no entries)")
        parts.append("")

    parts.append("— End of briefing —")
    return "\n".join(parts)

# Main execution

if __name__ == "__main__":
    try:
        briefing = collect_briefing()
        with open("latest.txt", "w", encoding="utf-8") as f:
            f.write(briefing)
        print("latest.txt updated successfully.")
    except Exception as e:
        msg = f"ERROR in briefing generation: {type(e).__name__}: {e}"
        print(msg)
        with open("latest.txt", "w", encoding="utf-8") as f:
            f.write("ERROR: Daily briefing failed to generate.\n" + msg + "\n")
        exit(0)