#!/usr/bin/env python3
import requests
import feedparser
import xml.etree.ElementTree as ET
from datetime import datetime

# ─── CONFIG ───────────────────────────────────────────────────────────────────

# Environment Canada XML for Ottawa
WEATHER_FEED = "https://dd.weather.gc.ca/citypage_weather/xml/ON/s0000660_e.xml"

SECTIONS = [
    ("WEATHER", None),
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
        "KrebsOnSecurity":     "https://krebsonsecurity.com/feed/",
        "Schneier on Security": "https://www.schneier.com/blog/atom.xml",
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
    header = f"Ottawa Weather – {datetime.now():%B %d, %Y}"
    try:
        r = requests.get(WEATHER_FEED, timeout=10)
        r.raise_for_status()
        tree = ET.fromstring(r.content)
        periods = tree.findall(".//period")[:3]
        lines = [header]
        for p in periods:
            name = p.findtext("name", default="").strip()
            desc = p.findtext("text", default="").strip().replace("\n", " ")
            lines.append(f"• {name}: {desc}")
        return "\n".join(lines)
    except Exception:
        return header + "\n• (weather data unavailable)"

def format_entry(e):
    title = e.get("title", "").strip()
    summary = e.get("summary", "").strip()
    # strip any embedded HTML tags
    summary = ET.fromstring(f"<root>{summary}</root>").text or summary
    pub = ""
    if e.get("published_parsed"):
        pub = datetime(*e.published_parsed[:6]).strftime("%b %d, %Y")
    return f"• {title}\n  {summary} {{ {pub} }}"

def collect_section(name, feeds, top_n=2):
    out = [f"\n{name}"]
    for label, url in feeds.items():
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            feed = feedparser.parse(r.content)
            if not feed.entries:
                out.append(f"• {label}: (no entries)")
            else:
                for e in feed.entries[:top_n]:
                    out.append(format_entry(e))
        except Exception:
            out.append(f"• {label}: (unavailable)")
    return "\n".join(out)

# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    parts = [fetch_weather()]
    for title, feeds in SECTIONS:
        if title == "WEATHER":
            continue
        parts.append(collect_section(title, feeds))
    parts.append("\n— End of briefing —")
    with open("latest.txt", "w", encoding="utf-8") as f:
        f.write("\n\n".join(parts))

if __name__ == "__main__":
    main()