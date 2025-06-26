#!/usr/bin/env python3
"""
generate_latest.py

Fetches Ottawa weather and news feeds, summarizes via ChatGPT,
strips metadata lines, and writes the result to latest.txt.
Automatically installs missing dependencies if needed.
"""

import sys
import subprocess
import os
import yaml
import feedparser
import requests
from datetime import datetime, timedelta
from dateutil import tz
import openai

# --- Bootstrap: ensure required packages are installed ---
required_packages = [
    "pyyaml",
    "feedparser",
    "requests",
    "python-dateutil",
    "openai"
]
for pkg in required_packages:
    try:
        __import__(pkg.replace("-", "_"))
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

# --- Configuration ---
SCHEMA_FILE = "briefing_schema.yaml"
OUTPUT_FILE = "latest.txt"

# Ensure OPENAI_API_KEY is set
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    print("Error: OPENAI_API_KEY environment variable not set.")
    sys.exit(1)

# Load briefing schema
with open(SCHEMA_FILE, 'r') as f:
    schema = yaml.safe_load(f)['briefing']

def fetch_weather(days=3):
    """Placeholder fetch for Ottawa weather (replace with real API parsing)."""
    now = datetime.now(tz=tz.tzlocal())
    data = []
    for i in range(days):
        d = now + timedelta(days=i)
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
    """Fetch up to max_items from the RSS/Atom feed URL in environment."""
    url = os.getenv(env_var, "").strip()
    if not url:
        return []
    feed = feedparser.parse(url)
    items = []
    for entry in feed.entries[:max_items]:
        items.append({
            "title": entry.title,
            "url": entry.link,
            "date": getattr(entry, 'published', datetime.now().isoformat())[:10],
            "source_name": feed.feed.get("title", "Unknown")
        })
    return items

def gather_feeds():
    """Aggregate feed items per schema sections (excluding weather)."""
    feeds = {}
    for section, info in schema['sections'].items():
        if section == 'weather':
            continue
        env_key = f"FEED_{section.upper()}_URL"
        feeds[section] = fetch_feed_items(env_key, info.get('max_items', 0))
    return feeds

def build_prompt(data):
    """Build the system and user messages for ChatGPT."""
    with open(SCHEMA_FILE, 'r') as f:
        schema_text = f.read()
    system_msg = (
        "You are a news-briefing assistant. Follow the provided briefing schema exactly.\n\n"
        "Schema:\n" + schema_text
    )
    user_msg = yaml.dump(data, sort_keys=False)
    return [
        {"role": "system", "content": system_msg},
        {"role": "user",   "content": user_msg}
    ]

def strip_metadata(text):
    """
    Remove lines that are purely ISO timestamps or standalone URLs
    so they don't appear in TTS output.
    """
    lines = text.splitlines()
    cleaned = []
    for line in lines:
        s = line.strip()
        if (s.startswith("20") and "T" in s and s.endswith("Z")) or \
           s.startswith("http://") or s.startswith("https://"):
            continue
        cleaned.append(line)
    return "\n".join(cleaned)

def generate_briefing():
    """Fetch data, call OpenAI, and return the raw briefing text."""
    weather = fetch_weather(days=schema['sections']['weather']['days'])
    feeds   = gather_feeds()
    payload = {"weather": weather, "feeds": feeds}

    messages = build_prompt(payload)
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.5,
        max_tokens=1200
    )
    return response.choices[0].message.content

def save_output(text):
    """Strip metadata and write the cleaned briefing to file."""
    cleaned = strip_metadata(text)
    with open(OUTPUT_FILE, 'w') as f:
        f.write(cleaned)

def main():
    briefing_text = generate_briefing()
    save_output(briefing_text)
    print(f"✅ Briefing generated and saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()