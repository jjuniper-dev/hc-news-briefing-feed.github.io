#!/usr/bin/env python3

import feedparser
import re
from datetime import datetime
from http.client import RemoteDisconnected
from transformers import pipeline

# --- CONFIG ---
RSS_FEEDS = [
    ("International", "http://feeds.reuters.com/Reuters/worldNews"),
    ("National",      "https://rss.cbc.ca/lineup/canada.xml"),
    ("US",            "https://feeds.npr.org/1001/rss.xml"),
    ("AI & IT",       "https://feeds.arstechnica.com/arstechnica/technology-policy"),
    ("AI & IT",       "https://www.theregister.com/headlines.atom"),
]
WEATHER_FEED = "https://dd.weather.gc.ca/rss/city/on-131_e.xml"

# Initialize summarizer (Hugging Face Transformers)
summarizer = pipeline("summarization")

# Utility to strip HTML tags
def strip_tags(html: str) -> str:
    return re.sub(r'<[^>]+>', '', html)

# Safe parse with error handling
def safe_parse(url):
    try:
        return feedparser.parse(url)
    except (RemoteDisconnected, Exception):
        return feedparser.FeedParserDict(entries=[], feed={})

# Get weather summary
def get_weather_summary() -> str:
    feed = safe_parse(WEATHER_FEED)
    if not feed.entries:
        return f"Ottawa Weather – {datetime.now():%B %d, %Y}: Data unavailable."
    today = feed.entries[0]
    tomorrow = feed.entries[1] if len(feed.entries) > 1 else None
    today_text = strip_tags(today.summary)
    tomorrow_text = strip_tags(tomorrow.summary) if tomorrow else ""
    header = f"Ottawa Weather – {datetime.now():%B %d, %Y}"
    return "\n".join([header, today_text, f"Tomorrow: {tomorrow_text}"])

# Summarize and format an entry
def format_entry(entry) -> str:
    text = ""
    if hasattr(entry, "content") and entry.content:
        text = entry.content[0].value
    else:
        text = entry.get("summary", "")
    text = strip_tags(text)
    # Use AI summarizer for a concise summary
    try:
        summary = summarizer(text, max_length=150, min_length=40)[0]["summary_text"]
    except Exception:
        summary = text[:300] + '...'
    pub = ""
    if entry.get('published_parsed'):
        pub = datetime(*entry.published_parsed[:6]).strftime("%B %d, %Y")
    source = entry.get("source", {}).get("title", entry.link.split("/")[2])
    return f"• {entry.title.strip()}\n  {summary} {{{pub} ({source})}}"

# Collect full briefing
def collect_briefing() -> str:
    parts = [get_weather_summary(), ""]
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

# Main execution
if __name__ == "__main__":
    briefing = collect_briefing()
    with open("latest.txt", "w", encoding="utf-8") as f:
        f.write(briefing)
    print("latest.txt updated with AI-enhanced summaries.")