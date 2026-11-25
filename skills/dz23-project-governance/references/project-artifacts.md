# Project artifact schemas

Use these compact schemas as defaults and adapt them to the project.

## Task record

```yaml
id: F2.03
phase: "Project-defined phase"
area: "UI"
title: "Evaluate schedule at 390px"
status: "⬜"
priority: P1
owner: "accountable decision-maker"
assignee: "agent or person executing"
dependencies: [F1.02]
current_state: "Not verified"
acceptance:
  - "Primary flow works at 390px without horizontal scrolling"
verification_plan:
  - "Open the route at 390px and run the focused smoke test"
evidence: []
closure: "open | self-verified | owner-signed-off"
next_step: "Open the route and measure the primary states"
updated_at: "YYYY-MM-DD"
```

Field rules:

- `owner` is accountable for the decision or outcome; `assignee` performs the work. If one person fills both roles, keep both labels explicit.
- `priority`: `P0` blocks release/production or causes critical harm; `P1` is important for the current milestone; `P2` improves the product without blocking it; `P3` is optional/future.
- `phase` is optional and project-defined; do not invent a universal phase taxonomy.
- `acceptance` and `verification_plan` must exist before `🌗`.
- `evidence` uses the one-line format from the skill.

## Decision Record

```markdown
## DEC-YYYY-MM-DD-001 — Title

- Status: proposed | approved | rejected | superseded
- Context: problem requiring a decision
- Options:
  - A — benefit / cost / risk
  - B — benefit / cost / risk
- Recommendation: chosen option and why
- Impact: code, data, operations, cost, security, external parties
- Owner: accountable approver
- Evidence: paths, commands, tests, or links
- Date: YYYY-MM-DD
```

## Progress panel minimum

```text
Header: project, phase, progress, last update, source plan
Current focus: one active task, objective, evidence, next step
Decisions: owner decision, options, impact, status
Risks: blocker, impact, owner, mitigation
Phases: counts by status and expandable tasks
Timeline: newest verified events first
Details: acceptance, evidence, files, checks, not-verified items
```

If the user requested visual tracking and the project has a workspace in files, the panel should support responsive viewing, status filtering, search, phase expansion, and a clear indication that it is derived from the plan.

## Session handoff

```markdown
# Handoff — YYYY-MM-DD — topic

## Current state
- Phase:
- Active slice:
- Status:

## Verified completion
- ID — result — evidence

## Blockers and decisions
- ID — blocker/decision — owner — next action

## Plan × reality reconciliation
- Plan items resolved:
- Orphan work:
- Work outside scope:
- Divergences preserved for follow-up:

## Files and systems changed
- path/system — change — reversible? yes/no

## Checks
- command/check — result
- Not run — reason

## Exact next action
1. ...
```

## End-of-slice report

```text
Result
- Done:
- Verified:
- EVIDENCE:
- Files/systems affected:
- Not verified:
- Blockers:
- Next step:
```
