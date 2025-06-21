#!/usr/bin/env python3

import feedparser
import re
from datetime import datetime, timedelta
from http.client import RemoteDisconnected
from transformers import pipeline

# --- CONFIG ---
DAYS_BACK = 5
CUT_OFF = datetime.now() - timedelta(days=DAYS_BACK)

# RSS feeds to include (last 5 days)
RSS_FEEDS = [
    ("International", "http://feeds.reuters.com/Reuters/worldNews"),
    ("Canadian",      "https://rss.cbc.ca/lineup/canada.xml"),
    ("US",            "https://feeds.npr.org/1001/rss.xml"),
    ("AI & IT",       "https://feeds.arstechnica.com/arstechnica/technology-policy"),
    ("AI & IT",       "https://www.theregister.com/headlines.atom"),
    ("PHAC Public Health", "https://www.canada.ca/content/canadasite/en/services/health/public-health-agency/news/updates.rss"),
    ("Digital Government", "https://open.canada.ca/data/en/dataset/6efa4955-.../rss.xml"),
    ("Gartner",        "http://blogs.gartner.com/gbn/feed/"),
    ("Gartner",        "https://blogs.gartner.com/smarterwithgartner/feed/"),
    ("WHO News",       "https://www.who.int/feeds/entity/mediacentre/news/en/rss.xml"),
    ("Nature Public Health", "https://www.nature.com/subjects/public-health.rss"),
    ("GDS Blog",       "https://gds.blog/feed/"),
    ("OECD Digital Gov", "https://oecd-rss.org/publications/digital-government-rss.xml"),
    ("Open Group",     "https://www.opengroup.org/news/rss/news-release.xml"),
    ("CIO Gov",        "https://www.cio.com/ciolib/rss/cio/government.xml"),
    ("MIT Tech Review AI", "https://www.technologyreview.com/feed/"),
    ("AI Weekly",      "http://aiweekly.co/rss"),
    ("VentureBeat AI", "https://venturebeat.com/category/ai/feed/"),
    ("Krebs on Security","https://krebsonsecurity.com/feed/"),
    ("NIST News",      "https://www.nist.gov/blogs/blog.rss"),
]

# Initialize summarizer once
summarizer = pipeline("summarization")

# Utility: strip HTML tags
TAG_RE = re.compile(r'<[^>]+>')
def clean_html(text: str) -> str:
    return TAG_RE.sub('', text)

def safe_parse(url):
    try:
        return feedparser.parse(url)
    except RemoteDisconnected:
        print(f"Warning: RemoteDisconnected for {url}")
        return feedparser.FeedParserDict(entries=[])
    except Exception as e:
        print(f"Warning: Failed to parse {url}: {e}")
        return feedparser.FeedParserDict(entries=[])

# Summarize text via AI
def ai_summarize(text: str) -> str:
    try:
        out = summarizer(text, max_length=120, min_length=40, do_sample=False)
        return out[0]['summary_text'].replace('\n', ' ').strip()
    except Exception as e:
        print(f"Warning: summarization failed: {e}")
        return text[:200] + '...'

# Main: collect multi-day briefing
def collect_briefing() -> str:
    entries = []
    for label, url in RSS_FEEDS:
        feed = safe_parse(url)
        for entry in feed.entries:
            if not hasattr(entry, 'published_parsed') or not entry.published_parsed:
                continue
            pub_date = datetime(*entry.published_parsed[:6])
            if pub_date < CUT_OFF:
                continue
            text = ''
            if hasattr(entry, 'content') and entry.content:
                text = entry.content[0].value
            elif 'summary' in entry:
                text = entry.summary
            clean = clean_html(text)
            summary = ai_summarize(clean)
            entries.append((pub_date, label, entry.title, summary))

    # sort by date desc
    entries.sort(key=lambda x: x[0], reverse=True)

    # group by date
    grouped = {}
    for pub_date, label, title, summary in entries:
        day = pub_date.strftime('%B %d, %Y')
        grouped.setdefault(day, []).append((label, title, summary))

    # build output
    lines = [f"Multi-Day News Briefing (Last {DAYS_BACK} days)", '']
    for day, items in grouped.items():
        lines.append(day)
        for label, title, summary in items:
            lines.append(f"• [{label}] {title}")
            lines.append(f"  {summary}")
        lines.append('')
    lines.append('— End of briefing —')
    return '\n'.join(lines)

if __name__ == '__main__':
    try:
        text = collect_briefing()
        with open('latest.txt', 'w', encoding='utf-8') as f:
            f.write(text)
        print('latest.txt updated successfully.')
    except Exception as e:
        msg = f"⚠️ ERROR: {type(e).__name__}: {e}"
        print(msg)
        with open('latest.txt', 'w', encoding='utf-8') as f:
            f.write('⚠️ Daily briefing failed to generate.\n')
            f.write(msg + '\n')
        exit(0)