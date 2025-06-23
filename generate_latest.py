#!/usr/bin/env python3
import sys
import requests
import feedparser
import xml.etree.ElementTree as ET
from datetime import datetime

# CONFIG
WEATHER_FEED = "https://dd.weather.gc.ca/rss/city/on-118_e.xml"
SECTIONS = {
    "CANADIAN NEWS": [
        "https://rss.cbc.ca/lineup/topstories.xml",
        "https://www.cbc.ca/cmlink/rss-canada",
        "https://www.ctvnews.ca/rss/ctvnews-ca-canada-1.2089050"
    ],
    "US NEWS": [
        "https://feeds.npr.org/1001/rss.xml",
        "https://rss.cnn.com/rss/edition_us.rss"
    ],
    "INTERNATIONAL NEWS": [
        "https://feeds.reuters.com/Reuters/worldNews",
        "http://feeds.bbci.co.uk/news/world/rss.xml"
    ],
    "PUBLIC HEALTH": [
        "https://www.canada.ca/etc/+/health/public-health-updates.rss",
        "https://www.who.int/feeds/entity/csr/don/en/rss.xml"
    ],
    "AI & EMERGING TECH": [
        "https://feeds.arstechnica.com/arstechnica/technology-policy",
        "https://www.technologyreview.com/feed/",
        "https://spectrum.ieee.org/rss/robotics"
    ],
    "CYBERSECURITY & PRIVACY": [
        "https://krebsonsecurity.com/feed/",
        "https://feeds.feedburner.com/TheHackersNews"
    ],
    "ENTERPRISE ARCHITECTURE": [
        "https://www.opengroup.org/news/rss",
        "https://www.gartner.com/en/newsroom/rss"
    ],
    "GEOMATICS": [
        "https://www.geospatialworld.net/feed/",
        "https://spatialnews.xyz/feed/"
    ],
    "CLOUD PROVIDERS": [
        "https://azure.microsoft.com/en-us/blog/feed/",
        "https://aws.amazon.com/new/feed/",
        "https://cloud.google.com/blog/rss/"
    ]
}

def fetch_weather():
    header = f"Ottawa Weather – {datetime.now():%B %d, %Y}"
    try:
        r = requests.get(WEATHER_FEED, timeout=10)
        r.raise_for_status()
        root = ET.fromstring(r.content)

        summary = root.findtext(".//currentConditions/textSummary", "").strip()
        lines = [header, f"• Now: {summary or '(unavailable)'}"]

        forecasts = root.findall(".//forecastGroup/forecast")[:2]
        for f in forecasts:
            period = f.findtext("period", "").strip()
            desc   = f.findtext("textForecast", "").strip()
            lines.append(f"• {period}: {desc or '(unavailable)'}")

        return "\n".join(lines)

    except Exception:
        return header + "\n• (weather data unavailable)"

def get_section(name, urls, n=2):
    """Try each URL until we get entries, then take top n."""
    items = []
    for url in urls:
        try:
            feed = feedparser.parse(requests.get(url, timeout=10).content)
            if feed.entries:
                for e in feed.entries[:n]:
                    date = ""
                    if getattr(e, "published_parsed", None):
                        date = datetime(*e.published_parsed[:6]).strftime("%b %d, %Y")
                    src = e.get("source", {}).get("title") or url.split("/")[2]
                    summary = (e.content[0].value if getattr(e, "content", None) else e.get("summary","")).strip()
                    items.append(f"• {e.title}\n  {summary} {{{date} ({src})}}")
                break
        except Exception:
            continue
    if not items:
        items = [f"• (unavailable)"]
    return f"\n{name}\n" + "\n".join(items)

def main():
    parts = []
    parts.append(fetch_weather())

    for section, urls in SECTIONS.items():
        parts.append(get_section(section, urls))

    parts.append("\n— End of briefing —")
    with open("latest.txt", "w", encoding="utf-8") as f:
        f.write("\n\n".join(parts))
    print("latest.txt written.")

if __name__=="__main__":
    main()