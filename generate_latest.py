#!/usr/bin/env python3
import requests
import feedparser
from datetime import datetime

# --- CONFIG ---

# Weather fallbacks
WEATHER_FEEDS = [
    ("EC Ottawa",    "https://dd.weather.gc.ca/rss/city/on-118_e.xml"),
    ("NOAA XML",     "https://w1.weather.gov/xml/current_obs/OTT.xml"),
    ("NOAA METAR",   "https://aviationweather.gov/adds/dataserver_current/httpparam"
                     "?dataSource=metars&requestType=retrieve&format=xml"
                     "&stationString=CYOW&hoursBeforeNow=2"),
]

# Section‐to‐list-of-(label, URL) mappings
SECTIONS = {
    "CANADIAN NEWS": [
        ("CBC Top Stories", "https://rss.cbc.ca/lineup/topstories.xml"),
        ("CTV Canada",      "https://www.ctvnews.ca/rss/ctvnews-ca-canada-1.2089050"),
    ],
    "US NEWS": [
        ("NPR US",           "https://feeds.npr.org/1001/rss.xml"),
        ("AP Top Stories",   "https://feeds.ap.org/rss/ap-top-news"),
    ],
    "INTERNATIONAL NEWS": [
        ("Reuters World",    "https://feeds.reuters.com/Reuters/worldNews"),
        ("BBC World",        "http://feeds.bbci.co.uk/news/world/rss.xml"),
    ],
    "PUBLIC HEALTH": [
        ("PHAC Updates",     "https://www.canada.ca/etc/+/health/public-health-updates.rss"),
    ],
    "AI & EMERGING TECH": [
        ("Ars Tech Policy",  "https://feeds.arstechnica.com/arstechnica/technology-policy"),
        ("MIT Tech Review",  "https://www.technologyreview.com/feed/"),
        ("IEEE Spectrum AI", "https://spectrum.ieee.org/rss/robotics"),
    ],
    "CYBERSECURITY & PRIVACY": [
        ("KrebsOnSecurity",  "https://krebsonsecurity.com/feed/"),
        ("The Hacker News",  "https://feeds.feedburner.com/TheHackersNews"),
    ],
    "ENTERPRISE ARCHITECTURE": [
        ("OpenGroup News",   "https://www.opengroup.org/news/rss"),
    ],
    "GEOMATICS": [
        ("Geospatial World", "https://www.geospatialworld.net/feed/"),
    ],
    "CLOUD PROVIDERS": [
        ("Azure Blog",       "https://azure.microsoft.com/en-us/updates/feed/"),
        ("AWS News",         "https://aws.amazon.com/new/feed/"),
        ("Google Cloud",     "https://cloud.google.com/blog/rss"),
    ],
}

# --- FUNCTIONS ---

def fetch_weather():
    """Try each WEATHER_FEEDS URL until one yields entries."""
    today = datetime.now().strftime("%A, %B %d, %Y")
    lines = [f"Ottawa Weather – {today}"]

    # get primary
    used = None
    for name, url in WEATHER_FEEDS:
        try:
            r = requests.get(url, timeout=30)
            r.raise_for_status()
            feed = feedparser.parse(r.content)
            if feed.entries:
                e = feed.entries[0]
                title   = e.get("title", "").strip()
                summary = (e.get("summary") or e.get("description") or "").strip()
                lines.append(f"• {name}: {title} — {summary}")
                used = WEATHER_FEEDS[0][1] if name == WEATHER_FEEDS[0][0] else None
                break
        except Exception:
            continue

    if not used:
        lines.append("• (weather data unavailable)")
    else:
        # if primary EC worked, add next two-day forecast
        try:
            r2 = requests.get(WEATHER_FEEDS[0][1], timeout=30)
            r2.raise_for_status()
            f2 = feedparser.parse(r2.content)
            for idx, label in ((1, "Tomorrow"), (2, "Day After")):
                if len(f2.entries) > idx:
                    e2 = f2.entries[idx]
                    lines.append(f"• {label}: {e2.title.strip()} — {e2.summary.strip()}")
        except Exception:
            pass

    return "\n".join(lines)


def collect_section(header, feed_list, top_n=2):
    """Fetch up to top_n entries from each feed in feed_list."""
    lines = [f"\n{header}"]
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
                    lines.append(f"• {name}: {e.title.strip()}  {{{pub}}}")
            else:
                lines.append(f"• {name}: (unavailable)")
        except Exception:
            lines.append(f"• {name}: (unavailable)")
    return "\n".join(lines)


def main():
    parts = []

    # Header with timestamp
    now = datetime.now().strftime("%B %d, %Y  %H:%M")
    parts.append(f"Morning News Briefing – {now}")

    # Weather
    parts.append(fetch_weather())

    # All other sections
    for section, feeds in SECTIONS.items():
        parts.append(collect_section(section, feeds))

    parts.append("\n— End of briefing —")

    # Write out
    text = "\n\n".join(parts) + "\n"
    with open("latest.txt", "w", encoding="utf-8") as f:
        f.write(text)
    print("latest.txt updated.")


if __name__ == "__main__":
    main()