# Site Test Plan Implementation (Automation + GitHub Pages)

This repository now includes a lightweight test strategy designed for GitHub Pages and focused on small, secure checks.

## 1) Functional smoke checks
- File: `scripts/test_functional.py`
- Validates:
  - Core public pages exist.
  - Internal links in `index.html` resolve.
  - A warning is raised when no custom `404.html` exists.

## 2) Accessibility baseline checks
- File: `scripts/test_accessibility.py`
- Runs static accessibility checks for key pages:
  - `<html lang>` exists.
  - Non-empty `<title>` exists.
  - All `<img>` tags include `alt`.

## 3) Security header checks
- File: `scripts/check_security_headers.py`
- Runs against deployed GitHub Pages URL (`SITE_URL`) and enforces required baseline headers:
  - `Strict-Transport-Security`
  - `X-Content-Type-Options`
- Reports missing recommended headers as warnings.

## 4) Performance budget checks
- File: `scripts/test_performance_budget.py`
- Enforces a small static-site budget:
  - Max single tracked asset size.
  - Max total tracked HTML/CSS/JS/JSON size.

## 5) Content integrity checks
- Markdown linting with `markdownlint-cli2`.
- Link validation with `lychee` over docs/reviews/site entry files.

## 6) CI orchestration in GitHub Actions
- Workflow file: `.github/workflows/site-test-plan.yml`
- Triggered on pull requests and pushes to `main`.
- Jobs are split by concern:
  - `content-integrity`
  - `static-quality`
  - `security-headers`

## Local developer commands
```bash
python scripts/test_functional.py
python scripts/test_accessibility.py
python scripts/test_performance_budget.py
SITE_URL="https://<org>.github.io/<repo>/" python scripts/check_security_headers.py
```
