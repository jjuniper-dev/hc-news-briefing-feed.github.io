#!/usr/bin/env python3
import requests
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime

# ─── CONFIG ───────────────────────────────────────────────────────────────────

# Environment Canada XML for Ottawa (city code ON/s0000660)
WEATHER_FEED = "https://dd.weather.gc.ca/citypage_weather/xml/ON/s0000660_e.xml"

SECTIONS = [
    ("WEATHER",      None),
    ("CANADIAN NEWS", {
        "CBC Top Stories":    "https://rss.cbc.ca/lineup/topstories.xml",
        "CTV Canada":         "https://www.ctvnews.ca/rss/ctvnews-ca-canada-1.2089050",
    }),
    ("US NEWS", {
        "NPR US":             "https://feeds.npr.org/1001/rss.xml",
        "AP Top Stories":     "https://www.apnews.com/apf-topnews?format=rss",
    }),
    ("INTERNATIONAL NEWS", {
        "Reuters World":      "https://feeds.reuters.com/Reuters/worldNews",
        "BBC World":          "http://feeds.bbci.co.uk/news/world/rss.xml",
    }),
    ("PUBLIC HEALTH", {
        "PHAC Updates":       "https://www.canada.ca/etc/+/health/public-health-updates.rss",
    }),
    ("AI & EMERGING TECH", {
        "Ars Tech Policy":    "https://feeds.arstechnica.com/arstechnica/technology-policy",
        "MIT Tech Review":    "https://www.technologyreview.com/feed/",
        "IEEE Spectrum AI":   "https://spectrum.ieee.org/rss/topic/artificial-intelligence",
    }),
    ("CYBERSECURITY & PRIVACY", {
        "KrebsOnSecurity":    "https://krebsonsecurity.com/feed/",
        "Schneier on Security":"https://www.schneier.com/blog/atom.xml",
    }),
    ("ENTERPRISE ARCHITECTURE", {
        "OpenGroup News":     "https://publications.opengroup.org/rss.xml",
    }),
    ("GEOMATICS", {
        "Geospatial World":   "https://www.geospatialworld.net/feed/",
    }),
    ("CLOUD PROVIDERS", {
        "Microsoft Azure":    "https://azure.microsoft.com/feed/",
        "AWS News Blog":      "https://aws.amazon.com/new/feed/",
        "Google Cloud":       "https://cloud.google.com/blog/rss",
    }),
]

# ─── HELPERS ──────────────────────────────────────────────────────────────────

def fetch_weather():
    hdr = f"Ottawa Weather – {datetime.now():%B %d, %Y}"
    try:
        r = requests.get(WEATHER_FEED, timeout=10)
        r.raise_for_status()
        # parse with BeautifulSoup to extract <description> of first three <period>s
        soup = BeautifulSoup(r.content, "xml")
        periods = soup.find_all("period")[:3]
        lines = [hdr]
        for p in periods:
            title = p.find("name").text
            desc  = p.find("text").text.replace("\n", " ")
            lines.append(f"• {title}: {desc}")
        return "\n".join(lines)
    except Exception:
        return hdr + "\n• (weather data unavailable)"

def format_entry(e):
    title   = e.get("title", "").strip()
    # strip HTML tags
    summary = BeautifulSoup(e.get("summary", ""), "html.parser").get_text().strip()
    pub     = ""
    if e.get("published_parsed"):
        pub = datetime(*e.published_parsed[:6]).strftime("%b %d, %Y")
    return f"• {title}\n  {summary} {{ {pub} }}"

def collect_section(name, feeds, top_n=2):
    parts = [f"\n{name}"]
    for label, url in feeds.items():
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            feed = feedparser.parse(r.content)
            if not feed.entries:
                parts.append(f"• {label}: (no entries)")
            else:
                for e in feed.entries[:top_n]:
                    parts.append(format_entry(e))
        except Exception:
            parts.append(f"• {label}: (unavailable)")
    return "\n".join(parts)

# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    sections = []
    # 1) weather
    sections.append(fetch_weather())

    # 2–n) all other
    for title, feeds in SECTIONS:
        if title == "WEATHER":
            continue
        sections.append(collect_section(title, feeds))

    sections.append("\n— End of briefing —")

    with open("latest.txt", "w", encoding="utf-8") as f:
        f.write("\n\n".join(sections))

if __name__ == "__main__":
    main()