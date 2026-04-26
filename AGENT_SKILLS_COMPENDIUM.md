# Agent Skills Compendium (DataCamp-Inspired)

This document expands the major categories from the DataCamp article on 100+ agent skills and turns them into an implementation-ready reference for OpenClaw/Codex/Claude-style skill systems.

## 1) Search & Research Skills (12)
- arxiv-watcher
- pubmed-edirect
- wikipedia
- google-search
- serper-search
- newsapi-search
- scholar-scraper
- semantic-search
- patent-search
- rss-monitor
- citation-formatter
- trend-spotter

## 2) Coding & Developer Copilot Skills (14)
- buildlog
- cc-godmode
- debug-pro
- repo-ranger
- unit-test-gen
- refactor-master
- api-stub-gen
- code-review-bot
- changelog-writer
- migration-helper
- docs-from-code
- lint-fixer
- perf-profiler
- dependency-upgrader

## 3) Git, GitHub & PR Workflow Skills (12)
- branch-manager
- commit-crafter
- pr-drafter
- release-notes-bot
- issue-triager
- conflict-resolver
- blame-investigator
- semantic-versioner
- ci-failure-diagnoser
- monorepo-scope-finder
- label-automator
- backport-assistant

## 4) Cloud & Infrastructure Skills (12)
- aws-cli-agent
- gcp-orchestrator
- azure-admin
- terraform-runner
- k8s-operator
- docker-builder
- helm-manager
- cloud-cost-optimizer
- iam-auditor
- serverless-deployer
- observability-provisioner
- incident-runbook-exec

## 5) Machine Learning & Data Skills (12)
- mlflow-runner
- huggingface-loader
- vector-db-agent
- data-cleaner
- feature-engineer
- model-eval-pro
- prompt-eval-suite
- dataset-versioner
- experiment-tracker
- synthetic-data-gen
- drift-detector
- model-card-writer

## 6) Security & Compliance Skills (12)
- vuln-scanner
- log-auditor
- policy-checker
- secret-detector
- threat-intel
- sbom-generator
- license-compliance-checker
- pii-redactor
- container-image-scanner
- sso-config-auditor
- soc2-evidence-helper
- incident-postmortem-writer

## 7) Communication, Docs & Chat Skills (12)
- email-sender
- slack-bot
- meeting-notes
- translator-pro
- tone-adjuster
- faq-builder
- support-reply-drafter
- doc-summarizer
- transcript-highlighter
- decision-log-writer
- policy-explainer
- onboarding-guide-bot

## 8) Growth, Marketing & Revenue Ops Skills (12)
- seo-analyzer
- content-generator
- crm-updater
- lead-scorer
- campaign-optimizer
- keyword-clusterer
- competitor-monitor
- landing-page-copilot
- newsletter-builder
- social-post-scheduler
- ad-copy-tester
- attribution-analyst

## 9) Media, Creative & Production Skills (12)
- image-editor
- video-cutter
- audio-cleaner
- thumbnail-generator
- script-writer
- subtitle-generator
- voiceover-director
- storyboard-planner
- brand-style-enforcer
- podcast-show-notes
- clip-highlighter
- asset-tagging-bot

## 10) Automation & Workflow Skills (12)
- task-runner
- cron-agent
- file-ops
- browser-automation
- form-filler
- webhook-router
- batch-etl-runner
- spreadsheet-sync
- invoice-processor
- qa-checklist-runner
- rpa-desktop-bridge
- human-in-the-loop-gater

## 11) Specialized & Emerging Skills (12)
- bioinformatics-agent
- legal-researcher
- finance-quant
- simulation-runner
- agent-benchmark
- clinical-trial-miner
- contract-risk-analyzer
- portfolio-stress-tester
- geospatial-insight-engine
- climate-scenario-modeler
- robotics-planner
- education-tutor-orchestrator

**Total skills listed:** 132

---

## Installation snippets

### A) Generic Codex-style skill install from GitHub path
```bash
python /opt/codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo mattpocock/skills \
  --path <skill-folder>
```

### B) Install multiple in one go
```bash
python /opt/codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo mattpocock/skills \
  --path repo-ranger debug-pro unit-test-gen
```

### C) URL-based install
```bash
python /opt/codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --url https://github.com/mattpocock/skills/tree/main/<skill-folder>
```

---

## OpenClaw-ready `SKILLS.md` manifest (starter)

```md
# SKILLS

- repo-ranger
- debug-pro
- unit-test-gen
- ci-failure-diagnoser
- task-runner
- browser-automation
- vuln-scanner
- policy-checker
- semantic-search
- meeting-notes
```

---

## Capability matrix template

| Skill | Category | Required tools | Data sensitivity | Human approval | Typical outputs |
|---|---|---|---|---|---|
| repo-ranger | Coding | filesystem, ripgrep | Low | No | code map, dependency graph |
| debug-pro | Coding | filesystem, test runner | Medium | Optional | root cause, patch plan |
| ci-failure-diagnoser | Git/CI | logs, git metadata | Medium | Optional | failure triage report |
| task-runner | Automation | shell, scheduler | Medium | Yes (prod) | workflow execution logs |
| browser-automation | Automation | browser, network | Medium | Yes | scraped records, screenshots |
| vuln-scanner | Security | scanner binary, SBOM | High | Yes | vulnerability report |
| policy-checker | Security | policy engine | High | Yes | pass/fail controls matrix |
| semantic-search | Research | vector DB, embeddings | Medium | No | ranked retrieval set |
| meeting-notes | Communication | transcript input | Low/Medium | No | summary, action items |
| finance-quant | Specialized | data API, compute | High | Yes | model outputs, charts |

---

## Recommended rollout packs

- **Starter (low-risk):** semantic-search, repo-ranger, meeting-notes, task-runner
- **Engineering-heavy:** debug-pro, unit-test-gen, ci-failure-diagnoser, refactor-master, dependency-upgrader
- **Ops + security:** vuln-scanner, policy-checker, secret-detector, incident-runbook-exec
- **Growth + content:** seo-analyzer, content-generator, campaign-optimizer, newsletter-builder

## Notes
- Treat this as a practical taxonomy and implementation blueprint.
- Enable high-risk skills (security/infra/finance) with explicit human approval gates.
