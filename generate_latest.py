#!/usr/bin/env python3

import feedparser
import re
from datetime import datetime, timedelta
from http.client import RemoteDisconnected
from transformers import pipeline

# --- CONFIG ---
DAYS_BACK = 5
CUT_OFF = datetime.now() - timedelta(days=DAYS_BACK)

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
        # placeholder for GC digital strategy if available
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

# Initialize AI summarizer once
summarizer = pipeline("summarization")

# Helpers

def safe_parse(url):
    try:
        return feedparser.parse(url)
    except RemoteDisconnected:
        return feedparser.FeedParserDict(entries=[], feed={})
    except Exception:
        return feedparser.FeedParserDict(entries=[], feed={})


def strip_tags(html: str) -> str:
    return re.sub(r'<[^>]+>', '', html)


def clean_text(text: str) -> str:
    # Remove image placeholders and markdown noise
    text = re.sub(r'【Image.*?】', '', text)
    text = re.sub(r'\(Image credit:.*?\)', '', text)
    text = re.sub(r'^####.*$', '', text, flags=re.MULTILINE)
    # Collapse multiple blank lines
    text = re.sub(r'\n{2,}', '\n\n', text)
    # Strip whitespace
    lines = [line.strip() for line in text.splitlines()]
    return '\n'.join([l for l in lines if l])


def ai_summary(text: str) -> str:
    words = text.split()
    if len(words) < 50:
        return text
    max_len = min(len(words)//2, 60)
    try:
        return summarizer(text, max_length=max_len, min_length=20, do_sample=False)[0]['summary_text'].strip()
    except Exception:
        return text


def get_weather():
    feed = safe_parse(GROUPED_FEEDS['Weather'][0])
    entries = feed.entries[:2]
    lines = []
    if entries:
        lines.append(f"Ottawa Weather – {datetime.now():%B %d, %Y}")
        for e in entries:
            title = strip_tags(e.title)
            summary = strip_tags(e.get('summary', ''))
            lines.append(f"{title}: {summary}")
    return '\n'.join(lines)


def collect_multi_day():
    all_items = []
    for section, urls in GROUPED_FEEDS.items():
        for url in urls:
            feed = safe_parse(url)
            for entry in feed.entries:
                if 'published_parsed' not in entry:
                    continue
                pub = datetime(*entry.published_parsed[:6])
                if pub < CUT_OFF:
                    continue
                all_items.append((pub, section, entry))
    # Sort and group by date
    all_items.sort(key=lambda x: x[0], reverse=True)
    grouped = {}
    for pub, section, entry in all_items:
        day = pub.strftime('%B %d, %Y')
        grouped.setdefault(day, []).append((section, entry))
    # Build text
    parts = [f"Multi-Day Briefing ({DAYS_BACK} days)\n"]
    parts.append(get_weather())
    for day, items in grouped.items():
        parts.append(f"\n{day}")
        for section, entry in items:
            title = strip_tags(entry.title)
            content = ''
            if hasattr(entry, 'content') and entry.content:
                content = entry.content[0].value
            else:
                content = entry.get('summary', '')
            content = strip_tags(content)
            summary = ai_summary(content)
            summary = clean_text(summary)
            pub_str = datetime(*entry.published_parsed[:6]).strftime('%B %d, %Y')
            parts.append(f"• [{section}] {title}\n  {summary} {{{pub_str}}}")
    parts.append("\n— End of briefing —")
    return '\n'.join(parts)

# Main
if __name__ == '__main__':
    try:
        text = collect_multi_day()
        with open('latest.txt', 'w', encoding='utf-8') as f:
            f.write(text)
        print('latest.txt updated successfully.')
    except Exception as e:
        err = f"⚠️ ERROR in briefing generation: {type(e).__name__}: {e}"
        print(err)
        with open('latest.txt', 'w', encoding='utf-8') as f:
            f.write("⚠️ Daily briefing failed to generate.\n")
            f.write(err)
        exit(0)
