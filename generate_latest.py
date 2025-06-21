#!/usr/bin/env python3

import feedparser
import re
from datetime import datetime, timedelta
from http.client import RemoteDisconnected
from transformers import pipeline

# --- CONFIG ---
DAYS_BACK = 5
CUT_OFF = datetime.now() - timedelta(days=DAYS_BACK)

# Grouped RSS feeds by section
GROUPED_FEEDS = {
    "Weather": [
        "https://weather.gc.ca/rss/city/on-131_e.xml"
    ],
    "International": [
        "http://feeds.reuters.com/Reuters/worldNews"
    ],
    "Canadian": [
        "https://rss.cbc.ca/lineup/canada.xml"
    ],
    "US": [
        "https://feeds.npr.org/1001/rss.xml"
    ],
    "Public Health": [
        "https://www.canada.ca/etc/+/health/public-health-updates.rss"
    ],
    "Public Sector AI": [
        "https://open.canada.ca/data/en/dataset/f5fb5b90/resource/4cb7fb774/feed.xml"
    ],
    "Gartner": [
        "http://blogs.gartner.com/gbn/feed/",
        "https://blogs.gartner.com/smarterwithgartner/feed/"
    ],
    "Global Health & Science": [
        "https://www.who.int/feeds/entity/mediacentre/news/en/rss.xml",
        "https://www.nature.com/subjects/public-health.rss"
    ],
    "Digital Government & Policy": [
        "https://gds.blog/feed/",
        "https://oecd-rss.org/publications/digital-government-rss.xml"
    ],
    "Enterprise Architecture & IT Governance": [
        "https://www.opengroup.org/news/rss/news-release.xml",
        "https://www.cio.com/ciolib/rss/cio/government.xml"
    ],
    "AI & Emerging Tech": [
        "https://www.technologyreview.com/feed/",
        "http://aiweekly.co/rss",
        "https://venturebeat.com/category/ai/feed/"
    ],
    "Cybersecurity & Privacy": [
        "https://krebsonsecurity.com/feed/",
        "https://www.nist.gov/blogs/blog.rss"
    ],
    "University AI": [
        "https://www.csail.mit.edu/rss.xml",
        "https://ai.stanford.edu/blog/feed/",
        "https://bair.berkeley.edu/blog/rss/",
        "https://ml.ox.ac.uk/rss.xml",
        "https://www.ml.cmu.edu/news/rss.xml"
    ],
    "Corporate AI": [
        "https://openai.com/blog/rss",
        "https://deepmind.com/blog/feed.xml",
        "https://ai.googleblog.com/feeds/posts/default",
        "https://www.microsoft.com/en-us/research/feed/?category=AI",
        "https://blogs.nvidia.com/blog/category/ai-blogs/feed/",
        "https://aws.amazon.com/blogs/machine-learning/feed/"
    ]
}

# Initialize summarizer once
def init_summarizer():
    try:
        return pipeline("summarization")
    except Exception as e:
        print(f"⚠️ WARNING: Failed to load summarizer: {e}")
        return None

summarizer = init_summarizer()

# Safe RSS parse
def safe_parse(url):
    try:
        return feedparser.parse(url)
    except RemoteDisconnected:
        print(f"⚠️ WARNING: RemoteDisconnected for {url}")
        return feedparser.FeedParserDict(entries=[])  # empty
    except Exception as e:
        print(f"⚠️ WARNING: Failed to parse {url}: {e}")
        return feedparser.FeedParserDict(entries=[])

# Clean HTML tags
def clean_html(text):
    return re.sub(r'<[^>]+>', '', text or '').strip()

# AI summary with safeguards
def ai_summary(text):
    text = clean_html(text)
    words = text.split()
    if not summarizer or len(words) < 50:
        return text
    max_len = min(len(words)//2, 60)
    try:
        out = summarizer(text, max_length=max_len, min_length=20, do_sample=False)
        return out[0]['summary_text'].strip()
    except Exception as e:
        print(f"⚠️ WARNING: Summarization failed: {e}")
        return text

# Collect multi-day briefing
def collect_briefing():
    sections = []
    # Weather first
    weather_feed = safe_parse(GROUPED_FEEDS['Weather'][0])
    if weather_feed.entries:
        today = weather_feed.entries[0]
        tomorrow = weather_feed.entries[1] if len(weather_feed.entries)>1 else None
        sections.append(f"Ottawa Weather – {datetime.now():%B %d, %Y}")
        sections.append(f"Tonight: {clean_html(today.summary)}")
        if tomorrow:
            sections.append(f"Tomorrow: {clean_html(tomorrow.summary)}")
        sections.append("")

    # News sections
    all_items = []
    for label, urls in GROUPED_FEEDS.items():
        if label == 'Weather': continue
        for url in urls:
            feed = safe_parse(url)
            for entry in feed.entries:
                if 'published_parsed' not in entry:
                    continue
                pub = datetime(*entry.published_parsed[:6])
                if pub >= CUT_OFF:
                    all_items.append((pub, label, entry))
    # sort by date desc
    all_items.sort(key=lambda x: x[0], reverse=True)

    # group by day
    day_groups = {}
    for pub, label, entry in all_items:
        day = pub.strftime('%B %d, %Y')
        day_groups.setdefault(day, []).append((label, entry))

    for day, items in day_groups.items():
        sections.append(day)
        for label, entry in items:
            title = clean_html(entry.title)
            text = entry.get('content', [{'value': entry.get('summary','')}])[0]['value']
            summary = ai_summary(text)
            source = entry.get('source',{}).get('title','') or label
            sections.append(f"• [{label}] {title}\n  {summary} {{{pub:%B %d, %Y} ({source})}}")
        sections.append("")

    sections.append("— End of briefing —")
    return "\n".join(sections)

if __name__ == "__main__":
    try:
        briefing = collect_briefing()
        with open('latest.txt','w',encoding='utf-8') as f:
            f.write(briefing)
        print("latest.txt updated successfully.")
    except Exception as e:
        errmsg = f"⚠️ ERROR in briefing generation: {type(e).__name__}: {e}"
        print(errmsg)
        with open('latest.txt','w',encoding='utf-8') as f:
            f.write(errmsg)
        exit(0)
