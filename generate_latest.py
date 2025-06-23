import requests
import feedparser
import time
from datetime import datetime

# --- Configuration ---
SECTIONS = {
    "Weather": [
        # Environment Canada RSS
        "https://dd.weather.gc.ca/citypage_weather/xml/ON/s0000434_e.xml"
    ],
    "Canadian News": [
        "https://www.cbc.ca/cmlink/rss-topstories",
        "https://rss.cbc.ca/lineup/canada.xml"
    ],
    "US News": [
        "https://feeds.npr.org/1001/rss.xml",
        "https://www.reddit.com/r/news/.rss"
    ],
    "International News": [
        "https://feeds.bbci.co.uk/news/world/rss.xml",
        "https://feeds.reuters.com/Reuters/worldNews"
    ],
    "Public Health": [
        "https://www.canada.ca/content/canada/en/public-health/services/rss-articles/public-health-updates.rss"
    ],
    "AI & Emerging Tech": [
        "https://feeds.arstechnica.com/arstechnica/technology-policy",
        "https://www.technologyreview.com/feed/"
    ],
    "Cybersecurity & Privacy": [
        "https://krebsonsecurity.com/feed/",
        "https://www.schneier.com/blog/atom.xml"
    ],
    "Enterprise Architecture": [
        "https://www.opengroup.org/news/rss",
        "https://www.gartner.com/en/newsroom/rss"
    ],
    "Geomatics": [
        "https://www.geospatialworld.net/feed/",
        "https://www.gwf.org/rss/news.xml"
    ]
}

MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds


def fetch_feed(url):
    """
    Try fetching the feed content with retries.
    Returns parsed feed or None on failure.
    """
    for attempt in range(1, MAX_RETRIES+1):
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            return feedparser.parse(resp.content)
        except Exception as e:
            print(f"Warning: fetch attempt {attempt} for {url} failed -> {e}")
            time.sleep(RETRY_DELAY)
    print(f"Error: all retries failed for {url}")
    return None


def format_entries(entries, limit=2):
    out = []
    for entry in entries[:limit]:
        title = entry.get('title', '').strip()
        summary = entry.get('summary', '').strip()
        pub = ''
        if entry.get('published_parsed'):
            pub = datetime(*entry.published_parsed[:6]).strftime('%b %d, %Y')
        source = entry.get('source', {}).get('title') or entry.link.split('/')[2]
        out.append(f"• {title}\n  {summary} {{{pub} ({source})}}")
    return out


def build_briefing():
    lines = []
    # Header
    now = datetime.now().strftime('%B %d, %Y %H:%M')
    lines.append(f"Morning News Briefing – {now}")
    lines.append("")

    for section, urls in SECTIONS.items():
        lines.append(f"{section.upper()}:")
        collected = False
        for url in urls:
            feed = fetch_feed(url)
            if feed and feed.entries:
                # weather handled specially
                if section == 'Weather':
                    # simple first entry
                    entry = feed.entries[0]
                    lines.append(f"• {entry.title.strip()}: {entry.summary.strip()}")
                else:
                    entries = format_entries(feed.entries, limit=2)
                    lines.extend(entries)
                collected = True
                break
        if not collected:
            lines.append(f"(no data available)")
        lines.append("")

    lines.append("— End of briefing —")
    return "\n".join(lines)


def main():
    briefing = build_briefing()
    with open('latest.txt', 'w', encoding='utf-8') as f:
        f.write(briefing)
    print("Successfully wrote latest.txt")


if __name__ == '__main__':
    main()
