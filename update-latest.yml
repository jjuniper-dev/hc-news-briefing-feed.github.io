name: Update latest.txt

on:
  schedule:
    # Run daily at 6:30 AM Eastern (10:30 UTC)
    - cron: '30 10 * * *'
  workflow_dispatch:

permissions:
  contents: write

jobs:
  update-latest:
    runs-on: ubuntu-latest

    steps:
      - name: Check out repository
        uses: actions/checkout@v4
        with:
          persist-credentials: true

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install feedparser requests python-dateutil

      - name: Generate latest.txt
        run: |
          mkdir -p scripts
          cat > scripts/generate_latest.py << 'EOF'
import feedparser
from datetime import datetime, timedelta
import requests

# Configuration
RSS_FEEDS = [
    ("CBC Canada", "https://rss.cbc.ca/lineup/topstories.xml"),
    ("CTV Canada", "https://www.ctvnews.ca/rss/ctvnews-ca-canada-1.2089050"),
    ("Reuters World", "https://feeds.reuters.com/Reuters/worldNews"),
    ("BBC World", "http://feeds.bbci.co.uk/news/world/rss.xml"),
]
WEATHER_FEED = "https://dd.weather.gc.ca/rss/city/on-118_e.xml"  # Ottawa

# Helper functions
def get_weather():
    feed = feedparser.parse(WEATHER_FEED)
    entries = feed.entries[:3]
    lines = [f"Ottawa Weather – {datetime.now().strftime('%B %d, %Y')}"]
    for e in entries:
        title = e.title
        summary = e.summary.replace('<![CDATA[', '').replace(']]>', '')
        lines.append(f"• {title}: {summary}")
    lines.append("")
    return lines

def fetch_feed(name, url, days=1):
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        feed = feedparser.parse(r.content)
        cutoff = datetime.now() - timedelta(days=days)
        items = []
        for entry in feed.entries:
            pub = getattr(entry, 'published_parsed', None)
            if pub:
                pubdt = datetime(*pub[:6])
                if pubdt < cutoff:
                    continue
                date = pubdt.strftime('%B %d, %Y')
            else:
                date = ''
            items.append(f"• {entry.title} {{{date}}}")
            if len(items) >= 2:
                break
        return [f"{name} – {datetime.now().strftime('%B %d, %Y')}"] + items + ['']
    except Exception as e:
        return [f"{name} – ERROR: {e}", '']

if __name__ == '__main__':
    lines = []
    # Weather
    lines += get_weather()
    # News sections
    for label, url in RSS_FEEDS:
        lines += fetch_feed(label, url, days=1)
    lines.append("— End of briefing —")

    # Write to latest.txt
    with open('latest.txt', 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))
    print("latest.txt updated")
EOF
          python scripts/generate_latest.py

      - name: Commit and push latest.txt
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git add latest.txt
          git diff --quiet --cached || (
            git commit -m "Auto-update latest.txt for $(date +'%Y-%m-%d')" &&
            git push
          )