#!/usr/bin/env python3

import feedparser
import re
from datetime import datetime, timedelta
from http.client import RemoteDisconnected
from transformers import pipeline

# --- CONFIG ---
DAYS_BACK = 5
CUT_OFF = datetime.now() - timedelta(days=DAYS_BACK)

# Ordered sections with their RSS feeds
GROUPED_FEEDS = {
    "Weather": [
        "https://weather.gc.ca/rss/city/on-131_e.xml"
    ],
    "Canadian CBC": [
        "https://rss.cbc.ca/lineup/canada.xml"
    ],
    "Canadian CTV": [
        "https://www.ctvnews.ca/rss/ctvnews-ca-canada-public-rss.xml"
    ],
    "U.S.": [
        "https://feeds.npr.org/1001/rss.xml"
    ],
    "International": [
        "http://feeds.reuters.com/Reuters/worldNews"
    ],
    # Special sections (one-liners)
    "Public Health": ["https://www.canada.ca/etc/+/health/public-health-updates.rss"],
    "AI & Emerging Tech": [
        "https://feeds.arstechnica.com/arstechnica/technology-policy"    ],
    "Cybersecurity": ["https://krebsonsecurity.com/feed/"],
    "Enterprise Architecture": ["https://www.opengroup.org/news/rss/news-release.xml"],
    "Geomatics": ["https://www.gstb.ca/rss-feed"],  # example geomatics feed
}

# Initialize summarizer once
tokenizer = pipeline("summarization")


def safe_parse(url):
    try:
        return feedparser.parse(url)
    except Exception:
        return feedparser.FeedParserDict(entries=[])


def strip_tags(html: str) -> str:
    return re.sub(r'<[^>]+>', '', html or '')


def clean_text(text: str) -> str:
    text = re.sub(r"【Image.*?】", "", text)
    text = re.sub(r"\(Image credit:.*?\)", "", text)
    text = re.sub(r"^####.*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n{2,}", "\n\n", text)
    return " ".join(line.strip() for line in text.splitlines() if line.strip())


def ai_summary(text: str) -> str:
    words = text.split()
    if len(words) < 50:
        return text
    max_len = min(len(words)//2, 60)
    try:
        out = tokenizer(text, max_length=max_len, min_length=20, do_sample=False)
        return out[0]["summary_text"].strip()
    except Exception:
        return text


def get_weather():
    feed = safe_parse(GROUPED_FEEDS["Weather"][0])
    if not feed.entries:
        return "Ottawa Weather data unavailable."
    ent = feed.entries[0]
    summary = strip_tags(ent.summary)
    lines = summary.split('</br>') if '</br>' in summary else summary.split('\n')
    today = clean_text(lines[0]) if lines else clean_text(summary)
    tomorrow = clean_text(lines[1]) if len(lines)>1 else ''
    return f"Ottawa Weather – {datetime.now():%B %d, %Y}\n• {today}\n• {tomorrow}"


def fetch_top(section, count=2):
    items = []
    urls = GROUPED_FEEDS.get(section, [])
    if not urls:
        return items
    feed = safe_parse(urls[0])
    for e in feed.entries[:count]:
        date = datetime(*e.published_parsed[:6]).strftime('%b %d') if 'published_parsed' in e else ''
        raw = strip_tags(e.content[0].value if hasattr(e,'content') and e.content else e.summary)
        summary = ai_summary(raw)
        items.append((e.title.strip(), clean_text(summary), date))
    return items


def collect_briefing():
    parts = []
    # Weather
    parts.append(get_weather())
    parts.append("")
    # Canadian CBC and CTV
    parts.append("CANADIAN HEADLINES")
    for section in ["Canadian CBC", "Canadian CTV"]:
        tops = fetch_top(section, count=2)
        for title, summ, date in tops:
            parts.append(f"• {title} ({date})\n  {summ}")
    parts.append("")
    # US
    parts.append("U.S. HEADLINES")
    for title, summ, date in fetch_top("U.S.",2):
        parts.append(f"• {title} ({date})\n  {summ}")
    parts.append("")
    # International
    parts.append("INTERNATIONAL HEADLINES")
    for title, summ, date in fetch_top("International",2):
        parts.append(f"• {title} ({date})\n  {summ}")
    parts.append("")
    # Special one-liners
    parts.append("SPECIAL SECTIONS")
    for section in ["Public Health","AI & Emerging Tech","Cybersecurity","Enterprise Architecture","Geomatics"]:
        urls = GROUPED_FEEDS.get(section, [])
        if not urls: continue
        feed = safe_parse(urls[0])
        if feed.entries:
            e = feed.entries[0]
            parts.append(f"• [{section}] {e.title.strip()}")
    parts.append("")
    parts.append("— End of briefing —")
    return "\n".join(parts)

if __name__ == '__main__':
    try:
        txt = collect_briefing()
        with open('latest.txt','w',encoding='utf-8') as f:
            f.write(txt)
        print('latest.txt updated.')
    except Exception as e:
        print(f"⚠️ ERROR: {e}")
        with open('latest.txt','w') as f:
            f.write(f"⚠️ Daily briefing failed: {e}\n")
```