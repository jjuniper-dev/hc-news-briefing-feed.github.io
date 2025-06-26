#!/usr/bin/env python3
import os
import sys
import yaml
import feedparser
import requests
from datetime import datetime, timedelta
from dateutil import tz
import openai

#— Configuration —#
SCHEMA_FILE = "briefing_schema.yaml"
OUTPUT_FILE = "latest.txt"
# e.g. set FEED_CANADA_URL, FEED_US_URL, etc., in your environment

# Ensure API key
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    print("Error: OPENAI_API_KEY not set")
    sys.exit(1)

# Load the schema
with open(SCHEMA_FILE, 'r') as f:
    schema = yaml.safe_load(f)['briefing']

def fetch_weather(days=3):
    # Placeholder: replace with real Environment Canada parsing
    url = "https://dd.weather.gc.ca/citypage_weather/xml/ON/s0000695_e.xml"
    resp = requests.get(url)
    resp.raise_for_status()
    today = datetime.now(tz=tz.tzlocal())
    data = []
    for i in range(days):
        d = today + timedelta(days=i)
        data.append({
            "day": d.strftime("%A"),
            "summary": "Placeholder summary",
            "high": 0,
            "low": 0,
            "precip_chance": 0,
            "uv": 0
        })
    return data

def fetch_feed_items(env_var, max_items):
    url = os.getenv(env_var)
    if not url:
        return []
    feed = feedparser.parse(url)
    items = []
    for entry in feed.entries[:max_items]:
        items.append({
            "title": entry.title,
            "url": entry.link,
            "date": getattr(entry, 'published', datetime.now().strftime("%Y-%m-%d"))[:10],
            "source_name": feed.feed.get("title", "Unknown")
        })
    return items

def gather_feeds():
    feeds = {}
    for section, info in schema['sections'].items():
        if section == 'weather':
            continue
        key = f"FEED_{section.upper()}_URL"
        feeds[section] = fetch_feed_items(key, info.get('max_items', 0))
    return feeds

def build_prompt(data):
    # System message with the full YAML schema
    with open(SCHEMA_FILE, 'r') as f:
        schema_text = f.read()
    system = (
        "You are a news-briefing assistant. Follow the provided briefing schema exactly.\n\n"
        "Schema:\n" + schema_text
    )
    user = yaml.dump(data, sort_keys=False)
    return [
        {"role": "system", "content": system},
        {"role": "user",   "content": user}
    ]

def strip_metadata(text):
    # Remove lines that are only ISO timestamps or standalone URLs
    lines = text.splitlines()
    cleaned = []
    for line in lines:
        stripped = line.strip()
        # skip pure timestamps (e.g., 2025-06-23T09:31:50Z)
        if stripped.startswith("20") and "T" in stripped and stripped.endswith("Z"):
            continue
        # skip standalone URLs
        if stripped.startswith("http://") or stripped.startswith("https://"):
            continue
        cleaned.append(line)
    return "\n".join(cleaned)

def generate_briefing():
    weather = fetch_weather(days=schema['sections']['weather']['days'])
    feeds   = gather_feeds()
    data    = {"weather": weather, "feeds": feeds}

    prompt = build_prompt(data)
    resp = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=prompt,
        temperature=0.5,
        max_tokens=1200
    )
    return resp.choices[0].message.content

def save_briefing(text):
    cleaned = strip_metadata(text)
    with open(OUTPUT_FILE, 'w') as f:
        f.write(cleaned)

def main():
    briefing = generate_briefing()
    save_briefing(briefing)
    print(f"✍️  Briefing generated and saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()