#!/usr/bin/env python3
import feedparser
import requests
from datetime import datetime

# --- CONFIG -------------------------------------------------------------

# Backup weather URLs
WEATHER_FEEDS = [
    ("Environment Canada (Ottawa)", "https://dd.weather.gc.ca/rss/city/on-118_e.xml"),
    ("NOAA (Ottawa)",               "https://w1.weather.gov/xml/current_obs/CYOW.xml")  # example; you may need to convert XML→RSS
]

RSS_FEEDS = {
    "CANADIAN NEWS": [
        ("CBC Canada",       "https://rss.cbc.ca/lineup/canada.xml"),
        ("CTV Canada",       "https://www.ctvnews.ca/rss/ctvnews-ca-canada-1.2089050"),
        ("Reddit – Canada",          "https://www.reddit.com/r/Canada/.rss"),
        ("Reddit – Canadian Politics","https://www.reddit.com/r/CanadianPolitics/.rss"),
        ("Reddit – Breaking Canada", "https://www.reddit.com/r/canadanews/.rss"),
    ],
    "US NEWS": [
        ("NPR US",         "https://feeds.npr.org/1001/rss.xml"),
        ("AP Top Stories", "https://apnews.com/apf-topnews?format=xml"),
    ],
    "INTERNATIONAL NEWS": [
        ("Reuters World", "https://feeds.reuters.com/Reuters/worldNews"),
        ("BBC World",     "http://feeds.bbci.co.uk/news/world/rss.xml"),
    ],
    "PUBLIC HEALTH": [
        ("PHAC Updates", "https://www.canada.ca/etc/+/health/public-health-updates.rss"),
    ],
    "AI & EMERGING TECH": [
        ("Ars Tech Policy",        "https://feeds.arstechnica.com/arstechnica/technology-policy"),
        ("Reddit – MachineLearning","https://www.reddit.com/r/MachineLearning/.rss"),
        ("Reddit – artificial",     "https://www.reddit.com/r/artificial/.rss"),
        ("Reddit – TechPolicy",     "https://www.reddit.com/r/TechPolicy/.rss"),
    ],
    "CYBERSECURITY & PRIVACY": [
        ("KrebsOnSecurity",      "https://krebsonsecurity.com/feed/"),
        ("Ars Security",         "https://feeds.arstechnica.com/arstechnica/security"),
    ],
    "ENTERPRISE ARCHITECTURE": [
        ("OpenGroup News",       "https://www.opengroup.org/news/rss"),
        ("Gartner EA (blog)",    "https://www.gartner.com/en/information-technology/insights/enterprise-architecture/rss"),
    ],
    "GEOMATICS": [
        ("Geospatial World",     "https://www.geospatialworld.net/feed/"),
    ],
    "CLOUD PROVIDERS": [
        ("Microsoft Azure",      "https://azure.microsoft.com/en-us/updates/feed/"),
        ("AWS News Blog",        "https://aws.amazon.com/about-aws/whats-new/recent/feed/"),
        ("Google Cloud",         "https://cloud.google.com/blog/feed.xml"),
    ],
}

# Number of items per source
ITEMS_PER_FEED = 2

# ------------------------------------------------------------------------


def fetch_weather():
    out = [f"Ottawa Weather – {datetime.now():%B %d, %Y}"]
    for name, url in WEATHER_FEEDS:
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            feed = feedparser.parse(resp.content)
            # take first two entries if available
            for entry in feed.entries[:2]:
                title = entry.get("title", "").strip()
                summary = entry.get("summary", "").strip()
                out.append(f"• {title}: {summary}")
            break  # stop after first successful feed
        except Exception:
            continue
    else:
        out.append("• (no weather data available)")
    return "\n".join(out)


def fetch_section(name, sources):
    lines = [f"\n{name} – {datetime.now():%B %d, %Y}"]
    any_ok = False
    for src_name, url in sources:
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            feed = feedparser.parse(resp.content)
            entries = feed.entries[:ITEMS_PER_FEED]
            if not entries:
                lines.append(f"• {src_name}: (unavailable)")
                continue
            any_ok = True
            for e in entries:
                # full text if available, else summary
                text = ""
                if e.get("content"):
                    text = e.content[0].value.strip()
                else:
                    text = e.get("summary", "").strip()
                pub = ""
                if e.get("published_parsed"):
                    pub = datetime(*e.published_parsed[:6]).strftime("%b %d, %Y")
                lines.append(f"• {src_name}: {e.title.strip()}\n  {text} {{{pub}}}")
        except Exception:
            lines.append(f"• {src_name}: (unavailable)")
    if not any_ok:
        lines.append("• (no data available)")
    return "\n".join(lines)


def main():
    parts = []
    parts.append(fetch_weather())
    for section, sources in RSS_FEEDS.items():
        parts.append(fetch_section(section, sources))
    parts.append("\n— End of briefing —")
    print("\n".join(parts))
    with open("latest.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(parts))


if __name__ == "__main__":
    main()