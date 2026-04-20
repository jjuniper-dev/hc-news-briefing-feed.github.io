# Assessments Module Authoring Guide

This repository supports versioned AI Offering Assessments using content-only additions.

## Directory layout

Each assessment version lives at:

```text
content/assessments/<vendor>/<version>/
```

Required files:

- `assessment.json` — canonical machine-readable payload
- `assessment.md` — narrative rendering content
- `meta.json` — metadata including `latest`

## Schema

The machine payload must validate against:

- `schemas/assessment.schema.json`

## Latest version rules

- Never overwrite prior versions.
- Add a new version folder (e.g., `v0.2`, `v1.0`).
- Set `"latest": true` only on the current latest version.

## Build-time loader

- `src/lib/loadAssessments.ts` loads all assessment versions.
- It validates `assessment.json` against the JSON schema.
- It produces:
  - vendor/version bundles
  - a latest-only index suitable for `/data/assessments/index.json`
- R/A/G status is computed as:
  1. Any gate = `Fail` → `Red`
  2. Else composite `>= 70` → `Green`
  3. Else composite `>= 50` → `Amber`
  4. Else → `Red`

## Adding a new vendor assessment

1. Create `content/assessments/<vendor>/<version>/`.
2. Add `assessment.json`, `assessment.md`, and `meta.json`.
3. Validate JSON structure against `schemas/assessment.schema.json`.
4. Confirm one `latest: true` version per vendor.
5. Open a PR with source notes in `assessment.md` under “Sources & Caveats”.
