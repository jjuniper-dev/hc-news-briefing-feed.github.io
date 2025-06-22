import feedparser
from datetime import datetime

# Define RSS feeds by category
feeds = {
    "Canada": [
        "https://www.cbc.ca/cmlink/rss-canada",
        "https://www.ctvnews.ca/rss/ctvnews-ca-canada-public-rss-1.822285"
    ],
    "US": [
        "https://feeds.npr.org/1001/rss.xml",
        "https://rss.cnn.com/rss/cnn_topstories.rss",
        "http://feeds.foxnews.com/foxnews/national"
    ],
    "International": [
        "http://feeds.bbci.co.uk/news/world/rss.xml",
        "http://rss.cnn.com/rss/edition_world.rss",
        "https://www.reutersagency.com/feed/?best-sectors=world&post_type=best"
    ],
    "Cybersecurity": [
        "https://www.wired.com/feed/category/security/latest/rss",
        "https://krebsonsecurity.com/feed/"
    ],
    "AI": [
        "https://www.technologyreview.com/feed/",
        "https://spectrum.ieee.org/rss/artificial-intelligence/fulltext"
    ]
}

# Ottawa 3-day weather (mock)
weather_forecast = [
    "Tonight (Ottawa): HEAT WARNING in effect – partly cloudy, low 22°C",
    "Monday: Sunny and clearing, high 34°C",
    "Tuesday: Mix of sun and cloud, high 31°C",
    "Wednesday: Chance of showers, high 28°C"
]

# Parse feeds with summary and safe error handling
def parse_feeds():
    briefing = {}
    user_agent = "Mozilla/5.0 (compatible; HC-NewsBriefingBot/1.0; +https://github.com/YOUR_REPO)"
    for category, urls in feeds.items():
        stories = []
        for url in urls:
            try:
                d = feedparser.parse(url, agent=user_agent)
                for entry in d.entries[:5]:
                    title = entry.get("title", "No title").strip()
                    summary = entry.get("summary", "").strip().replace('\n', ' ').replace('\r', ' ')
                    if len(summary) > 300:
                        summary = summary[:297] + "..."
                    source = d.feed.get("title", "Unknown Source")
                    published = entry.get("published", "")[:16]
                    stories.append(f"• {title}\n  {summary}\n  [{source}, {published}]")
            except Exception as e:
                print(f"⚠️ Failed to fetch {url}: {e}")
        briefing[category] = stories[:5] if stories else ["• No stories available."]
    return briefing

# Compile full news briefing
def generate_latest_txt():
    briefing = parse_feeds()
    date_str = datetime.now().strftime("%B %d, %Y")
    lines = [f"Multi-Day News Briefing — {date_str}\n"]

    # Weather section
    lines.append("📍 Ottawa Weather")
    for w in weather_forecast:
        lines.append(f"• {w}")
    lines.append("")

    # News categories
    for section in ["Canada", "US", "International", "Cybersecurity", "AI"]:
        lines.append(f"🌐 {section} News")
        lines.extend(briefing.get(section, ["• No stories available."]))
        lines.append("")

    lines.append("— End of briefing —")
    return "\n".join(lines)

# Write to latest.txt
if __name__ == "__main__":
    output = generate_latest_txt()
    with open("latest.txt", "w", encoding="utf-8") as f:
        f.write(output)