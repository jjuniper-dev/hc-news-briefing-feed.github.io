#!/usr/bin/env python3
import json
import re
import sys
from datetime import datetime
from dateutil import tz
import requests
import feedparser

# ─── CONFIG ────────────────────────────────────────────────────────────────────
WEATHER_FEEDS = [
    ("Environment Canada (Ottawa)", "https://dd.weather.gc.ca/rss/city/on-118_e.xml"),
    ("NOAA (Ottawa)",          "https://w1.weather.gov/xml/current_obs/CYOW.rss"),
    ("OpenWeatherMap (Ottawa)", "https://api.openweathermap.org/data/2.5/weather?q=Ottawa,CA&mode=xml&appid=YOUR_API_KEY"),
]

CANADIAN_FEEDS = [
    ("CBC Top Stories", "https://rss.cbc.ca/lineup/topstories.xml"),
    ("CTV Canada",      "https://www.ctvnews.ca/rss/ctvnews-ca-canada-1.2089050"),
    ("BBC Canada",      "http://feeds.bbci.co.uk/news/world/us_and_canada/rss.xml"),
]

AI_EA_FEEDS = [
    ("Ars Technica – Tech Policy", "https://feeds.arstechnica.com/arstechnica/technology-policy"),
    ("MIT Tech Review – AI",       "https://www.technologyreview.com/feed/"),
    ("IEEE Spectrum – AI",         "https://spectrum.ieee.org/rss/robotics/artificial-intelligence"),
]

CACHE_FILE = "cache.json"
OUTPUT_FILE = "latest.txt"
MAX_PER_SECTION = 2

# ─── UTILITIES ──────────────────────────────────────────────────────────────────
def clean_html(raw):
    return re.sub(r'<[^>]+>', '', raw or "").strip()

def try_feeds(feeds):
    for name, url in feeds:
        try:
            r = requests.get(url, timeout=15)
            r.raise_for_status()
            fp = feedparser.parse(r.content)
            if fp.entries:
                return name, fp.entries
        except Exception:
            continue
    return None, []

# ─── WEATHER ───────────────────────────────────────────────────────────────────
def fetch_weather():
    label, entries = try_feeds(WEATHER_FEEDS)
    if not entries:
        return None
    # take first three items if available
    items = entries[:3]
    lines = [f"{label} – {datetime.now(tz.tzlocal()).strftime('%B %d, %Y')}"]
    for e in items:
        title = clean_html(getattr(e, "title", ""))
        summary = clean_html(getattr(e, "summary", ""))
        lines.append(f"• {title}: {summary}")
    return "\n".join(lines)

# ─── NEWS SECTIONS ─────────────────────────────────────────────────────────────
def collect_section(header, feeds):
    lines = [f"{header}"]
    for name, url in feeds[:]:  # slice in case you want to trim
        try:
            r = requests.get(url, timeout=15)
            r.raise_for_status()
            fp = feedparser.parse(r.content)
            entries = fp.entries[:MAX_PER_SECTION]
        except Exception:
            entries = []
        if not entries:
            lines.append(f"• {name}: (unavailable)")
            continue
        for e in entries:
            title = clean_html(getattr(e, "title", ""))
            txt   = clean_html(getattr(e, "summary", ""))
            date  = ""
            if "published_parsed" in e:
                date = datetime(*e.published_parsed[:6]).strftime("%b %d, %Y")
            source = getattr(e, "source", {}).get("title", "")
            lines.append(f"• {title}\n  {txt} {{{date}{(' ('+source+')') if source else ''}}}")
    return "\n".join(lines)

# ─── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    # load cache
    try:
        cache = json.load(open(CACHE_FILE))
    except FileNotFoundError:
        cache = {}

    weather = fetch_weather()
    can_news = collect_section("CANADIAN NEWS", CANADIAN_FEEDS)
    ai_ea    = collect_section("AI & EA", AI_EA_FEEDS)

    # if sections all empty, fallback to cache
    if not any([weather, can_news.strip("CANADIAN NEWS\r\n "), ai_ea.strip("AI & EA\r\n ")]):
        print("⚠️ All sources failed – using last‐good cache.", file=sys.stderr)
        prev = cache.get(max(cache.keys(), default=""), {})
        weather = prev.get("weather")
        can_news = prev.get("can_news")
        ai_ea    = prev.get("ai_ea")

    # write output
    now = datetime.now(tz.tzlocal()).strftime("%B %d, %Y %H:%M")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(f"Morning News Briefing – {now}\n\n")
        f.write("WEATHER:\n")
        f.write((weather or "(weather data unavailable)") + "\n\n")
        f.write(can_news + "\n\n")
        f.write(ai_ea + "\n\n")
        f.write("— End of briefing —\n")

    # update cache
    cache[datetime.now().strftime("%Y-%m-%d")] = {
        "weather": weather,
        "can_news": can_news,
        "ai_ea": ai_ea,
    }
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2)

if __name__ == "__main__":
    main()