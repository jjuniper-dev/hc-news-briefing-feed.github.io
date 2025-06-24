#!/usr/bin/env python3
# generate_latest.py

import sys
import requests
import feedparser
from datetime import datetime, timedelta
from html.parser import HTMLParser

# -----------------------------------------------------------------------------
# HTML stripper (no bs4 needed)
# -----------------------------------------------------------------------------
class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return "".join(self.fed).strip()

def clean_html(html: str) -> str:
    s = MLStripper()
    s.feed(html or "")
    return s.get_data()

# -----------------------------------------------------------------------------
# CONFIG: your RSS/ATOM/WEATHER feeds by category
# -----------------------------------------------------------------------------
# Environment Canada Ottawa + NOAA fallback
WEATHER_FEEDS = [
    "https://dd.weather.gc.ca/rss/city/on-118_e.xml",           # EnvCan Ottawa
    "https://w1.weather.gov/xml/current_obs/CYOW.rss"           # NOAA Ottawa (fallback)
]

FEEDS = {
    "CANADIAN NEWS": [
        "https://rss.cbc.ca/lineup/topstories.xml",
        "https://www.ctvnews.ca/rss/ctvnews-ca-canada-1.2089050"
    ],
    "US NEWS": [
        "https://feeds.npr.org/1001/rss.xml",
        "https://www.apnews.com/apf-topnews?outputType=xml"
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
        "https://newsroom.ibm.com/feeds/press_releases.xml"
    ],
    "CYBERSECURITY & PRIVACY": [
        "https://krebsonsecurity.com/feed/",
        "https://rss.darkreading.com/DRTopStories"
    ],
    "ENTERPRISE ARCHITECTURE": [
        "https://www.opengroup.org/news/rss",
        "https://www.gartner.com/en/rss/insights"
    ],
    "GEOMATICS": [
        "https://www.geospatialworld.net/feed/",
        "https://www.xyht.com/feed/"
    ],
    "CLOUD PROVIDERS": [
        "https://azure.microsoft.com/en-us/updates/feed/",
        "https://aws.amazon.com/new/feed/",
        "https://cloud.google.com/feeds/news.xml"
    ]
}

# -----------------------------------------------------------------------------
# Fetch weather: today + next two days
# -----------------------------------------------------------------------------
def fetch_weather():
    for url in WEATHER_FEEDS:
        try:
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()
            feed = feedparser.parse(resp.content)
            if not feed.entries:
                continue
            # EnvCan gives multiple items; NOAA gives single current obs
            # we just take first three entries if available
            lines = []
            today = datetime.now().strftime("%B %d, %Y")
            lines.append(f"Ottawa Weather – {today}")
            for entry in feed.entries[:3]:
                title = clean_html(entry.get("title", ""))
                summary = clean_html(entry.get("summary", entry.get("description", "")))
                lines.append(f"• {title}: {summary}")
            return "\n".join(lines)
        except Exception:
            continue
    # if all fail
    return "Ottawa Weather – data unavailable for today\n"

# -----------------------------------------------------------------------------
# Fetch and format one section
# -----------------------------------------------------------------------------
def collect_section(name, urls):
    parts = [f"\n{name} – {datetime.now().strftime('%B %d, %Y')}"]
    any_ok = False
    for url in urls:
        try:
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()
            feed = feedparser.parse(resp.content)
            if not feed.entries:
                parts.append(f"• {name.split()[0]} source unavailable")
            else:
                any_ok = True
                entry = feed.entries[0]
                title = clean_html(entry.get("title", ""))
                # full content if available
                content = entry.get("content", [{}])[0].get("value", "")
                summary = clean_html(content) or clean_html(entry.get("summary", ""))
                date = ""
                if entry.get("published_parsed"):
                    date = datetime(*entry.published_parsed[:6]).strftime("%b %d, %Y")
                parts.append(f"• {title}\n  {summary} {{{date}}}")
        except Exception:
            parts.append(f"• {name.split()[0]} source error")
    if not any_ok:
        parts = [f"\n{name} – no data available"]
    return "\n".join(parts)

# -----------------------------------------------------------------------------
# Main: build latest.txt
# -----------------------------------------------------------------------------
def main():
    out = []

    # Weather first
    out.append(fetch_weather())

    # Then each section in desired order
    for section in [
        "CANADIAN NEWS", "US NEWS", "INTERNATIONAL NEWS",
        "PUBLIC HEALTH", "AI & EMERGING TECH",
        "CYBERSECURITY & PRIVACY", "ENTERPRISE ARCHITECTURE",
        "GEOMATICS", "CLOUD PROVIDERS"
    ]:
        out.append(collect_section(section, FEEDS[section]))

    out.append("\n— End of briefing —")

    with open("latest.txt", "w", encoding="utf-8") as f:
        f.write("\n\n".join(out))

if __name__ == "__main__":
    main()