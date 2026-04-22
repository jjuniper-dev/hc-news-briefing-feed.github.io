#!/usr/bin/env python3
"""Minimal HTTP response header checks for a deployed GitHub Pages site."""

from __future__ import annotations

import os
import sys
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen

SITE_URL = os.environ.get("SITE_URL", "").strip()
TIMEOUT_SECONDS = 20

REQUIRED_HEADERS = {
    "strict-transport-security": "max-age",
    "x-content-type-options": "nosniff",
}

RECOMMENDED_HEADERS = [
    "content-security-policy",
    "x-frame-options",
    "referrer-policy",
]

if not SITE_URL:
    print("SITE_URL is not set; skipping deployed header checks.")
    sys.exit(0)

request = Request(SITE_URL, headers={"User-Agent": "hc-site-security-check/1.0"})

try:
    with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        status_code = response.getcode()
        headers = {k.lower(): v.lower() for k, v in response.headers.items()}
except HTTPError as exc:
    print(f"Target returned HTTP {exc.code}: {SITE_URL}")
    sys.exit(1)
except URLError as exc:
    print(f"Failed to fetch {SITE_URL}: {exc}")
    sys.exit(1)

if status_code >= 400:
    print(f"Target returned HTTP {status_code}: {SITE_URL}")
    sys.exit(1)

missing_required = []
for header, expected in REQUIRED_HEADERS.items():
    value = headers.get(header)
    if not value or expected not in value:
        missing_required.append((header, expected, value))

if missing_required:
    print("Missing required security headers:")
    for header, expected, actual in missing_required:
        print(f"- {header} (expected to include '{expected}', got: {actual!r})")
    sys.exit(1)

print("Required security headers are present.")

for header in RECOMMENDED_HEADERS:
    if header not in headers:
        print(f"Warning: recommended header is missing: {header}")
