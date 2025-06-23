#!/usr/bin/env python3
import requests
import feedparser
import re
from datetime import datetime

# --- CONFIG ---

WEATHER_FEEDS = [
    ("EC Ottawa",  "https://dd.weather.gc.ca/rss/city/on-118_e.xml"),
    ("NOAA XML",   "https://w1.weather.gov/xml/current_obs/OTT.xml"),
    ("NOAA METAR", "https://aviationweather.gov/adds/dataserver_current/httpparam"
                   "?dataSource=metars&requestType=retrieve&format=xml"
                   "&stationString=CYOW&hoursBeforeNow=2"),
]

SECTIONS = {
    "CANADIAN NEWS": [
        ("CBC Top Stories", "https://rss.cbc.ca/lineup/topstories.xml"),
        ("CTV Canada",      "https://www.ctvnews.ca/rss/ctvnews-ca-canada-1.2089050"),
    ],
    "US NEWS": [
        ("NPR US",         "https://feeds.npr.org/1001/rss.xml"),
        ("AP Top Stories", "https://feeds.ap.org/rss/ap-top-news"),
    ],
    "INTERNATIONAL NEWS": [
        ("Reuters World", "https://feeds.reuters.com/Reuters/worldNews"),
        ("BBC World",     "http://feeds.bbci.co.uk/news/world/rss.xml"),
    ],
    "PUBLIC HEALTH": [
        ("PHAC Updates", "https://www.canada.ca/etc/+/health/public-health-updates.rss"),
    ],
    "AI & EMERGING TECH": [
        ("Ars Tech Policy",  "https://feeds.arstechnica.com/arstechnica/technology-policy"),
        ("MIT Tech Review",  "https://www.technologyreview.com/feed/"),
        ("IEEE Spectrum AI", "https://spectrum.ieee.org/rss/robotics"),
    ],
    "CYBERSECURITY & PRIVACY": [
        ("KrebsOnSecurity", "https://krebsonsecurity.com/feed/"),
        ("The Hacker News", "https://feeds.feedburner.com/TheHackersNews"),
    ],
    "ENTERPRISE ARCHITECTURE": [
        ("OpenGroup News", "https://www.opengroup.org/news/rss"),
    ],
    "GEOMATICS": [
        ("Geospatial World", "https://www.geospatialworld.net/feed/"),
    ],
    "CLOUD PROVIDERS": [
        ("Azure Blog",   "https://azure.microsoft.com/en-us/updates/feed/"),
        ("AWS News",     "https://aws.amazon.com/new/feed/"),
        ("Google Cloud", "https://cloud.google.com/blog/rss"),
    ],
}

# --- UTILITIES ---

def clean_html(raw: str) -> str:
    """Strip HTML tags and collapse whitespace."""
    text = re.sub(r'<[^>]+>', '', raw)
    return re.sub(r'\s+', ' ', text).strip()

# --- WEATHER ---

def fetch_weather():
    today = datetime.now().strftime("%A, %B %d, %Y")
    lines = [f"Ottawa Weather – {today}"]
    got = False

    for name, url in WEATHER_FEEDS:
        try:
            r = requests.get(url, timeout=30)
            r.raise_for_status()
            feed = feedparser.parse(r.content)
            if feed.entries:
                e = feed.entries[0]
                title   = clean_html(e.get("title", ""))
                summary = clean_html(e.get("summary", e.get("description", "")))
                lines.append(f"• {name}: {title} — {summary}")
                got = True
                break
        except Exception:
            continue

    if not got:
        lines.append("• (weather data unavailable)")
        return "\n".join(lines)

    # also pull next two-day forecast from primary
    try:
        r2 = requests.get(WEATHER_FEEDS[0][1], timeout=30)
        r2.raise_for_status()
        f2 = feedparser.parse(r2.content)
        for idx, label in ((1, "Tomorrow"), (2, "Day After")):
            if len(f2.entries) > idx:
                e2 = f2.entries[idx]
                lines.append(
                    f"• {label}: {clean_html(e2.title)} — {clean_html(e2.summary)}"
                )
    except Exception:
        pass

    return "\n".join(lines)

# --- NEWS SECTIONS ---

def collect_section(header, feed_list, top_n=2):
    parts = [f"\n{header}"]
    for name, url in feed_list:
        try:
            r = requests.get(url, timeout=20)
            r.raise_for_status()
            feed = feedparser.parse(r.content)
            entries = feed.entries[:top_n]
            if entries:
                for e in entries:
                    pub = ""
                    if hasattr(e, "published_parsed"):
                        pub = datetime(*e.published_parsed[:6]).strftime("%b %d, %Y")
                    summary = clean_html(e.get("summary", e.get("description", "")))
                    parts.append(f"• {name}: {e.title.strip()} — {summary} {{{pub}}}")
            else:
                parts.append(f"• {name}: (unavailable)")
        except Exception:
            parts.append(f"• {name}: (unavailable)")
    return "\n".join(parts)

# --- MAIN ---

def main():
    now = datetime.now().strftime("%B %d, %Y  %H:%M")
    sections = [f"Morning News Briefing – {now}", fetch_weather()]

    for header, feeds in SECTIONS.items():
        sections.append(collect_section(header, feeds))

    sections.append("\n— End of briefing —\n")

    with open("latest.txt", "w", encoding="utf-8") as f:
        f.write("\n\n".join(sections))
    print("latest.txt updated.")

if __name__ == "__main__":
    main()