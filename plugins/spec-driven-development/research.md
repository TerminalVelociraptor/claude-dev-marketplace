# Spec-driven development research

Date: 2026-09-23. Our chain: Vision + System + Open decisions → Component specs → Slices → Tasks, with ADRs alongside.

## Result
- **The chain holds.** No source has a level we're missing. Two of our levels, Open decisions and superseded ADRs, fill gaps that other tools' users report.
- **The main risk is weight, not structure.** Every tool draws the same complaint: too many documents that are too long for the size of the problem. Our chain has more levels than any of them, so keeping each document short matters more than adding anything.
- **Borrow for the generators:** ask one question at a time, never invent (mark unknowns instead), and draft a section, then challenge it.

## How sources map to our levels

| Source | Vision | System | Open decisions | Component specs | Slices | Tasks | ADRs |
|---|---|---|---|---|---|---|---|
| GitHub Spec Kit | `constitution.md` (engineering principles only) | inside per-feature `plan.md` | inline `[NEEDS CLARIFICATION]` markers, removed when answered | inside `plan.md` | per-feature `spec.md` | `tasks.md` | none (constitution amended in place) |
| OpenSpec | `project.md` (conventions only) | none | inside per-change `proposal.md` | living `specs/<capability>/spec.md` | per-change `proposal.md` + delta specs | `tasks.md` | none (updated in place) |
| Kiro | steering `product.md` (optional) | steering `structure.md`/`tech.md` + per-feature `design.md` | none (Q&A and approval gates) | inside `design.md` | per-feature `requirements.md` (EARS) | `tasks.md` | none |
| Agent OS | `mission.md`, `roadmap.md` | `tech-stack.md` (technology only) | `shape.md` (decisions already made) | per-feature `spec.md` (v2) | inside `shape.md` | `plan.md` | none |
| Tessl (method tile) | none | none | none | `.spec.md` per feature | merged into `.spec.md` with `[@test]` links | none | none |
| BMAD | `brief.md`, first half of `prd.md` | `architecture.md` | none; issue #1638 asks for one | inside epics/stories | stories (a story is between a slice and a task) | stories | inside `architecture.md` (edited) |
| Shape Up | pitch: problem, appetite, no-gos | pitch: solution sketch | pitch: rabbit holes (settled once) | none | none (scopes found while building) | none | none |
| Story mapping (Patton) | backbone of activities | none | none | none | release slices; the first one is the walking skeleton | stories | none |
| C4 / arc42 | arc42 §1–3 | C4 context + container; arc42 §3–5 | arc42 §11 risks | C4 component; arc42 §5 | none | none | arc42 §9 (in the doc) |
| Nygard ADR / MADR | none | none | none | none | none | none | yes: superseded, never edited |

**Patterns:**
- Most tools work per feature: one feature spec (≈ our Slice) → design → tasks. Only OpenSpec keeps living specs per capability (≈ our Component specs) apart from per-change documents (≈ our Slices). That's the closest match to our lower chain.
- Project-level documents (Vision, System) exist only in BMAD, Agent OS, Kiro steering and arc42, and are thin or optional in all of them except BMAD and arc42.

## What each source asks at each level

**Vision level**
- **Shape Up pitch:**
  - Problem: "The best problem definition consists of a single specific story that shows why the status quo doesn't work."
  - Appetite: "How much time we want to spend and how that constrains the solution".
  - No-gos: "Anything we're not doing in this concept".
- **Agent OS `mission.md`:** "Product mission, vision, target users, use cases, differentiators". Its roadmap asks for MVP features and post-launch features. *(from the agent's report, not checked)*
- **Patton:** the backbone is found by narration: "explain to me what the system does at a high level – just tell me the activities. That's the order."

**System level**
- **Spec Kit's pre-plan gates ask:** "No future-proofing?" and "Using framework directly?"
- **C4:** a context diagram plus a container diagram "will often be sufficient" *(secondary source, not checked)*. This matches our System section plus its context diagram.

**Component spec level**
- **OpenSpec:** "A spec is a behavior contract, not an implementation plan." It says to avoid "Internal class/function names; Library or framework choices; Step-by-step implementation details".

**Slice level**
- **Spec Kit `spec.md`:** "Focus on WHAT users need and WHY / ❌ Avoid HOW to implement (no tech stack, APIs, code structure)".
- **Kiro:** acceptance criteria in EARS form ("WHEN … THE SYSTEM SHALL …") *(not checked)*. Our "situation and what the user sees" does the same job.

**ADRs**
- **Nygard:** "we will keep the old one around, but mark it as superseded". Our rule matches his.
- **MADR** adds Considered Options, which our Alternatives already covers.

## Interaction patterns the generators could borrow

| Pattern | Source | Checked |
|---|---|---|
| "Ask exactly one question per message during requirement gathering" | Tessl tile | ✔ |
| Don't guess: mark it, e.g. `[NEEDS CLARIFICATION: auth method not specified - email/password, SSO, OAuth?]` | Spec Kit `spec-driven.md` | ✔ |
| Draft a section, then offer a menu of five challenge methods (pick, reshuffle, list all, proceed). A method's changes are applied only if you accept them. | BMAD advanced elicitation `SKILL.md` | ✔ |
| Challenge methods that fit planning: Pre-mortem, 5 Whys, First Principles, Socratic Questioning, Inversion, Occam's Razor, Subtraction, Abstraction Laddering | BMAD `methods.csv` | ✔ |
| Conversational explore mode that writes nothing until you ask | OpenSpec `/opsx:explore` | agent report only |
| "Keep it lightweight — This is shaping, not exhaustive documentation" | Agent OS `shape-spec.md` | ✔ |
| Short answers are fine; a skipped section gets "To be defined" | Agent OS `plan-product.md` | agent report only |
| Others comment "to poke holes or contribute missing information", not to approve | Shape Up ch. 6 | ✔ |

## What people report as too heavy

- **Kiro on a small bug** (Böckeler, martinfowler.com):
  - "the workflow was like using a sledgehammer to crack a nut"
  - the documents were "very verbose and tedious to review"
  - "An effective SDD tool would at the very least have to provide flexibility for a few different core workflows, for different sizes and types of changes." ✔
- **The same article on how far structure helps:** "Even with all of these files and templates and prompts and workflows and checklists, I frequently saw the agent ultimately not follow all the instructions." ✔
- **BMAD, from a solo developer on a personal project (issue #446):**
  - "[the analyst] created 500+ page brief from 440+ page summary. A brief should be brief"
  - "I become the workflow engine."
  - They also rated the elicitation techniques "Exceptional for requirements gathering". ✔
- **BMAD, planning is one-way (issue #1638, closed):** "when these decisions surface, I have to manually remember to go back and update the upstream documents." ✔
- **Spec Kit and OpenSpec on Reddit:** "overkill" for small projects; "Specs drift, and you end up re-speccing more than building"; "eight files and roughly 1,300 lines of specification text" for a trivial feature. *(agent report only, not checked)*

## Considered and not adopted
These fall under the "Not wanted" list in `brief.md`: gates, tracked state, or checks on other steps.
- Approval gates between phases (Kiro, Tessl).
- Readiness checks and cross-document analysis gates (BMAD, Spec Kit `/analyze`). The update skill's contradiction check covers this on demand.
- Task status tracking (Kiro, BMAD).
- Per-change delta specs (OpenSpec).
- Inline markers in place of Open decisions (Spec Kit). Simpler, but there'd be no one place to see every open question, and technology preferences raised early would have nowhere to go.

## What was checked
- **✔ Read in the primary source:**
  - BMAD issues #446 and #1638, plus the elicitation `SKILL.md` and `methods.csv` (via `gh api`)
  - Spec Kit `spec-driven.md`
  - OpenSpec `docs/concepts.md`
  - Shape Up chapter 6
  - Patton's "The New Backlog"
  - the Tessl tile README
  - Böckeler's article on martinfowler.com
  - Agent OS `shape-spec.md`
- **Agent report only, not checked:**
  - Reddit quotes
  - Kiro doc details (EARS, Quick Spec, Sync Files)
  - Agent OS `plan-product.md` quotes
  - arc42 and C4 details
  - the ozimmer.ch article on ADR mistakes
  - BMAD's Medium, Scribd and dev.to sources
  - OpenSpec `/opsx:explore` transcripts
  None of these alone supports anything in `sdd.md` or `brief.md`.
- **Method:** four Sonnet subagents, each on a group of sources, followed by spot checks against the primary sources.
