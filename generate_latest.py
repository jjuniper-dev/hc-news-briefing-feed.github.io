#!/usr/bin/env python3
"""
generate_latest.py

Fetches multiple RSS/Atom feeds (weather, news, etc.), compiles a daily briefing,
and writes it to latest.txt.
"""
import os
import re
import requests
import feedparser
from datetime import datetime
from dateutil import tz

# --- CONFIGURATION ---
# Output file
OUTPUT_FILE = 'latest.txt'

# Weather feed for Ottawa (Environment Canada)
WEATHER_FEED = 'https://dd.weather.gc.ca/rss/city/on-118_e.xml'
WEATHER_DAYS = 3  # today + next two days

# News feeds organized by section
NEWS_FEEDS = {
    'Canadian Headlines': [
        ('CBC', 'https://rss.cbc.ca/lineup/topstories.xml'),
        ('CTV', 'https://www.ctvnews.ca/rss/ctvnews-ca-canada-1.2089050'),
    ],
    'U.S. Top Stories': [
        ('NPR US', 'https://feeds.npr.org/1001/rss.xml'),
        ('Reuters US', 'https://feeds.reuters.com/Reuters/domesticNews'),
    ],
    'International Top Stories': [
        ('Reuters World', 'https://feeds.reuters.com/Reuters/worldNews'),
        ('BBC World', 'http://feeds.bbci.co.uk/news/world/rss.xml'),
    ],
    'AI & Emerging Tech': [
        ('Ars Technica', 'https://feeds.arstechnica.com/arstechnica/technology-policy'),
        ('The Register', 'https://www.theregister.com/headlines.atom'),
        ('TechCrunch AI', 'http://feeds.feedburner.com/TechCrunch/ai'),
    ],
    'Public Health': [
        ('PHAC News', 'https://www.canada.ca/etc/+/health/public-health-updates.rss'),
    ],
    'Enterprise Architecture & IT Governance': [
        ('Open Group', 'https://www.opengroup.org/news/rss'),
    ],
    'Geomatics': [
        ('GeoSpatial World', 'https://www.geospatialworld.net/feed/'),
    ],
}

# Utility to strip HTML tags
TAG_RE = re.compile(r'<[^>]+>')
def clean_html(raw):
    return TAG_RE.sub('', raw).strip()

# Fetch and parse feed with requests
def fetch_feed(url):
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()
    return feedparser.parse(resp.content)

# Generate weather section
def get_weather_section():
    try:
        feed = fetch_feed(WEATHER_FEED)
        entries = feed.entries[:WEATHER_DAYS]
    except Exception as e:
        return f"Ottawa Weather – Error fetching forecast: {e}\n"

    # Convert times to local
    now = datetime.now(tz.tzlocal())
    header = f"Ottawa Weather – {now.strftime('%B %d, %Y')}"
    lines = [header]
    for entry in entries:
        title = entry.get('title', '').strip()
        summary = clean_html(entry.get('summary', ''))
        lines.append(f"• {title}: {summary}")
    return "\n".join(lines)

# Format a feed entry
def format_entry(entry):
    title = entry.get('title', '').strip()
    # Prefer content over summary
    content = ''
    if 'content' in entry and entry.content:
        content = clean_html(entry.content[0].value)
    else:
        content = clean_html(entry.get('summary', ''))
    # Published date
    pub = ''
    if 'published_parsed' in entry and entry.published_parsed:
        pub = datetime(*entry.published_parsed[:6]).strftime('%B %d, %Y')
    # Source domain
    src = entry.get('source', {}).get('title') or entry.link.split('/')[2]
    return f"• {title}\n  {content} {{{pub} ({src})}}"

# Generate news sections
def get_news_sections():
    sections = []
    for section, feeds in NEWS_FEEDS.items():
        lines = [f"{section}"]
        for name, url in feeds:
            try:
                feed = fetch_feed(url)
                for entry in feed.entries[:2]:
                    lines.append(format_entry(entry))
            except Exception as e:
                lines.append(f"• {name}: Error fetching feed ({e})")
        sections.append("\n".join(lines))
    return sections

# Main
if __name__ == '__main__':
    all_sections = []
    # Weather first
    all_sections.append(get_weather_section())
    all_sections.append('')
    # News
    news = get_news_sections()
    for sec in news:
        all_sections.append(sec)
        all_sections.append('')
    all_sections.append('-- End of briefing --')

    # Write to file
    content = "\n".join(all_sections)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Written daily briefing to {OUTPUT_FILE}")
