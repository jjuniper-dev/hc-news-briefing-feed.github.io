#!/usr/bin/env python3

import feedparser
import re
from datetime import datetime, timedelta
from http.client import RemoteDisconnected
from transformers import pipeline

# --- CONFIG ---
# Number of days to include in multi-day briefing
DAYS_BACK = 5
# RSS feeds list: label and URL
RSS_FEEDS = [
    ("International", "http://feeds.reuters.com/Reuters/worldNews"),
    ("Canadian",      "https://rss.cbc.ca/lineup/canada.xml"),
    ("US",            "https://feeds.npr.org/1001/rss.xml"),
    ("AI & IT",       "https://feeds.arstechnica.com/arstechnica/technology-policy"),
    ("AI & IT",       "https://www.theregister.com/headlines.atom"),
    ("Public Health", "https://www.canada.ca/etc/+/health/public-health-updates.rss"),
    ("Digital Gov",   "https://open.canada.ca/data/en/dataset/f5fb5b90-cdc1-4cb7-b774-62f30d0cebb1.atom"),
    ("Enterprise Arch", "https://www.opengroup.org/news/rss/news-release.xml"),
    ("Gartner",       "http://blogs.gartner.com/gbn/feed/"),
    ("Gartner",       "https://blogs.gartner.com/smarterwithgartner/feed/"),
    ("Global Health", "https://www.who.int/feeds/entity/mediacentre/news/en/rss.xml"),
    ("Nature PH",     "https://www.nature.com/subjects/public-health.rss"),
    ("UK GDS",        "https://gds.blog/feed/"),
    ("OECD Gov",      "https://oecd-rss.org/publications/digital-government-rss.xml"),
    ("CIO Gov",       "https://www.cio.com/ciolib/rss/cio/government.xml"),
    ("MIT AI",        "https://www.technologyreview.com/feed/"),
    ("AI Weekly",     "http://aiweekly.co/rss"),
    ("VB AI",         "https://venturebeat.com/category/ai/feed/"),
    ("Cybersec",      "https://krebsonsecurity.com/feed/"),
    ("NIST News",     "https://www.nist.gov/blogs/blog.rss"),
]
# Weather feed
WEATHER_FEED = "https://weather.gc.ca/rss/city/on-131_e.xml"

# Initialize AI summarizer
summarizer = pipeline("summarization")

# Helpers
def strip_html(text):
    return re.sub(r'<[^>]+>', '', text)

def safe_parse(url):
    try:
        return feedparser.parse(url)
    except (RemoteDisconnected, Exception):
        return []

# Summarization function
def ai_summary(text: str) -> str:
    prompt = strip_html(text)
    result = summarizer(prompt, max_length=120, min_length=40, do_sample=False)
    return result[0]['summary_text'].strip()

# Collect multi-day briefing
def collect_multi_day():
    cutoff = datetime.now() - timedelta(days=DAYS_BACK)
    entries = []
    # Weather section
    weather = safe_parse(WEATHER_FEED)
    if weather and weather.entries:
        entries.append((datetime.now(), "Weather", f"Ottawa Weather: {strip_html(weather.entries[0].summary)}"))
    # News sections
    for label, url in RSS_FEEDS:
        feed = safe_parse(url)
        for e in getattr(feed, 'entries', []):
            if 'published_parsed' in e:
                pub = datetime(*e.published_parsed[:6])
                if pub >= cutoff:
                    entries.append((pub, label, e))
    # Sort by date desc
    entries.sort(key=lambda x: x[0], reverse=True)
    # Group by date
    days = {}
    for pub, label, e in entries:
        date_str = pub.strftime('%B %d, %Y')
        days.setdefault(date_str, []).append((label, e))
    # Build output
    lines = [f"Multi-day Briefing (Last {DAYS_BACK} days)"]
    for day, items in days.items():
        lines.append(f"\n{day}")
        for label, e in items:
            text = e.content[0].value if 'content' in e and e.content else e.summary
            summary = ai_summary(text)
            lines.append(f"• [{label}] {e.title}\n  {summary}")
    return '\n'.join(lines)

# Main
if __name__ == '__main__':
    briefing = collect_multi_day()
    with open('latest.txt', 'w', encoding='utf-8') as f:
        f.write(briefing)
    print('latest.txt updated.')