#!/usr/bin/env python3
import requests
import feedparser
from datetime import datetime, timedelta
from dateutil import parser as date_parser

# --- CONFIG ---
SOURCES = [
    # 1) Environment Canada RSS for Ottawa
    ("EC", "https://dd.weather.gc.ca/citypage_weather/xml/ON/s0000316_e.xml"),
    # 2) NOAA forecast XML (city code for Ottawa: CAXX0694, adjust as needed)
    ("NOAA", "https://forecast.weather.gov/MapClick.php?lat=45.4215&lon=-75.6972&unit=0&lg=english&FcstType=dwml"),
    # 3) Fallback wttr.in plain text
    ("WTTR", "https://wttr.in/Ottawa?format=3&m")
]

def fetch_ec(entries_needed=3):
    resp = requests.get(SOURCES[0][1], timeout=15)
    resp.raise_for_status()
    feed = feedparser.parse(resp.content)
    items = feed.entries[:entries_needed]
    out = []
    for e in items:
        # title like "Monday Jun 23: Cloudy 25 °C"
        title = e.title.replace("\n", " ").strip()
        out.append(f"• {title}")
    return out

def fetch_noaa():
    # NOAA DWML is complex XML; for brevity, we’ll skip detailed parsing here
    # You could use xml.etree.ElementTree to extract temperatures and conditions
    raise NotImplementedError("NOAA parsing not yet implemented")

def fetch_wttr():
    resp = requests.get(SOURCES[2][1], timeout=10)
    resp.raise_for_status()
    # wttr.in returns e.g. "Ottawa: 🌦️ +23°C"
    return [f"• {resp.text.strip()}"]

def fetch_weather():
    today = datetime.utcnow().strftime("%B %d, %Y")
    parts = [f"Ottawa Weather – {today}\n"]
    # Try EC first
    try:
        ec = fetch_ec()
        if ec:
            return "\n".join(parts + ec)
    except Exception:
        pass

    # Try NOAA next
    try:
        noaa = fetch_noaa()
        if noaa:
            return "\n".join(parts + noaa)
    except Exception:
        pass

    # Fallback wttr.in
    try:
        wt = fetch_wttr()
        return "\n".join(parts + wt)
    except Exception as e:
        parts.append("(weather data unavailable)")
        return "\n".join(parts)

if __name__ == "__main__":
    print(fetch_weather())