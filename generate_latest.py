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
    "Weather": [
        "https://weather.gc.ca/rss/city/on-118_e.xml"  # Ottawa
    ],
    "International": [
        "http://feeds.reuters.com/Reuters/worldNews"
    ],
    "National (Canada)": [
        "https://rss.cbc.ca/lineup/canada.xml",
        "https://www.ctvnews.ca/rss/ctvnews-ca-canada-public-rss-1.822009"
    ],
    "US": [
        "https://feeds.npr.org/1001/rss.xml"
    ],
    "Public Health": [
        "https://www.canada.ca/etc/+/health/public-health-updates.rss"
    ],
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

def strip_html(text):
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    text = html.unescape(text)
    return text.strip()

def safe_parse(url):
    try:
        return feedparser.parse(url)
    except RemoteDisconnected:
        return feedparser.FeedParserDict(entries=[])
    except Exception as e:
        print(f"Warning: Failed to parse {url}: {e}")
        return feedparser.FeedParserDict(entries=[])

def summarize_text(text):
    cleaned = strip_html(text)
    if not cleaned:
        return ""
    result = summarizer(cleaned, max_length=120, min_length=40, do_sample=False)
    return result[0]['summary_text'].strip()

def collect_multi_day_briefing():
    parts = []
    parts.append(f"Multi-Day News Briefing (Last {DAYS_BACK} days) â {datetime.now():%B %d, %Y}")
    parts.append("")

    for section, urls in GROUPED_FEEDS.items():
        section_items = []
        for url in urls:
            feed = safe_parse(url)
            for entry in feed.entries:
                if hasattr(entry, 'published_parsed'):
                    pub_dt = datetime(*entry.published_parsed[:6])
                    if pub_dt >= CUT_OFF:
                        section_items.append((pub_dt, entry))
        if not section_items:
            if section == "National (Canada)":
                parts.append("â ï¸ No Canadian national news items found in the last 5 days.")
                parts.append("Check RSS feed availability or add backup sources.
")
            continue
        section_items.sort(key=lambda x: x[0], reverse=True)
        parts.append(section.upper())
        count = 0
        for pub_dt, entry in section_items:
            if section == "Weather" and count >= 3:
                break
            count += 1
            title = strip_html(entry.title)
            content = entry.get('content', [{}])[0].get('value') if entry.get('content') else entry.get('summary')
            summary = summarize_text(content)
            date_str = pub_dt.strftime('%B %d, %Y')
            parts.append(f"â¢ {title} ({date_str})")
            parts.append(f"  {summary}")
            parts.append("(â pause â)
")

    parts.append("â End of briefing â")
    return "
".join(parts)

# Main execution
if __name__ == "__main__":
    try:
        briefing = collect_multi_day_briefing()
        with open("latest.txt", "w", encoding="utf-8") as f:
            f.write(briefing)
        print("latest.txt updated successfully.")
    except Exception as e:
        err_msg = f"â ï¸ ERROR: {type(e).__name__}: {e}"
        print(err_msg)
        with open("latest.txt", "w", encoding="utf-8") as f:
            f.write("â ï¸ Daily briefing failed to generate due to an error.
")
            f.write(err_msg + "
")