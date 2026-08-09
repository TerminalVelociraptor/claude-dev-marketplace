---
name: spec-writer
description: Draft a project design or architecture specification that will pass a peer-established rubric. Use this whenever the user asks you to write, draft, create, or put together a design doc, architecture spec, technical design, RFC, or design proposal — including loose phrasings like "help me spec out this system", "I need a design doc for X", or "write up the architecture for this". Prefer this skill over an ad-hoc draft so the spec is complete, measurable, and traceable from the start.
---

# Spec Writer

Produce a project design/architecture specification that satisfies the rubric. Your job is
to run the process below and output the spec itself — not commentary about the process.

## Load the rubric first

The rubric is the target your draft must satisfy and the source of truth for which sections
belong at which tier. Read it before drafting:

```
${CLAUDE_PLUGIN_ROOT}/shared/rubric.md
```

Read the file each run rather than relying on memory of it. Do not restate the rubric to the
user; use it to shape the spec.

## Determine the tier before drafting

Write only the sections the tier requires, using the rubric's trigger rules:

- **Tier 1 (Core):** always.
- **Tier 2 (Standard):** add when the system has more than one component, more than one team,
  or an external dependency.
- **Tier 3 (Extended):** add for safety-critical, regulated, distributed, or long-lived systems.

If the tier is unclear from what the user has told you, ask — or state the tier you assumed
at the top of the draft so they can correct it.

## Ask the up-front questions before drafting

If the answers are not already in the conversation or any provided material, ask these first.
Do not invent facts to fill a required section — a missing answer is a question to ask, not a
blank to guess.

- What problem does this system solve, and for whom?
- What is explicitly out of scope?
- Who are the stakeholders, and what does each care about most?
- What is fixed and cannot change (platforms, languages, deadlines, budget, compliance)?
- What external systems, services, or actors does it interact with?
- Which quality attributes matter most, and what are the measurable targets?
- What are the known constraints, assumptions, and risks?
- What is the expected scale, load, and lifespan of the system?

Ask only what you actually need for the tier in play. Do not force a long interview for a
small Tier-1 spec — gather the essentials, note any assumptions inline, and draft.

## Drafting rules

Apply these throughout, because they are what the rubric's cross-cutting checks score:

- **Make every quality target measurable and testable.** Replace vague adjectives — "fast",
  "secure", "scalable", "robust", "user-friendly" — with a number, threshold, or concrete
  condition (e.g. "p95 API latency < 200 ms at 1,000 req/s", not "fast"). Where useful,
  express a quality attribute as a scenario: source, stimulus, environment, artifact,
  response, response measure.
- **Record each significant decision as an ADR-style block** with these fields: Title
  (numbered), Status (proposed/accepted/superseded), Context (the forces, in neutral
  language), Decision, Alternatives considered (and why rejected), Consequences (positive
  and negative). Only record decisions that affect structure, dependencies, interfaces, or
  quality attributes.
- **Keep every decision traceable** to a requirement, constraint, or stakeholder concern.
- **Include at least one structural diagram**; add runtime and deployment diagrams at
  Tier 2+. Express diagrams as text-based diagram code (Mermaid) unless the user asks
  otherwise, and keep diagram names consistent with the text.
- **State document version, date, owner, and status** at the top.
- **Define non-obvious terms** in a short glossary.

## Section order

Follow the rubric's section list for the tier in play. A typical Tier 1+2 spec runs:
purpose and scope; stakeholders and concerns; constraints; system context and boundary;
high-level solution and structure; key design decisions (ADRs); quality attributes; data
design; interface/API design; runtime behavior; deployment and infrastructure; dependencies
and assumptions; risks and technical debt. Add Tier 3 sections when the tier applies.

## Self-check before returning the draft

Before you output the spec, verify each of these and fix any that fail. Keep this check
lightweight — it catches obvious misses, it is not a full grading (the spec-evaluator skill
is the honest judge):

- Every required section for the chosen tier is present.
- Every quality target is measurable and testable; no vague adjectives remain.
- Every design decision traces to a requirement, constraint, or concern.
- Diagrams and text agree and use the same names.
- Version, date, owner, and status are stated at the top.
- No section contradicts another.

If the user wants a rigorous score afterward, tell them the spec-evaluator skill can grade
the draft against the full rubric.

## Output

- Produce the specification as the deliverable, in Markdown.
- For anything longer than a short Tier-1 spec, write it as a file the user can keep and edit,
  rather than burying it inline.
- Do not include process narration or a restatement of the rubric in the output — just the spec.
