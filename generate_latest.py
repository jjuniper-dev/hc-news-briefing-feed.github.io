#!/usr/bin/env python3
import feedparser
import requests
from datetime import datetime

# ─── CONFIG ───────────────────────────────────────────────────────────────────

WEATHER_FEED = "https://dd.weather.gc.ca/citypage_weather/xml/ON/s0000660_e.xml"

SECTIONS = {
    "Canadian News": {
        "CBC Top Stories":    "https://rss.cbc.ca/lineup/topstories.xml",
        "CTV Canada":         "https://www.ctvnews.ca/rss/ctvnews-ca-canada-1.2089050",
    },
    "US News": {
        "NPR US":             "https://feeds.npr.org/1001/rss.xml",
        "AP Top Stories":     "https://www.apnews.com/apf-topnews?format=rss",
    },
    "International News": {
        "Reuters World":      "https://feeds.reuters.com/Reuters/worldNews",
        "BBC World":          "http://feeds.bbci.co.uk/news/world/rss.xml",
    },
    "Public Health": {
        "PHAC Updates":       "https://www.canada.ca/etc/+/health/public-health-updates.rss",
    },
    "AI & Emerging Tech": {
        "Ars Tech Policy":    "https://feeds.arstechnica.com/arstechnica/technology-policy",
        "MIT Tech Review":    "https://www.technologyreview.com/feed/",
    },
    "Cybersecurity & Privacy": {
        "KrebsOnSecurity":    "https://krebsonsecurity.com/feed/",
        "Schneier on Security":"https://www.schneier.com/blog/atom.xml",
    },
    "Enterprise Architecture": {
        "OpenGroup News":     "https://publications.opengroup.org/rss.xml",
    },
    "Geomatics": {
        "Geospatial World":   "https://www.geospatialworld.net/feed/",
    },
    "Cloud Providers": {
        "Microsoft Azure":    "https://azure.microsoft.com/feed/",
        "AWS News Blog":      "https://aws.amazon.com/new/feed/",
        "Google Cloud":       "https://cloud.google.com/blog/rss",
    },
}

# ─── HELPERS ──────────────────────────────────────────────────────────────────

def fetch_weather():
    lines = [f"Ottawa Weather – {datetime.now():%B %d, %Y}"]
    try:
        resp = requests.get(WEATHER_FEED, timeout=10)
        resp.raise_for_status()
        feed = feedparser.parse(resp.content)
        for e in feed.entries[:3]:
            lines.append(f"• {e.title.strip()}: {e.summary.strip()}")
    except Exception:
        lines.append("• (weather data unavailable)")
    return "\n".join(lines)


def format_entry(e):
    title = e.get("title", "").strip()
    summary = e.get("summary", "").replace("\n", " ").strip()
    pub = ""
    if e.get("published_parsed"):
        pub = datetime(*e.published_parsed[:6]).strftime("%b %d, %Y")
    source = e.get("source", {}).get("title", "")
    cite = f"{pub}{(' – ' + source) if source else ''}"
    return f"• {title}\n  {summary} {{{cite}}}"


def collect_section(label, feeds, top_n=2):
    parts = [f"\n{label.upper()}"]
    for name, url in feeds.items():
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            feed = feedparser.parse(resp.content)
            entries = feed.entries[:top_n]
            if entries:
                for e in entries:
                    parts.append(format_entry(e))
            else:
                parts.append(f"• {name}: (no entries)")
        except Exception:
            parts.append(f"• {name}: (unavailable)")
    return "\n".join(parts)


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    out = []
    out.append(fetch_weather())
    for section, feeds in SECTIONS.items():
        out.append(collect_section(section, feeds))
    out.append("\n— End of briefing —")

    with open("latest.txt", "w", encoding="utf-8") as f:
        f.write("\n\n".join(out))


if __name__ == "__main__":
    main()