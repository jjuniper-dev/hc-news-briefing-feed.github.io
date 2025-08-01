# System Architecture

This repository powers a small static site that publishes a daily news briefing and feed health dashboard. It demonstrates the kind of automation and dynamic content you might expect from a mid‑range website project.

```
+------------+        +---------------+         +------------------+
|  GitHub    |  CI    |  Python       |  Data   |  Static Site      |
|  Actions   +------->|  Scripts      +-------> |  (GitHub Pages)   |
+------------+        +---------------+         +------------------+
        ^                        |                         |
        |                        v                         v
        |                 RSS Feeds & APIs           index.html + assets
        |                        |
        +------------------------+
```

## Components

1. **RSS Ingestion** – `generate_latest.py` fetches grouped RSS feeds. Articles from the last five days are summarised using a Transformer model and written to `latest.txt`.
2. **Feed Health** – `test_feeds.py` checks primary and backup feeds defined in `feeds.yaml`. Results are stored in `health.json`.
3. **Uptime Pings** – the `ping_canadian_feeds.yml` workflow records hourly availability of key Canadian feeds into `uptime.json`.
4. **Static Dashboard** – `index.html` loads the JSON files via JavaScript and presents the health table, uptime percentages and the latest briefing.
5. **Automation** – `news_pipeline.yml` runs on a schedule to refresh the data and commit the updated JSON and text files back to the repository.
6. **Deployment** – GitHub Pages (see `pages-build-deployment.yml`) publishes the repository contents, turning the static assets into a publicly accessible website.

Together these components deliver a lightweight news dashboard with automated data collection. The design can be expanded with additional services, databases or a CMS as project requirements grow.
