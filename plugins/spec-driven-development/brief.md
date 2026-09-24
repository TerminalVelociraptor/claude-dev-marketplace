# Tooling brief

What to build for this plugin, and the decisions already made. Read it with `sdd.md` (the document definitions), `research.md` (the evidence behind them) and the repo's `CLAUDE.md` (conventions for every plugin).

## Goal
Help a solo developer write the documents `sdd.md` defines and keep them consistent with each other. The developer stays in the loop and keeps the mental model; the tools interview, challenge, generate and report.

## Hard rule: `sdd.md` is the single source of truth
- `sdd.md` defines every document: what it contains, why each item is there, where it lives, its size, and what it links back to. Skills and scripts read it from the plugin at runtime. They never restate an item, a Why, a location or a size.
- The test: changing an item, a Why, a location or a size in `sdd.md` changes what the tools do, with no other edit. Only a new document or a new derived file needs new tooling.
- There are no template files. A generator builds its document's skeleton from the entry's Contains list.
- The challenge step draws on the Whys: each Why names the mistake its item prevents, which is what to push back on.
- The update script parses `sdd.md`. If the script needs `sdd.md` structured differently, propose the change to `sdd.md`; don't work around it.

## Not wanted
- An idea-to-app pipeline.
- Implementing tasks. The developer's own workflow does that.
- Hooks, state files or automation. Every tool runs when the developer runs it, on what they name.
- Activities or process steps as formal parts of the design.
- Approval gates, readiness checks, or status tracking of any kind.
- Checks on the developer's habits. Tools check documents only.

## Over-engineering: stop and flag
Before adding anything, check it against these signs. If one fits, say so and propose removing or simplifying instead:
- a rule, field or exception that fixes a problem another rule created (the main sign)
- something whose only job is to check that another step happened
- state that has to be tracked (current, due, synced, done)
- anything that happens on an event, or wording that makes a document event-aware
- a rule about how or when the developer works, rather than what a document says
- the same fact stated in two places, so one can drift

## Tools

### Generators
- One per document: Vision, System, ADR, Component spec, Slice and Task. There is no Open decisions generator; the developer maintains that section by hand.
- Vision, System, ADR and Component spec generators write to the location `sdd.md` gives. Slice and Task generators return the contents; the developer decides where they go.
- A generator writes only its own document. Knock-on changes to other documents are found by the update skill.
- Interview one question per message. Short answers are fine.
- Never guess. A question the generator can't settle is reported to the developer, who adds it to Open decisions.
- After drafting each section, offer a menu of 3–5 challenge methods suited to the document (e.g. Pre-mortem, 5 Whys, First Principles, Inversion, Occam's Razor, Subtraction), plus "proceed". Apply a method's changes only if the developer accepts them. Offer the menu on every document; it must be possible to turn it off.

### Derived-files generator
- Generates the derived files `sdd.md` defines: the CLAUDE.md block, path rules and the context diagram.
- Proposes changes; never overwrites. In CLAUDE.md it touches only its own marked block.

### Update skill
- Runs on `docs/`, plus any slices or tasks the developer names.
- A script in `bin/` reports what's deterministic: structure against `sdd.md`, links that don't resolve, pieces a document relies on that don't exist, and links to a superseded ADR.
- An agent reports what needs judgment: content outside a document's Contains, and contradictions between documents.
- Reports only. The developer approves every edit.

### README
For the developer, not the tools:
- what each tool does and when to run it, including regenerating the derived files
- what level of thinking belongs in each document (Shape Up's problem, appetite and no-gos; Patton's "just tell me the activities")
- the walking skeleton: the first slice is the thinnest thing that runs end to end
- that an agent can draft any document from an interview, and the developer edits it until it's theirs

## Open: for the plan to propose
- The link format every document uses (e.g. relative Markdown links to a heading).
- The start and end marker text for the CLAUDE.md block.
- How a component maps to its code paths for path rules, and that no rule file is written before the component has code.
- How skills find `sdd.md` inside the installed plugin.
- How the script parses `sdd.md`.
- How the challenge menu is turned off.
- The build order.
