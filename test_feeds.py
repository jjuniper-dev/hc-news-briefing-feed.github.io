#!/usr/bin/env python3

import yaml
import json
import requests
import datetime
import time
import os

# 1. Load feeds list from feeds.yaml
cfg_path = os.path.join(os.path.dirname(__file__), "feeds.yaml")
with open(cfg_path, "r") as f:
    cfg = yaml.safe_load(f)

feeds = cfg.get("primary_feeds", []) + cfg.get("backup_feeds", [])

# 2. Prepare results container
now = datetime.datetime.utcnow().isoformat() + "Z"
results = {
    "generated_at": now,
    "feeds": []
}

# 3. Helper to fetch with retry and timeout
def fetch_url(url):
    for attempt in range(2):
        try:
            resp = requests.get(url, timeout=20, allow_redirects=True)
            return resp
        except requests.exceptions.Timeout:
            if attempt == 0:
                time.sleep(2)
                continue
            raise

# 4. Test each feed URL
for feed in feeds:
    name = feed.get("name", feed["url"])
    url = feed["url"]
    entry = {
        "name": name,
        "url": url,
        "last_checked": now
    }
    try:
        response = fetch_url(url)
        entry["ok"] = (response.status_code == 200)
        if not entry["ok"]:
            entry["status_code"] = response.status_code
    except Exception as e:
        entry["ok"] = False
        entry["error"] = str(e)
    results["feeds"].append(entry)

# 5. Write out health.json
out_path = os.path.join(os.path.dirname(__file__), "health.json")
with open(out_path, "w") as f:
    json.dump(results, f, indent=2)

print(f"Wrote health.json with {len(results['feeds'])} feed entries.")