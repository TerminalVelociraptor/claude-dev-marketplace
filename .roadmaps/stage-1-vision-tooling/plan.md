# Stage 1 (Vision & Scope) tooling — `/vision`

## Context

`~/plan-tooling/stages.md` describes a nine-stage process for solo projects. Its tooling is being
built as the `spec-driven-development` plugin in `~/agent-tools/plugin-marketplace`. **This plan
covers Stage 1 (Vision & Scope) only**; later stages are separate sessions and separate plans.

The premise: a vision written by an AI is one the author never internalises. So Claude interviews
and drafts into a throwaway file, the user writes the real document, and a small check plus a fresh
read keep it honest.

An earlier version of this plan was three times this size. It was trimmed on purpose: the word
limit, tiny mode, numbered-list rules, template check-flags, heading-order and duplicate checks, a
reviewer subagent, an eval harness, a lint test and a recall skill were all cut as more machinery
than the job needs. Any of them can be added later without rework.

## Goal

A user runs `/vision` in a project, is interviewed, writes `docs/01-overview.md` themselves, and can
run `/vision review` to have the result checked mechanically and read critically.

## What we are NOT building

- **No tooling for Stages 2–9.** `## System` stays an empty placeholder in the template.
- **No AI prose in `docs/01-overview.md`.** Claude creates the file from the template, title only.
- **No technology, component or schema advice.** Review flags technology names when they appear.
- **No recall check.** Dropped deliberately; see Stale claims below.
- **No word limit, tiny mode, list-format rules or template check-flags.**
- **No reviewer subagent, no eval harness, no plugin lint test.**
- **No hooks**, and no changes to other plugins.

## Terms

- **Stage**: one of Stages 1–9 in `stages.md`. This implements Stage 1.
- **Unit**: U1–U3 below.
- **Overview**: `docs/01-overview.md` in a target project — what the user writes.
- **Draft**: `docs/drafts/vision.md` in a target project — Claude's disposable output.
- **Plugin root**: `~/agent-tools/plugin-marketplace/plugins/spec-driven-development/`. Paths are
  relative to it unless they start with `~` or `.claude`.

## Where we are

Verified on disk 2026-09-19: branch `spec-driven-development_stage-1`, working tree clean, HEAD
`888edd5 spec-driven-development: scaffold Stage 1 plugin`. The plugin holds exactly three files:

```
plugins/spec-driven-development/.claude-plugin/plugin.json
plugins/spec-driven-development/config.json
plugins/spec-driven-development/templates/01-overview.md
```

No `bin/`, `tests/`, `skills/`, `agents/`, `shared/`, `evals/` or `README.md`.

`config.json` as it stands. The `vision` block is now dead weight — U1 removes it:

```json
{
  "project_paths": {
    "_comment": "Relative to the root of the project the plugin is used in.",
    "overview": "docs/01-overview.md",
    "vision_draft": "docs/drafts/vision.md"
  },
  "plugin_paths": {
    "_comment": "Relative to this plugin's root directory.",
    "overview_template": "templates/01-overview.md"
  },
  "vision": {
    "word_limit": { "normal": 500, "tiny": 150 },
    "tiny_marker": "<!-- size: tiny -->",
    "priorities_min_items": 2
  }
}
```

`templates/01-overview.md`, whose eight `### ` headings drive everything. Do not edit it in this
plan:

```markdown
# <project name>

## Vision

### Problem and users
<!-- What problem does this solve, and for whom: you, friends, or the public? -->

### Goals and success criteria
<!-- How will you know it's working? For each goal, what would you check? -->

### Priorities
<!-- Rank the goals as a numbered list. When two conflict, which one wins? -->

### Non-goals
<!-- What are you explicitly not building? -->

### Appetite
<!-- How much time and money (hosting, APIs) are you willing to spend? -->

### MVP
<!-- What is the first version you would actually use, in user terms? Does it run end to end, thinly? -->

### Risks and unknowns
<!-- What are the biggest unknowns: feasibility, data, cost? List them instead of guessing answers. -->

### Learning goals
<!-- Is there something you want to learn? It decides which parts you write yourself. Write "None" if not. -->

## System
<!-- Filled in at Stage 2. -->
```

Also on disk: `~/agent-tools/plugin-marketplace/CLAUDE.md` (rules for every plugin) and
`.claude/rules/spec-driven-development.md` (path-scoped rules with a fact-ownership table whose
"Word limits, tiny marker, Priorities minimum items" row goes stale in U1).

## Stale claims to fix

- **`stages.md:109`** still names an exit criterion — "You can state the goal, MVP and non-goals in
  three sentences without looking" — that nothing will now check, because the recall skill is cut.
  Leave the criterion (it is a human habit worth keeping) but do not build tooling for it.
- **The rules-file ownership row** for word limits and list minimums is removed in U1, since
  `config.json` no longer holds them.

## Dependency statement

`U1 ──► U2 ──► U3`

- **U1** depends on nothing; the scaffold is committed.
- **U2** needs U1, because the skill calls `check-vision --status` and `check-vision`.
- **U3** needs both, because it documents and exercises them.

## Conventions

From `~/agent-tools/plugin-marketplace/CLAUDE.md:5-13` and the `learning` plugin.

- **Runtime:** Python 3.13.5, standard library only.
- **Scripts:** `bin/`, no extension, executable, `#!/usr/bin/env python3`, module docstring first.
- **Tests:** `unittest` in `tests/`, named `test_<script name with underscores>.py`, running the
  script through `subprocess` with `sys.executable`, as
  `~/agent-tools/plugin-marketplace/plugins/learning/tests/test_learn_log.py:17` does.
- **Test data:** built in a `TemporaryDirectory` from the real template, never from fixture files
  that copy the headings.
- **Skills:** `skills/<name>/SKILL.md` with `name`, `description`, `argument-hint`, `allowed-tools`,
  `disable-model-invocation: true`.
- **Pre-approving the script:** `Bash(${CLAUDE_SKILL_DIR}/../../bin/check-vision *)`, matching
  `~/agent-tools/plugin-marketplace/plugins/learning/skills/pair/SKILL.md:6`.

## Cross-cutting gotchas

Verified this session unless marked.

1. **`claude` is a shell alias for `clodex claude`.** Use `~/.local/bin/claude` for
   `claude plugin validate`, or you get the wrapper's help.
2. **JSON has no comments.** `config.json` carries `_comment` keys; code drops keys starting with
   `_` at every level.
3. **Path-scoped rules never appear in `/context`.** The `Loaded .claude/rules/...` line printed
   after Claude reads a plugin file is the only signal. Verified by the user 2026-09-14.
4. **`stages.md` is not in git** and is being retired; the plugin is the source of truth.
5. **The user makes every commit decision.** Ask first; never push or rebase.
6. **`/roadmap` writes `.roadmaps/<slug>/` into the directory the session started in.** Start
   execution sessions in `~/agent-tools/plugin-marketplace`. (Assumed.)

## Stop-and-ask triggers

- A test fails and the tempting fix is to change the assertion.
- A unit needs a file outside its **Files** list.
- Any **Undecided** item.
- An instruction here contradicts `CLAUDE.md`, the rules file, or the code.
- Anything needing a subagent, a commit, a push or a rebase.

---

## U1 — `bin/check-vision` and its tests

The mechanical half: what needs no judgment.

**Files:**
- Create: `bin/check-vision` (executable), `tests/test_check_vision.py`, `.gitignore`
- Modify: `config.json` (remove the `vision` block), and
  `~/agent-tools/plugin-marketplace/.claude/rules/spec-driven-development.md` (drop the word-limit
  row, add `| Deterministic checks and their finding IDs | bin/check-vision |`)
- Must not touch: `templates/01-overview.md`, `.claude-plugin/plugin.json`

**Contract:**
- **Usage:** `check-vision [--root DIR] [--draft] [--status] [--config FILE]`
- Checks `<root>/<project_paths.overview>`, or the draft with `--draft`. `--root` defaults to the
  current directory. `--config` exists so tests can point at their own template.
- **Exit codes:** `0` clean, `1` findings, `2` usage, config or template problem, including a
  missing document.
- **Findings:** `missing-vision`, `missing-heading`, `empty-heading`, `leftover-draft`. Printed as
  `<path>:<line>: error [<id>] <message>`, or without `:<line>` where there is none, then
  `N error(s)` or `OK`.
- **`--status`** prints one word and exits 0: `missing`, `empty` or `filled`.
- **Invariant:** no heading names and no limits in the script. The checked section is the template's
  first `## ` section that has `### ` headings.

**Content** — `bin/check-vision`, in full:

```python
#!/usr/bin/env python3
"""Check a project's Vision section against the plugin's overview template.

Reports only what needs no judgment: headings the template has and the document doesn't, headings
left blank, and a throwaway draft still present once the vision is written. Anything that needs a
reading of what the words mean belongs to `/vision review`.

Headings come from the template and paths from config.json, so neither is restated here.

Exit status: 0 no findings, 1 findings, 2 usage, config or template problem.
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = PLUGIN_ROOT / "config.json"
COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)

REQUIRED_CONFIG_KEYS = (
    ("project_paths", "overview"),
    ("project_paths", "vision_draft"),
    ("plugin_paths", "overview_template"),
)


class ConfigError(Exception):
    pass


class TemplateError(Exception):
    pass


@dataclass
class Finding:
    check: str
    message: str
    line: int = None


@dataclass
class Section:
    name: str
    line: int
    lines: list = field(default_factory=list)   # (line number, text, inside a code fence)


def drop_comment_keys(value):
    """config.json carries "_comment" keys because JSON has no comments."""
    if isinstance(value, dict):
        return {k: drop_comment_keys(v) for k, v in value.items() if not k.startswith("_")}
    return value


def load_config(path):
    try:
        config = drop_comment_keys(json.loads(Path(path).read_text()))
    except OSError as exc:
        raise ConfigError(f"{path}: {exc.strerror}") from None
    except json.JSONDecodeError as exc:
        raise ConfigError(f"{path}: not valid JSON ({exc})") from None
    for keys in REQUIRED_CONFIG_KEYS:
        node = config
        for key in keys:
            if not isinstance(node, dict) or key not in node:
                raise ConfigError(f"{path}: missing key {'.'.join(keys)}")
            node = node[key]
    return config


def split_sections(text):
    """Split Markdown into `## ` sections, ignoring headings inside code fences."""
    sections, current, in_fence = [], None, False
    for number, line in enumerate(text.split("\n"), 1):
        marker = line.lstrip().startswith(("```", "~~~"))
        inside = in_fence or marker
        if marker:
            in_fence = not in_fence
        if not inside and line.startswith("## "):
            current = Section(line[3:].strip(), number)
            sections.append(current)
            continue
        if current is not None:
            current.lines.append((number, line, inside))
    return sections


def split_headings(section):
    """[(name, line number, body lines)] for each `### ` heading in one section."""
    blocks = []
    for number, line, inside in section.lines:
        if not inside and line.startswith("### "):
            blocks.append((line[4:].strip(), number, []))
        elif blocks:
            blocks[-1][2].append(line)
    return blocks


def load_template(path):
    """(section name, heading names in order), from the first `## ` section that has headings."""
    try:
        text = Path(path).read_text()
    except OSError as exc:
        raise TemplateError(f"{path}: {exc.strerror}") from None
    for section in split_sections(text):
        blocks = split_headings(section)
        if blocks:
            return section.name, [name for name, _, _ in blocks]
    raise TemplateError(f"{path}: no '## ' section with '### ' headings")


def answered(body_lines):
    """True when something other than the template's prompt comments is written here."""
    return bool(COMMENT_RE.sub("", "\n".join(body_lines)).strip())


def check_document(text, section_name, headings, draft_path, is_draft):
    target = next((s for s in split_sections(text) if s.name == section_name), None)
    if target is None:
        return [Finding("missing-vision", f"'## {section_name}' section is missing")]

    blocks = split_headings(target)
    present = {name for name, _, _ in blocks}
    findings = [Finding("empty-heading", f"'### {name}' is empty", line)
                for name, line, body in blocks if name in headings and not answered(body)]
    findings += [Finding("missing-heading", f"'### {name}' is required", target.line)
                 for name in headings if name not in present]

    written = {name for name, _, body in blocks if answered(body)}
    if not is_draft and set(headings) <= written and draft_path.exists():
        findings.append(Finding(
            "leftover-draft",
            f"{draft_path} still exists; delete it once the Vision section is written"))
    return findings


def status(doc_path, section_name):
    """One word for the skill: missing, empty or filled."""
    if not doc_path.exists():
        return "missing"
    target = next((s for s in split_sections(doc_path.read_text()) if s.name == section_name), None)
    if target is None:
        return "empty"
    return "filled" if any(answered(body) for _, _, body in split_headings(target)) else "empty"


def report(doc_path, findings):
    for finding in sorted(findings, key=lambda f: f.line or 0):
        where = f"{doc_path}:{finding.line}" if finding.line else str(doc_path)
        print(f"{where}: error [{finding.check}] {finding.message}")
    print(f"{len(findings)} error(s)" if findings else "OK")
    return 1 if findings else 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Check a Vision section against the plugin's overview template.")
    parser.add_argument("--root", type=Path, default=Path("."),
                        help="project root (default: the current directory)")
    parser.add_argument("--draft", action="store_true",
                        help="check the interview draft instead of the overview")
    parser.add_argument("--status", action="store_true",
                        help="print missing, empty or filled, and exit")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG,
                        help="config file (default: the plugin's config.json)")
    args = parser.parse_args(argv)

    try:
        config = load_config(args.config)
        section_name, headings = load_template(
            PLUGIN_ROOT / config["plugin_paths"]["overview_template"])
    except (ConfigError, TemplateError) as exc:
        print(f"check-vision: {exc}", file=sys.stderr)
        return 2

    root = args.root.expanduser().resolve()
    draft_path = root / config["project_paths"]["vision_draft"]
    doc_path = draft_path if args.draft else root / config["project_paths"]["overview"]

    if args.status:
        print(status(doc_path, section_name))
        return 0

    if not doc_path.exists():
        print(f"check-vision: {doc_path} does not exist", file=sys.stderr)
        return 2

    return report(doc_path, check_document(
        doc_path.read_text(), section_name, headings, draft_path, args.draft))


if __name__ == "__main__":
    sys.exit(main())
```

**Content** — `.gitignore`, one line:

```
__pycache__/
```

**Content** — `tests/test_check_vision.py`, in full:

```python
"""Tests for bin/check-vision. Documents are built from the real template, so renaming a heading
needs no test edits."""

import importlib.util
import json
import subprocess
import sys
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path
from tempfile import TemporaryDirectory

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "bin" / "check-vision"


def load_script():
    loader = SourceFileLoader("check_vision", str(SCRIPT))
    spec = importlib.util.spec_from_loader("check_vision", loader)
    module = importlib.util.module_from_spec(spec)
    sys.modules["check_vision"] = module
    loader.exec_module(module)
    return module


CV = load_script()
CONFIG = CV.load_config(ROOT / "config.json")
TEMPLATE = ROOT / CONFIG["plugin_paths"]["overview_template"]
SECTION, NAMES = CV.load_template(TEMPLATE)
BODY = "Something the user actually wrote."


def document(names=None, bodies=None, section=SECTION, extra=""):
    names = NAMES if names is None else names
    bodies = bodies or {}
    lines = ["# Toy project", "", f"## {section}", ""]
    for name in names:
        lines += [f"### {name}", bodies.get(name, BODY), ""]
    if extra:
        lines += [extra, ""]
    return "\n".join(lines)


class CheckVisionTest(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.overview = self.root / CONFIG["project_paths"]["overview"]
        self.draft = self.root / CONFIG["project_paths"]["vision_draft"]

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, text, path=None):
        path = path or self.overview
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return path

    def run_check(self, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(self.root), *args],
            capture_output=True, text=True)

    def ids(self, result):
        return [line.split("[", 1)[1].split("]", 1)[0]
                for line in result.stdout.splitlines() if "[" in line]

    def test_untouched_template_reports_every_heading_empty(self):
        self.write(TEMPLATE.read_text())
        result = self.run_check()
        self.assertEqual(result.returncode, 1)
        self.assertEqual(self.ids(result), ["empty-heading"] * len(NAMES))

    def test_filled_document_passes(self):
        self.write(document())
        result = self.run_check()
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("OK", result.stdout)

    def test_missing_heading(self):
        self.write(document(names=NAMES[1:]))
        result = self.run_check()
        self.assertIn("missing-heading", self.ids(result))
        self.assertIn(NAMES[0], result.stdout)

    def test_missing_section(self):
        self.write(document(section="Something else"))
        result = self.run_check()
        self.assertEqual(self.ids(result), ["missing-vision"])
        self.assertEqual(result.returncode, 1)

    def test_other_sections_are_ignored(self):
        self.write(document(extra="## System\n\nnonsense\n\n## Parked for later\n\nmore nonsense"))
        self.assertEqual(self.run_check().returncode, 0)

    def test_comment_only_body_is_empty(self):
        self.write(document(bodies={NAMES[0]: "<!-- just the prompt -->"}))
        self.assertIn("empty-heading", self.ids(self.run_check()))

    def test_leftover_draft(self):
        self.write(document())
        self.write("draft text", path=self.draft)
        self.assertIn("leftover-draft", self.ids(self.run_check()))

    def test_no_leftover_draft_when_absent(self):
        self.write(document())
        self.assertEqual(self.run_check().returncode, 0)

    def test_draft_mode_ignores_the_leftover_draft(self):
        self.write(document(), path=self.draft)
        self.assertNotIn("leftover-draft", self.ids(self.run_check("--draft")))

    def test_leftover_draft_waits_until_the_vision_is_written(self):
        self.write(document(bodies={NAMES[0]: "<!-- unanswered -->"}))
        self.write("draft text", path=self.draft)
        self.assertNotIn("leftover-draft", self.ids(self.run_check()))

    def test_status(self):
        self.assertEqual(self.run_check("--status").stdout.strip(), "missing")
        self.write(TEMPLATE.read_text())
        self.assertEqual(self.run_check("--status").stdout.strip(), "empty")
        self.write(document())
        self.assertEqual(self.run_check("--status").stdout.strip(), "filled")

    def test_missing_document_is_a_usage_error(self):
        result = self.run_check()
        self.assertEqual(result.returncode, 2)
        self.assertIn("does not exist", result.stderr)

    def test_config_missing_a_key(self):
        broken = self.root / "broken.json"
        broken.write_text(json.dumps({"project_paths": {"overview": "docs/01-overview.md"}}))
        result = self.run_check("--config", str(broken))
        self.assertEqual(result.returncode, 2)
        self.assertIn("missing key", result.stderr)

    def test_headings_come_from_the_template(self):
        template = self.root / "template.md"
        # The new heading has to land inside the checked section, so split on the next `## `
        # rather than appending at the end of the file.
        parts = TEMPLATE.read_text().split("\n## ")
        parts[1] = parts[1].rstrip() + "\n\n### Extra heading\n<!-- prompt -->\n"
        template.write_text("\n## ".join(parts))
        config = self.root / "config.json"
        patched = json.loads((ROOT / "config.json").read_text())
        patched["plugin_paths"]["overview_template"] = str(template)
        config.write_text(json.dumps(patched))
        self.write(document())
        result = self.run_check("--config", str(config))
        self.assertIn("missing-heading", self.ids(result))
        self.assertIn("Extra heading", result.stdout)


if __name__ == "__main__":
    unittest.main()
```

**Test cases:**

| Input | Expected |
|---|---|
| Untouched template as the overview | 8 × `empty-heading`, exit 1 |
| Every heading answered | `OK`, exit 0 |
| First heading deleted | `missing-heading` naming it |
| No section matching the template's | `missing-vision` alone |
| Junk under other `## ` sections | exit 0 |
| Body holding only a comment | `empty-heading` |
| Answered overview + draft present | `leftover-draft` |
| Answered overview, no draft | exit 0 |
| `--draft` while the draft exists | no `leftover-draft` |
| One heading unanswered + draft present | no `leftover-draft` |
| `--status` at each stage | `missing`, then `empty`, then `filled`, exit 0 |
| No overview file | exit 2, `does not exist` |
| Config missing `plugin_paths` | exit 2, `missing key` |
| Config naming a template with an extra heading | `missing-heading` for it |

**Gotchas:**
- Strip comments before judging a heading empty; the template's prompts are comments, and an
  untouched template must read as entirely unanswered.
- `chmod +x bin/check-vision`, or every subprocess test fails on permissions.
- Import the script with the `SourceFileLoader` helper: its filename has no `.py`.
- `--status` is handled before the missing-document check, so `missing` is an answer, not an error.

**Agreed:** standard-library Python and unittest; headings from the plugin's template; paths from
`config.json`; `_`-prefixed keys ignored; works on the overview and the draft.

**Undecided:** none.

**Assumed:** the CLI, exit codes, output format and finding IDs; removing the now-unused `vision`
block from `config.json`.

**Done when:**
- `python3 -m unittest discover -s plugins/spec-driven-development/tests` prints `OK`, 14 tests.
- `cd /tmp && <plugin>/bin/check-vision --root .` prints
  `check-vision: /tmp/docs/01-overview.md does not exist` and exits 2.
- It can fail: `test_headings_come_from_the_template` passes only because headings are read from
  the template file named in config, so hardcoding them breaks it.

---

## U2 — the `/vision` skill

The interview and the review, in one file. Two verbs: `/vision` and `/vision review`.

**Files:**
- Create: `skills/vision/SKILL.md`
- Must not touch: `bin/check-vision`, `config.json`, `templates/01-overview.md`

**Contract:** `/vision` creates the overview from the template if it is missing, interviews the
user, writes the draft, and stops. `/vision review` runs the script, then reads the document against
six named checks and reports. Neither ever writes prose into the overview.

**Content** — `skills/vision/SKILL.md`, in full:

```markdown
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
```

**Gotchas:**
- `${CLAUDE_SKILL_DIR}` is literal, in the frontmatter and the body. Never expand it.
- The skill must contain no heading list: the template owns that, and a copy here rots.
- Review in the same session as the interview is the failure mode this design is trying to avoid;
  the warning at the top of Review is the only thing preventing it.

**Agreed:** interview style; technology never suggested; draft in a throwaway file; setup creating
the overview from the template; no AI prose in the overview; review as a fresh-session read rather
than a subagent.

**Undecided:** what `/vision` should do when status is `filled`. The draft asks the user rather than
assuming, because a re-interview overwrites a draft they may still be using.

**Assumed:** `disable-model-invocation: true`; the three closing instructions; folding the review
checks into this file rather than a separate one.

**Done when:**
- In an empty temp project, `/vision` creates `docs/01-overview.md` from the template with the title
  filled in, and the prompt comments still present.
- A real interview on a toy idea produces `docs/drafts/vision.md` that `check-vision --draft`
  reports `OK` on.
- With a vision pasted into the overview, `/vision review` in a **new** session prints a
  **Structure** section and a **Judgment** section.
- It can fail: a vision containing "probably on Postgres" and "should feel fast" produces at least
  those two findings; a clean vision produces exactly `No findings.`
- `grep -c '^### ' skills/vision/SKILL.md` counts only this skill's own subheadings, never the
  template's eight.

---

## U3 — README and a real run

**Files:**
- Create: `README.md`
- Modify: the rules file, if any ownership row is stale
- Must not touch: `bin/`, `skills/` — a fix found here becomes its own reviewed change

**Content** — `README.md`, in full:

```markdown
# spec-driven-development

Tooling for a human-in-the-loop, spec-driven process for solo projects. This version covers
**Stage 1: Vision & Scope**.

The premise: a vision written by an AI is one you never internalise. So Claude interviews you and
drafts into a throwaway file, you write the real document, and the tooling checks what you wrote.

## How to use it

1. `/vision` — interviews you and writes `docs/drafts/vision.md`. It creates `docs/01-overview.md`
   from the template first if it does not exist, filling in the title only.
2. **You write the Vision section of `docs/01-overview.md` in your own words,** then delete the
   draft.
3. Start a new session and run `/vision review`. It reports blank or missing headings and a
   leftover draft, then reads what you wrote for technology names, an MVP that outruns your
   appetite or is not end to end, success criteria nobody could check, guesses stated as fact, and
   priorities with no tiebreak.

A new session matters for step 3: an agent that just interviewed you tends to agree with the
answers it helped you write.

## What it will not do

Write your vision for you, name technologies, design components, or decide anything Stage 2 owns.

## Commands

| Command | Does |
|---|---|
| `bin/check-vision` | Blank headings, missing headings, leftover draft |
| `bin/check-vision --draft` | The same, against the interview draft |
| `bin/check-vision --status` | Prints `missing`, `empty` or `filled` |
| `python3 -m unittest discover -s tests` | The test suite |

## Configuration

`config.json` says where the documents live. The headings and their prompts live in
`templates/01-overview.md`, which is the only place they are defined. See the ownership table in
`.claude/rules/spec-driven-development.md` at the repository root.
```

**Gotchas:**
- The README must not list the headings or restate anything from the template; a second copy is
  what this plugin exists to avoid.

**Agreed:** the README comes last, so it describes what was built.

**Undecided:** **which real project to validate against** — this plugin itself, a project you name,
or a throwaway directory, which is the weakest evidence because the content is invented.

**Done when:**
- A real `docs/01-overview.md` exists for the chosen project, written by the user, and
  `check-vision` reports `OK` with exit 0.
- `/vision review` in a fresh session prints findings the user judged useful, or `No findings.`
- Every command in the README's table runs as written from the plugin root.

---

## Verification

Uniform for every unit. Run from `~/agent-tools/plugin-marketplace`.

| Check | Command | Expected |
|---|---|---|
| Tests | `python3 -m unittest discover -s plugins/spec-driven-development/tests` | `OK`, no skips |
| Plugin manifest | `~/.local/bin/claude plugin validate plugins/spec-driven-development` | `✔ Validation passed` |
| Marketplace manifest | `~/.local/bin/claude plugin validate .` | `✔ Validation passed` |
| Scope | `git status --short` | only the unit's **Files** |
| Script permissions | `git ls-files -s plugins/spec-driven-development/bin` | mode `100755` |

Reporting a unit complete:

- Mark every check ✔ or ✘ with the command and its real output. Before trusting a pass, confirm the
  command can fail; each unit's **Done when** ends with how.
- Validate on at least one real input, not only unit tests: for U1 a document outside the test
  suite, for U2 an actual interview, for U3 the real project.
- Stop for the user's review after each unit. Ask before any commit; never push or rebase.

## Decisions left for you

1. **U3's real project** — this plugin, a project you name, or a throwaway directory.
2. **What `/vision` does when a vision already exists** — ask, as drafted, or re-interview.
3. **The Assumed items**: the `check-vision` CLI and output format, removing the `vision` block from
   `config.json`, and `disable-model-invocation: true` on the skill.
4. **Where execution runs** — assumed `~/agent-tools/plugin-marketplace`, so `/roadmap` commits
   alongside the code.
