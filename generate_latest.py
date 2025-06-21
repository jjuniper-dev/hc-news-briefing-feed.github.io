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
    "Canadian (CBC)": [
        "https://rss.cbc.ca/lineup/canada.xml"
    ],
    "Canadian (Global/CTV)": [
        "https://www.theglobeandmail.com/canada/toronto/feed/"  # example Global feed
    ],
    "U.S.": [
        "https://feeds.npr.org/1001/rss.xml"
    ],
    "International": [
        "http://feeds.reuters.com/Reuters/worldNews"
    ],
    # the remaining sections in whatever order you prefer
    "Public Health": [
        "https://www.canada.ca/etc/+/health/public-health-updates.rss"
    ],
    "Public Sector AI": [
        "https://open.canada.ca/data/en/dataset/f5fb5b90…/4cb7fb774…"
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
        "https://feeds.arstechnica.com/arstechnica/technology-policy",
        "https://www.theregister.com/headlines.atom",
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
    ],
}

# Initialize summarizer once
summarizer = pipeline("summarization")

def safe_parse(url):
    try:
        return feedparser.parse(url)
    except RemoteDisconnected:
        print(f"Warning: disconnected from {url}")
        return feedparser.FeedParserDict(entries=[])
    except Exception as e:
        print(f"Warning: failed to parse {url}: {e}")
        return feedparser.FeedParserDict(entries=[])

def strip_tags(html: str) -> str:
    return re.sub(r'<[^>]+>', '', html or '')

def clean_text(text: str) -> str:
    text = re.sub(r"【Image.*?】", "", text)
    text = re.sub(r"\(Image credit:.*?\)", "", text)
    text = re.sub(r"^####.*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n{2,}", "\n\n", text)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)

def ai_summary(text: str) -> str:
    words = text.split()
    if len(words) < 50:
        return text
    max_len = min(len(words)//2, 60)
    try:
        out = summarizer(text, max_length=max_len, min_length=20, do_sample=False)
        return out[0]["summary_text"].strip()
    except Exception as e:
        print(f"Warning: summarization failed: {e}")
        return text

def get_weather_summary():
    url = GROUPED_FEEDS["Weather"][0]
    feed = safe_parse(url)
    if not feed.entries:
        return "Ottawa Weather data unavailable."
    today = feed.entries[0]
    summary = strip_tags(today.summary)
    return f"Ottawa Weather – {datetime.now():%B %d, %Y}\n{clean_text(summary)}"

def collect_briefing():
    parts = []
    # 1. Weather
    parts.append(get_weather_summary())
    parts.append("")

    # 2–4. Canadian, U.S., International (only top item per sub-section)
    for section in ["Canadian (CBC)", "Canadian (Global/CTV)", "U.S.", "International"]:
        urls = GROUPED_FEEDS.get(section, [])
        if not urls: continue
        # Fetch only the first feed in list
        feed = safe_parse(urls[0])
        if feed.entries:
            e = feed.entries[0]
            raw = e.content[0].value if hasattr(e, 'content') and e.content else e.summary
            text = strip_tags(raw)
            summary = ai_summary(text)
            clean = clean_text(summary)
            date = datetime(*e.published_parsed[:6]).strftime("%B %d, %Y") if 'published_parsed' in e else ""
            parts.append(f"{section} Top Story – {date}")
            parts.append(f"• {e.title.strip()}\n  {clean}")
            parts.append("")
    
    # 5. Remaining sections
    remaining = [s for s in GROUPED_FEEDS if s not in
                 ["Weather", "Canadian (CBC)", "Canadian (Global/CTV)", "U.S.", "International"]]
    entries = []
    for section in remaining:
        for url in GROUPED_FEEDS[section]:
            feed = safe_parse(url)
            for e in feed.entries:
                if 'published_parsed' not in e: continue
                pub = datetime(*e.published_parsed[:6])
                if pub < CUT_OFF: continue
                entries.append((pub, section, e))
    entries.sort(key=lambda x: x[0], reverse=True)

    # Group by day
    grouped = {}
    for pub, section, e in entries:
        day = pub.strftime("%B %d, %Y")
        grouped.setdefault(day, []).append((section, e))

    for day, items in grouped.items():
        parts.append(day)
        for section, e in items:
            raw = e.content[0].value if hasattr(e, 'content') and e.content else e.summary
            text = strip_tags(raw)
            summary = ai_summary(text)
            clean = clean_text(summary)
            parts.append(f"• [{section}] {e.title.strip()}\n  {clean}")
        parts.append("")

    parts.append("— End of briefing —")
    return "\n".join(parts)

if __name__ == "__main__":
    try:
        briefing = collect_briefing()
        with open("latest.txt", "w", encoding="utf-8") as f:
            f.write(briefing)
        print("latest.txt updated successfully.")
    except Exception as e:
        msg = f"⚠️ ERROR in briefing generation: {type(e).__name__}: {e}"
        print(msg)
        with open("latest.txt", "w", encoding="utf-8") as f:
            f.write("⚠️ Daily briefing failed to generate.\n")
            f.write(msg + "\n")
        exit(0)