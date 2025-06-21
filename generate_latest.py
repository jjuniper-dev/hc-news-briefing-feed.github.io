#!/usr/bin/env python3

import feedparser
import re
from datetime import datetime
from http.client import RemoteDisconnected

# --- CONFIG ---
RSS_FEEDS = [
    ("International", "http://feeds.reuters.com/Reuters/worldNews"),
    ("Canadian",     "https://rss.cbc.ca/lineup/canada.xml"),
    ("US",           "https://feeds.npr.org/1001/rss.xml"),
    ("AI & IT",      "https://feeds.arstechnica.com/arstechnica/technology-policy"),
    ("Public Health", "https://www.canada.ca/content/dam/phac-aspc/rss/new-eng.xml"),
    ("Public Sector AI", "https://open.canada.ca/data/en/dataset.atom.xml")
]
WEATHER_FEED = "https://dd.weather.gc.ca/rss/city/on-131_e.xml"  # Ottawa

# --- HELPERS ---
def safe_parse(url):
    try:
        return feedparser.parse(url)
    except RemoteDisconnected:
        return feedparser.FeedParserDict(entries=[], feed={})
    except Exception:
        return feedparser.FeedParserDict(entries=[], feed={})

def strip_html(text):
    return re.sub(r'<[^>]+>', '', text or '').strip()

# --- SECTION GENERATORS ---
def get_weather_summary():
    feed = safe_parse(WEATHER_FEED)
    if not feed.entries:
        return f"Ottawa Weather – {datetime.now():%B %d, %Y}: Data unavailable."
    today = feed.entries[0]
    tomorrow = feed.entries[1] if len(feed.entries) > 1 else None
    header = f"Ottawa Weather – {datetime.now():%B %d, %Y}"
    today_text = strip_html(today.summary)
    tomorrow_text = strip_html(tomorrow.summary) if tomorrow else ""
    return f"{header}\n• Today: {today_text}\n• Tomorrow: {tomorrow_text}"

# --- ENTRY FORMATTER ---
def format_entry(entry):
    content = entry.get('content', [{}])[0].get('value', '')
    summary = entry.get('summary', '')
    text = strip_html(content) if content else strip_html(summary)
    pub = ''
    if 'published_parsed' in entry and entry.published_parsed:
        pub = datetime(*entry.published_parsed[:6]).strftime("%B %d, %Y")
    source = entry.get('source', {}).get('title', '') or entry.link.split('/')[2]
    title = entry.title.strip()
    link = entry.link
    lines = [f"• {title} {{{pub} ({source})}}", f"  {text}", f"  Link: {link}"]
    return "\n".join(lines)

# --- MAIN ---
def collect_briefing():
    parts = []
    # Weather
    parts.append(get_weather_summary())
    parts.append("")
    # News
    for label, url in RSS_FEEDS:
        feed = safe_parse(url)
        entries = feed.entries[:2]
        if not entries:
            continue
        parts.append(f"{label.upper()} HEADLINES")
        for e in entries:
            parts.append(format_entry(e))
        parts.append("")
    parts.append("— End of briefing —")
    return "\n".join(parts)

if __name__ == '__main__':
    briefing = collect_briefing()
    with open("latest.txt", "w", encoding="utf-8") as f:
        f.write(briefing)
    print("latest.txt updated with detailed content.")