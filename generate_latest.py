#!/usr/bin/env python3

import feedparser
import re
from datetime import datetime, timedelta
from http.client import RemoteDisconnected
from transformers import pipeline

# --- CONFIG ---
DAYS_BACK = 5
CUT_OFF = datetime.now() - timedelta(days=DAYS_BACK)

# RSS feeds to include
RSS_FEEDS = [
    ("International", "http://feeds.reuters.com/Reuters/worldNews"),
    ("Canadian",      "https://rss.cbc.ca/lineup/canada.xml"),
    ("US",            "https://feeds.npr.org/1001/rss.xml"),
    ("AI & IT",       "https://feeds.arstechnica.com/arstechnica/technology-policy"),
    ("AI & IT",       "https://www.theregister.com/headlines.atom"),
    ("Public Health", "https://www.canada.ca/etc/+/health/public-health-updates.rss"),
    ("Public Sector AI", "https://open.canada.ca/data/en/dataset/f5fb5b90-.../4cb7fb774.../rss"),
    ("Gartner",       "http://blogs.gartner.com/gbn/feed/"),
    ("Gartner",       "https://blogs.gartner.com/smarterwithgartner/feed/"),
    ("Global Health", "https://www.who.int/feeds/entity/mediacentre/news/en/rss.xml"),
    ("Public Health Sci", "https://www.nature.com/subjects/public-health.rss"),
    ("Digital Gov",    "https://gds.blog/feed/"),
    ("OECD Digital Gov","https://oecd-rss.org/publications/digital-government-rss.xml"),
    ("EA & Governance","https://www.opengroup.org/news/rss/news-release.xml"),
    ("Gov CIO",        "https://www.cio.com/ciolib/rss/cio/government.xml"),
    ("MIT Tech AI",    "https://www.technologyreview.com/feed/"),
    ("AI Weekly",      "http://aiweekly.co/rss"),
    ("VB AI",          "https://venturebeat.com/category/ai/feed/"),
    ("Security",       "https://krebsonsecurity.com/feed/"),
    ("NIST",           "https://www.nist.gov/blogs/blog.rss"),
]

WEATHER_FEED = "https://weather.gc.ca/rss/city/on-131_e.xml"  # Ottawa

# --- UTILITIES ---

# strip HTML tags
TAG_RE = re.compile(r'<[^>]+>')
def clean_html(text: str) -> str:
    return TAG_RE.sub('', text)

# safe parsing
def safe_parse(url: str):
    try:
        return feedparser.parse(url)
    except RemoteDisconnected:
        return feedparser.FeedParserDict(entries=[], feed={})
    except Exception as e:
        print(f"Warning: failed to parse {url}: {e}")
        return feedparser.FeedParserDict(entries=[], feed={})

# initialize summarizer
summarizer = pipeline("summarization")

def ai_summarize(text: str) -> str:
    # prepend instruction
    instr = "As a public-sector enterprise architect at PHAC, summarize focusing on policy implications and system design considerations."
    prompt = instr + "\n" + text
    result = summarizer(prompt, max_length=100, min_length=40, do_sample=False)
    return result[0]['summary_text'].strip()

# --- GENERATE BRIEFING ---

def get_weather_section():
    feed = safe_parse(WEATHER_FEED)
    entries = feed.entries[:2]
    lines = [f"Ottawa Weather – {datetime.now():%B %d, %Y}"]
    for i, e in enumerate(entries):
        day = "Today" if i == 0 else "Tomorrow"
        text = clean_html(e.summary)
        lines.append(f"{day}: {text}")
    return "\n".join(lines)


def collect_multi_day_news() -> str:
    # gather entries within cutoff
    items = []
    for label, url in RSS_FEEDS:
        feed = safe_parse(url)
        for entry in feed.entries:
            if 'published_parsed' not in entry:
                continue
            pub = datetime(*entry.published_parsed[:6])
            if pub < CUT_OFF:
                continue
            items.append((pub, label, entry))
    # sort descending
    items.sort(key=lambda x: x[0], reverse=True)
    # group by date
    grouped = {}
    for pub, label, entry in items:
        date_str = pub.strftime('%B %d, %Y')
        grouped.setdefault(date_str, []).append((label, entry))
    # build text
    parts = [f"Multi-Day Briefing: Last {DAYS_BACK} days", get_weather_section(), ""]
    for date_str, records in grouped.items():
        parts.append(date_str)
        for label, entry in records:
            text = entry.content[0].value if hasattr(entry, 'content') and entry.content else entry.summary
            clean = clean_html(text)
            summary = ai_summarize(clean)
            parts.append(f"• [{label}] {entry.title.strip()}\n  Summary: {summary}")
        parts.append("")
    parts.append("— End of briefing —")
    return "\n".join(parts)

if __name__ == "__main__":
    briefing = collect_multi_day_news()
    with open("latest.txt", "w", encoding="utf-8") as f:
        f.write(briefing)
    print("latest.txt updated.")