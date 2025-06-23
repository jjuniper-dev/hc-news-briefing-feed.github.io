#!/usr/bin/env python3
import feedparser
import requests
from datetime import datetime

# ─── CONFIG ───────────────────────────────────────────────────────────────────

# Weather (Ottawa) RSS
WEATHER_FEED = "https://dd.weather.gc.ca/citypage_weather/xml/ON/s0000660_e.xml"

# Section → { "Source name": "RSS URL", ... }
CANADIAN_FEEDS = {
    "CBC Top Stories":    "https://rss.cbc.ca/lineup/topstories.xml",
    "CTV Canada":         "https://www.ctvnews.ca/rss/ctvnews-ca-canada-1.2089050"
}
US_FEEDS = {
    "NPR US":             "https://feeds.npr.org/1001/rss.xml",
    "AP Top Stories":     "https://www.apnews.com/apf-topnews?format=rss"
}
INTERNATIONAL_FEEDS = {
    "Reuters World":      "https://feeds.reuters.com/Reuters/worldNews",
    "BBC World":          "http://feeds.bbci.co.uk/news/world/rss.xml"
}
PUBLIC_HEALTH_FEEDS = {
    "PHAC Updates":       "https://www.canada.ca/etc/+/health/public-health-updates.rss"
}
AI_FEEDS = {
    "Ars Tech Policy":    "https://feeds.arstechnica.com/arstechnica/technology-policy",
    "MIT Tech Review":    "https://www.technologyreview.com/feed/"
}
CYBER_FEEDS = {
    "KrebsOnSecurity":    "https://krebsonsecurity.com/feed/",
    "Schneier on Security":"https://www.schneier.com/blog/atom.xml"
}
EA_FEEDS = {
    "OpenGroup News":     "https://publications.opengroup.org/rss.xml"
}
GEOMATICS_FEEDS = {
    "Geospatial World":   "https://www.geospatialworld.net/feed/"
}
# ─── NEW: Cloud Providers ──────────────────────────────────────────────────────
CLOUD_FEEDS = {
    "Microsoft Azure":    "https://azure.microsoft.com/feed/",
    "AWS News Blog":      "https://aws.amazon.com/new/feed/",
    "Google Cloud":       "https://cloud.google.com/blog/rss",
    # add more as needed...
}

# ─── HELPERS ──────────────────────────────────────────────────────────────────

def fetch_weather():
    """Return a three-day Ottawa forecast plus any warnings."""
    feed = feedparser.parse(WEATHER_FEED)
    entries = feed.entries[:3]
    lines = [f"Ottawa Weather – {datetime.now():%B %d, %Y}"]
    for e in entries:
        # title often contains period/time; summary is description
        lines.append(f"• {e.title.strip()}: {e.summary.strip()}")
    return "\n".join(lines)

def format_entry(e):
    """Format one feedparser entry into a bullet + summary + citation."""
    title = e.title.strip()
    link = getattr(e, "link", "")
    summary = getattr(e, "summary", "").replace("\n"," ").strip()
    pub = ""
    if hasattr(e, "published_parsed") and e.published_parsed:
        pub = datetime(*e.published_parsed[:6]).strftime("%b %d, %Y")
    source = getattr(e, "source", {}).get("title", "") or ""
    cite = f"{pub}{(' – ' + source) if source else ''}"
    return f"• {title}\n  {summary} {{{cite}}}"

def collect_section(label, feeds, top_n=2):
    """Pull top_n entries from each feed in feeds dict."""
    parts = [f"\n{label.upper()}"]
    for name, url in feeds.items():
        feed = feedparser.parse(url)
        entries = feed.entries[:top_n]
        if entries:
            for e in entries:
                parts.append(format_entry(e))
        else:
            parts.append(f"• {name}: (no data)")
    return "\n".join(parts)

# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    all_parts = []
    all_parts.append(fetch_weather())
    all_parts.append(collect_section("Canadian News", CANADIAN_FEEDS))
    all_parts.append(collect_section("US News", US_FEEDS))
    all_parts.append(collect_section("International News", INTERNATIONAL_FEEDS))
    all_parts.append(collect_section("Public Health", PUBLIC_HEALTH_FEEDS))
    all_parts.append(collect_section("AI & Emerging Tech", AI_FEEDS))
    all_parts.append(collect_section("Cybersecurity & Privacy", CYBER_FEEDS))
    all_parts.append(collect_section("Enterprise Architecture", EA_FEEDS))
    all_parts.append(collect_section("Geomatics", GEOMATICS_FEEDS))
    all_parts.append(collect_section("Cloud Providers", CLOUD_FEEDS))
    all_parts.append("\n— End of briefing —")

    with open("latest.txt", "w", encoding="utf-8") as f:
        f.write("\n\n".join(all_parts))

if __name__ == "__main__":
    main()