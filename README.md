# hc-news-briefing-feed.github.io

This repository now ships a lightweight, mobile-first blog theme inspired by `github.blog`, ready for GitHub Pages hosting.

## How content updates work

Posts are stored in `posts.json` and rendered by `index.html`.

For each post object:

- `slug`: unique URL identifier (`#post/<slug>`)
- `date`: ISO date (`YYYY-MM-DD`)
- `type`: shown as the status chip (for example `Improvement` or `Release`)
- `title`: post title shown in list + detail pages
- `category`: upper label beneath each title
- `readTime`: number shown as minute read on detail pages
- `image` and `imageAlt` (optional): hero image shown on detail pages

This data-first structure is intentionally simple so automated agents can add posts by editing only `posts.json`.
