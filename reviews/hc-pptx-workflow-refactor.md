# HC PPTX Workflow Refactor Playbook

## 1) Refactor Goals
- Reduce manual copy/paste between Excel and PowerPoint.
- Enforce HC standards as **gates**, not post-hoc review notes.
- Make every slide auditable.

## 2) Refactored Operating Model

### Gate A — Brief Intake (mandatory)
Required fields:
- audience
- objective
- decision requested
- timeframe
- source workbook + tabs + ranges
- delivery deadline

### Gate B — Insight Contract (mandatory)
Claude output must include:
- KPI values
- trend direction
- outlier explanation
- source range for each metric
- known limitations

Reject output if source ranges are missing.

### Gate C — Story Contract (mandatory)
Each planned slide must include:
- message title (assertive statement)
- evidence list
- chart/table type
- desired executive action

Reject if message is descriptive but not decision-oriented.

### Gate D — Build Contract (mandatory)
PowerPoint build rules:
- must use HC template master
- max one core claim per slide
- footer contains source and as-of date
- avoid decorative visuals without analytical purpose

### Gate E — QA Contract (mandatory)
- Content QA pass: metrics, labels, dates, units
- Visual QA pass: overlap, overflow, contrast, alignment, consistency
- Accessibility pass: minimum font sizes, readable color pairs, alt text policy

## 3) Prompt/Instruction Patterns to Standardize

### Excel analysis prompt pattern
"Analyze ranges [X] for [objective]. Return KPI table with values, deltas, and `source_cell_range` per KPI. Highlight anomalies and confidence notes."

### Story synthesis prompt pattern
"Create a decision-oriented slide plan from this KPI table. For each slide provide: title, key takeaway, evidence, chart type, and action."

### Deck build prompt pattern
"Build slides using HC template constraints: typography, spacing, footer citations, and accessibility requirements."

### QA prompt pattern
"Perform compliance QA against HC checklist. Return only violations with severity, slide number, fix, and recheck status."

## 4) KPI Targets After Refactor
- 30–50% reduction in deck production cycle time.
- 90%+ first-pass compliance on HC formatting standards.
- 100% source traceability for numeric claims.

## 5) Rollout Plan
1. Pilot on one recurring weekly deck.
2. Measure baseline vs refactored cycle time and defect rate.
3. Codify exceptions into checklist.
4. Expand to all briefing decks.
