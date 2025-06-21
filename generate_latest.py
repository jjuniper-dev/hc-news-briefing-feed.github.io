#!/usr/bin/env python3

import feedparser
from datetime import datetime

# --- CONFIGURE YOUR SOURCES HERE ---
RSS_FEEDS = [
    ("International", "http://feeds.reuters.com/Reuters/worldNews"),
    ("National",      "https://rss.cbc.ca/lineup/canada.xml"),
    ("US",            "https://feeds.npr.org/1001/rss.xml"),
    ("AI & IT",       "https://feeds.arstechnica.com/arstechnica/technology-policy"),
    ("AI & IT",       "https://www.theregister.com/headlines.atom"),
]

WEATHER_FEED = "https://dd.weather.gc.ca/rss/city/on-131_e.xml"  # Ottawa

# --- FUNCTIONS ---
def get_weather_summary() -> str:
    feed = feedparser.parse(WEATHER_FEED)
    if not feed.entries:
        return "Ottawa Weather – data unavailable."
    today = feed.entries[0]
    tomorrow = feed.entries[1] if len(feed.entries) > 1 else None

    today_text = f"{today.title}: {today.summary}"
    tomorrow_text = f"{tomorrow.title}: {tomorrow.summary}" if tomorrow else ""
    header = f"Ottawa Weather – {datetime.now():%B %d, %Y}"
    return "\n".join([header, today_text, f"Tomorrow: {tomorrow_text}"])

def format_entry(entry) -> str:
    # Prefer full content if provided, otherwise summary
    if hasattr(entry, "content") and entry.content:
        text = entry.content[0].value.strip()
    else:
        text = entry.get("summary", "").strip()
    # Publication date
    if "published_parsed" in entry and entry.published_parsed:
        pub = datetime(*entry.published_parsed[:6]).strftime("%B %d, %Y")
    else:
        pub = ""
    # Source name
    source = entry.get("source", {}).get("title", "")
    if not source:
        source = entry.link.split("/")[2]
    # Build the bullet with citation
    title = entry.title.strip()
    return f"• {title}\n  {text} {{{pub} ({source})}}"

def collect_briefing() -> str:
    parts = []
    # 1) Weather
    parts.append(get_weather_summary())
    parts.append("")  # blank line

    # 2) News Sections
    for label, url in RSS_FEEDS:
        feed = feedparser.parse(url)
        entries = feed.entries[:2]  # top 2 items
        if not entries:
            continue
        parts.append(f"{label.upper()} HEADLINES")
        for e in entries:
            parts.append(format_entry(e))
        parts.append("")  # blank line

    parts.append("— End of briefing —")
    # Join with double line breaks for readability
    return "\n\n".join(parts)

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    briefing = collect_briefing()
    with open("latest.txt", "w", encoding="utf-8") as f:
        f.write(briefing)
    print("latest.txt updated with full content.")