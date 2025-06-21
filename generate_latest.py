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
        "https://www.theglobeandmail.com/canada/toronto/feed/"
    ],
    "US": [
        "https://feeds.npr.org/1001/rss.xml"
    ],
    "International": [
        "http://feeds.reuters.com/Reuters/worldNews"
    ],
    "Public Health": [
        "https://www.canada.ca/etc/+/health/public-health-updates.rss"
    ],
    "AI & Emerging Tech": [
        "https://feeds.arstechnica.com/arstechnica/technology-policy",
        "https://www.theregister.com/headlines.atom"
    ],
    "Cybersecurity": [
        "https://krebsonsecurity.com/feed/",
        "https://www.nist.gov/blogs/blog.rss"
    ],
    "Enterprise Arch & IT Gov": [
        "https://www.opengroup.org/news/rss/news-release.xml",
        "https://www.cio.com/ciolib/rss/cio/government.xml"
    ],
    "Geomatics": [
        "https://geomatics-news.example.com/rss"
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
    text = re.sub(r"Read More.*", "", text)
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


def get_weather_summary() -> str:
    url = GROUPED_FEEDS["Weather"][0]
    feed = safe_parse(url)
    if not feed.entries:
        return "Ottawa Weather data unavailable."
    today = feed.entries[0]
    summary = strip_tags(today.summary)
    lines = clean_text(summary).split("\n")
    # Simplify to tonight/tomorrow
    result = [f"Ottawa Weather – {datetime.now():%B %d, %Y}"]
    if len(lines) >= 2:
        result.append(f"• Tonight: {lines[0]}")
        result.append(f"• Tomorrow: {lines[1]}")
    else:
        result.extend([f"• {l}" for l in lines])
    return "\n".join(result)


def collect_briefing() -> str:
    parts = []
    # 1. Weather
    parts.append(get_weather_summary())
    parts.append("")

    # 2. Canadian CBC and CTV top 2
    for section in ["Canadian CBC", "Canadian CTV"]:
        urls = GROUPED_FEEDS.get(section, [])
        for url in urls:
            feed = safe_parse(url)
            entries = feed.entries[:2]
            if entries:
                parts.append(f"{section} Top Stories:")
                for e in entries:
                    raw = e.content[0].value if hasattr(e, 'content') and e.content else e.summary
                    summary = ai_summary(strip_tags(raw))
                    parts.append(f"• {e.title.strip()} — {clean_text(summary)}")
                parts.append("")
                break

    # 3. US Top 2
    parts.append("US Top Stories:")
    us_feed = safe_parse(GROUPED_FEEDS["US"][0])
    for e in us_feed.entries[:2]:
        raw = e.summary
        parts.append(f"• {e.title.strip()} — {clean_text(ai_summary(strip_tags(raw)))}")
    parts.append("")

    # 4. International Top 2
    parts.append("International Top Stories:")
    int_feed = safe_parse(GROUPED_FEEDS["International"][0])
    for e in int_feed.entries[:2]:
        raw = e.summary
        parts.append(f"• {e.title.strip()} — {clean_text(ai_summary(strip_tags(raw)))}")
    parts.append("")

    # 5. Special Sections, headline-only one per category
    special = ["Public Health", "AI & Emerging Tech", "Cybersecurity", "Enterprise Arch & IT Gov", "Geomatics"]
    for section in special:
        urls = GROUPED_FEEDS.get(section, [])
        for url in urls:
            feed = safe_parse(url)
            if feed.entries:
                e = feed.entries[0]
                parts.append(f"{section}: {e.title.strip()}")
                break
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