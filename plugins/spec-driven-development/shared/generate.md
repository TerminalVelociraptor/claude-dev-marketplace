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
3. **Draft** the item following `sdd.md`'s rules, sized so the whole document fits the entry's size, and show it for review. Do not start the next item's questions in the same message.
4. **Review.** If the Challenge menu setting is `false`, ask whether to keep or revise the draft. After a revision, show it and ask again. Otherwise, offer a numbered challenge menu:
   - 3–5 methods from `shared/challenge-methods.md` in the plugin root, chosen for the mistake this item's *Why* names;
   - **reshuffle**: other methods;
   - **proceed**: go on to the next item.

   When the developer picks a method, apply it to the draft and show what it found and the change it proposes. Make the change only if the developer accepts it, then offer the menu again. Treat any other reply as direction: apply it, then offer the menu again.
5. Go on to the next item only after the developer explicitly accepts the draft (for example, "keep it" or "proceed").

## 4. Deliver
- Show the whole document. If it is well over the entry's size, name the item that looks like it's doing another document's job, and ask. Don't cut anything on your own.
- Write it to its location only after the developer confirms, or return it if the entry names no path. Write nothing else: knock-on changes to other documents are the update skill's job.
- End with:
  - **Open questions:** each question you couldn't settle, with where it came from, for the developer to add to Open decisions.
  - **Next:** the update skill, if this may affect other documents; the derive skill, if a derived file draws on this document.
