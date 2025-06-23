#!/usr/bin/env python3

import yaml
import json
import requests
import datetime
import re
from typing import List, Dict

# --- CONFIG ---
PRUNE_THRESHOLD = 0.70  # was 0.50
SCHEMA = {
    "order": ["weather", "canada", "us", "international", "ai_news", "policy_government", "geomatics"],
    "max_items": {
        "canada": 3, "us": 3, "international": 1,
        "ai_news": 3, "policy_government": 3, "geomatics": 3
    }
}

# --- HELPERS ---
def load_feeds() -> Dict[str, List[Dict]]:
    cfg = yaml.safe_load(open("feeds.yaml"))
    return {
        "canada": cfg["primary_feeds"] + cfg.get("backup_feeds", []),
        "us": cfg.get("backup_feeds", []),
        "international": cfg.get("backup_feeds", []),
        # Map other sections as needed...
    }

def load_health() -> Dict[str, float]:
    # Reads health.json and returns a map of URL to uptime_last_5
    with open("health.json", "r") as hf:
        data = json.load(hf)
    return { entry["url"]: entry.get("uptime_last_5", 1.0) for entry in data["feeds"] }


def prune_feeds(items, health_map, primary_urls):
    kept = []
    for feed in items:
        url = feed["url"]
        uptime = health_map.get(url, 1.0)
        if url in primary_urls or uptime >= PRUNE_THRESHOLD:
            kept.append(feed)
    return kept


def pad_items(items, section):
    needed = SCHEMA["max_items"][section] - len(items)
    for _ in range(needed):
        items.append({
            "title": f"No major headlines today in {section.upper().replace('_',' ')}. Stay tuned for updates.",
            "url": "",
            "date": datetime.date.today().isoformat(),
            "source_name": ""
        })
    return items[:SCHEMA["max_items"][section]]


def strip_metadata(text: str) -> str:
    lines = text.splitlines()
    filtered = [
        ln for ln in lines
        if not ln.startswith("URL:") and not re.match(r"^\d{4}-\d{2}-\d{2}T", ln)
    ]
    return "\n".join(filtered)


def call_summarizer(payload_json: str) -> str:
    # Invoke your ChatGPT API here with temperature=0.5 and the updated prompt
    # Example placeholder:
    # return chatgpt_summarize(payload_json, temperature=0.5)
    raise NotImplementedError("Implement summarizer integration")


def fetch_weather():
    # Your existing weather fetch logic goes here.
    # Should return a list of dicts matching schema, including statements.
    raise NotImplementedError("Implement weather fetch logic")


def post_to_github(latest_txt_path: str):
    # Your existing GitHub push logic
    pass


def email_to_evernote(latest_txt_path: str):
    # Your existing Evernote email logic
    pass


def post_to_teams_webhook(latest_txt_path: str):
    # Your existing Teams webhook logic
    pass

# --- MAIN PIPELINE ---
def main():
    feeds_by_section = load_feeds()
    health_map = load_health()
    primary_canada_urls = {f["url"] for f in yaml.safe_load(open("feeds.yaml"))["primary_feeds"]}

    # 1. Prune feeds per section, bypassing primaries for Canada
    pruned = {}
    for section, items in feeds_by_section.items():
        pruned_list = prune_feeds(items, health_map, primary_canada_urls if section == "canada" else set())
        pruned[section] = pad_items(pruned_list, section)

    # 2. Build JSON payload for summarizer
    payload = {
        "weather": fetch_weather(),
        "feeds": pruned
    }
    payload_json = json.dumps(payload)

    # 3. Call summarizer
    briefing = call_summarizer(payload_json)

    # 4. Strip metadata lines before saving/writing
    clean_briefing = strip_metadata(briefing)

    # 5. Write out latest.txt
    with open("latest.txt", "w") as f:
        f.write(clean_briefing)

    # 6. Push to GitHub & send to Evernote / Teams
    post_to_github(latest_txt_path="latest.txt")
    email_to_evernote("latest.txt")
    post_to_teams_webhook("latest.txt")

if __name__ == "__main__":
    main()