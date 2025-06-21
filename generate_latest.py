#!/usr/bin/env python3

import feedparser
import re
from datetime import datetime, timedelta
from http.client import RemoteDisconnected
from transformers import pipeline

# --- CONFIG ---
RSS_FEEDS = [
    ("International", "http://feeds.reuters.com/Reuters/worldNews"),
    ("Canadian",      "https://rss.cbc.ca/lineup/canada.xml"),
    ("US",            "https://feeds.npr.org/1001/rss.xml"),
    ("AI & IT",       "https://feeds.arstechnica.com/arstechnica/technology-policy"),
    ("Public Health", "https://www.canada.ca/content/canadasite.service/feeds/public-health-updates/rss.xml"),
    ("Public Sector AI", "https://www.digital.canada.ca/news-and-announcements/feed/")
]
WEATHER_FEED = "https://dd.weather.gc.ca/rss/city/on-131_e.xml"  # Ottawa
DAYS_BACK = 5

# Initialize summarizer
summarizer = pipeline("summarization")

def safe_parse(url):
    try:
        return feedparser.parse(url)
    except (RemoteDisconnected, Exception):
        return feedparser.FeedParserDict(entries=[], feed={})


def strip_html(text):
    return re.sub(r'<[^>]*>', '', text or '').strip()


def get_weather_summary():
    feed = safe_parse(WEATHER_FEED)
    today = datetime.now().strftime('%B %d, %Y')
    if not feed.entries:
        return f"Ottawa Weather – {today}: data unavailable."
    today_entry = feed.entries[0]
    summary = strip_html(today_entry.summary)
    return f"Ottawa Weather – {today}\n{summary}"


def format_and_summarize(entry):
    content = ''
    if hasattr(entry, 'content') and entry.content:
        content = strip_html(entry.content[0].value)
    else:
        content = strip_html(entry.get('summary', ''))
    # Generate AI summary
    try:
        ai = summarizer(content, max_length=60, min_length=20, do_sample=False)
        summary = ai[0]['summary_text']
    except Exception:
        summary = content[:200] + '...'
    # Citation
    pub = ''
    if entry.get('published_parsed'):
        pub = datetime(*entry.published_parsed[:6]).strftime('%B %d, %Y')
    source = entry.get('source', {}).get('title') or entry.link.split('/')[2]
    link = entry.link
    return f"• {entry.title.strip()}\n  {summary}\n  Link: {link} {{{pub} ({source})}}"


def collect_multiday_briefing():
    cutoff = datetime.now() - timedelta(days=DAYS_BACK)
    stories = []
    # Gather entries
    for label, url in RSS_FEEDS:
        feed = safe_parse(url)
        for entry in feed.entries:
            if not entry.get('published_parsed'):
                continue
            pub_date = datetime(*entry.published_parsed[:6])
            if pub_date >= cutoff:
                stories.append((pub_date, label, entry))
    # Sort by date descending
    stories.sort(key=lambda x: x[0], reverse=True)
    # Group by date
    grouped = {}
    for pub_date, label, entry in stories:
        day = pub_date.strftime('%B %d, %Y')
        grouped.setdefault(day, []).append((label, entry))
    # Build briefing text
    lines = [f"Multi-Day News Briefing – Last {DAYS_BACK} days", "", get_weather_summary(), ""]
    for day, items in grouped.items():
        lines.append(day)
        for label, entry in items:
            lines.append(format_and_summarize(entry))
        lines.append("")
    lines.append("— End of briefing —")
    return "\n".join(lines)


if __name__ == '__main__':
    briefing = collect_multiday_briefing()
    with open('latest.txt', 'w', encoding='utf-8') as f:
        f.write(briefing)
    print('latest.txt updated with multi-day detailed briefing.')