# dz23-project-governance

Govern new and existing software projects with an evidence-based decision gate, architecture plan, controlled execution slices, verification, risks, and a progress panel derived from the canonical plan.

## Use when

- a new project or project chat needs an initial decision;
- architecture, migration, deployment, integrations, or multi-step implementation must be planned;
- work needs approval boundaries, evidence, handoffs, or visual progress tracking.

## Do not use when

- the request is a trivial, reversible one-file edit and the user did not request project tracking.

## Arsenal

This skill is part of the [dz23-arsenal](../../README.md) and is designed for any new or existing project, not only Brizu.

## Contents

- [`SKILL.md`](SKILL.md) — operating rules and routing;
- [`references/project-artifacts.md`](references/project-artifacts.md) — schemas for tasks, decisions, panels, and handoffs;
- [`evals/evals.json`](evals/evals.json) — behavior scenarios;
- [`PROMPT-ATIVACAO.txt`](PROMPT-ATIVACAO.txt) — compact invocation prompt.

## Invocation

```text
Use the dz23-project-governance skill to start this project.
```

The project defines its own plan and panel filenames. The skill defines the governance process, not a product-specific architecture.
