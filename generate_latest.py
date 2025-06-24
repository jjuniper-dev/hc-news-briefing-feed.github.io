#!/usr/bin/env python3
import os
import sys
import time
import json
import logging
from datetime import datetime
import requests
import feedparser
from dateutil import tz

# ——— CONFIG ———
CACHE_PATH = "cache.json"
LOG_PATH   = "debug.log"

SECTIONS = {
    "Weather": [
        # Env Canada RSS
        "https://dd.weather.gc.ca/rss/city/on-118_e.xml",
        # NOAA JSON API
        "https://api.weather.gov/gridpoints/MTR/100,69/forecast",
        # Backup: Open-Meteo JSON API (no key required)
        "https://api.open-meteo.com/v1/forecast?latitude=45.4215&longitude=-75.6972&daily=weathercode,temperature_2m_max,temperature_2m_min&timezone=America%2FToronto",
    ],
    "Canadian News": [
        "https://rss.cbc.ca/lineup/topstories.xml",
        "https://www.cbc.ca/cmlink/rss-canada",
        "http://feeds.bbci.co.uk/news/world/canada/rss.xml",
    ],
    "AI & EA": [
        "https://feeds.arstechnica.com/arstechnica/technology-policy",
        "https://www.technologyreview.com/feed/",
        "https://www.opengroup.org/enterprise-architect/rss.xml",
    ],
}

# ——— SETUP LOGGING & CACHE ———
logging.basicConfig(filename=LOG_PATH, level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s")

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


# ——— HELPERS ———
def fetch_with_retries(url, headers=None, timeout=10, max_retries=2):
    backoff = 1
    for attempt in range(max_retries + 1):
        try:
            logging.debug(f"Fetching {url} (attempt {attempt+1})")
            r = requests.get(url, timeout=timeout, headers=headers)
            r.raise_for_status()
            return r
        except Exception as e:
            logging.warning(f"{url} failed on attempt {attempt+1}: {e}")
            if attempt == max_retries:
                raise
            time.sleep(backoff)
            backoff *= 2

def get_feed_entries(url):
    if url.endswith(".xml"):
        r = fetch_with_retries(url)
        feed = feedparser.parse(r.content)
        return feed.entries
    else:
        # JSON sources
        r = fetch_with_retries(url, headers={"Accept": "application/json"})
        j = r.json()
        # NOAA
        if "properties" in j and "periods" in j["properties"]:
            return j["properties"]["periods"]
        # Open-Meteo: convert daily to pseudo-entries
        if "daily" in j:
            days = j["daily"]
            entries = []
            for idx, date in enumerate(days["time"]):
                entries.append({
                    "title": date,
                    "summary": f"Max {days['temperature_2m_max'][idx]}°C, "
                               f"Min {days['temperature_2m_min'][idx]}°C, "
                               f"Weather code {days['weathercode'][idx]}"
                })
            return entries
        return []

def render_weather(entries):
    if not entries:
        return "(weather data unavailable)"
    lines = []
    # NOAA style entries are dicts with 'name'
    if isinstance(entries[0], dict) and "name" in entries[0]:
        for p in entries[:3]:
            lines.append(f"• {p['name']}: {p.get('detailedForecast', p.get('summary',''))}")
    else:
        # RSS style
        today_rss = entries[0]
        tom_rss   = entries[1] if len(entries) > 1 else None
        lines.append(f"• {today_rss.title}: {today_rss.summary}")
        if tom_rss:
            lines.append(f"• {tom_rss.title}: {tom_rss.summary}")
    return "\n".join(lines)

def collect_section(name, urls):
    logging.info(f"Collecting section {name}")
    entries = []
    for url in urls:
        try:
            es = get_feed_entries(url)
            if es:
                logging.info(f"→ {name}: {len(es)} entries from {url}")
                entries = es
                break
        except Exception as e:
            logging.error(f"→ {name} failed on {url}: {e}")
    if not entries:
        # fallback to cache if available
        last = cache.get(today, {}).get(name)
        if last:
            logging.info(f"→ {name}: using cached entries")
            entries = last
            note = "(cached)"
        else:
            note = "(no data)"
    else:
        note = ""
    cache.setdefault(today, {})[name] = entries

    if name == "Weather":
        body = render_weather(entries)
    else:
        lines = []
        for e in entries[:2]:
            title   = getattr(e, "title", e.get("title", ""))
            summary = getattr(e, "summary", e.get("summary","")).replace("\n"," ").strip()
            date    = getattr(e, "published", e.get("time", ""))[:12]
            lines.append(f"• {title}\n  {summary} {{{date}}}")
        body = "\n".join(lines) if lines else "(no data)"
    return f"\n{name}:\n{note}\n{body}\n"

# ——— MAIN ———
def main():
    parts = [f"Morning News Briefing – {datetime.now().strftime('%B %d, %Y %H:%M')}"]
    for section, urls in SECTIONS.items():
        parts.append(collect_section(section, urls))
    parts.append("— End of briefing —")

    with open("latest.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(parts))

    save_cache(cache)
    logging.info("Writing latest.txt and cache.json complete")

if __name__ == "__main__":
    main()