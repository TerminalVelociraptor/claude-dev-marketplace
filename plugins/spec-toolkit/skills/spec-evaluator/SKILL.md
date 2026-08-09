---
name: spec-evaluator
description: Run a full evaluation of a project design or architecture specification — consistency, completeness against a peer-established rubric, technical fact-checking via web search, and concision — and return a graded, actionable review. Use this whenever the user asks you to evaluate, review, assess, critique, grade, or do a full/thorough check of a design doc, architecture spec, technical design, RFC, or design proposal, including loose phrasings ("is this spec any good?", "review my architecture", "what's wrong with my design doc?"). For a consistency-only check use spec-consistency; to only validate technical claims use spec-factcheck.
---

# Spec Evaluator

Run the full evaluation as an ordered sequence of passes. The order matters: each pass
depends on the ground established by the ones before it. Run them in this order, keep each
pass's output compact and clearly labeled, and do not let a later pass silently undo an
earlier one.

Get the spec first. If the user referred to a spec without providing it, ask for the file or
path — do not invent one.

## Pass 1 — Consistency (establish ground truth)

Read and follow the shared procedure:

```
${CLAUDE_PLUGIN_ROOT}/shared/consistency-checks.md
```

Run this first because every later pass must judge a coherent spec. Resolve — or at least
surface — contradictions and terminology drift before checking completeness, facts, or length.

## Pass 2 — Completeness (the one additive pass)

Read and score against the rubric:

```
${CLAUDE_PLUGIN_ROOT}/shared/rubric.md
```

Determine the applicable tier using the rubric's rules, then score each applicable criterion
(2 / 1 / 0), plus the cross-cutting checks. For any score below 2, name the gap and give one
concrete fix tied to what the criterion asks for. Apply the blocking rule: any Tier-1
criterion at 0 is a blocking defect regardless of total score.

This is the only pass that recommends *adding* content. Keep its additions to genuinely
missing required material — do not pad.

**Record which sections/criteria you confirmed as present.** Pass 5 uses this.

## Pass 3 — Technical fact-check (validate checkable claims)

Read and follow the shared procedure, including its abstention rules:

```
${CLAUDE_PLUGIN_ROOT}/shared/factcheck-procedure.md
```

Now that the spec is coherent and structurally assessed, verify its web-checkable technical
claims via search, and explicitly abstain on claims that are internal to the system or are
design opinions. Report Confirmed / Wrong / Outdated / Unsupported with sources for Wrong and
Outdated, and list the non-verifiable claims separately.

## Pass 4 — Concision (moderate)

Condense last among the working passes, because Passes 1 and 3 often expose the redundancy,
and there is no point tightening prose you were about to flag as wrong or contradictory.

Keep this **moderate**: flag clear duplication (the same fact stated in multiple places) and
obvious padding, and identify sections that repeat each other or restate the same decision.
Point to locations and say what to cut or merge. Do **not** set a target length or produce an
aggressive trim list, and do not cut anything required — defer to Pass 5 on retention.

## Pass 5 — Retention check (guard against over-cutting)

This is a targeted guard, not a fresh completeness pass, so it cannot re-trigger additions.
Compare your Pass 4 cut/merge recommendations against the sections and criteria you confirmed
present in Pass 2. Flag any recommended cut that would remove or gut a required section.
Output is flag-only: "cutting X would drop required section Y — keep or relocate instead."
Do not propose new content here.

## Output format

Return one review with these labeled sections, in this order:

```
# Spec Evaluation: [spec name]

**Assumed tier:** [1 / 1+2 / 1+2+3] — [one line on why]

## Blocking issues
[Blocking contradictions from Pass 1 and any Tier-1 criterion at 0 from Pass 2. "None" if none.]

## Consistency (Pass 1)
[Findings: locations, the conflict, severity, suggested resolution. "Consistent" if clean.]

## Completeness (Pass 2)
[Table: Criterion | Score (0/1/2) | Gap and fix. Cover all applicable criteria incl. Q1-Q5.]
[Per-tier score summary and overall percentage.]

## Technical fact-check (Pass 3)
[Checkable claims: Confirmed / Wrong / Outdated / Unsupported, with sources for Wrong/Outdated.]
[Separately: claims deliberately not judged (internal facts, opinions, predictions).]

## Concision (Pass 4)
[Redundancy and padding, with locations and what to cut or merge. Moderate — no target length.]

## Retention flags (Pass 5)
[Any Pass 4 cut that would remove required content. "None" if concision is safe.]

## Top priorities
[The 3-5 highest-leverage fixes across all passes, ordered by impact: blocking first,
then wrong/outdated facts and 0-score criteria, then high-value 1s, then redundancy.]
```

## Rules

- Keep each pass's output terse and structured — findings, not re-explanations of the spec —
  so the running review stays lean even on a long spec.
- Be specific and honest across every pass; do not credit intent that is not on the page, and
  do not invent facts to fill gaps.
- Do not rewrite the spec. This skill diagnoses; the user (or spec-writer) revises.
- Do not reproduce the rubric or the shared procedures in the output; the graded review is the
  deliverable.
