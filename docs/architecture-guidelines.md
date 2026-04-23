# Static Site Architecture Guidelines

These guidelines define baseline structure and navigation expectations for this repository's static pages.

## 1) Site-wide metadata

- Every top-level page MUST include:
  - `<meta name="viewport" content="width=device-width, initial-scale=1.0">` (or equivalent `initial-scale=1`).
  - A non-empty `<title>`.
  - Social preview metadata (`og:title`, `og:description`, `og:image`, and `twitter:card`).

## 2) Status-Site navigation contract

The three status pages under `status-site/` MUST expose a consistent header nav containing these labels and destinations:

1. Dashboard → `../index.html`
2. Intelligence Editor → `../intelligence-editor.html`
3. Intelligence Posts → `../status-site/intelligence.html` (or local `intelligence.html` on that page)
4. PPTX Builder → `../status-site/pptx-builder.html` (or local `pptx-builder.html` on that page)
5. Backlog → `../status-site/backlog.html` (or local `backlog.html` on that page)

Each status page SHOULD mark its own nav link with `aria-current="page"`.

## 3) Backlog linking rule

- Backlog must be discoverable from:
  - `index.html`
  - `intelligence-editor.html`
  - all status pages

## 4) CI/CD enforcement

- Architecture checks are enforced by `scripts/validate_site_architecture.py`.
- Pull requests must pass `.github/workflows/site-test-plan.yml` before merge.
