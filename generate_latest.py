#!/usr/bin/env python3
"""
generate_latest.py

Fetch RSS/Atom feeds for weather, news, and specialty topics,
compose a plain-text briefing, and write to latest.txt.
"""

import feedparser
from datetime import datetime
import sys

# === Configuration ===

FEEDS = {
    "Ottawa Weather":       "https://weather.gc.ca/rss/city/on-118_e.xml",
    "CBC Canada":           "https://www.cbc.ca/cmlink/rss-canada",
    "CTV News Canada":      "https://www.ctvnews.ca/rss/ctvnews-ca-canada-public-rss-1.822678",
    "NPR US Top Stories":   "https://feeds.npr.org/1001/rss.xml",
    "Reuters US":           "https://www.reuters.com/rssFeed/usaNews",
    "Reuters World":        "https://www.reuters.com/rssFeed/worldNews",
    "BBC World":            "http://feeds.bbci.co.uk/news/world/rss.xml",
    "Ars Technica Tech Policy": "https://feeds.arstechnica.com/arstechnica/technology-policy",
    "The Register AI & Tech":    "https://www.theregister.com/headlines.rss",
    "TechCrunch":           "http://feeds.feedburner.com/TechCrunch/",
    "Open Group EA News":   "https://public.opengroup.org/open_group_rss.xml",
    "GWF - Geomatics 1":    "https://geospatialworld.net/feed/",
    # Add any other specialty feeds here…
}

# Control how many items per section
MAX_ITEMS_PER_SECTION = 5

# Output file
OUTPUT_FILE = "latest.txt"

# === Helper functions ===

def fetch_feed(name, url):
    """
    Attempt to parse the feed; on error, return None and log to stderr.
    """
    try:
        feed = feedparser.parse(url)
        if feed.bozo:
            raise feed.bozo_exception
        return feed
    except Exception as e:
        print(f"• {name}: Error fetching feed ({e})", file=sys.stderr)
        return None

def format_entries(entries, max_items=MAX_ITEMS_PER_SECTION):
    """
    Given a list of feed entries, return up to `max_items` formatted strings.
    """
    lines = []
    for entry in entries[:max_items]:
        title = entry.get("title", "No title")
        # Some feeds use 'published', some 'updated'
        date = entry.get("published", entry.get("updated", ""))
        source = entry.get("link", "")
        lines.append(f"• {title}\n  {date} ({source})")
    return lines

# === Main composition ===

def compose_briefing():
    now = datetime.now().strftime("%A, %B %d, %Y %H:%M")
    sections = []
    
    # Header
    sections.append(f"Multi-Source News Briefing – {now}\n")

    # Iterate through the configured feeds, grouping by logical sections
    # You can rearrange or rename these as desired.
    grouping = [
        ("Weather", ["Ottawa Weather"]),
        ("Canadian Headlines", ["CBC Canada", "CTV News Canada"]),
        ("U.S. Top Stories",    ["NPR US Top Stories", "Reuters US"]),
        ("International Top Stories", ["Reuters World", "BBC World"]),
        ("AI & Emerging Tech",  ["Ars Technica Tech Policy", "The Register AI & Tech", "TechCrunch"]),
        ("Public Health",       []),  # add feeds here once available
        ("Enterprise Architecture & IT Governance", ["Open Group EA News"]),
        ("Geomatics",           ["GWF - Geomatics 1"]),
    ]

    for section_title, feed_names in grouping:
        sections.append(f"=== {section_title} ===")
        any_items = False
        for name in feed_names:
            url = FEEDS.get(name)
            if not url:
                continue
            feed = fetch_feed(name, url)
            if not feed or not feed.entries:
                continue
            entries = format_entries(feed.entries)
            if entries:
                any_items = True
                sections.append(f"\n-- {name} --")
                sections.extend(entries)
        if not any_items:
            sections.append("No items available or all feeds failed.\n")
        else:
            sections.append("")  # blank line

    return "\n".join(sections)

def write_output(text, filename=OUTPUT_FILE):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Wrote briefing to {filename}")

if __name__ == "__main__":
    briefing = compose_briefing()
    write_output(briefing)