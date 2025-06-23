#!/usr/bin/env python3
import requests, feedparser
from datetime import datetime

# ---- CONFIG ----
# Weather: Environment Canada RSS for Ottawa
WEATHER_FEED = "https://dd.weather.gc.ca/rss/city/on-118_e.xml"

# Section → list of RSS URLs (try each until we get enough entries)
FEEDS = {
    "Canadian News": [
        "https://rss.cbc.ca/lineup/topstories.xml",
        "https://www.cbc.ca/cmlink/rss-canada",
        "https://www.ctvnews.ca/rss/ctvnews-ca-canada-1.796439"
    ],
    "US News": [
        "https://feeds.npr.org/1001/rss.xml",
        "https://rss.cnn.com/rss/edition_us.rss"
    ],
    "International News": [
        "https://feeds.reuters.com/Reuters/worldNews",
        "http://feeds.bbci.co.uk/news/world/rss.xml"
    ],
    "Public Health": [
        "https://www.canada.ca/etc/+/health/public-health-updates.rss"
    ],
    "AI & Emerging Tech": [
        "https://feeds.arstechnica.com/arstechnica/technology-policy",
        "https://www.technologyreview.com/feed/"
    ],
    "Cybersecurity & Privacy": [
        "https://krebsonsecurity.com/feed/",
        "https://feeds.feedburner.com/TheHackersNews"
    ],
    "Enterprise Architecture": [
        "https://www.opengroup.org/news/rss"
    ],
    "Geomatics": [
        "https://www.geospatialworld.net/feed/"
    ],
    "Cloud Providers": [
        "https://azure.microsoft.com/en-us/updates/feed/",
        "https://aws.amazon.com/new/feed/",
        "https://cloud.google.com/feeds/news.rss"
    ]
}

# How many top entries per section
TOP_N = 2

# ---- HELPERS ----
def fetch_feed_entries(url):
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return feedparser.parse(r.content).entries
    except:
        return []

def pick_entries(urls, n=TOP_N):
    """Try each feed URL until we collect n entries."""
    for url in urls:
        entries = fetch_feed_entries(url)
        if len(entries) >= n:
            return entries[:n]
    # fallback: whatever we got from first feed
    return fetch_feed_entries(urls[0])[:n]

def format_item(e):
    title = e.get("title", "").strip()
    date = ""
    if "published_parsed" in e and e.published_parsed:
        date = datetime(*e.published_parsed[:6]).strftime("%b %d, %Y")
    source = e.get("link", "").split("/")[2]
    summary = (e.get("content", [{}])[0].get("value") 
               if e.get("content") else e.get("summary", ""))
    summary = summary.replace("\n", " ").strip()
    return f"• {title}\n  {summary} {{{date} ({source})}}"

def fetch_weather():
    e = fetch_feed_entries(WEATHER_FEED)
    if not e:
        return ["(no weather data)"]
    today, tomorrow, day3 = e[0], e[1] if len(e)>1 else None, e[2] if len(e)>2 else None
    out = [f"{today.title}: {today.summary.strip()}"]
    if tomorrow:
        out.append(f"{tomorrow.title}: {tomorrow.summary.strip()}")
    if day3:
        out.append(f"{day3.title}: {day3.summary.strip()}")
    return out

# ---- BUILD ----
lines = []
now = datetime.now().strftime("%B %d, %Y %H:%M")
lines.append(f"Morning News Briefing – {now}\n")
lines.append("WEATHER:")
for w in fetch_weather():
    lines.append(f"• {w}")
lines.append("")

for section, urls in FEEDS.items():
    lines.append(f"{section.upper()}:")
    entries = pick_entries(urls, TOP_N)
    if not entries:
        lines.append("• (no data available)\n")
        continue
    for e in entries:
        lines.append(format_item(e))
    lines.append("")  # blank line

lines.append("— End of briefing —")

# ---- WRITE OUT ----
with open("latest.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print("latest.txt updated.")