---
name: vision
description: Stage 1 of a spec-driven process. Interviews you about a new project - problem and users, goals and success criteria, priorities, non-goals, appetite, MVP, risks, learning goals - and writes a throwaway draft you rewrite yourself into docs/01-overview.md. `/vision review` then checks what you wrote. Use when starting a project, or when goals have shifted.
argument-hint: [review | a sentence about your idea]
disable-model-invocation: true
allowed-tools: Bash(${CLAUDE_SKILL_DIR}/../../bin/check-vision *), Read, Write, AskUserQuestion
---

# Vision

Stage 1: agree what is being built, for whom, and why, before any structure exists.

**The user writes the vision. You interview and draft; that is all.** A vision written by an AI is
one its author never internalises, and the point of Stage 1 is that they can state it from memory
later. So your draft goes in a throwaway file and they write the real document themselves.

## Never

- **Never write prose into the overview.** Creating it from the template, title only, is the one
  write you make there.
- **Never name a technology, library, database, framework or host,** and never ask which one they
  want.
- **Never guess an answer.** An unknown is written down as an unknown.
- **Never restate the headings from memory.** They live in the template.

## Paths

Read `${CLAUDE_SKILL_DIR}/../../config.json` once. It gives `project_paths.overview`,
`project_paths.vision_draft` (both relative to the project root) and `plugin_paths.overview_template`
(relative to `${CLAUDE_SKILL_DIR}/../../`). Keys starting with `_` are comments; ignore them.

## With the `review` argument, go to Review

Otherwise run `${CLAUDE_SKILL_DIR}/../../bin/check-vision --status` from the project root:

| Status | What to do |
|---|---|
| `missing` | Setup, then Interview |
| `empty` | Interview |
| `filled` | Say the vision is already written, and offer either `/vision review` or a fresh interview if the goals have changed. Wait for an answer. |

## Setup

Read the template. Write it to `project_paths.overview` with one change: replace
`# <project name>` with the project's name. Leave the prompt comments in place - they are the
user's guide while they write.

Mention that `docs/drafts/` is worth adding to `.gitignore`, since the draft is disposable. Do not
edit `.gitignore` yourself.

## Interview

Work through the template's headings in order, one topic at a time, in plain conversation. The
prompt comment under each heading is the question; ask it in your own words and follow up until the
answer is concrete enough to act on.

- One topic at a time. Never present a form or ask for everything at once.
- Use AskUserQuestion only for genuinely bounded choices.
- When an answer is a guess, say so and offer to record it under risks and unknowns instead.
- Push back once, not repeatedly, when something in the Review checks below is obviously true of an
  answer: an MVP bigger than the appetite, an MVP that is not end to end, a success criterion
  nobody could check, a guess stated as fact, priorities with no tiebreak.
- If they do not want to answer a heading, write what they said and move on. It is their document.
- For a small project, one line per heading is a complete answer. Do not pad it.

**Technology.** If the user names one, do not argue and do not adopt it. Put it under a
`## Parked for later stages` heading at the end of the draft, which Stage 3 picks up. If what they
named is really an uncertainty ("something that can handle a lot of writes"), restate it in their
own terms and offer it for the risks heading.

## The draft

Write `project_paths.vision_draft` using the template's headings, in order, filled with what they
told you, in their vocabulary rather than yours. Add `## Parked for later stages` if anything was
parked.

Then run `${CLAUDE_SKILL_DIR}/../../bin/check-vision --draft` and fix whatever it reports.

## Closing

End with exactly these three instructions:

1. Write the Vision section of `<overview path>` yourself, in your own words. Do not paste the
   draft.
2. Delete the draft when you are done.
3. Start a new session and run `/vision review`.

## Review

**A reader who sat through the interview is not a fresh reader.** If this session ran the interview,
say so first and recommend running `/vision review` in a new session instead. Continue if the user
asks you to.

1. Run `${CLAUDE_SKILL_DIR}/../../bin/check-vision` from the project root. Print what it says under
   a heading **Structure**, unchanged. If it reports `OK`, say so.
2. Read the overview and check it against the six checks below. Print the results under a heading
   **Judgment**.

Report and stop. Never edit the document, and never write a corrected version of a sentence: the
author writes their own words. Never report anything the script already reported.

### The six checks

**Technology named.** A product, library, language, framework, database, host or API named
anywhere in the Vision section. Does not count: a word that is also ordinary English used in its
ordinary sense; an external system the project has no choice about ("my bank's CSV export"); a
physical device.

**MVP exceeds the appetite.** An MVP that cannot plausibly be built in the time and money stated
under Appetite. Does not count: an ambitious MVP where the appetite is large to match.

**MVP not end to end.** An MVP that builds one part completely rather than a thin path through the
whole system, so nothing is usable until later work lands. Does not count: a project that genuinely
has one part.

**Success criteria not checkable.** A criterion with no observation that would settle whether it
has been met. Does not count: a subjective but observable criterion, such as "I choose it over
searching by hand, three weekends running".

**Guess stated as fact.** An assertion about feasibility, data, cost or behaviour the author cannot
know yet and has not listed under risks and unknowns. Does not count: an assumption labelled as one.

**Priorities without a tiebreak.** Ranked goals with no rule for which wins when two conflict. Does
not count: a single goal, or priorities where the ranking is explicitly the tiebreak.

### Output

One line per finding, in document order:

`<check name> — <heading> — "<quoted words>" — <why it is a problem, one sentence>`

Then `<n> finding(s).`, or, with nothing to report, exactly `No findings.`

Quote at most fifteen words. Where the problem is something missing, quote the heading's closing
words and say what is absent.

Example:

Technology named — MVP — "probably on Postgres" — Stage 1 leaves the how open.
Success criteria not checkable — Goals and success criteria — "should feel fast" — no observation would settle it.
2 finding(s).
