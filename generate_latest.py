#!/usr/bin/env python3
import os
import time
import json
from datetime import datetime, timedelta
import requests
import feedparser
from dateutil import tz  # install python-dateutil

# --- CONFIG ---

CACHE_PATH = "cache.json"
SECTIONS = {
    "Weather": [
        "https://dd.weather.gc.ca/rss/city/on-118_e.xml",               # Environment Canada
        "https://api.weather.gov/gridpoints/MTR/100,69/forecast",      # NOAA (JSON)
        # ...add a third backup if you like...
    ],
    "Canadian News": [
        "https://rss.cbc.ca/lineup/topstories.xml",
        "https://www.cbc.ca/cmlink/rss-canada",
        "https://www.bbc.co.uk/feeds/rss/world/canada/rss.xml",
    ],
    "AI & EA": [
        "https://feeds.arstechnica.com/arstechnica/technology-policy",
        "https://www.technologyreview.com/feed/",
        "https://www.opengroup.org/enterprise-architect/rss.xml",
    ],
}

# --- CACHE HANDLING ---

def load_cache():
    try:
        return json.load(open(CACHE_PATH))
    except Exception:
        return {}

def save_cache(cache):
    with open(CACHE_PATH, "w") as f:
        json.dump(cache, f, indent=2)

cache = load_cache()
today = datetime.now().strftime("%Y-%m-%d")

# --- HELPERS ---

def fetch_with_retries(url, headers=None, timeout=10, max_retries=2):
    backoff = 1
    for attempt in range(max_retries+1):
        try:
            resp = requests.get(url, timeout=timeout, headers=headers)
            resp.raise_for_status()
            return resp
        except Exception:
            if attempt == max_retries:
                raise
            time.sleep(backoff)
            backoff *= 2

def get_feed_entries(url):
    if url.startswith("http") and url.endswith(".xml"):
        resp = fetch_with_retries(url)
        return feedparser.parse(resp.content).entries
    else:
        # assume JSON NOAA
        resp = fetch_with_retries(url, headers={"Accept":"application/ld+json"})
        j = resp.json()
        # pull periods from forecast
        return j.get("properties",{}).get("periods", [])

def render_weather(entries):
    if not entries:
        return "(weather data unavailable)"
    out = []
    # If NOAA: list today+tomorrow+day after
    if isinstance(entries[0], dict) and "temperature" in entries[0]:
        for p in entries[:3]:
            out.append(f"• {p['name']}: {p['detailedForecast']}")
    else:
        # RSS: Environment Canada summary
        today, tomorrow = entries[0], entries[1] if len(entries)>1 else None
        out.append(f"• {today.title}: {today.summary}")
        if tomorrow:
            out.append(f"• {tomorrow.title}: {tomorrow.summary}")
    return "\n".join(out)

def collect_section(name, urls):
    entries = []
    for url in urls:
        try:
            es = get_feed_entries(url)
            if es:
                entries = es
                break
        except Exception as e:
            continue
    if not entries and cache.get(today,{}).get(name):
        # fall back to yesterday
        entries = cache.get(today,{}).get(name)
        note = f"(using cached {name})"
    else:
        note = ""
    # store for cache
    cache.setdefault(today,{})[name] = entries
    # Render
    if name == "Weather":
        body = render_weather(entries)
    else:
        lines = []
        for e in entries[:2]:
            title = getattr(e, "title", e.get("name",""))
            summary = getattr(e, "summary", e.get("shortForecast","")).strip()
            date = getattr(e, "published", datetime.now().strftime("%b %d, %Y"))
            source = getattr(e, "link", "")
            lines.append(f"• {title}\n  {summary} {{{date}}}")
        body = "\n".join(lines) if lines else "(no data)"
    return f"\n{name}:\n{note}\n{body}\n"

# --- MAIN ---

def main():
    parts = [f"Morning News Briefing – {datetime.now().strftime('%B %d, %Y %H:%M')}"]
    for section, urls in SECTIONS.items():
        parts.append(collect_section(section, urls))
    parts.append("\n— End of briefing —")
    # Write out
    with open("latest.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(parts))
    # save updated cache
    save_cache(cache)

if __name__=="__main__":
    main()