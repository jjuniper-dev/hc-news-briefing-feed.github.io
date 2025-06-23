#!/usr/bin/env python3
import yaml
import json
import requests
import datetime
import os

# 1. Load feeds list
with open("feeds.yaml") as f:
    cfg = yaml.safe_load(f)
feeds = cfg.get("primary_feeds", []) + cfg.get("backup_feeds", [])

# 2. Prepare results container
results = {"generated_at": datetime.datetime.utcnow().isoformat() + "Z", "feeds": []}

# 3. Test each feed URL
for feed in feeds:
    url = feed["url"]
    name = feed.get("name", url)
    status = {"name": name, "url": url, "last_checked": results["generated_at"]}
    try:
        r = requests.get(url, timeout=10)
        status["ok"] = r.status_code == 200
    except Exception as e:
        status["ok"] = False
        status["error"] = str(e)
    results["feeds"].append(status)

# 4. Compute simple uptime_last_5 if you have history
# For now, just record ok/fail counts
# (You could load previous health.json and compute a rolling rate.)

# 5. Write out health.json
with open("health.json", "w") as f:
    json.dump(results, f, indent=2)

print(f"Wrote health.json for {len(results['feeds'])} feeds.")