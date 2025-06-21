#!/usr/bin/env python3

import feedparser
import re
from datetime import datetime, timedelta
from http.client import RemoteDisconnected
from transformers import pipeline

# --- CONFIG ---
DAYS_BACK = 5
CUT_OFF = datetime.now() - timedelta(days=DAYS_BACK)

# Ordered sections with their RSS feeds
GROUPED_FEEDS = {
    "Weather": [
        "https://weather.gc.ca/rss/city/on-131_e.xml"
    ],
    "Canadian CBC": [
        "https://rss.cbc.ca/lineup/canada.xml"
    ],
    "Canadian CTV": [
        "https://www.ctvnews.ca/rss/ctvnews-ca-canada-public-rss.xml"
    ],
    "U.S.": [
        "https://feeds.npr.org/1001/rss.xml"
    ],
    "International": [
        "http://feeds.reuters.com/Reuters/worldNews"
    ],
    # Special one-liner sections
    "Public Health": [
        "https://www.canada.ca/etc/+/health/public-health-updates.rss"
    ],
    "AI & Emerging Tech": [
        "https://feeds.arstechnica.com/arstechnica/technology-policy",
        "https://www.theregister.com/headlines.atom"
    ],
    "Cybersecurity & Privacy": [
        "https://krebsonsecurity.com/feed/",
        "https://www.nist.gov/blogs/blog.rss"
    ],
    "Enterprise Architecture": [
        "https://www.opengroup.org/news/rss/news-release.xml",
        "https://www.cio.com/ciolib/rss/cio/government.xml"
    ],
    "Geomatics": [
        "https://www.gislounge.com/feed/",
        "https://www.directionsmag.com/feed"
    ]
}

# Initialize summarizer once