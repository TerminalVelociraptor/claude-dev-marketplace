# sdd

Interview skills and consistency checks for the project documents defined in [`sdd.md`](sdd.md), from an idea to tasks. You stay in the loop and keep the mental model: the tools interview, challenge, draft and report. Building a task stays in your own workflow.

`sdd.md` is the only definition of the documents. The skills and the script read it when they run, so editing it changes what they do.

## Tools
Every tool runs only when you run it, on what you name.

| Command | What it does | Run it when |
|---|---|---|
| [`/sdd:vision`](skills/vision/SKILL.md) | Interviews you and writes the Vision. | You start a project, or change what this version is. |
| [`/sdd:system`](skills/system/SKILL.md) | Interviews you and writes the System section. | The Vision is settled enough to name the parts. |
| [`/sdd:adr`](skills/adr/SKILL.md) | Interviews you and writes a decision record. | You settle a question someone would ask "why?" about. |
| [`/sdd:component <name>`](skills/component/SKILL.md) | Interviews you and writes one component's spec. | A slice is about to touch that component. |
| [`/sdd:slice`](skills/slice/SKILL.md) | Interviews you and returns a slice. | You pick the next piece to build. |
| [`/sdd:task`](skills/task/SKILL.md) | Interviews you and returns a task. | You split a slice, or need a change that needs no slice. |
| [`/sdd:derive`](skills/derive/SKILL.md) | Proposes the [derived files](sdd.md#derived-files). Writes what you approve. | You've changed a document they're derived from. |
| [`/sdd:update`](skills/update/SKILL.md) | Reports structure problems, broken links, missing pieces, links to superseded ADRs, and contradictions. With nothing named, it checks every document `sdd.md` gives a location; name slices and tasks (files or issue numbers) to include them. Edits only what you approve. | You've changed a document, or before starting a slice. |

There's no [Open decisions](sdd.md#open-decisions) generator: each generator drafts an entry for every question it couldn't settle and adds the ones you approve. Anything else in that section you keep by hand.

**How the generators work.** One question per message; short answers are fine. They never guess: a question you can't answer yet becomes a proposed Open decisions entry. Before drafting, they ask about any open question that has to be settled before this document. After each drafted item they offer a menu of challenge methods (Pre-mortem, Inversion, Subtraction and others), plus "proceed". A method's changes apply only if you accept them. To turn the menu off, run `/config` in a session and set the plugin's Challenge menu option to false. Each draft still waits for you to keep or revise it.

## What level of thinking goes where
`sdd.md` says what each document holds; this is the altitude to write it at.
- **[Vision](sdd.md#vision)** is shaping, not specifying. Shape Up's pitch is the model: one specific story of the problem, an appetite (how much time it's worth), and no-gos. For the MVP, Patton's advice applies: "just tell me the activities". Narrate what the system does at a high level, then take the thinnest path through it. Technology you're tempted to name belongs in Open decisions.
- **[System](sdd.md#system)** is the parts and the seams between them, in plain language. No formats, hosts or products yet.
- **[Component specs](sdd.md#component-spec)** are promises precise enough to build and test against, not an implementation plan.
- **[Slices](sdd.md#slice)** say what the user can do afterwards and what they see; **[tasks](sdd.md#task)** say what changes and how you'll check it.
- **[ADRs](sdd.md#adr-decision-record)** are for decisions someone would ask "why?" about, and nothing else.

## The first slice is a walking skeleton
Make the first slice the thinnest thing that runs end to end through the components the MVP touches, even if each part does almost nothing. It proves the split and the contracts while they're cheap to change; later slices thicken it.

## Drafted by an agent, owned by you
Any document can start as a draft from an interview. It's done when you've edited it until it says what you mean, not when the interview ends.

## Design notes
[`brief.md`](brief.md) says what the tooling is for and the decisions behind it; [`research.md`](research.md) has the evidence.
