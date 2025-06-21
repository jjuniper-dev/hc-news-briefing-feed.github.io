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
    "U.S.": [
        "https://feeds.npr.org/1001/rss.xml"
    ],
    "Public Health": [
        "https://www.canada.ca/etc/+/health/public-health-updates.rss"
    ],
    "Public Sector AI": [
        # placeholder for Government digital strategy feed(s)
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
summarizer = pipeline("summarization")

# Helper: safe parse to handle disconnections
def safe_parse(url):
    try:
        return feedparser.parse(url)
    except RemoteDisconnected:
        return feedparser.FeedParserDict(entries=[], feed={})
    except Exception as e:
        print(f"Warning: failed to parse {url}: {e}")
        return feedparser.FeedParserDict(entries=[], feed={})

# Helper: strip HTML tags
def clean_html(text):
    return re.sub(r'<[^>]+>', '', text or '').strip()

# AI summary with skip for short text
def ai_summary(text):
    words = text.split()
    if len(words) < 50:
        return text.strip()
    max_len = min(len(words)//2, 120)
    return summarizer(
        text,
        max_length=max_len,
        min_length=20,
        do_sample=False
    )[0]["summary_text"].strip()

# Build multi-day briefing
def collect_briefing():
    lines = []
    # Header
    lines.append(f"Multi-Day News Briefing (Last {DAYS_BACK} days) - {datetime.now().strftime('%B %d, %Y')}")
    lines.append("")
    for section, urls in GROUPED_FEEDS.items():
        lines.append(section.upper())
        for url in urls:
            feed = safe_parse(url)
            for entry in feed.entries:
                if 'published_parsed' not in entry:
                    continue
                pub = datetime(*entry.published_parsed[:6])
                if pub < CUT_OFF:
                    continue
                title = clean_html(entry.title)
                content = ''
                if hasattr(entry, 'content') and entry.content:
                    content = entry.content[0].value
                else:
                    content = entry.get('summary', '')
                text = clean_html(content)
                summary = ai_summary(text)
                date_str = pub.strftime('%B %d, %Y')
                lines.append(f"• {title} ({date_str})")
                lines.append(f"  {summary}")
        lines.append("")
    lines.append("— End of briefing —")
    return "\n".join(lines)

if __name__ == '__main__':
    try:
        briefing = collect_briefing()
        with open('latest.txt', 'w', encoding='utf-8') as f:
            f.write(briefing)
        print('latest.txt updated successfully.')
    except Exception as e:
        err = f"⚠️ ERROR in briefing generation: {type(e).__name__}: {e}"
        print(err)
        with open('latest.txt', 'w', encoding='utf-8') as f:
            f.write(err)
        exit(0)