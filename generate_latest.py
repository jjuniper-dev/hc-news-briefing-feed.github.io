import feedparser
from datetime import datetime

# --- CONFIG ---
RSS_FEEDS = [
    # International News
    ("International", "http://feeds.reuters.com/Reuters/worldNews"),
    # Canada News
    ("National", "https://rss.cbc.ca/lineup/canada.xml"),
    # U.S. News
    ("US", "https://feeds.npr.org/1001/rss.xml"),
    # IT and AI News (General, relevant to HC/PHAC)
    ("AI & IT", "https://feeds.arstechnica.com/arstechnica/technology-policy"),
    ("AI & IT", "https://www.theregister.com/headlines.atom")
]

WEATHER_FEED = "https://dd.weather.gc.ca/rss/city/on-118_e.xml"  # Ottawa

# --- FUNCTIONS ---
def get_weather_summary():
    feed = feedparser.parse(WEATHER_FEED)
    today = feed.entries[0]
    tomorrow = feed.entries[1] if len(feed.entries) > 1 else None
    today_text = f"{today.title}: {today.summary}"
    tomorrow_text = f"{tomorrow.title}: {tomorrow.summary}" if tomorrow else ""
    return f"Ottawa Weather – {datetime.now().strftime('%B %d, %Y')}\n{today_text}\nTomorrow: {tomorrow_text}"


def format_entry(entry):
    # Use content if available, else summary
    if hasattr(entry, 'content') and entry.content:
        text = entry.content[0].value.strip()
    else:
        text = entry.get('summary', '').strip()
    # Clean HTML tags if necessary
    published = datetime(*entry.published_parsed[:6]).strftime('%B %d, %Y') if 'published_parsed' in entry else ""
    source = entry.get('source', {}).get('title', '') or entry.link.split('/')[2]
    return f"• {entry.title.strip()}\n  {text} {{{published} ({source})}}"


def collect_headlines():
    sections = []
    # Weather section
    sections.append(get_weather_summary())

    # News sections
    for label, url in RSS_FEEDS:
        feed = feedparser.parse(url)
        entries = feed.entries[:2]  # Top 2 stories
        if entries:
            sections.append(f"\n{label.upper()} HEADLINES")
            for e in entries:
                sections.append(format_entry(e))

    sections.append("\n— End of briefing —")
    return "\n\n".join(sections)

# --- MAIN ---
if __name__ == "__main__":
    briefing_text = collect_headlines()
    with open("latest.txt", "w", encoding="utf-8") as f:
        f.write(briefing_text)
    print("latest.txt updated with full content.")