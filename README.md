# hc-news-briefing-feed.github.io

This repository hosts a lightweight news dashboard that publishes a daily briefing and monitors the health of several RSS feeds.  The site is deployed via GitHub Pages and the data is refreshed automatically using GitHub Actions.

See [ARCHITECTURE.md](ARCHITECTURE.md) for an overview of how the pieces fit together.

## Pages

- `index.html`: feed health dashboard + latest generated briefing.
- `updates.html`: EA/TPO updates workspace for pasting latest text, retaining local context history, and running AI-assisted analysis using a user-supplied OpenAI API key in the browser.
