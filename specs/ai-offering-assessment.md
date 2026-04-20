# Development Specification — AI Offering Assessment Module (Cohere Example)

## 1. Purpose

Extend `status-site` to support publishing, versioning, and rendering AI Offering Assessments (e.g., Cohere, Azure OpenAI, Gemini, GC LLM). These assessments follow the HC/PHAC four-layer rubric and must be:

- Machine-readable (JSON/YAML)
- Human-readable (Markdown → rendered HTML)
- Versioned (each assessment has versions)
- Queryable via the existing `/data/` JSON endpoints
- Displayed as a structured, navigable page on the site

The Cohere assessment provided in uploaded documents is the first implemented instance.

## 2. Functional Requirements

### 2.1 Content ingestion

Add a new content directory:

```text
content/assessments/<vendor>/<version>/
```

Each assessment contains:

- `assessment.json` — canonical machine-readable representation
- `assessment.md` — human-readable narrative
- `meta.json` — metadata (`vendor`, `version`, `date`, `reviewer`, `status`)

### 2.2 Data model

Define a new schema under `schemas/assessment.schema.json`:

```json
{
  "vendor": "Cohere",
  "version": "0.1",
  "review_date": "2026-04-01",
  "item_type": "Product",
  "capability_type": "Embedded",
  "tier": "Tier 3",
  "gates": {
    "G1": "Pass",
    "G2": "Fail",
    "G3": "Fail",
    "G4": "N/A",
    "G5": "N/A",
    "G6": "Pass",
    "G7": "Pass",
    "G8": "Pass",
    "G9": "Pass",
    "G10": "N/A"
  },
  "scores": {
    "governance": 2.75,
    "architecture": 2.75,
    "capability": 3.25,
    "procurement": 3.0,
    "composite": 58.5
  },
  "positioning": {
    "openness": "Mixed",
    "sovereignty": "Nuanced",
    "runtime": "Partial"
  },
  "recommendation": "Approve with conditions"
}
```

### 2.3 Rendering

Add a new route:

```text
/assessments/<vendor>/<version>/
```

Page must render:

- Executive summary
- Layer 1 classifier table
- Layer 2 gates table (with fail highlighting)
- Layer 3 scoring tables
- Layer 4 positioning profile
- Recommendation block
- Source citations

### 2.4 Index page

Add:

```text
/assessments/
```

Listing:

- Vendor name
- Latest version
- Composite score
- R/A/G status
- Link to full assessment

### 2.5 API endpoints

Expose machine-readable data:

- `/data/assessments/index.json`
- `/data/assessments/<vendor>/<version>.json`

### 2.6 Versioning rules

- New versions must not overwrite old ones.
- Index must always point to the latest version.
- Add `latest: true` flag in `meta.json`.

## 3. Non-Functional Requirements

### 3.1 Static-site compatibility

- No server-side logic.
- All data must be prebuilt at compile time.

### 3.2 Accessibility

- Tables must be WCAG AA compliant.
- Colour-coded R/A/G must include text labels.

### 3.3 Maintainability

- New assessments should require no code changes.
- Only content additions.

## 4. Implementation Plan

### 4.1 Directory structure

```text
/content
  /assessments
    /cohere
      /v0.1
        assessment.json
        assessment.md
        meta.json

/schemas
  assessment.schema.json

/src
  /lib
    loadAssessments.ts
  /routes
    /assessments
      index.tsx
      [vendor]
        [version].tsx
```

## 5. Build-time pipeline

### 5.1 Loader

Create `loadAssessments.ts`:

- Recursively scan `/content/assessments`
- Validate JSON against schema
- Build:
  - `index.json`
  - vendor/version JSON bundles
- Inject into static build context

### 5.2 Markdown rendering

Use existing MDX pipeline.

### 5.3 R/A/G computation

If not provided, compute:

```text
if any gate == Fail → Red
else if composite >= 70 → Green
else if composite >= 50 → Amber
else → Red
```

## 6. UI Specification

### 6.1 Assessment index page

Components:

- Vendor card
- Composite score badge
- R/A/G badge
- “View assessment” link

### 6.2 Assessment detail page

Sections:

1. Header
   - Vendor
   - Version
   - Review date
   - Composite score
   - R/A/G
2. Executive Summary
3. Layer 1 — Classifier
   - Render table from JSON
4. Layer 2 — Mandatory Gates
   - Table with:
     - Pass = green
     - Fail = red
     - N/A = grey
5. Layer 3 — Rated Dimensions
   - Four expandable sections
   - Each with score tables
6. Layer 4 — Positioning Profile
   - Three subsections
   - Horizontal sliders or labelled tables
7. Recommendation
   - Highlighted callout box
8. Sources & Caveats

## 7. Testing Requirements

### 7.1 Unit tests

- JSON schema validation
- Loader correctness
- R/A/G logic

### 7.2 Integration tests

- Page renders with full Cohere dataset
- Index lists correct latest version

### 7.3 Visual regression

- Tables render correctly across breakpoints

## 8. Deployment Considerations

- No new infra required.
- Compatible with GitHub Pages / Vercel static export.
- New assessments added via PRs.

## 9. Future Extensions

- Add comparison view across vendors.
- Add timeline view for version changes.
- Add rubric visualisation (radar chart).
- Add search/filter across assessments.

## 10. Deliverables

1. `assessment.schema.json`
2. Cohere v0.1 assessment JSON + MD
3. Loader implementation
4. Assessment index page
5. Assessment detail page
6. API JSON endpoints
7. Tests
8. Documentation (`/docs/assessments.md`)
