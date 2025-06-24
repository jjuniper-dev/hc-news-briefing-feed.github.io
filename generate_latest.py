#!/usr/bin/env python3
import requests
import feedparser
from datetime import datetime, timedelta

# ——— CONFIG ———

CANADIAN_FEEDS = [
    ("CBC Top Stories",     "https://rss.cbc.ca/lineup/topstories.xml"),
    ("CTV Canada",          "https://www.ctvnews.ca/rss/ctvnews-ca-canada-1.2089050"),
    ("BBC Canada",          "https://feeds.bbci.co.uk/news/world/canada/rss.xml"),
]

US_FEEDS = [
    ("NPR US",              "https://feeds.npr.org/1001/rss.xml"),
    ("AP Top Stories",      "https://feeds.a.dj.com/rss/RSSWorldNews.xml"),
]

INTERNATIONAL_FEEDS = [
    ("Reuters World",       "https://feeds.reuters.com/Reuters/worldNews"),
    ("BBC World",           "http://feeds.bbci.co.uk/news/world/rss.xml"),
]

PUBLIC_HEALTH_FEEDS = [
    ("PHAC Updates",        "https://www.canada.ca/etc/+/health/public-health-updates.rss"),
]

AI_FEEDS = [
    ("Ars Tech Policy",     "https://feeds.arstechnica.com/arstechnica/technology-policy"),
    ("Tech Review AI",      "https://www.technologyreview.com/feed/"),
    ("IEEE Spectrum AI",    "https://spectrum.ieee.org/rss/topic/artificial-intelligence"),
]

CYBER_FEEDS = [
    ("KrebsOnSecurity",     "https://krebsonsecurity.com/feed/"),
]

EA_FEEDS = [
    ("OpenGroup News",      "https://www.opengroup.org/news/rss"),
]

GEOMATICS_FEEDS = [
    ("Geospatial World",    "https://www.geospatialworld.net/feed/"),
]

CLOUD_FEEDS = [
    ("Azure Blog",          "https://azure.microsoft.com/en-us/blog/feed/"),
    ("AWS News Blog",       "https://aws.amazon.com/new/feed/"),
    ("Google Cloud",        "https://cloud.google.com/blog/rss/"),
]

WEATHER_FEEDS = [
    # 1) EC
    ("EnvCanada Ottawa",     "https://dd.weather.gc.ca/rss/city/on-118_e.xml"),
    # 2) NOAA
    ("NOAA Ottawa",          "https://w1.weather.gov/xml/current_obs/ CYOW.rss"),
    # 3) OpenWeatherMap (example; requires an API key query param)
    ("OWM Ottawa",           "https://api.openweathermap.org/data/2.5/forecast?q=Ottawa,CA&appid=YOUR_KEY&units=metric&mode=xml"),
]

# ——— HELPERS ———

def fetch_feed_entries(label, url, max_items=2):
    """Fetch up to max_items entries from the RSS, returning list of (title, summary, date)."""
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        feed = feedparser.parse(resp.content)
        items = []
        for e in feed.entries[:max_items]:
            # pick summary or content
            summary = ""
            if "content" in e:
                summary = e.content[0].value
            else:
                summary = e.get("summary", "")
            date = ""
            if "published_parsed" in e:
                date = datetime(*e.published_parsed[:6]).strftime("%b %d, %Y")
            items.append((e.title, summary.strip().replace("\n"," "), date))
        return items
    except Exception:
        return []

def get_weather_block():
    today = datetime.now().date()
    lines = [f"Ottawa Weather – {today.strftime('%B %d, %Y')}"]
    for label, url in WEATHER_FEEDS:
        entries = fetch_feed_entries(label, url, max_items=3)
        if entries:
            lines.append(f"\n{label}:")
            for title, summary, date in entries:
                lines.append(f"• {title}: {summary}")
            return "\n".join(lines)
    # fallback
    return "Ottawa Weather – (data unavailable)"

def section_block(name, feeds):
    lines = [f"\n{name.upper()}"]
    for label, url in feeds:
        items = fetch_feed_entries(label, url, max_items=2)
        if not items:
            lines.append(f"• {label}: (unavailable)")
        else:
            for title, summary, date in items:
                block = f"• {title}\n  {summary}"
                if date:
                    block += f" {{ {date} }}"
                lines.append(block)
    return "\n".join(lines)

# ——— MAIN ———

def main():
    header = f"Morning News Briefing – {datetime.now().strftime('%B %d, %Y %H:%M')}"
    parts = [header, get_weather_block()]
    parts.append(section_block("Canadian News",    CANADIAN_FEEDS))
    parts.append(section_block("US News",          US_FEEDS))
    parts.append(section_block("International News", INTERNATIONAL_FEEDS))
    parts.append(section_block("Public Health",    PUBLIC_HEALTH_FEEDS))
    parts.append(section_block("AI & Emerging Tech", AI_FEEDS))
    parts.append(section_block("Cybersecurity & Privacy", CYBER_FEEDS))
    parts.append(section_block("Enterprise Architecture", EA_FEEDS))
    parts.append(section_block("Geomatics",        GEOMATICS_FEEDS))
    parts.append(section_block("Cloud Providers",  CLOUD_FEEDS))
    parts.append("\n— End of briefing —")
    with open("latest.txt", "w", encoding="utf-8") as f:
        f.write("\n\n".join(parts))

if __name__ == "__main__":
    main()