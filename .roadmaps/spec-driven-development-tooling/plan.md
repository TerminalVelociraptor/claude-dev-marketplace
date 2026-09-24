# Build plan: spec-driven-development tooling

## Context
`plugins/spec-driven-development/` has `sdd.md` (the document definitions), `brief.md` (what to build) and `research.md`, but no tooling yet. This plan builds what the brief lists:
- six generators
- a derived-files generator
- an update skill backed by a `bin/` script
- a README

It follows the brief's hard rule: skills and the script read `sdd.md` at run time and never restate an item, a Why, a location or a size.

**Not building:**
- An Open decisions generator
- Hooks, state files or automation
- Status or approval tracking
- A staleness check on derived files (it would be sync state)
- Template files
- Implementation of tasks

---

## Decisions

### Agreed (this session)
| Decision | Units |
|---|---|
| A targeted research pass; its findings go into `research.md`. | U1 |
| A challenge menu after **each Contains item**; per document is the fallback if that proves annoying. | U4 |
| "Pieces a document relies on that don't exist" covers three cases: link text not found at its target, a component with no spec (made a broken link by S2), and a path rule with no spec (a broken link). | U2, U3 |
| The update skill accepts files and GitHub issues (`gh issue view`, piped to the script on stdin). | U3, U6 |
| Code in this plan: contracts, exact rules and test cases. Code is written out only where prose would be ambiguous, marked as an untested draft. | U3 |
| O1–O6, O5b and Q1 resolved as A; O7 build order confirmed; S1–S5 approved (2026-09-24). The table below keeps the options for reference. | all |
| The component-spec generator skill is named `component`. | U4, U7, U8 |
| The live run is done by you, on a project you're starting. | U4–U6, Verification |
| Judgment checks run in the main session, not in a subagent. Your subagent pre-flight rule would otherwise stop every update run, and the documents are small. | U6 |
| Other skill names: `vision`, `system`, `adr`, `slice`, `task`, `derive`, `update`. The script is `sdd-check`. | U3–U8 |
| All skills use `disable-model-invocation: true`: nothing runs unless you run it. | U4–U6 |
| Size is judged only by the generators. The update skill's list in the brief doesn't include size. | U4, U6 |
| Re-running a generator on an existing document revises only the items you name. | U4 |
| The update skill reads one GitHub issue per `sdd-check` run, because stdin can be read once. | U6 |
| The plugin version stays 0.1.0. `brief.md` and `research.md` stay in the plugin directory. | none |

### Resolved labels (A chosen for each; S1–S5 approved)
| Label | Point | Options | Units |
|---|---|---|---|
| **O1** | Link format | **A (rec):** a relative Markdown link to a file or a heading, whose text names the target in that section's own words (S1). Lets the script check both that the link resolves and that the named thing is there. **B:** file links, with names in prose. Makes the "named, not in target" check impossible. | U2, U3, U4 |
| **O2** | CLAUDE.md block markers | **A (rec):** `<!-- sdd:start -->` / `<!-- sdd:end -->`, stated in sdd.md (S4). **B:** the same markers stated in the derive skill, which makes it a second source of truth. | U2, U5 |
| **O3** | Component → code paths; no rule file before code | **A (rec):** the glob lives only in the rule file's `paths` frontmatter. The derive skill keeps an existing glob, or proposes one and checks it with Glob. sdd.md says a path rule exists only for a component that has code (S5). **B:** a "Code" item in the Component spec. Rejected: a spec states promises, not code locations. | U2, U5 |
| **O4** | How skills find sdd.md | **A (rec):** `${CLAUDE_PLUGIN_ROOT}/sdd.md` in SKILL.md content (the docs say it substitutes anywhere in skill content). The script finds sdd.md relative to its own file. **B:** `${CLAUDE_SKILL_DIR}/../../sdd.md`, as `plugins/learning` does; it isn't in the docs page I read. | U3–U6 |
| **O5** | How the script parses sdd.md | **A (rec):** by line, relying on conventions sdd.md already states. The rules are in U3. It needs S3. | U3 |
| **O5b** | Superseded ADRs, the one meaning the script can't read from sdd.md's structure | **A (rec):** one constant naming the `ADR` entry and its `Supersedes` item, checked against sdd.md on every run; if either is missing, the script exits 2. ⚠ This bends the hard rule: renaming the item means a one-line script edit, but the failure is loud. **B:** treat any ADR→ADR link as "supersedes". No names held, but it goes silently wrong if ADRs ever link to each other for another reason. | U3 |
| **O6** | How the challenge menu is turned off | **A (rec):** a plugin `userConfig` boolean `challenge_menu`, read in skills as `${user_config.challenge_menu}`. It persists and isn't a state file. **B:** per run, by saying "no challenges" when you invoke a generator. | U4, U8 |
| **O7** | Build order | U1 → U2 → U3 → U4 → U5 → U6 → U7 → U8. The script comes before the generators so every generated document can be checked. | all |
| **Q1** | Question style | **A (rec):** open questions, infer-and-confirm, and asking for specific past cases. No recommended answers, since a recommendation is a guess that does your thinking (BMAD `bmad-prd`, the Mom Test). **B:** Spec Kit style, with a recommended option on each question. | U1, U4 |
| **S1–S5** | sdd.md edits, below | Approve each separately. | U2 |

### sdd.md edits (all approved)
**S1**: new rule inserted after `sdd.md:13` (the end of "Keep it short"). Needed by O1 and the structure check.
```markdown
**Headings and links.** A document opens with a heading: its title, or, for a section of a file, the section heading. Each Contains item is a heading one level below it, named as in this file; an item marked optional or "only if" is left out when it doesn't apply. A link is a relative Markdown link to a file or a heading, and its text names what it points at in that section's own words, e.g. `[reliability over speed](../01-overview.md#priorities)`.
*Why:* a heading per item gives every item a link target, and a link that names its target can be checked when the target changes.
```
**S2**: System → Components (`sdd.md:57-58`).
- Line 57, before: `…and, if the user touches it, through what (a page, a command, a report).`
- Line 57, after: `…and, if the user touches it, through what (a page, a command, a report); and a link to its component spec.`
- Line 58: append ` The link takes you and agents from the map to what the component promises.`

**S3**: ADR location (`sdd.md:90`): `` `docs/decisions/NNNN-<title>.md` `` → `` `docs/decisions/<NNNN>-<title>.md` ``.

**S4**: CLAUDE.md block location (`sdd.md:180`).
- Before: `A marked block in the project's CLAUDE.md; everything outside the block is yours. About 20–30 lines.`
- After: ``A block in the project's CLAUDE.md, between the lines `<!-- sdd:start -->` and `<!-- sdd:end -->`; everything outside the block is yours. About 20–30 lines.``

**S5**: Path rules location (`sdd.md:200`).
- Before: `` `.claude/rules/<component>.md`, one per component spec.``
- After: `` `.claude/rules/<component>.md`, one per component spec whose component has code.``
- Add a new line under it: `*Why only with code:* a rule whose paths match nothing never loads.`

---

## Conventions
- **Python and tests** (from the repo `CLAUDE.md`):
  - Python 3.13.5 (verified), standard library only.
  - Scripts live in `bin/`, have no extension, are executable and start with `#!/usr/bin/env python3`.
  - Tests use unittest, named `tests/test_<script_with_underscores>.py`, and run scripts through `subprocess` with `sys.executable`.
  - To reuse a parser, a test may load the script as `plugins/learning/tests/test_skill_lint.py:31-37` does.
- **Skills:**
  - Each skill is `skills/<name>/SKILL.md` with frontmatter `name`, `description`, `argument-hint`, `disable-model-invocation`, `allowed-tools`. See `plugins/learning/skills/flag/SKILL.md:1-6` for the style.
  - Shared prose lives in `shared/*.md`, as in `plugins/learning/shared/`.
- **Commands:**
  - `python3 -m unittest discover -s plugins/spec-driven-development/tests`
  - `claude plugin validate plugins/spec-driven-development` (passes today; verified)

## Cross-cutting gotchas
- **Substitution** (verified in the Claude Code docs): `${CLAUDE_PLUGIN_ROOT}` and `${user_config.*}` substitute only in SKILL.md content, not in files the agent Reads later and not in Bash-tool commands. Each SKILL.md therefore states `Plugin root: ${CLAUDE_PLUGIN_ROOT}` and passes it to `shared/` files in prose.
- **Plugin `bin/` is on the Bash `PATH`** (verified in the docs). Skills still call scripts by full path, so `allowed-tools` can match them.

## Stop-and-ask triggers
- A wording or spec ambiguity, or anything that would restate an sdd.md item, Why, location or size in a skill.
- A failing test that tempts you to change its assertion.
- A file needed outside the unit's **Files** list.
- sdd.md not parsing as U3's rules describe.
- Default: stop and ask; never work around. Stop for review after each unit.

## Dependencies
- U2 before U3 (U3's smoke test parses the real sdd.md).
- U2 before U4 and U5.
- U3 before U6.
- U4–U6 before U7 and U8.
- U1 is independent.

---

## U1: Record the follow-up research
**Deliverables:** additions to `research.md`.
**Files:** modify `plugins/spec-driven-development/research.md`; must not touch anything else.
**Content:**
1. In the "Interaction patterns" table, set "Checked" to ✔ on both Agent OS rows.
2. Insert before `## What people report as too heavy`:
```markdown
## Follow-up: interviews and challenge menus
Three questions for the generators, checked in primary sources on 2026-09-23.

**How to ask so a short answer is enough**
- **Spec Kit `/clarify`:** at most 5 questions a session, "EXACTLY ONE question at a time", each with a "Why it matters" line and a recommended option or a suggested answer of 5 words or fewer; it stops when you say "done". ✔
- **BMAD `bmad-prd` (current):** "Open-ended 'tell me about X' beats multiple choice." "Infer-and-confirm ('I'm assuming X works like Y — right?') is fine; quizzing the user through a tree of LLM-shaped choices is not." "Fight the urge to do the thinking for them." ✔
- **The Mom Test (Fitzpatrick):** "Ask about specifics in the past instead of generics or opinions about the future." *(four book summaries agree; the book wasn't checked)*
- **Adopted:** open questions, infer-and-confirm, past specifics. No recommended answers: a recommendation is a guess, and it does the developer's thinking.

**Whether challenge menus get skipped**
- **BMAD issue #2373:** a user types "C" (continue) past nearly every step's menu; the maintainer replied that the PRD skill "gets rid of this constant continuation gating". ✔
- **BMAD `bmad-prd` (current):** no menu after each section; elicitation is offered once, as available "at any point", and final reviews are "Stakes-calibrated — hobby/solo may run quietly or skip." ✔
- **Adopted anyway:** a menu after each item, with an off switch. One menu per document is the fallback if it proves annoying.

**When to stop, and what to do with unknowns**
- **Agent OS `plan-product.md`:** "Keep it lightweight", "One question at a time", "If the user provides very brief answers, that's fine"; a skipped section gets "To be defined". ✔
- **Adopted:** the interview is bounded by the Contains items. A question the developer can't settle goes into the end-of-run report for Open decisions, not into the document.
```
3. Under "What was checked" → "✔ Read in the primary source", add:
   - Spec Kit `templates/commands/clarify.md`
   - BMAD `skills/bmad-prd/SKILL.md`, `skills/bmad-advanced-elicitation/SKILL.md` and issue #2373
   - Agent OS `commands/agent-os/plan-product.md`

   Remove "Agent OS `plan-product.md` quotes" from "Agent report only".

**Gotchas:** if Q1 = B or O6 = B, change the matching "Adopted" line before writing.
**Done when:**
- `grep -c "Follow-up: interviews" research.md` prints `1`.
- `grep -n "plan-product" research.md` prints no line containing `agent report`.

## U2: Apply the approved sdd.md edits
**Deliverables:** the approved labels among S1–S5, applied verbatim.
**Files:** modify `plugins/spec-driven-development/sdd.md`; must not touch anything else.
**Done when:** `git diff --stat` lists only `sdd.md`, and every hunk in `git diff` is one of the approved before → after pairs. An extra hunk fails the check.

## U3: `bin/sdd-check` and its tests
**Deliverables:** the executable `bin/sdd-check` and `tests/test_sdd_check.py`.
**Files:** create both; must not touch `sdd.md`.

**Contract:**
- Usage: `sdd-check [--root DIR] [--sdd FILE] [--doc ENTRY PATH]...`
  - `--root` defaults to the current directory.
  - `--sdd` defaults to `Path(__file__).resolve().parent.parent / "sdd.md"`.
  - `--doc` checks PATH as a document of ENTRY, for documents with no fixed location. ENTRY matches an entry name case-insensitively. PATH `-` reads stdin, at most once per run.
- Output:
  - one line per finding, `path:line: kind: message`, deduplicated and sorted;
  - then a last line, `N finding(s)` or `no findings`;
  - kinds: `structure`, `broken-link`, `not-in-target`, `superseded-link`.
- Exit codes: 0 no findings; 1 findings; 2 usage error or an unexpected sdd.md shape, with the message on stderr prefixed `sdd-check: `. Exit 2 cases:
  - an unknown ENTRY (the message lists the entry names);
  - a second stdin `--doc` (`only one --doc may read stdin`);
  - a missing `--doc` file;
  - sdd.md with no entries, an entry with no location line, or a Contains list with no items;
  - O5b's constant not found (message contains `update SUPERSEDES in bin/sdd-check`).
- Invariant: the only sdd.md names in the code are O5b's `("ADR", "Supersedes")`.

**Content: rules the executor must not reinvent**

*Parsing sdd.md (O5)*
1. Split sdd.md at level-2 and level-3 headings. A block is an **entry** if it contains a line that is exactly `**Contains:**` or exactly `**Holds:**`. An entry with `**Holds:**` is **derived**.
2. The **entry name** is the heading text with a trailing ` (…)` removed, so `ADR (decision record)` becomes `ADR`.
3. The **location line** is the block's second non-empty line (sdd.md's intro: "opens with what the document is for, then where it lives"). Of its backtick spans:
   - the first that ends in `.md` is the **path pattern**;
   - the first that starts with `#` is the **section**, e.g. `## Vision`.

   Neither may exist; for example, Slice's location is "wherever you put it".
4. **Items** are the lines between `**Contains:**` and the next line starting `**Links back to:**` that match the regex below. Group 1 is the name. The item is optional if group 2 matched.
5. Placeholders: every `<…>` in a path pattern becomes `*` for globbing.

*Which files are checked*
- For each entry with a path pattern, glob it under `--root`:
  - A non-derived entry's files get a **structure** check and a **link** check.
  - A derived entry's files get a link check only.
- A non-derived fixed path (no `*`) that doesn't exist gives one finding per path, not one per entry: `<path>:1: structure: missing file (<entry names, comma-separated> live here)`.
- A missing derived file isn't reported.
- Each `--doc` adds a structure and link check against its entry. Stdin shows in findings as `<stdin>`, with links resolved against `--root`.
- Each file is link-checked once, even if several entries share it (for example `docs/01-overview.md`).

*Structure check (per document, per entry)*
- **Document heading:**
  - if the entry has a section, the first heading whose level is that section's `#` count and whose text equals its title (case-insensitive);
  - otherwise the first level-1 heading.
- If there is none, report `no \`<section>\` section (<entry>)` or ``no `#` title heading (<entry>)`` at line 1.
- **Item headings** are the headings exactly one level below the document heading, before the next heading at the document heading's level or higher. Deeper headings are free.
- Report:
  - ``missing item `<name>` (<entry>)`` for each required item absent, at the document heading's line;
  - `` `<text>` is not an item of <entry> in sdd.md `` for an unknown item heading;
  - `` `<text>` appears twice (first at line N) `` for a duplicate item heading.
- Name comparison is case-insensitive and exact.

*Link check*
- Links are inline `[text](target)` only, not images, and not inside ``` / ~~~ fences or inline code spans. Skip a target with a URL scheme (`http:`, `mailto:`, …).
- Split the target at `#` into file and anchor. The file resolves against the linking file's directory. An empty file part means the same document.
- Report:
  - `` `<target>`: no such file `` if the file doesn't exist;
  - `` `<target>`: no heading for `#<anchor>` `` if an anchor is given, the target is a Markdown file, and the anchor isn't one of its heading slugs;
  - `` `<text>` doesn't appear under `#<anchor>` `` (kind `not-in-target`) if the anchor exists, but the normalised link text isn't a substring of the normalised target section. The section runs from the anchored heading's line up to the next heading at the same level or higher.
- **Normalise:** replace `[x](y)` with `x`, remove the characters `` ` `` `*` `_`, casefold, and collapse whitespace.
- **Heading slug** (GitHub style): replace `[x](y)` with `x`, lowercase, remove every character that isn't a word character, `-` or a space, and turn spaces into `-`. A repeated slug gets `-1`, `-2`, … in order.

*Superseded ADRs (O5b A)*
- In each ADR file (files globbed from the `ADR` entry), take the item heading named `Supersedes`. Every non-scheme link between it and the next item heading, or the end of the document, marks its target file as **superseded by** that ADR. Those link lines are exempt.
- Any other link, in any checked document, to a superseded file is reported as `` `<target>` is superseded by <path of the superseding ADR> ``.

**Untested draft: the regexes** (prose alone would be ambiguous here):
```python
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
ITEM_RE = re.compile(r"^- \*\*(.+?):?\*\*:?\s*(\((?:optional|only if[^)]*)\))?")
TICK_RE = re.compile(r"`([^`]+)`")
FENCE_RE = re.compile(r"^\s*(```|~~~)")
CODE_SPAN_RE = re.compile(r"`[^`]*`")
LINK_RE = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
```
`ITEM_RE` must give `Problem and users` for `- **Problem and users:** …`, and `Evidence` (optional) for `- **Evidence** (only if a spike was run): …`.

**Tests:** each test builds a temporary root and passes `--sdd` pointing at this **synthetic** fixture, so tests don't depend on the real sdd.md. Case 20 is the exception.
```markdown
# Docs

## What this is not
- **Not a thing.** x

## Overview
Purpose.
`docs/overview.md`, `## Overview` section. Short.

**Contains:**
- **Goals:** g
  *Why:* w
- **Notes** (optional): n
  *Why:* w

**Links back to:** nothing.

## ADR (record)
Purpose.
`docs/decisions/<NNNN>-<title>.md`, one per decision. Short.

**Contains:**
- **Decision:** d
  *Why:* w
- **Supersedes** (only if it replaces one): s
  *Why:* w

**Links back to:** x.

## Slice
Purpose.
Wherever you put it. Short.

**Contains:**
- **Outcome:** o
  *Why:* w

**Links back to:** x.

## Derived files

### Rules
Purpose.
`.claude/rules/<component>.md`, one per spec.

**Derived from:** x.

**Holds:**
- A link.
  *Why:* w
```
| # | Setup (under the temp root) | Expected |
|---|---|---|
| 1 | Nothing | exit 1; `docs/overview.md:1: structure: missing file (Overview live here)` |
| 2 | `docs/overview.md` = `## Overview\n### Goals\nx` | exit 0; last line `no findings` (Notes is optional) |
| 3 | Overview with `### Notes` only | ``missing item `Goals` (Overview)`` |
| 4 | Goals plus `### Risks` | `` `Risks` is not an item of Overview in sdd.md `` |
| 5 | Goals twice | `appears twice (first at line 2)` |
| 6 | **Hard rule:** case 2's document, with the fixture's `**Goals:**` changed to `**Outcomes:**` | `` `Goals` is not an item `` and ``missing item `Outcomes` `` |
| 7 | **Hard rule:** case 2's document, with the fixture location changed to `` `docs/intro.md` `` | `docs/intro.md:1: structure: missing file`; nothing for `docs/overview.md` |
| 8 | Overview line `[x](nope.md)` | `broken-link` … `no such file` |
| 9 | `[Goals](overview.md#nope)` | `broken-link` … ``no heading for `#nope` `` |
| 10 | `[speed](overview.md#goals)` placed under `### Notes`, with the Goals body `x` | `not-in-target` |
| 11 | As case 10, with the Goals body `Speed over polish` | no finding |
| 12 | `docs/decisions/0001-a.md` = `# A\n## Decision\nx`; `0002-b.md` = `# B\n## Decision\nx\n## Supersedes\n[A](0001-a.md)`; the overview links `decisions/0001-a.md` | one `superseded-link` on the overview line naming `docs/decisions/0002-b.md`; none on 0002's line |
| 13 | A broken link inside a ``` fence, and one inside a code span | no finding |
| 14 | `[site](https://example.com)` | no finding |
| 15 | `--doc Slice -`, stdin `# S\n## Outcome\nx`, plus a valid overview | exit 0 |
| 16 | `--doc Slice -`, stdin `# S\n` | ``<stdin>:1: structure: missing item `Outcome` (Slice)`` |
| 17 | `--doc Nope f.md` | exit 2; stderr lists `Overview, ADR, Slice` |
| 18 | Fixture without the Supersedes item | exit 2; stderr contains `update SUPERSEDES` |
| 19 | The fixture replaced by `# x\n` | exit 2 |
| 20 | **Real sdd.md** (no `--sdd`), empty root | exit 1; stderr empty; every finding line contains `missing file` |
| 21 | `.claude/rules/x.md` links `../../docs/components/x.md`, which is missing | `broken-link` on `.claude/rules/x.md` |
| 22 | `--doc Slice - --doc Slice -` | exit 2; `only one --doc may read stdin` |

**Gotchas:**
- The slug rule approximates GitHub's; it is unverified for emoji or unusual punctuation.
- Reference-style links aren't checked.
- Relative links in a GitHub issue don't click through on GitHub. The script still resolves them against `--root`; that limitation is accepted.
- The `.claude/rules/*.md` glob also matches your own rule files; those get link checks only.

**Done when:**
- `python3 -m unittest discover -s plugins/spec-driven-development/tests` ends with `OK` and `Ran 22 tests`.
-  Temporarily removing the casefold step from normalisation makes case 11 fail (it relies on "speed" matching "Speed over polish"); restore it after.

## U4: Generators (six thin skills, a shared protocol and methods), plus the menu setting
**Deliverables:**
- `shared/generate.md` and `shared/challenge-methods.md`
- six `skills/<name>/SKILL.md` files
- `userConfig` in `.claude-plugin/plugin.json` (if O6 = A)

**Files:** create the above; modify `plugin.json`; must not touch `sdd.md` or `bin/`.
**Contract:** a thin skill holds only the Document name, the plugin root, the menu setting and the developer's input. Everything about the document comes from sdd.md; the procedure comes from `generate.md`.

**Content: thin skill template** (identical apart from the table below):
```markdown
---
name: <name>
description: <description>
argument-hint: <hint>
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Bash(gh issue view *)
---

Document: `<Document>`
Plugin root: `${CLAUDE_PLUGIN_ROOT}`
Challenge menu: `${user_config.challenge_menu}`
From the developer: $ARGUMENTS

Read `${CLAUDE_PLUGIN_ROOT}/shared/generate.md` and follow it for this document.
```
| name | Document | description | argument-hint |
|---|---|---|---|
| vision | Vision | Drafts or revises the project's Vision by interview, challenging each item, and writes it where sdd.md says. | [your idea, in a line or two] |
| system | System | Drafts or revises the System section by interview, challenging each item, and writes it where sdd.md says. | [anything to start from] |
| adr | ADR | Drafts a decision record by interview, challenging each item, and writes it where sdd.md says. | [the question it settles] |
| component | Component spec | Drafts or revises one component's spec by interview, challenging each item, and writes it where sdd.md says. | <component name> |
| slice | Slice | Drafts a slice by interview, challenging each item, and returns it for you to put where you want. | [what the user should be able to do] |
| task | Task | Drafts a task by interview, challenging each item, and returns it for you to put where you want. | [the slice file or issue, or the change] |

**Content: `shared/generate.md`** (the Ask bullets follow Q1 = A)
```markdown
# Generating a document

The skill that sent you here names a **Document** (an entry in `sdd.md`), the **Plugin root**, the **Challenge menu** setting, and anything the developer said when running it. You interview the developer, draft the document one item at a time, challenge each item, and deliver it. The developer keeps the thinking: you ask, draft and push back.

## 1. Read the definition
Read `sdd.md` in the plugin root, in full. Everything about the document comes from there, not from this file:
- its entry (the heading matching the Document): what it is for, where it lives, its size, its **Contains** items with their *Why*s, and **Links back to**;
- the rules above the entries, which apply to every document.

## 2. Find where it goes and what it draws on
- **Location.** The entry's location says where the document lives.
  - A path: you write there. Fill any `<...>` placeholder from the interview (for a number, the next unused one in that directory) and show the path before writing.
  - A section of a file: change only that section and leave the rest of the file as it is.
  - No path: return the document in your reply; the developer puts it where they want.
- **Already there.** If the document exists, show it and ask which items to revise, or whether to stop. Interview only on the items the developer names.
- **Sources.** Of the documents in **Links back to**, read a single document in full. Where it names a set (one of several files), list the set and open only the members the interview makes relevant. Link to them; never restate them. For one with no fixed location, ask where it is (a file, or an issue number to read with gh issue view <n>). If one doesn't exist yet, say so once and carry on.

## 3. Interview, draft and challenge, one item at a time
Take the Contains items in the order `sdd.md` lists them. For each item:
1. **Ask**, one question per message. The item's description says what you need; its *Why* says what a good answer has to do.
   - Ask open questions. Offer options only if the developer asks for them, and don't recommend one.
   - Ask for a specific past case rather than a general statement or a prediction: "When did this last get in your way?", not "Would you use this?"
   - Don't ask what a source or an earlier answer already settles; confirm it instead: "Vision says no cloud accounts, so this runs on your machine — right?"
   - Short answers are fine.
   - For an item marked optional or "only if", first ask whether it applies. If not, leave it out.
2. **Don't guess.** If the developer can't settle something, don't fill it in. Keep the question, and where it came from, for the report at the end, and draft the item with what is settled.
3. **Draft** the item following `sdd.md`'s rules, sized so the whole document fits the entry's size, and show it.
4. **Challenge**, unless the Challenge menu setting is `false`. Offer a numbered menu:
   - 3–5 methods from `shared/challenge-methods.md` in the plugin root, chosen for the mistake this item's *Why* names;
   - **reshuffle**: other methods;
   - **proceed**: go on to the next item.

   When the developer picks a method, apply it to the draft and show what it found and the change it proposes. Make the change only if the developer accepts it, then offer the menu again. Treat any other reply as direction: apply it, then offer the menu again.
5. Go on to the next item when the developer says proceed.

## 4. Deliver
- Show the whole document. If it is well over the entry's size, name the item that looks like it's doing another document's job, and ask. Don't cut anything on your own.
- Write it to its location only after the developer confirms, or return it if the entry names no path. Write nothing else: knock-on changes to other documents are the update skill's job.
- End with:
  - **Open questions:** each question you couldn't settle, with where it came from, for the developer to add to Open decisions.
  - **Next:** the update skill, if this may affect other documents; the derive skill, if a derived file draws on this document.
```

**Content: `shared/challenge-methods.md`**
```markdown
# Challenge methods

Each method pushes back on one drafted item. Offer the ones that attack the mistake the item's *Why* names. Apply a method in a few lines: what it found, and the change it proposes.

| Method | Apply it to a drafted item by |
|---|---|
| Pre-mortem | Assuming the project failed because of this item. Name the likeliest reason, and the change that prevents it. |
| 5 Whys | Asking why the item says what it says, then why that, up to five times, until you reach the need behind it. Propose restating the item at that level if it differs. |
| First Principles | Stripping the item to what must be true. Propose dropping anything that rests on habit or on what other projects do. |
| Socratic Questioning | Asking the developer 2–3 questions that test the item's assumptions. Propose changes only from their answers. |
| Inversion | Asking what would make this item fail its *Why*. Propose a change that rules that out. |
| Occam's Razor | Finding the simplest version that still meets the *Why*. Propose it if it is simpler than the draft. |
| Subtraction | Removing each part in turn, in thought. Propose keeping only the parts whose removal would break the *Why*. |
| Abstraction Laddering | Moving the item one level up (why it matters) and one level down (a concrete example). Propose the level that fits this document. |
```

**Content: `plugin.json` addition** (O6 = A):
```json
"userConfig": {
  "challenge_menu": {
    "type": "boolean",
    "title": "Challenge menu",
    "description": "After each drafted item, offer a menu of challenge methods. Set to false to turn it off."
  }
}
```
**Gotchas** (all unverified):
- What `${user_config.challenge_menu}` becomes when unset. `generate.md` treats anything but `false` as on, so both outcomes are safe.
- Whether `userConfig` supports a default.
- `$ARGUMENTS` in skills.

**Done when:**
- `claude plugin validate plugins/spec-driven-development` prints `Validation passed`.
- In the live run (see Verification), `/spec-driven-development:vision`:
  - asks one question per message;
  - shows a menu after each item;
  - lists an answer of "I don't know" under **Open questions** at the end, with nothing invented in the document.

## U5: Derive skill
**Files:** create `skills/derive/SKILL.md`; must not touch anything else.
**Content:**
```markdown
---
name: derive
description: Proposes the derived files sdd.md defines, from the current documents, and writes only what you approve.
argument-hint: [one derived file to regenerate; default all]
disable-model-invocation: true
allowed-tools: Read, Glob, Grep
---

Plugin root: `${CLAUDE_PLUGIN_ROOT}`
Asked for: $ARGUMENTS

# Derive files

1. Read `${CLAUDE_PLUGIN_ROOT}/sdd.md` in full. Its derived-files entries define each derived file: where it lives, what it is **Derived from**, and what it **Holds**, each with a *Why*. Work on the one the developer asked for, or all of them.
2. For each derived file:
   - Read everything its **Derived from** names. Build exactly what **Holds** lists and nothing else: copy only where Holds says to copy, and link otherwise.
   - If its location limits when it exists, or a source it needs doesn't exist yet, skip it and say why.
   - If its location is a block between markers in a file the developer owns, change only the lines between the markers. If the markers aren't there, propose adding the block, markers included, at the end of the file. Never edit outside them.
   - If **Derived from** names something taken from the repo rather than a document (such as code paths), take it from the existing derived file if there is one. Otherwise propose it from the repo layout, check with Glob that it matches files, and confirm it with the developer.
   - A file under `.claude/rules/` starts with YAML frontmatter holding a `paths` list of globs, so it loads only for those files.
   - A Mermaid diagram goes in a fenced `mermaid` block.
3. Show the difference from what is there now, or the whole content for a new file.
4. Write only the changes the developer approves. Propose; never overwrite unasked.
5. End with one line per derived file: written, proposed and declined, skipped (with the reason), or unchanged.
```
**Done when:** in the live run, with a Vision and a System but no component specs and no code:
- it proposes a CLAUDE.md block between `<!-- sdd:start -->` and `<!-- sdd:end -->`, and a context diagram;
- it writes no rule file, and gives "no code yet" as the reason for each component;
- declining a proposal leaves `git status` clean.

## U6: Update skill
**Files:** create `skills/update/SKILL.md`; must not touch anything else.
**Content:**
```markdown
---
name: update
description: Checks the project's documents against sdd.md and against each other, and reports what's inconsistent. Runs on docs/ plus any slices or tasks you name (files or GitHub issue numbers). Reports only; you approve every edit.
argument-hint: [slice or task files, or issue numbers]
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Bash(${CLAUDE_PLUGIN_ROOT}/bin/sdd-check *), Bash(gh issue view *)
---

Plugin root: `${CLAUDE_PLUGIN_ROOT}`
Named by the developer: $ARGUMENTS

# Update

## 1. Deterministic checks
From the project root, run:

    ${CLAUDE_PLUGIN_ROOT}/bin/sdd-check --doc <entry> <file> ...

Add one `--doc` per slice or task file the developer named. `<entry>` is the `sdd.md` entry the file is; ask if you can't tell. For a GitHub issue, pipe it in, one issue per run:

    gh issue view <n> --json title,body --jq '"# " + .title + "\n\n" + .body' | ${CLAUDE_PLUGIN_ROOT}/bin/sdd-check --doc <entry> -

Exit 2 means the script itself failed: show its message and stop.

## 2. Judgment checks
Read `${CLAUDE_PLUGIN_ROOT}/sdd.md` and every document checked in step 1. Report, with `path:line`:
- **Outside Contains:** content that isn't one of its entry's Contains items. Say which document it belongs in, if any.
- **Contradictions:** two documents that say incompatible things. Quote both sides.

Don't repeat what the script reported. Don't comment on style, or on how or when the developer works.

## 3. Report
Group findings by document, each as `path:line — finding — (script)` or `(judgment)`. Then list proposed edits as E1, E2, …: each with its file, the change as before/after, and the finding it fixes. For a finding only the developer can settle, propose nothing and say so.

## 4. Edits
Make no edit until the developer approves it by label. Apply only the approved edits, then run `sdd-check` again and show its last line.
```
**Gotchas:** it is unverified whether a pipe into `sdd-check` matches `allowed-tools` without a prompt. A prompt is acceptable.
**Done when:** in the live run, on a project with one planted contradiction and one broken link:
- the report lists both, labelled `(judgment)` and `(script)`;
- `git status` stays clean until you approve an edit label.

## U7: Skill lint test
**Files:** create `tests/test_skill_lint.py`; must not touch anything else.
**Contract:**
- Loads `parse_sdd` from `bin/sdd-check` as `plugins/learning/tests/test_skill_lint.py:31-37` does.
- Reads Whys with a test-local regex over sdd.md: `^\s*\*Why[^*]*:\*\s*(.+)$`.

| Check | Fails when |
|---|---|
| Every `${CLAUDE_PLUGIN_ROOT}/<path>` and `shared/<file>` named in `skills/*/SKILL.md` exists | a referenced file is missing (the message names the skill and the path) |
| Every `bin/<tool>` in a skill body is in its `allowed-tools` as `Bash(${CLAUDE_PLUGIN_ROOT}/bin/<tool> *)` | a used tool isn't pre-approved |
| Every skill has `disable-model-invocation: true` | the line is missing or false |
| A skill that references `shared/generate.md` has a `` Document: `X` `` line, and X is a non-derived sdd.md entry | X isn't in sdd.md |
| No entry path pattern from sdd.md, as written (e.g. `docs/components/<name>.md`), appears in `skills/`, `shared/` or `README.md` | a location is restated |
| The first 40 characters of no Why appear in `skills/`, `shared/` or `README.md` | a Why is restated |

**Done when:**
- The tests pass.
- Pasting `docs/components/<name>.md` into `shared/generate.md` fails the location check with a message naming that file (then remove the paste).

## U8: README
**Files:** create `README.md`; must not touch anything else.
**Content:**
```markdown
# spec-driven-development

Interview skills and consistency checks for the project documents defined in [`sdd.md`](sdd.md), from an idea to tasks. You stay in the loop and keep the mental model: the tools interview, challenge, draft and report. Building a task stays in your own workflow.

`sdd.md` is the only definition of the documents. The skills and the script read it when they run, so editing it changes what they do.

## Tools
Every tool runs only when you run it, on what you name.

| Command | What it does | Run it when |
|---|---|---|
| `/spec-driven-development:vision` | Interviews you and writes the Vision. | You start a project, or change what this version is. |
| `/spec-driven-development:system` | Interviews you and writes the System section. | The Vision is settled enough to name the parts. |
| `/spec-driven-development:adr` | Interviews you and writes a decision record. | You settle a question someone would ask "why?" about. |
| `/spec-driven-development:component <name>` | Interviews you and writes one component's spec. | A slice is about to touch that component. |
| `/spec-driven-development:slice` | Interviews you and returns a slice. | You pick the next piece to build. |
| `/spec-driven-development:task` | Interviews you and returns a task. | You split a slice, or need a change that needs no slice. |
| `/spec-driven-development:derive` | Proposes the derived files: the CLAUDE.md block, path rules and the context diagram. Writes what you approve. | You've changed a document they're derived from. |
| `/spec-driven-development:update` | Reports structure problems, broken links, missing pieces, links to superseded ADRs, and contradictions. Edits only what you approve. | You've changed a document, or before starting a slice. |

There's no Open decisions generator: you keep that section by hand. The generators hand you the questions they couldn't settle.

**How the generators work.** One question per message; short answers are fine. They never guess: a question you can't answer yet comes back to you for Open decisions. After each drafted item they offer a menu of challenge methods (Pre-mortem, Inversion, Subtraction and others), plus "proceed". A method's changes apply only if you accept them. To turn the menu off, set the plugin's `challenge_menu` option to false.

## What level of thinking goes where
`sdd.md` says what each document holds; this is the altitude to write it at.
- **Vision** is shaping, not specifying. Shape Up's pitch is the model: one specific story of the problem, an appetite (how much time it's worth), and no-gos. For the MVP, Patton's advice applies: "just tell me the activities". Narrate what the system does at a high level, then take the thinnest path through it. Technology you're tempted to name belongs in Open decisions.
- **System** is the parts and the seams between them, in plain language. No formats, hosts or products yet.
- **Component specs** are promises precise enough to build and test against, not an implementation plan.
- **Slices** say what the user can do afterwards and what they see; **tasks** say what changes and how you'll check it.
- **ADRs** are for decisions someone would ask "why?" about, and nothing else.

## The first slice is a walking skeleton
Make the first slice the thinnest thing that runs end to end through the components the MVP touches, even if each part does almost nothing. It proves the split and the contracts while they're cheap to change; later slices thicken it.

## Drafted by an agent, owned by you
Any document can start as a draft from an interview. It's done when you've edited it until it says what you mean, not when the interview ends.

## Design notes
[`brief.md`](brief.md) says what the tooling is for and the decisions behind it; [`research.md`](research.md) has the evidence.
```
**Gotchas:** how you change a `userConfig` value after install is unverified. Check it, and name the exact step in the "How the generators work" paragraph.
**Done when:**
- U7 passes with the README present.
- Each README bullet in `brief.md:52-57` maps to a section above; a bullet with no section fails the check.

---

## Verification (end to end, after U8)
1. `python3 -m unittest discover -s plugins/spec-driven-development/tests` ends with `OK`.
2. `claude plugin validate plugins/spec-driven-development` prints `Validation passed`.
3. **Live run**, done by you in the project you're starting, with the plugin loaded (`claude --plugin-dir plugins/spec-driven-development`; the flag is unverified, so fall back to the local marketplace install):
   1. Run vision → system → adr (on one question) → component (for one component) → slice → task.
   2. Then run `sdd-check` from the repo root. It should report nothing except broken links for components that have no spec yet.
4. **Hard-rule check on the skills.** Temporarily rename Vision's `Constraints` item to `Fixed limits` in sdd.md, then:
   1. Run the vision generator: it must ask about and write `### Fixed limits`.
   2. Run `sdd-check`: it must flag `### Constraints` as not an item.
   3. Revert the rename with Edit, not `git restore`.
5. **Menu off.** With `challenge_menu` set to false, a vision run shows no menu.

## Over-engineering check (flagged)
- **O5b A** is an exception to the hard rule: one constant, with a loud failure. B avoids it but can fail silently.
- **S1's "link text names its target"** exists partly so the "named, not in target" check you chose can work. It also helps readers.
- **O6 A (userConfig)** is a setting, not tracked state. B avoids it at the cost of repeating yourself every run.
- Nothing else adds a field, a state or an event.
