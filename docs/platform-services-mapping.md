# Platform Services Mapping (v0.1)

This document maps the HC News Briefing pipeline to Application Platform Service domains (TOGAF-style) and defines baseline standards, controls, and ownership.

## 1) Scope

In scope:

- Scheduled pipeline execution and orchestration (`news_pipeline.yml`)
- Feed health testing (`test_feeds.py`)
- Brief generation (`generate_latest.py`)
- Published artifacts (`health.json`, `latest.txt`)
- Status and workflow pages (`status-site/*.html`, root `*.html`)

Out of scope (for v0.1):

- Full EA repository/package structure and viewpoints
- End-to-end DR runbooks
- Cost/FinOps optimization

## 2) Platform Service Taxonomy

The following service domains are used:

1. Data Interchange Services
2. Data Management Services
3. Security Services
4. Location and Directory Services
5. Network Services
6. System and Network Management Services

## 3) Component-to-Service Mapping Matrix

| Component / Artifact | Role in system | Applicable service domains |
|---|---|---|
| `news_pipeline.yml` | Scheduling, orchestration, dependency install, commit automation | System & Network Mgmt, Security, Network, Data Interchange |
| `test_feeds.py` | Connectivity and feed health validation | Data Interchange, Network, System & Network Mgmt |
| `generate_latest.py` | Transforms source data into latest briefing output | Data Management, Data Interchange, Security |
| `health.json` | Machine-readable health/status output | Data Management, Data Interchange |
| `latest.txt` | Published latest briefing artifact | Data Management, Data Interchange |
| `status-site/intelligence.html` | Human-readable status/reporting UI | Network, Security, System & Network Mgmt |
| `status-site/pptx-builder.html` | Workflow support UI for PPTX artifacts | Network, Security, System & Network Mgmt |
| `index.html` / `intelligence-editor.html` / `pptx-builder.html` | Public/static interaction surface | Network, Security |

## 4) Baseline Standards by Service Domain

### 4.1 Data Interchange Services

Standards:

- All external feed/API calls must use explicit request timeouts.
- Response parsing must validate expected structure before write/publish.
- Failed exchange attempts must produce machine-readable status details in `health.json`.

Controls/checks:

- Unit/integration checks for parser failures and malformed payloads.
- Status serialization check in CI.

Owner: Pipeline Maintainer

### 4.2 Data Management Services

Standards:

- `health.json` and `latest.txt` are canonical generated artifacts and must be reproducible from source + scripts.
- Generated files should maintain stable schema/format and document version bumps.
- Retention/rollover policy for generated artifacts must be explicit (to be defined in v0.2).

Controls/checks:

- Schema/format validation for `health.json` and `latest.txt`.
- Change review for any breaking format change.

Owner: Data/Content Maintainer

### 4.3 Security Services

Standards:

- Secrets (tokens/keys) must never be committed to repository content.
- Use least-privilege credentials for workflow write-back actions.
- Workflow actions should be pinned to trusted versions and reviewed periodically.

Controls/checks:

- Secret scanning in CI.
- Quarterly review of action versions and permissions.

Owner: Repo Administrator

### 4.4 Location and Directory Services

Standards:

- External endpoint inventory (feeds, APIs, domains) must be maintained in a single reference.
- Domain/source ownership and trust level must be documented.

Controls/checks:

- Automated check to detect unknown/unapproved endpoints (to be implemented).

Owner: Source Governance Maintainer

### 4.5 Network Services

Standards:

- All remote calls must use HTTPS unless explicitly justified.
- Retry and backoff policy must be consistent across fetch paths.
- Scheduled workloads should respect source rate limits and polite crawl intervals.

Controls/checks:

- Endpoint protocol check (https://).
- Timeout/retry configuration linting (to be implemented).

Owner: Pipeline Maintainer

### 4.6 System and Network Management Services

Standards:

- Pipeline execution must be observable via workflow logs and `health.json`.
- Daily scheduled run and periodic feed health runs are required operational controls.
- Failure paths should produce actionable statuses and not silently succeed.

Controls/checks:

- Scheduled run verification.
- Alerting mechanism for repeated failure (to be implemented).

Owner: Operations Maintainer

## 5) Current Gaps and Backlog (v0.1)

| Gap | Risk | Priority | Proposed action |
|---|---|---|---|
| No single endpoint inventory file | Untracked source risk | High | Add `docs/source-endpoints.md` with owner + trust level |
| No explicit retry/backoff standard doc | Inconsistent resiliency | High | Add shared fetch policy section in `README.md` or `docs/` |
| Limited formal schema checks for outputs | Silent data quality regressions | Medium | Add schema/format validation step in workflow |
| No formal alerting on repeated failures | Delayed incident response | Medium | Add notification hook after N consecutive failures |
| No documented retention policy | Growth/traceability ambiguity | Low | Define retention/versioning policy for artifacts |

## 6) Change Management and Review Cadence

- Trigger a platform-services review when:
  - adding a new feed/source/API,
  - changing output format/schema,
  - changing workflow permissions/actions,
  - adding/removing scheduled jobs.
- Review cadence: monthly light review, quarterly control review.

## 7) RACI (Initial)

| Activity | Repo Admin | Pipeline Maintainer | Data/Content Maintainer | Ops Maintainer |
|---|---|---|---|---|
| Maintain taxonomy and mapping | A | R | C | C |
| Approve security control changes | A | C | C | C |
| Implement pipeline/network controls | C | A/R | C | R |
| Validate data artifact format changes | C | C | A/R | C |
| Run monthly review | A | R | R | R |

Legend: R = Responsible, A = Accountable, C = Consulted

## 8) Definition of Done for v0.1

This mapping is considered adopted when:

1. Document is merged and linked from project documentation.
2. Each service domain has at least one concrete control/check.
3. Top-3 high/medium gaps have tracked implementation issues.
