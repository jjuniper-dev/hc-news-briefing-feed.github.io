import feedparser
from datetime import datetime

# Define updated feeds per category
feeds = {
    "Canada": [
        "https://www.cbc.ca/cmlink/rss-canada",
        "https://www.theglobeandmail.com/rss/",
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

# Mock Ottawa weather for 3-day forecast
weather_forecast = [
    "Tonight (Ottawa): HEAT WARNING in effect â partly cloudy, low 22Â°C",
    "Monday: Sunny and clearing, high 34Â°C",
    "Tuesday: Mix of sun and cloud, high 31Â°C",
    "Wednesday: Chance of showers, high 28Â°C"
]

def parse_feeds():
    briefing = {}
    for category, urls in feeds.items():
        stories = []
        for url in urls:
            d = feedparser.parse(url)
            for entry in d.entries[:5]:
                title = entry.title
                source = d.feed.get("title", "Unknown Source")
                published = entry.get("published", "")
                stories.append(f"â¢ {title}  [{source}, {published[:16]}]")
        briefing[category] = stories[:5]
    return briefing

def generate_latest_txt():
    briefing = parse_feeds()
    date_str = datetime.now().strftime("%B %d, %Y")
    lines = [f"Multi-Day News Briefing â {date_str}\n"]

    # Weather
    lines.append("ð Ottawa Weather")
    for w in weather_forecast:
        lines.append(f"â¢ {w}")
    lines.append("")

    # News Sections
    for section in ["Canada", "US", "International", "Cybersecurity", "AI"]:
        lines.append(f"ð {section} News")
        lines.extend(briefing.get(section, ["â¢ No stories available."]))
        lines.append("")

    lines.append("â End of briefing â")
    return "\n".join(lines)

if __name__ == "__main__":
    output = generate_latest_txt()
    with open("latest.txt", "w", encoding="utf-8") as f:
        f.write(output)
