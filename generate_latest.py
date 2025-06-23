import feedparser
from datetime import datetime

# --- CONFIG ---
RSS_FEEDS = {
    "Canadian Headlines": [
        "https://rss.cbc.ca/lineup/topstories.xml",
        "https://www.ctvnews.ca/rss/ctvnews-ca-canada-1.2089050"
    ],
    "U.S. Top Stories": [
        "https://feeds.npr.org/1001/rss.xml",
        "https://rss.cnn.com/rss/edition_us.rss"
    ],
    "International Top Stories": [
        "https://feeds.reuters.com/Reuters/worldNews",
        "http://feeds.bbci.co.uk/news/world/rss.xml"
    ],
    "Public Health": [
        "https://www.canada.ca/etc/+/health/public-health-updates.rss"
    ],
    "AI & Emerging Tech": [
        "https://feeds.arstechnica.com/arstechnica/technology-policy",
        "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml"
    ],
    "Cybersecurity & Privacy": [
        "https://krebsonsecurity.com/feed/",
        "https://www.schneier.com/blog/atom.xml"
    ],
    "Enterprise Architecture & IT Governance": [
        "https://www.opengroup.org/news/rss",
        "https://enterprisearchitect.org/rss"
    ],
    "Geomatics": [
        "https://www.geospatialworld.net/feed/",
        "https://www.gim-international.com/rss"
    ]
}

# Environment Canada Ottawa forecast
WEATHER_FEED = "https://dd.weather.gc.ca/citypage_weather/xml/ON/s0000430_e.xml"

def fetch_weather():
    feed = feedparser.parse(WEATHER_FEED)
    entries = feed.entries
    today = entries[0] if len(entries) > 0 else None
    tomorrow = entries[1] if len(entries) > 1 else None
    day_after = entries[2] if len(entries) > 2 else None
    lines = [f"Ottawa Weather – {datetime.now():%B %d, %Y}"]
    for e in (today, tomorrow, day_after):
        if not e: continue
        period = e.title
        desc = e.summary.replace("<![CDATA[", "").replace("]]>", "").strip()
        lines.append(f"• {period}: {desc}")
    return "\n".join(lines)

def format_entry(entry):
    text = entry.get("summary", "").strip()
    if hasattr(entry, "content") and entry.content:
        text = entry.content[0].value.strip()
    import re
    text = re.sub(r"<[^>]+>", "", text)
    date = ""
    if getattr(entry, "published_parsed", None):
        date = datetime(*entry.published_parsed[:6]).strftime("%B %d, %Y")
    return f"• {entry.title}\n  {text} {{{date}}}"

def collect_section(name, urls, count=2):
    lines = [f"{name} – {datetime.now():%B %d, %Y}"]
    added = 0
    for url in urls:
        feed = feedparser.parse(url)
        for e in feed.entries[:count]:
            lines.append(format_entry(e))
            added += 1
        if added >= count:
            break
    if added == 0:
        lines.append("(no entries)")
    return "\n".join(lines)

def main():
    parts = [fetch_weather(), ""]
    for section, urls in RSS_FEEDS.items():
        parts.append(collect_section(section, urls))
        parts.append("")
    parts.append("— End of briefing —")
    out = "\n".join(parts)
    with open("latest.txt", "w", encoding="utf-8") as f:
        f.write(out)
    print("latest.txt updated")

if __name__ == "__main__":
    main()