#!/usr/bin/env python3

import requests
import feedparser
import re
from datetime import datetime, timedelta

# --- CONFIG ---
DAYS_BACK = 5
CUT_OFF = datetime.now() - timedelta(days=DAYS_BACK)

# RSS Feeds by category with multiple URLs for fallback
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
        "http://feeds.bbci.co.uk/news/world/rss.xml",
        "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"
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

# HTTP fetch with timeout

def safe_fetch(url):
    try:
        resp = requests.get(url, timeout=20)
        resp.raise_for_status()
        return resp.content
    except Exception:
        return None

# Parse feed content

def parse_feed(url):
    content = safe_fetch(url)
    if content:
        return feedparser.parse(content)
    return feedparser.FeedParserDict(entries=[])

# Get entries for a section, trying each URL

def get_entries(section, limit=1):
    urls = GROUPED_FEEDS.get(section, [])
    for url in urls:
        feed = parse_feed(url)
        if feed.entries:
            return feed.entries[:limit]
    return []

# Strip HTML tags

def strip_tags(html: str) -> str:
    return re.sub(r'<[^>]+>', '', html or '')

# Generate detailed weather summary

def get_weather_summary():
    entries = get_entries("Weather", limit=10)
    if not entries:
        return "Ottawa Weather data unavailable."
    warnings = []
    forecasts = []
    for e in entries:
        title = strip_tags(e.title or "").strip()
        summary = strip_tags(e.summary or "").strip()
        if any(w in title for w in ["WARNING", "WATCH", "ADVISORY"]):
            warnings.append(f"• {title}: {summary}")
        else:
            forecasts.append((title, summary))
    today = datetime.now().strftime('%B %d, %Y')
    lines = [f"Ottawa Weather – {today}"]
    if warnings:
        lines.append("Warnings:")
        lines.extend(warnings)
    # take first three forecasts for today, tomorrow, day after
    labels = ["Today", "Tomorrow", "Day After Tomorrow"]
    for i in range(min(3, len(forecasts))):
        lbl = labels[i]
        t, s = forecasts[i]
        lines.append(f"• {lbl}: {t}. {s}")
    return "\n".join(lines)

# Main briefing assembly

def collect_briefing():
    today = datetime.now()
    parts = []

    # Weather
    parts.append(get_weather_summary())
    parts.append("")

    # Canadian Headlines with fallback BBC Canada
    parts.append(f"Canadian Headlines – {today:%B %d, %Y}")
    cbc = get_entries("Canadian CBC", limit=2)
    ctv = get_entries("Canadian CTV", limit=2)
    if cbc:
        for e in cbc:
            date = datetime(*e.published_parsed[:6]).strftime("%b %d") if 'published_parsed' in e else ""
            parts.append(f"• CBC: {e.title.strip()} ({date})")
    if ctv:
        for e in ctv:
            date = datetime(*e.published_parsed[:6]).strftime("%b %d") if 'published_parsed' in e else ""
            parts.append(f"• CTV: {e.title.strip()} ({date})")
    if not cbc and not ctv:
        bbc = get_entries("Canadian BBC", limit=2)
        if bbc:
            for e in bbc:
                parts.append(f"• BBC Canada: {e.title.strip()}")
        else:
            parts.append("• (No Canadian headlines available)")
    parts.append("")

    # U.S. Top Stories
    parts.append("U.S. Top Stories")
    us = get_entries("U.S.", limit=2)
    for e in us:
        parts.append(f"• {e.title.strip()}")
    parts.append("")

    # International Top Stories
    parts.append("International Top Stories")
    intl = get_entries("International", limit=2)
    for e in intl:
        parts.append(f"• {e.title.strip()}")
    parts.append("")

    # Special Sections
    for section in ["Public Health", "AI & Emerging Tech", "Cybersecurity & Privacy",
                    "Enterprise Architecture & IT Governance", "Geomatics"]:
        entries = get_entries(section, limit=1)
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
        msg = f"ERROR generating briefing: {e}"
        print(msg)
        with open("latest.txt", "w", encoding="utf-8") as f:
            f.write(msg + "\n")
        exit(0)
