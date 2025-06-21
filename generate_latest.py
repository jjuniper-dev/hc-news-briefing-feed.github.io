#!/usr/bin/env python3

import feedparser
from datetime import datetime
from http.client import RemoteDisconnected

# --- CONFIG ---
RSS_FEEDS = [
    ("International", "http://feeds.reuters.com/Reuters/worldNews"),
    ("National", "https://rss.cbc.ca/lineup/canada.xml"),
    ("US", "https://feeds.npr.org/1001/rss.xml"),
    ("AI & IT", "https://feeds.arstechnica.com/arstechnica/technology-policy"),
    ("AI & IT", "https://www.theregister.com/headlines.atom"),
]
WEATHER_FEED = "https://dd.weather.gc.ca/rss/city/on-118_e.xml"  # Ottawa

# --- HELPER FUNCTIONS ---
def safe_parse(url):
    """
    Parse an RSS feed URL safely, returning an empty feed if errors occur.
    """
    try:
        return feedparser.parse(url)
    except RemoteDisconnected:
        return feedparser.FeedParserDict(entries=[], feed={})
    except Exception:
        return feedparser.FeedParserDict(entries=[], feed={})


# --- CONTENT GENERATION ---
def get_weather_summary():
    feed = safe_parse(WEATHER_FEED)
    if not feed.entries:
        return f"Ottawa Weather – {datetime.now():%B %d, %Y}: Data unavailable."
    today = feed.entries[0]
    tomorrow = feed.entries[1] if len(feed.entries) > 1 else None
    today_text = f"{today.title}: {getattr(today, 'summary', '').strip()}"
    tomorrow_text = f"{tomorrow.title}: {getattr(tomorrow, 'summary', '').strip()}" if tomorrow else ""
    header = f"Ottawa Weather – {datetime.now():%B %d, %Y}"
    return "\n".join([header, today_text, f"Tomorrow: {tomorrow_text}"])


def format_entry(entry):
    # Prefer full content if available
    text = ''
    if hasattr(entry, 'content') and entry.content:
        text = entry.content[0].value.strip()
    else:
        text = getattr(entry, 'summary', '').strip()
    # Publication date
    if hasattr(entry, 'published_parsed') and entry.published_parsed:
        pub = datetime(*entry.published_parsed[:6]).strftime('%B %d, %Y')
    else:
        pub = ''
    # Source name
    src = ''
    if hasattr(entry, 'source') and entry.source:
        src = getattr(entry.source, 'title', '')
    if not src:
        try:
            src = entry.link.split('/')[2]
        except Exception:
            src = ''
    title = getattr(entry, 'title', '').strip()
    return f"• {title}\n  {text} {{{pub} ({src})}}"


def collect_briefing():
    parts = []
    # Weather
    parts.append(get_weather_summary())
    parts.append("")
    # News sections
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
    print('latest.txt updated with full content.')