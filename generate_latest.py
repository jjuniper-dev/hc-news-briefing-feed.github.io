#!/usr/bin/env python3
import sys
import requests
import feedparser
from datetime import datetime
from xml.etree import ElementTree

# --- CONFIG ---
SECTIONS = {
    "WEATHER": [
        "https://dd.weather.gc.ca/citypage_weather/xml/ON/s0000430_e.xml",  # Ottawa
    ],
    "CANADIAN NEWS": [
        "https://rss.cbc.ca/lineup/topstories.xml",
        "https://www.ctvnews.ca/rss/ctvnews-ca-canada-1.2089050",
        # fallback:
        "http://feeds.bbci.co.uk/news/world/us_and_canada/rss.xml"
    ],
    "US NEWS": [
        "https://feeds.npr.org/1001/rss.xml",
        "https://rss.nytimes.com/services/xml/rss/nyt/US.xml",
    ],
    "INTERNATIONAL": [
        "https://feeds.reuters.com/Reuters/worldNews",
        "http://feeds.bbci.co.uk/news/world/rss.xml",
    ],
    # … add other sections here …
}

TODAY = datetime.now().strftime("%B %d, %Y")

def safe_fetch(url, parser_fn):
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        return parser_fn(r.content)
    except Exception as e:
        print(f"⚠️  fetch failed for {url}: {e}", file=sys.stderr)
        return None

def get_weather():
    data = safe_fetch(SECTIONS["WEATHER"][0], lambda c: ElementTree.fromstring(c))
    if data is None: 
        return "(no weather data available)"
    # parse the first three periods
    periods = data.findall(".//period")
    out = [f"Ottawa Weather – {TODAY}"]
    for p in periods[:3]:
        name = p.findtext("period-hour") or p.findtext("period")
        desc = p.findtext("weather") or p.findtext("textForecast")
        out.append(f"• {name}: {desc}")
    return "\n".join(out)

def parse_feed_items(content):
    feed = feedparser.parse(content)
    items = []
    for e in feed.entries[:2]:
        date = getattr(e, "published", "")
        items.append(f"• {e.title.strip()} {{{date}}}")
    return items

def collect_section(title, urls):
    lines = [f"\n{title} – {TODAY}"]
    for url in urls:
        items = safe_fetch(url, lambda c: parse_feed_items(c))
        if items:
            lines.extend(items)
            return lines
    lines.append("(no data available)")
    return lines

def main():
    parts = [f"Morning News Briefing – {TODAY}", ""]
    # WEATHER
    parts.append(get_weather())
    # other sections
    for section, urls in SECTIONS.items():
        if section == "WEATHER":
            continue
        parts.extend(collect_section(section, urls))
    parts.append("\n— End of briefing —")
    text = "\n\n".join(parts)
    with open("latest.txt", "w", encoding="utf-8") as f:
        f.write(text)
    print("✅ latest.txt updated")

if __name__ == "__main__":
    main()