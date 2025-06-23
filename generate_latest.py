#!/usr/bin/env python3
import sys
import requests
import feedparser
from datetime import datetime

# --- CONFIG ---
# RSS feeds by section (add or remove URLs as you wish)
SECTIONS = {
    "CANADIAN NEWS": [
        "https://rss.cbc.ca/lineup/topstories.xml",
        "https://www.ctvnews.ca/rss/ctvnews-ca-canada-1.2089050"
    ],
    "US NEWS": [
        "https://feeds.npr.org/1001/rss.xml",
        "https://rss.cnn.com/rss/edition_us.rss"
    ],
    "INTERNATIONAL NEWS": [
        "https://feeds.reuters.com/Reuters/worldNews",
        "http://feeds.bbci.co.uk/news/world/rss.xml"
    ],
    "PUBLIC HEALTH": [
        "https://www.canada.ca/etc/+/health/public-health-updates.rss"
    ],
    "AI & EMERGING TECH": [
        "https://feeds.arstechnica.com/arstechnica/technology-policy",
        "https://www.technologyreview.com/feed/"
    ],
    "CYBERSECURITY & PRIVACY": [
        "https://krebsonsecurity.com/feed/",
        "https://www.schneier.com/blog/atom.xml"
    ],
    "ENTERPRISE ARCHITECTURE": [
        "https://www.opengroup.org/news/rss"
    ],
    "GEOMATICS": [
        "https://www.geospatialworld.net/feed/"
    ],
    "CLOUD PROVIDERS": [
        "https://azure.microsoft.com/en-us/updates/feed/",
        "https://aws.amazon.com/new/feed/",
        "https://cloud.google.com/blog/feed.atom"
    ],
}

# Coordinates for Ottawa
LAT, LON = 45.4215, -75.6972

# --- WEATHER FETCHING ---

def fetch_environment_canada():
    """Try Environment Canada RSS for Ottawa (on-region)."""
    try:
        url = "https://dd.weather.gc.ca/citypage_weather/xml/ON/s0000430_e.xml"
        feed = feedparser.parse(url)
        today = feed.entries[0]
        tomorrow = feed.entries[1] if len(feed.entries) > 1 else None
        lines = [
            f"Ottawa Weather – {datetime.now():%B %d, %Y} (EnvCan)",
            f"• {today.title}: {today.summary}",
        ]
        if tomorrow:
            lines.append(f"• {tomorrow.title}: {tomorrow.summary}")
        return "\n".join(lines)
    except Exception:
        raise

def fetch_wttr():
    """Fallback to wttr.in JSON for Ottawa."""
    try:
        url = "https://wttr.in/Ottawa?format=j1"
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        j = r.json()
        today = j["current_condition"][0]
        forecast = j["weather"][:2]
        lines = [f"Ottawa Weather – {datetime.now():%B %d, %Y} (wttr.in)"]
        lines.append(f"• Now: {today['weatherDesc'][0]['value']}, {today['temp_C']}°C")
        for day in forecast:
            d = datetime.strptime(day["date"], "%Y-%m-%d").strftime("%A")
            lines.append(f"• {d}: {day['maxtempC']}°C/{day['mintempC']}°C, {day['hourly'][4]['weatherDesc'][0]['value']}")
        return "\n".join(lines)
    except Exception:
        raise

def fetch_noaa():
    """Tertiary fallback: NOAA/NWS API by lat/lon."""
    try:
        # 1) Find gridpoint for Ottawa
        pts = requests.get(f"https://api.weather.gov/points/{LAT},{LON}", timeout=5,
                           headers={"User-Agent":"DailyBriefingBot"}).json()
        grid = pts["properties"]["forecastGridData"]
        # 2) Fetch forecast grid
        r2 = requests.get(grid, timeout=5, headers={"User-Agent":"DailyBriefingBot"})
        r2.raise_for_status()
        periods = r2.json()["properties"]["periods"][:3]
        lines = [f"Ottawa Weather – {datetime.now():%B %d, %Y} (NOAA)"]
        for p in periods:
            lines.append(f"• {p['name']}: {p['shortForecast']} ({p['temperature']}°{p['temperatureUnit']})")
        return "\n".join(lines)
    except Exception:
        raise

def fetch_weather():
    """Attempt the three-tiered weather fetch, else indicate failure."""
    for fn in (fetch_environment_canada, fetch_wttr, fetch_noaa):
        try:
            return fn()
        except Exception:
            continue
    return f"Ottawa Weather – {datetime.now():%B %d, %Y}\n• (weather data unavailable)"

# --- NEWS FETCHING & FORMATTING ---

def format_entry(entry):
    """Use full content if available, else summary; strip excessive whitespace."""
    text = ""
    if entry.get("content"):
        text = entry.content[0].value
    else:
        text = entry.get("summary", "")
    text = text.replace("\n", " ").strip()
    date = ""
    if entry.get("published_parsed"):
        date = datetime(*entry.published_parsed[:6]).strftime("%b %d, %Y")
    source = entry.get("source", {}).get("title") or entry.get("link", "").split("/")[2]
    return f"• {entry.title.strip()}\n  {text} {{{date} ({source})}}"

def collect_section(name, urls, topn=2):
    """Collect up to topn entries from each URL in this section."""
    parts = [f"\n{name} – {datetime.now():%B %d, %Y}"]
    any_found = False
    for url in urls:
        try:
            feed = feedparser.parse(url)
            entries = feed.entries[:topn]
            for e in entries:
                parts.append(format_entry(e))
                any_found = True
        except Exception:
            continue
    if not any_found:
        parts.append("• (no entries)")
    return "\n".join(parts)

# --- MAIN ---

def main():
    with open("latest.txt", "w", encoding="utf-8") as f:
        # WEATHER
        f.write(fetch_weather())
        f.write("\n\n")
        # NEWS SECTIONS
        for section, urls in SECTIONS.items():
            f.write(collect_section(section, urls))
            f.write("\n\n")
        f.write("— End of briefing —\n")

if __name__ == "__main__":
    main()