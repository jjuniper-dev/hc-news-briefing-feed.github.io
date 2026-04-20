# HC PPTX Workflow Assessment

## Objective
Create a repeatable workflow that uses Claude's Excel + PowerPoint shared context capability while enforcing HC standards before delivery.

## Current-State Risks (typical)
1. **Linear handoff workflow**: data extraction, story drafting, slide building, and QA happen in separate passes.
2. **No explicit quality gates**: compliance checks happen late, usually after visual build is complete.
3. **Weak traceability**: insights in slides are not always linked to source-table locations or refresh timestamps.
4. **Manual formatting drift**: recurring decks gradually diverge from HC design standards.
5. **Single-pass generation**: generated content is accepted without extract-and-verify loops.

## Target-State Architecture

### Stage 1 — Inputs and Constraints
- Define objective, audience, decision required, and time horizon.
- Pin source workbook tabs/ranges and refresh timestamp.
- Load HC standard constraints (tone, typography, layout, citation, accessibility).

### Stage 2 — Insight Extraction in Excel
- Ask Claude to extract KPIs, trends, anomalies, and deltas from specified ranges.
- Require a table with: `insight`, `value`, `source_cell_range`, `confidence_note`.
- Flag assumptions and missing data explicitly.

### Stage 3 — Narrative Blueprint
- Convert insights into a slide-by-slide outline:
  - slide objective
  - audience takeaway
  - evidence and chart type
  - action/decision statement

### Stage 4 — Deck Build in PowerPoint
- Build from approved HC template/master.
- Keep one message per slide and one primary visual per message.
- Auto-insert source + date footers from extracted ranges.

### Stage 5 — Two-Layer QA (Required)
1. **Content QA**
   - Extract slide text and compare metrics against source ranges.
   - Check every claim has a citation and timestamp.
2. **Visual QA**
   - Render slides to images and inspect overlap, truncation, color contrast, and alignment.
   - Enforce HC accessibility checks (font size floors, contrast, alt text rules where required).

### Stage 6 — Remediation Loop
- Fix violations.
- Re-run both QA layers.
- Produce a final compliance summary for sign-off.

## Maturity Scorecard
Use this 0–3 scoring model (0 = absent, 3 = fully automated):
- Source traceability
- Standards enforcement
- Accessibility enforcement
- Reusability of templates/components
- QA automation depth
- Auditability/sign-off readiness

## Definition of Done
A deck is only complete when:
- all claims trace to source ranges,
- all HC checks pass,
- no visual defects remain,
- and a compliance summary is attached.
