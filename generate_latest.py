#!/usr/bin/env python3

import feedparser
import re
import html
from datetime import datetime, timedelta
from http.client import RemoteDisconnected
from transformers import pipeline

# --- CONFIG ---
DAYS_BACK = 5
CUT_OFF = datetime.now() - timedelta(days=DAYS_BACK)

# RSS Feeds
GROUPED_FEEDS = {
    "Weather": ["https://weather.gc.ca/rss/city/on-118_e.xml"],
    "International": ["http://feeds.reuters.com/Reuters/worldNews"],
    "National (Canada)": [
        "https://rss.cbc.ca/lineup/canada.xml",
        "https://www.ctvnews.ca/rss/ctvnews-ca-canada-public-rss-1.822009"
    ],
    "US": ["https://feeds.npr.org/1001/rss.xml"],
    "Public Health": ["https://www.canada.ca/etc/+/health/public-health-updates.rss"],
    "Digital Government / Public Sector AI": [
        "https://gds.blog/feed/",
        "https://oecd-rss.org/publications/digital-government-rss.xml"
    ],
    "Enterprise Architecture": [
        "https://www.opengroup.org/news/rss/news-release.xml",
        "https://www.cio.com/ciolib/rss/cio/government.xml"
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
    "Academic & Industry Research": [
        "http://export.arxiv.org/rss/cs.AI",
        "https://www.technologyreview.com/feed/",
        "http://aiweekly.co/rss",
        "https://venturebeat.com/category/ai/feed/"
    ],
    "Cybersecurity & Privacy": [
        "https://krebsonsecurity.com/feed/",
        "https://www.nist.gov/blogs/blog.rss"
    ]
}

# Initialize summarizer
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def strip_html(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    return html.unescape(text).strip()

def safe_parse(url: str):
    try:
        return feedparser.parse(url)
    except RemoteDisconnected:
        return feedparser.FeedParserDict(entries=[])
    except Exception as e:
        print(f"Warning: Failed to parse {url}: {e}")
        return feedparser.FeedParserDict(entries=[])

def summarize_text(text: str) -> str:
    """Summarize text, with a fallback if the pipeline fails or returns empty."""
    cleaned = strip_html(text)
    if not cleaned:
        return ""
    try:
        result = summarizer(cleaned, max_length=120, min_length=40, do_sample=False)
        # Guard against empty result
        if not result or 'summary_text' not in result[0]:
            raise IndexError
        return result[0]['summary_text'].strip()
    except (IndexError, KeyError) as e:
        # Fallback to first 300 chars of clean text
        print(f"⚠️ Summarizer fallback for text: {e}")
        return cleaned[:300].rstrip() + "…"
    except Exception as e:
        print(f"⚠️ Summarization error: {e}")
        return cleaned[:300].rstrip() + "…"

def collect_multi_day_briefing() -> str:
    parts = []
    header = datetime.now().strftime("%B %d, %Y")
    parts.append(f"Multi-Day News Briefing (Last {DAYS_BACK} days) – {header}")
    parts.append("")

    for section, urls in GROUPED_FEEDS.items():
        items = []
        for url in urls:
            feed = safe_parse(url)
            for entry in feed.entries:
                if hasattr(entry, "published_parsed"):
                    pub_dt = datetime(*entry.published_parsed[:6])
                    if pub_dt >= CUT_OFF:
                        items.append((pub_dt, entry))

        if not items and section == "National (Canada)":
            parts.append(section.upper())
            parts.append("⚠️ No Canadian national news items found in the last 5 days.")
            parts.append("Check RSS feed availability or add backup sources.")
            parts.append("")
            continue

        items.sort(key=lambda x: x[0], reverse=True)
        parts.append(section.upper())

        count = 0
        for pub_dt, entry in items:
            if section == "Weather":
                if count >= 3:
                    break
                count += 1

            title = strip_html(entry.title)
            content_list = entry.get("content", [])
            if content_list and isinstance(content_list[0], dict):
                content = content_list[0].get("value", "")
            else:
                content = entry.get("summary", "")

            summary = summarize_text(content)
            date_str = pub_dt.strftime("%B %d, %Y")

            parts.append(f"• {title} ({date_str})")
            parts.append(f"  {summary}")
            parts.append("(— pause —)")
            parts.append("")

    parts.append("— End of briefing —")
    return "\n".join(parts)

if __name__ == "__main__":
    try:
        briefing = collect_multi_day_briefing()
        with open("latest.txt", "w", encoding="utf-8") as f:
            f.write(briefing)
        print("latest.txt updated successfully.")
    except Exception as e:
        err_msg = f"⚠️ ERROR: {type(e).__name__}: {e}"
        print(err_msg)
        with open("latest.txt", "w", encoding="utf-8") as f:
            f.write("⚠️ Daily briefing failed to generate due to an error.\n")
            f.write(err_msg + "\n")
        exit(0)