# Project Documents

What each document in a project contains, why, and which documents it links back to. The chain runs from an idea to tasks: Vision, System and Open decisions → Component specs → Slices → Tasks. ADRs sit alongside.

Each entry opens with what the document is for, then where it lives and its size. After that:
- **Contains:** the items the document holds, each with *why* it's there: the decision it forces or the mistake it prevents. An item with no clear why doesn't belong, and nothing outside this list belongs in the document.
- **Links back to:** the documents it draws on.

**Link, don't copy.** A document links to what it draws on and never restates it. Derived files are the only copies, and they're regenerated from their source.
*Why:* a fact stated once can't disagree with itself.

**Keep it short.** Each document you write gives a size. A document well over it is usually doing another document's job.
*Why:* long documents are tedious to review, and more text doesn't make agents follow it any better.

These documents have a "not" item: Vision's Non-goals, System's Not in the system, a component's Doesn't do, and a slice's and a task's Out of scope. It lists only what a reader might expect or an agent might add, each with where it lives instead or why not.

## What this process is not
- **Not implementation.** The chain ends at Tasks. Building a task happens in your own workflow.
  *Why:* the documents say what to build; how you build it stays yours.
- **Not a project tracker.** The documents are the only state. Nothing records which slice is current, what's been reviewed, or what's due, and no field exists only so a later step can check an earlier one.
  *Why:* tracked state needs a rule for every change of state, and those rules need patches.
- **Not automation.** A skill runs when you run it, on what you name. Nothing fires when a PR merges or a slice finishes.
  *Why:* triggers need tracked state and tie skills to each other.
- **Not a check on you.** It checks documents. How and when you work is yours.

---

## Vision

What you're building, for whom and why, and how much of it this version includes.
`docs/01-overview.md`, `## Vision` section. About a page.

**Contains:**
- **Problem and users:** the problem, told as one specific story of why today's way doesn't work; who has it (you, friends, the public); and what you do today instead.
  *Why:* anchors every later trade-off. A specific story keeps the problem concrete enough to check the MVP against; a general statement fits any solution. "For whom" sets the scale: just you vs. the public changes hosting, security and polish. Today's workaround is the bar the MVP has to beat.
- **Goals:** a handful of outcomes for this version, each with a check you could actually run.
  *Why:* defines success, and the checks tell you when you're done rather than still adding. Goals say what success looks like; the MVP says the smallest thing that achieves it. When the appetite forces cuts, the goals say what has to survive.
- **MVP:** the smallest thing you'd use, in user terms: running end to end, thinly. Plus its appetite: how much time you're willing to spend on it.
  *Why:* the scope line for this version; everything outside it waits. The appetite turns "small enough to finish" into a number you set up front, and makes scope, not time, the thing that gives.
- **Non-goals:** what you're not building in this version, including things you want eventually.
  *Why:* the strongest single guard against scope creep and over-engineering, for you and for agents.
- **Priorities:** 2–4 things ranked for when they conflict: qualities (e.g. reliability over speed), or something you want to learn by building this (e.g. learning Rust over shipping fast). Features aren't ranked.
  *Why:* settles trade-offs in the System section and ADRs without asking you again. Left alone, agents make their own trade-offs, usually toward more features and more flexibility. A learning priority is the one legitimate reason to choose unfamiliar technology.
- **Constraints:** what is fixed and not yours to choose: things you own or must work with, rules you hold to (e.g. no cloud accounts), money limits (e.g. free tiers only).
  *Why:* stops the design choosing something you can't use, and separates what's fixed from what's still a choice.

**Links back to:** nothing. It's the top of the chain and starts from your idea.

---

## System

What the parts are, what each is responsible for, and how they connect.
`docs/01-overview.md`, `## System` section. One to two pages.

**Contains:**
- **Components:** each with a one-sentence role, what it owns, where it runs (conceptually: your machine, an always-on server, a phone, the user's browser; no hosts or products), and, if the user touches it, through what (a page, a command, a report).
  *Why:* the map you and agents navigate by. "Owns" stops two components doing the same job; a role that needs "and" is probably two components. Where it runs catches mismatches that break the design, such as a scraper that must run daily when the MVP only runs on your laptop. "Through what" shows where the user meets the system, which is where every slice's outcome shows up.
- **Contracts:** who provides what to whom, in plain language (e.g. "Scraper provides events: venue, date, artists, source URL").
  *Why:* the seams each component can rely on, agreed before anyone picks a format.
- **Shared data model:** only entities that cross a component boundary; for each, what it means (only fields that could be misread) and its one owner.
  *Why:* catches duplication (an entity wanting two owners) and coupling (a component needing much of another's data) early, and settles the meanings agents would otherwise guess, such as whether an event's date is local time.
- **External systems:** APIs, scraped sites, devices; for each, what still works and what the user sees when it fails.
  *Why:* the dependencies you don't control, and the likeliest to break. What the user sees when one fails is a design choice; left open, it gets made in code.
- **MVP trace:** the MVP walked through the components, each step with an owner.
  *Why:* proves the split works end to end. A step with no owner is a gap; a component the MVP never touches isn't needed yet.
- **Not in the system:** structure a reader or agent might expect that deliberately isn't there (e.g. no user accounts, no plugin mechanism, no configuration layer).
  *Why:* System is where agents add generality, such as a layer for swapping providers or settings nobody asked for. Saying what isn't there stops it at the level that decides structure.

**Links back to:** Vision; Open decisions and ADRs, where a part depends on something unsettled or decided there.

---

## Open decisions

Questions that need deciding or checking, what would settle each, and a link to each answer.
`docs/01-overview.md`, `## Open decisions` section, after System. One line per question.

**Contains:**
- **Questions:** a choice not made yet (a technology you mentioned, where something runs) or a risk nobody has checked (feasibility, data, cost); a link to where it came from (a document, or you); if answering it needs a spike (a task that tries something out), what result would settle it; and, for a settled question, a link to its answer: its ADR, or the document it concerns.
  *Why:* keeps technology preferences and guesses out of Vision and System without losing them. Agents fill gaps confidently; this marks where the gaps are. What would settle it tells a spike when it's done. A settled question keeps its line, so nothing that links to it breaks; a question with no answer link is still open.

**Links back to:** the document each question came from.

---

## ADR (decision record)

Why a decision was made that someone would ask "why?" about, and what was rejected.
`docs/decisions/NNNN-<title>.md`, one file per decision. Half a page.

**Contains:**
- **Context:** the question it settles, linked in Open decisions, and the priorities and constraints it relies on, each named and linked (e.g. "relies on: reliability over speed").
  *Why:* shows why this answer fits this project, so you can tell later whether it still holds when a priority or constraint changes.
- **Evidence** (only if a spike was run): what the spike tried and found.
  *Why:* this is where a spike's result survives, whatever happens to its code. It shows the decision rests on something tested, not a guess.
- **Decision:** the choice, in a sentence or two.
  *Why:* the answer itself, stated once, so other documents can point to it instead of restating it.
- **Alternatives:** each option not taken, with one line on why not.
  *Why:* stops the same question being reopened. Agents often suggest a rejected option again, and the "why not" lets you dismiss it quickly.
- **Consequences:** what the decision makes easier or harder, and what would make you revisit it.
  *Why:* the costs you accepted, stated up front, and the signal that the decision has stopped fitting.
- **Supersedes** (only if it replaces an earlier ADR): the ADR it replaces.
  *Why:* a decision is replaced by a new ADR, never by editing the old one, so the reasons for the old one survive. An ADR is current unless a later one supersedes it.

**Links back to:** Open decisions (the question it settles); Vision (the priorities and constraints it relies on); the ADR it supersedes.

---

## Component spec

What one component promises to the rest of the system, precisely enough to build and test against.
`docs/components/<name>.md`, one per component. A few pages at most; longer probably means it's two components.

**Contains:**
- **Doesn't do:** things a reader might expect here that belong elsewhere, and options, extension points or generality it deliberately lacks.
  *Why:* agents fill gaps, absorb neighbouring jobs and add generality nobody asked for. This states the boundary where they'll read it.
- **Contracts it provides:** for each contract System says it provides: fields and types, errors and bad-input behaviour, and one example. Shared entities link to their meaning in System's data model.
  *Why:* what other components and tasks build against. System says it in plain language; this makes it exact. The example doubles as a test case and is what agents copy best. One definition per contract means the two sides can't disagree.
- **Owned data:** for each entity it owns, its fields, what identifies it, and when it's created, changed or deleted.
  *Why:* System gives an entity's meaning; this adds identity and lifecycle, which is where most data bugs come from (a re-scrape duplicating a record instead of updating it).
- **External quirks:** for each external system it talks to, the limits and quirks the design relies on (rate limits, formats, how it fails).
  *Why:* facts often learned once, in a spike, that agents can't guess. Without them they get rediscovered the hard way.
- **Approach** (optional): a short paragraph on how it does its job, only where that isn't obvious from the contracts.
  *Why:* keeps your mental model of the component, and stops agents inventing a different approach on each task.

**Links back to:** System; the ADRs behind its technology; the specs of components whose contracts it uses; Open decisions, for anything it leaves unsettled.

---

## Slice

One thin, user-visible piece of this version, and what "working" means for it.
Wherever you put it (a file, a GitHub issue). About half a page.

**Contains:**
- **Outcome:** one line: what the user can do afterwards that they couldn't before.
  *Why:* keeps slices vertical. "Build the database" has no user outcome, so it isn't a slice. An outcome that needs "and" is two slices.
- **Why this slice:** the Vision goal it advances, or the open question it settles.
  *Why:* a slice with neither is scope creep. Slices that settle open questions early find what could sink the project while it's still cheap to change.
- **Acceptance scenarios:** each a situation and what the user sees.
  *Why:* defines "working" across components. They become the tasks' checks. What the user sees is decided here, not left to whoever builds it.
- **Out of scope:** nearby behaviour this slice deliberately doesn't handle (edge cases, options, variations).
  *Why:* without it, agents handle every edge case and add options no scenario needs.
- **Touches:** the components and what changes in each, with links to the contracts it needs in the component specs.
  *Why:* shows the slice is vertical, which contracts it relies on, and how it splits into tasks.

**Links back to:** the Vision goal or open question it serves; the contracts it touches.

---

## Task

One change small enough to review in one sitting, and how you'll know it's done.
Part of a slice, or standalone for a change that needs no slice (e.g. a dependency bump). Wherever you put it (a file, a GitHub sub-issue). A few lines.

**Contains:**
- **What:** the change, in a sentence or two.
  *Why:* the unit of work. If it needs "and", it's two tasks. It usually touches one component; one that crosses components is usually a contract plus its two sides, and splits into tasks for each.
- **Spec link:** the exact spec or ADR section(s) it builds or relies on, or `none` for a change with no specced behaviour (e.g. a refactor).
  *Why:* gives whoever builds it the exact contract without copying it, which keeps agent context small and keeps one source of truth. The task builds what the spec says; a design choice the spec doesn't make (a contract field, a new dependency, an option, behaviour the user sees) goes back to the spec, not into the task.
- **Out of scope:** what's nearby but not this task.
  *Why:* agents do more than they're asked. Only what's specific to this task; its slice's Out of scope already applies.
- **Check:** a command, or steps and what you should see, naming the acceptance scenario it proves or the open question it settles, if any.
  *Why:* "done" that anyone can run; without it, "looks done" is the only signal. Naming the scenario tells the builder which behaviour the check proves; for a spike, it links to what would settle its question.
- **Depends on** (optional): tasks that must land first.
  *Why:* a fact about the work: one task builds a contract another uses.

**Links back to:** its slice, if it has one; the sections in its Spec link; for a spike, the open question it settles.

---

## Derived files

Generated; you don't write them. Each gives what it's **Derived from** and what it **Holds**.

### CLAUDE.md block

What an agent needs in every session, without loading the documents.
A marked block in the project's CLAUDE.md; everything outside the block is yours. About 20–30 lines.
*Why the size:* it loads in every session.

**Derived from:** Vision (Problem and users, Priorities, Non-goals); current ADRs; the documents in `docs/`; the Task entry's Spec link in this file.

**Holds:**
- The project in one line, with a link to `docs/01-overview.md`.
  *Why:* agents know what the project is for without you restating it.
- Where each document in `docs/` lives, one line each.
  *Why:* agents open the right document; this replaces a code map.
- Priorities and non-goals, copied from Vision.
  *Why:* what an agent most needs in every session to avoid over-engineering and scope creep.
- One line per current ADR (e.g. "uses X — ADR 0003").
  *Why:* agents know the chosen stack and stop suggesting rejected options.
- One rule: if the work needs a design choice the spec doesn't make (a contract field, a new dependency, an option, behaviour the user sees), stop and ask; don't choose.
  *Why:* design choices stay yours. An agent that picks one silently builds it into the code, where you won't see it.

### Path rules

What an agent must not do in a component's code, in front of it while it works there.
`.claude/rules/<component>.md`, one per component spec.

**Derived from:** the component spec; the component's code paths, taken from the repo (the one fact no document holds).

**Holds:**
- A path glob for the component's code.
  *Why:* makes the file load when an agent works in those files, which advice in CLAUDE.md can't guarantee.
- A link to the component spec, and a copy of its "Doesn't do" list.
  *Why:* puts the boundary in front of an agent at the moment it could cross it.

### Context diagram

The single picture of the system.
`docs/context-diagram.md`.

**Derived from:** System's Components (including where the user touches them), Contracts and External systems.

**Holds:**
- A Mermaid diagram of the user, the components, the external systems, and the contracts between them.
  *Why:* the fastest way to reload your mental model after a break. Derived, so it's regenerated rather than edited by hand.
