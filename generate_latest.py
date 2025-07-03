#!/usr/bin/env python3

import feedparser
import re
from datetime import datetime, timedelta
from http.client import RemoteDisconnected
from transformers import pipeline

# --- CONFIG ---
DAYS_BACK = 5
CUT_OFF = datetime.now() - timedelta(days=DAYS_BACK)

# Grouped RSS feeds by category (split problematic combos)
GROUPED_FEEDS = {
    "Weather": [
        "https://weather.gc.ca/rss/city/on-131_e.xml"
    ],
    "International News": [
        "http://feeds.reuters.com/Reuters/worldNews"
    ],
    "Canadian News": [
        "https://rss.cbc.ca/lineup/canada.xml"
    ],
    "U.S. Top Stories": [
        "https://feeds.npr.org/1001/rss.xml"
    ],
    "Artificial Intelligence": [
        "https://feeds.arstechnica.com/arstechnica/technology-policy"
    ],
    "Digital Strategy": [
        "https://www.theregister.com/headlines.atom"
    ],
    "Public Health": [
        "https://www.who.int/feeds/entity/mediacentre/news/en/rss.xml"
    ],
    "Science": [
        "https://www.nature.com/subjects/public-health.rss"
    ],
    "Government & Policy": [
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

# Helper to strip HTML
TAG_RE = re.compile(r'<[^>]+>')

def clean_html(text):
    return TAG_RE.sub('', text).strip()

# Summarize with longer output
def ai_summary(text):
    text = clean_html(text)
    words = text.split()
    # Longer summary: up to 250 tokens, min 80
    max_len = min(len(words), 250)
    max_len = max(max_len, 80)
    try:
        result = summarizer(text, max_length=max_len, min_length=80, do_sample=False)
        return result[0]['summary_text'].strip()
    except Exception:
        return text

# Safe parse
def safe_parse(url):
    try:
        return feedparser.parse(url)
    except RemoteDisconnected:
        return feedparser.FeedParserDict(entries=[], feed={})
    except Exception:
        return feedparser.FeedParserDict(entries=[], feed={})

def section_emoji(name):
    return {
        'Weather': '🧾',
        'International News': '🌍',
        'Canadian News': '🍁',
        'U.S. Top Stories': '🇺🇸',
        'Artificial Intelligence': '🧠',
        'Digital Strategy': '💻',
        'Public Health': '🏥',
        'Science': '🔬',
        'Government & Policy': '🧾',
        'Enterprise Architecture & IT Governance': '🏛️',
        'AI & Emerging Tech': '🤖',
        'Cybersecurity & Privacy': '🔒',
        'University AI': '🎓',
        'Corporate AI': '🏢'
    }.get(name, '')

# Generate briefing
def generate_briefing():
    now = datetime.now()
    date_str = now.strftime('%B %d, %Y %H:%M')
    iso_date = now.strftime('%Y-%m-%d %H:%M')
    header = [
        f"✅ Morning News Briefing – {date_str}",
        "",
        f"📅 Date: {iso_date}",
        "🏷️ Tags: #briefing #ai #publichealth #digitalgov",
        "",
        "⸻",
        ""
    ]
    body = []
    for section, urls in GROUPED_FEEDS.items():
        body.append(f"{section_emoji(section)} {section}")
        has_items = False
        all_entries = []
        for url in urls:
            feed = safe_parse(url)
            for entry in feed.entries:
                if 'published_parsed' in entry:
                    pub = datetime(*entry.published_parsed[:6])
                    if pub >= CUT_OFF:
                        all_entries.append(entry)
        # Special handling for Weather: only show 3 entries (current + next 2 days)
        if section == "Weather":
            selected_entries = all_entries[:3]
        else:
            selected_entries = all_entries[:5]
        for entry in selected_entries:
            title = clean_html(entry.title)
            content = entry.get('content', [{'value': entry.get('summary','')}])[0]['value']
            summary = ai_summary(content)
            body.append(f"• {title}\n  {summary}")
            has_items = True
        if not has_items:
            body.append("No updates.")
        body.append("")
    body.append("⸻")
    return '\n'.join(header + body)

if __name__ == '__main__':
    try:
        briefing = generate_briefing()
        with open('latest.txt', 'w', encoding='utf-8') as f:
            f.write(briefing)
        print('latest.txt updated successfully.')
    except Exception as e:
        print(f"⚠️ ERROR in briefing generation: {e}")
        with open('latest.txt', 'w', encoding='utf-8') as f:
            f.write(f"⚠️ Daily briefing failed: {e}\n")
        exit(0)
