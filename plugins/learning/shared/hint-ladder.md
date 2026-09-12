# Hint ladder — graduated unblocking

Read this when they are stuck, predicted wrong, or are being walked through an end-of-session review.

## The ladder

Bias toward the **top**. Make them work down it. Never open at rung 3 or 4 because it feels
faster — speed is not the objective, and jumping the ladder discards the retrieval benefit the
stuckness was about to produce.

**Rung 1 — Nudge.** Direct attention, supply nothing.
> "Look at what happens to `buf` between the two loops."

**Rung 2 — Concept.** Name the mechanism, do not apply it.
> "This is about false sharing. Two threads, one cache line."

**Rung 3 — Direction.** Say where and roughly what, not the answer.
> "The counters are adjacent in the struct. Pad them to a cache line and re-measure."

**Rung 4 — Full solution.** The complete answer with the mechanism explained. **Guaranteed** — the
ladder always bottoms out. Nobody is left stuck.

## Movement rules

- **One rung per exchange.** Give a rung, then stop and let them respond.
- **Never skip a rung downward** unless the escape valve fires (see `teaching-protocol.md` Rule 4),
  which jumps straight to rung 4.
- **Move up** if a hint lands and they start making progress — go quiet and let them work.
- **Two failed attempts caps it.** Per Rule 2, after the second wrong answer go to rung 4 regardless
  of where you are on the ladder. The ladder governs *how* you unblock, not *whether* — bounded
  correction always wins.
- On a growth edge, spend an extra beat at rungs 1–2. Off a growth edge, drop quickly to rung 3–4;
  making them grind on breadth material they already command is wasted session time.

## Where each skill uses this

| Skill | Trigger |
|---|---|
| `pair` | They are stuck and have asked, or a check-in found a real problem. |
| `guided` | They predicted wrong on a growth-edge mechanism. |

## Retrieval-first review

Used at the end of `pair` sessions. This is a **review, not a lecture** — the point is that they
find the problems, because self-generated errors are retained far better than reported ones.

1. **Evaluate silently first.** Build the full list of what you found. Show none of it yet.
2. **Open generic.** *"Where do you think this is weakest?"* Nothing more specific.
3. **Walk the ladder per item**, escalating only as they fail to find it. If they name a problem
   themselves, say so and move to the next item — do not elaborate on a point they already own.
4. **Correction guaranteed.** Every item on your list gets stated before the session ends, including
   the ones they never found.
5. **Weight toward growth edges.** This is not a general code review. Style, naming, and structure
   issues get one line at the end, if that.
6. **Log the delta** — the gap between their self-assessment and what you actually found is the
   highest-value signal in this system. With `learn-log` (toolkit `bin/`):

   ```
   learn-log --type self-assessment --concept <slug> --signal <found-self|missed-self|overconfident|underconfident>
   ```

   - `found-self` — they identified it unprompted.
   - `missed-self` — they never got there; you stated it.
   - `overconfident` — they called it fine; it was not.
   - `underconfident` — they called it weak; it was fine.
