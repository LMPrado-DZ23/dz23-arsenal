---
name: dz23-project-governance
version: 1.0.0
description: Govern L1-L3 project work with a decision gate, evidence-based planning, architecture, execution, verification, and a panel derived from the canonical plan.
user-invocable: true
argument-hint: "<project request or task>"
metadata:
  category: governance
  license: MIT
---

# Project governance

Use for discovery, architecture, multi-step implementation, deployment, integrations, or auditable project tracking. Do not invoke for a trivial one-file edit unless requested.

## 1. Ceremony level

Classify before acting:

- **L1 — small:** one file, reversible, no external integration. No full gate; state goal, scope, and check in three lines, then execute if authorized.
- **L2 — normal:** a coherent feature or investigation. Use a compact gate of at most eight lines, reference the plan, and update plan/panel at the end.
- **L3 — high impact:** architecture, migration, production, irreversible/external action, secrets, payments, DNS, data, or security. Use the full gate, a decision record when required, and point confirmation.

A **cold start** has no readable plan or valid handoff and requires the full gate. A **continuation** has a valid handoff and uses a condensed gate: phase, verified work, blockers, next slice, and approval boundary.

## 2. Core principles

1. The plan is the source of truth for intent, scope, decisions, acceptance, and evidence. Repository, tests, and environment are the source of truth for current state. Record and reconcile divergence; ignore neither source.
2. Separate facts, hypotheses, proposals, and approved decisions. Support material claims with a path/line, command/output, test, or link; label unverified claims.
3. Approval covers only enumerated slices. Destructive, irreversible, externally visible, or high-risk actions inside a slice still need point confirmation unless permanent authorization is recorded.
4. Work incrementally: prepare, execute one slice, verify, record evidence, reconcile, and report the next decision.
5. Completion requires pre-stated acceptance criteria and verification evidence; code written alone is not completion.
6. Use the smallest ceremony and verification safe for the risk.

## 3. Decision gate and approval

At the start of L2/L3 work, read the plan, requested panel, latest handoff, relevant decisions, and repository/environment status. Present:

- objective and current phase;
- verified state and related task IDs;
- completed, missing, blocked, and unverified work;
- risks, dependencies, scope, and out-of-scope items;
- numbered slices with acceptance criteria and checks;
- exact approval boundary.

End with an explicit approval request in the user's language and state which artifacts were read. Do not mutate while waiting, except read-only discovery. If the user waives the gate, record it and retain all safety rules.

Before a task becomes `🌗`, apply Definition of Ready: acceptance criteria, verification check, and files/systems in scope are written. Criteria invented after execution do not qualify. Closure is `self-verified` (agent ran and recorded the check) or `owner-signed-off` (user confirmed); do not confuse them.

## 4. Rituals and artifacts

Use the schemas in [references/project-artifacts.md](references/project-artifacts.md). Keep these symbols unchanged: `⬜ 🌗 ✅ ⚠️ ❌ ➡️ 🟣`.

The panel is a **derived view** of the canonical plan, not a second source of truth. Generate or update it in the same step that closes a slice; never maintain both manually. If generation is unavailable, document and test the manual procedure once. At session end reconcile plan × repository/environment: close orphan tasks, record work outside the plan, and resolve or preserve divergences.

Use one-line evidence:

`EVIDENCE: <command/check> → <short result> (<path>:<line>)`

Do not paste long raw output. Create a Decision Record when a choice is irreversible, expensive to reverse, cross-team, or externally visible. A local reversible choice may be a one-line plan decision.

At session end update the plan/panel and write a handoff when durable memory is used. Include current phase, verified completion, active slice, blockers, decisions, changed files/systems, checks, divergences, and exact next action.

## 5. Architecture mode

Cover only relevant items: goals/non-goals, actors/journeys, boundaries/integrations, data ownership/lifecycle, state transitions, API/errors, authorization/tenant isolation, secrets/auditability, deployment/observability/recovery, performance, compatibility, tests, acceptance, and open decisions. Mark assumptions and give the cheapest validation for material uncertainty.

## 6. Execution mode

For each ready slice: set `🌗`, state scope, avoid unrelated cleanup, run risk-proportional checks, record evidence, and update the plan/derived panel. Use the applicable ladder:

`format → type/lint → unit → integration → e2e/smoke`

State which checks were not run and why. Mark `✅` only when acceptance passes; use `⚠️` with the exact blocker and owner otherwise. After each slice report: done, verified, evidence, affected files/systems, not verified, blockers, and next step.

Stop and escalate when plan/state conflict; discovery exceeds the gate; scope expands; a secret/production data would be touched; or acceptance cannot be verified.

## 7. Security and anti-patterns

Never put tokens, passwords, private keys, service-account JSON, webhook secrets, or personal data in artifacts or output. Inspect presence by name only (`Select-String`/`rg`), redact `*_KEY`, `*_TOKEN`, `PASSWORD`, and `SECRET`, prefer quiet/name-only commands, and never print values.

Avoid: **gate theater** (plan ignored), **evidence inflation** (no reproducible check), **panel drift** (panel disagrees with plan/state), **plan rot** (stale counts/tasks), **approval hoarding** (gate for harmless L1), **silent scope drift**, **discovery restart**, **secret leakage**, and **late verification**.

## 8. Reference

Read [references/project-artifacts.md](references/project-artifacts.md) when creating or validating task records, decisions, panels, or handoffs. Keep detailed schemas there; do not duplicate them here.
