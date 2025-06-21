#!/usr/bin/env python3

import feedparser
import re
from datetime import datetime
from http.client import RemoteDisconnected

# --- CONFIG ---
RSS_FEEDS = [
    ("International", "http://feeds.reuters.com/Reuters/worldNews"),
    ("National",      "https://rss.cbc.ca/lineup/canada.xml"),
    ("US",            "https://feeds.npr.org/1001/rss.xml"),
    ("AI & IT",       "https://feeds.arstechnica.com/arstechnica/technology-policy"),
    ("AI & IT",       "https://www.theregister.com/headlines.atom"),
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


def strip_html(text: str) -> str:
    # Remove HTML tags
    clean = re.sub(r'<[^>]+>', '', text)
    # Unescape HTML entities if needed
    return clean.replace('&nbsp;', ' ').replace('&amp;', '&').strip()

# --- FUNCTIONS ---

def get_weather_summary() -> str:
    feed = safe_parse(WEATHER_FEED)
    if not feed.entries:
        return f"Ottawa Weather – {datetime.now():%B %d, %Y}: Data unavailable."
    today = feed.entries[0]
    tomorrow = feed.entries[1] if len(feed.entries) > 1 else None
    today_text = strip_html(today.summary)
    tomorrow_text = strip_html(tomorrow.summary) if tomorrow else ""
    header = f"Ottawa Weather – {datetime.now():%B %d, %Y}"
    return f"{header}\n{today.title}: {today_text}\nTomorrow: {tomorrow_text}"


def format_entry(entry) -> str:
    # Prefer full content if provided, otherwise summary
    if hasattr(entry, 'content') and entry.content:
        raw = entry.content[0].value
    else:
        raw = entry.get('summary', '')
    text = strip_html(raw)
    # Publication date
    if 'published_parsed' in entry and entry.published_parsed:
        pub = datetime(*entry.published_parsed[:6]).strftime("%B %d, %Y")
    else:
        pub = ''
    # Source name
    source = entry.get('source', {}).get('title', '') or entry.link.split('/')[2]
    title = strip_html(entry.title)
    return f"• {title}\n  {text} {{{pub} ({source})}}"


def collect_briefing() -> str:
    parts = []
    # 1) Weather
    parts.append(get_weather_summary())
    parts.append("")

    # 2) News sections
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
    return "\n\n".join(parts)


# --- MAIN ---
if __name__ == '__main__':
    briefing = collect_briefing()
    with open('latest.txt', 'w', encoding='utf-8') as f:
        f.write(briefing)
    print('latest.txt updated with cleaned content.')