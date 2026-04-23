# hc-news-briefing-feed.github.io

Daily news briefing feed.

## HC PPTX workflow artifacts
- Assessment: `reviews/hc-pptx-workflow-assessment.md`
- Refactor playbook: `reviews/hc-pptx-workflow-refactor.md`
- Compliance checklist: `reviews/hc-pptx-compliance-checklist.md`


Web page: `status-site/pptx-builder.html`


## Phase 1 checks

Run the baseline quality gate locally:

```bash
python scripts/run_phase1_checks.py
```

This executes:
- site architecture contract validation
- feed health test generation
- latest briefing generation
