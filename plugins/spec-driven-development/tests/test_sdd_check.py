"""End-to-end checks of sdd-check using isolated project roots."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "bin" / "sdd-check"
FIXTURE = """# Docs

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
"""
OVERVIEW = "## Overview\n### Goals\nx\n"


class SddCheckTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.sdd = self.root / "sdd.md"
        self.sdd.write_text(FIXTURE, encoding="utf-8")

    def write(self, path, text):
        file = self.root / path
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(text, encoding="utf-8")
        return file

    def run_check(self, *args, stdin=None, real_sdd=False):
        command = [sys.executable, str(SCRIPT), "--root", str(self.root)]
        if not real_sdd:
            command.extend(["--sdd", str(self.sdd)])
        command.extend(args)
        return subprocess.run(command, input=stdin, text=True, capture_output=True)

    def assert_clean(self, result):
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout.splitlines()[-1], "no findings")
        self.assertEqual(result.stderr, "")

    def test_01_missing_fixed_file(self):
        missing = self.run_check()
        self.assertEqual(missing.returncode, 1)
        self.assertIn("docs/overview.md:1: structure: missing file (Overview live here)", missing.stdout)
        self.write("docs/overview.md", OVERVIEW)
        self.assert_clean(self.run_check())

    def test_02_optional_item_absent(self):
        self.write("docs/overview.md", OVERVIEW)
        self.assert_clean(self.run_check())
        self.write("docs/overview.md", "## Overview\n### Notes\nx\n")
        self.assertIn("missing item `Goals` (Overview)", self.run_check().stdout)

    def test_03_required_item_missing(self):
        self.write("docs/overview.md", "## Overview\n### Notes\nx\n")
        missing = self.run_check()
        self.assertEqual(missing.returncode, 1)
        self.assertIn("missing item `Goals` (Overview)", missing.stdout)
        self.write("docs/overview.md", OVERVIEW)
        self.assert_clean(self.run_check())

    def test_04_unknown_item(self):
        self.write("docs/overview.md", OVERVIEW + "### Risks\nx\n")
        unknown = self.run_check()
        self.assertEqual(unknown.returncode, 1)
        self.assertIn("`Risks` is not an item of Overview in sdd.md", unknown.stdout)
        self.write("docs/overview.md", OVERVIEW)
        self.assert_clean(self.run_check())

    def test_05_duplicate_item(self):
        self.write("docs/overview.md", OVERVIEW + "### Goals\nx\n")
        duplicate = self.run_check()
        self.assertEqual(duplicate.returncode, 1)
        self.assertIn("`Goals` appears twice (first at line 2)", duplicate.stdout)
        self.write("docs/overview.md", OVERVIEW)
        self.assert_clean(self.run_check())

    def test_06_item_names_come_from_sdd(self):
        self.write("docs/overview.md", OVERVIEW)
        self.sdd.write_text(FIXTURE.replace("**Goals:**", "**Outcomes:**"), encoding="utf-8")
        changed = self.run_check()
        self.assertEqual(changed.returncode, 1)
        self.assertIn("`Goals` is not an item of Overview in sdd.md", changed.stdout)
        self.assertIn("missing item `Outcomes` (Overview)", changed.stdout)
        self.sdd.write_text(FIXTURE, encoding="utf-8")
        self.assert_clean(self.run_check())

    def test_07_locations_come_from_sdd(self):
        self.write("docs/overview.md", OVERVIEW)
        self.sdd.write_text(FIXTURE.replace("`docs/overview.md`", "`docs/intro.md`"),
                            encoding="utf-8")
        changed = self.run_check()
        self.assertEqual(changed.returncode, 1)
        self.assertIn("docs/intro.md:1: structure: missing file", changed.stdout)
        self.assertNotIn("docs/overview.md:", changed.stdout)
        self.sdd.write_text(FIXTURE, encoding="utf-8")
        self.assert_clean(self.run_check())

    def test_08_broken_file_link(self):
        self.write("docs/overview.md", OVERVIEW + "[x](nope.md)\n")
        broken = self.run_check()
        self.assertEqual(broken.returncode, 1)
        self.assertIn("broken-link: `nope.md`: no such file", broken.stdout)
        self.write("docs/nope.md", "# Destination\n")
        self.assert_clean(self.run_check())

    def test_09_broken_anchor_link(self):
        self.write("docs/overview.md", OVERVIEW + "[Goals](overview.md#nope)\n")
        broken = self.run_check()
        self.assertEqual(broken.returncode, 1)
        self.assertIn("broken-link: `overview.md#nope`: no heading for `#nope`", broken.stdout)
        self.write("docs/overview.md", OVERVIEW + "[Goals](overview.md#goals)\n")
        self.assert_clean(self.run_check())

    def test_10_link_text_not_in_target(self):
        self.write("docs/overview.md", OVERVIEW + "### Notes\n[speed](overview.md#goals)\n")
        missing = self.run_check()
        self.assertEqual(missing.returncode, 1)
        self.assertIn("not-in-target: `speed` doesn't appear under `#goals`", missing.stdout)
        self.write("docs/overview.md", OVERVIEW.replace("\nx\n", "\nSpeed over polish\n")
                   + "### Notes\n[speed](overview.md#goals)\n")
        self.assert_clean(self.run_check())

    def test_11_link_text_casefolds(self):
        self.write("docs/overview.md", OVERVIEW.replace("\nx\n", "\nSpeed over polish\n")
                   + "### Notes\n[speed](overview.md#goals)\n")
        self.assert_clean(self.run_check())
        self.write("docs/overview.md", OVERVIEW + "### Notes\n[speed](overview.md#goals)\n")
        self.assertIn("not-in-target: `speed` doesn't appear under `#goals`",
                      self.run_check().stdout)

    def test_12_superseded_adr_link(self):
        self.write("docs/overview.md", OVERVIEW + "[A](decisions/0001-a.md)\n")
        self.write("docs/decisions/0001-a.md", "# A\n## Decision\nx\n")
        successor = self.write("docs/decisions/0002-b.md",
                               "# B\n## Decision\nx\n## Supersedes\n[A](0001-a.md)\n")
        changed = self.run_check()
        self.assertEqual(changed.returncode, 1)
        lines = [line for line in changed.stdout.splitlines() if ": superseded-link:" in line]
        self.assertEqual(len(lines), 1, changed.stdout)
        self.assertIn("docs/overview.md:4:", lines[0])
        self.assertIn("docs/decisions/0002-b.md", lines[0])
        successor.write_text("# B\n## Decision\nx\n", encoding="utf-8")
        self.assert_clean(self.run_check())

    def test_13_links_in_code_ignored(self):
        text = OVERVIEW + "```\n[x](missing-fence.md)\n```\n`[x](missing-inline.md)`\n"
        self.write("docs/overview.md", text)
        self.assert_clean(self.run_check())
        self.write("docs/overview.md", OVERVIEW + "[x](missing-fence.md)\n"
                   + "[x](missing-inline.md)\n")
        changed = self.run_check()
        self.assertEqual(changed.returncode, 1)
        self.assertIn("`missing-fence.md`: no such file", changed.stdout)
        self.assertIn("`missing-inline.md`: no such file", changed.stdout)

    def test_14_scheme_link_ignored(self):
        self.write("docs/overview.md", OVERVIEW + "[site](https://example.com)\n")
        self.assert_clean(self.run_check())
        self.write("docs/overview.md", OVERVIEW + "[site](missing.md)\n")
        self.assertIn("broken-link: `missing.md`: no such file", self.run_check().stdout)

    def test_15_stdin_document_valid(self):
        self.write("docs/overview.md", OVERVIEW)
        self.assert_clean(self.run_check("--doc", "Slice", "-", stdin="# S\n## Outcome\nx\n"))
        changed = self.run_check("--doc", "Slice", "-", stdin="# S\n")
        self.assertEqual(changed.returncode, 1)
        self.assertIn("<stdin>:1: structure: missing item `Outcome` (Slice)", changed.stdout)

    def test_16_stdin_document_missing_item(self):
        self.write("docs/overview.md", OVERVIEW)
        missing = self.run_check("--doc", "Slice", "-", stdin="# S\n")
        self.assertEqual(missing.returncode, 1)
        self.assertIn("<stdin>:1: structure: missing item `Outcome` (Slice)", missing.stdout)
        self.assert_clean(self.run_check("--doc", "Slice", "-", stdin="# S\n## Outcome\nx\n"))

    def test_17_unknown_entry_and_missing_doc_errors(self):
        self.write("docs/overview.md", OVERVIEW)
        unknown = self.run_check("--doc", "Nope", "f.md")
        self.assertEqual(unknown.returncode, 2)
        self.assertIn("sdd-check: unknown entry", unknown.stderr)
        self.assertIn("Overview, ADR, Slice", unknown.stderr)
        absent = self.run_check("--doc", "Slice", "f.md")
        self.assertEqual(absent.returncode, 2)
        self.assertIn("sdd-check: missing --doc file", absent.stderr)
        self.write("f.md", "# S\n## Outcome\nx\n")
        self.assert_clean(self.run_check("--doc", "Slice", "f.md"))

    def test_18_missing_supersedes_source_item(self):
        self.write("docs/overview.md", OVERVIEW)
        self.sdd.write_text(FIXTURE.replace(
            "- **Supersedes** (only if it replaces one): s\n", ""), encoding="utf-8")
        malformed = self.run_check()
        self.assertEqual(malformed.returncode, 2)
        self.assertIn("update SUPERSEDES in bin/sdd-check", malformed.stderr)
        self.sdd.write_text(FIXTURE, encoding="utf-8")
        self.assert_clean(self.run_check())

    def test_19_no_entries_in_sdd(self):
        self.write("docs/overview.md", OVERVIEW)
        self.sdd.write_text("# x\n", encoding="utf-8")
        malformed = self.run_check()
        self.assertEqual(malformed.returncode, 2)
        self.assertIn("sdd-check: sdd.md has no entries", malformed.stderr)
        self.sdd.write_text(FIXTURE, encoding="utf-8")
        self.assert_clean(self.run_check())

    def test_20_real_sdd_with_empty_root(self):
        missing = self.run_check(real_sdd=True)
        self.assertEqual(missing.returncode, 1, missing.stderr)
        self.assertEqual(missing.stderr, "")
        lines = missing.stdout.splitlines()
        self.assertGreater(len(lines), 1)
        self.assertTrue(all("missing file" in line for line in lines[:-1]), missing.stdout)
        self.assertIn("docs/01-overview.md:1: structure: missing file", missing.stdout)
        self.write("docs/01-overview.md", "")
        changed = self.run_check(real_sdd=True)
        self.assertNotIn("missing file", changed.stdout)
        self.assertIn("structure:", changed.stdout)

    def test_21_derived_file_links_checked(self):
        self.write("docs/overview.md", OVERVIEW)
        self.write(".claude/rules/x.md", "[spec](../../docs/components/x.md)\n")
        broken = self.run_check()
        self.assertEqual(broken.returncode, 1)
        self.assertIn(".claude/rules/x.md:1: broken-link: `../../docs/components/x.md`:",
                      broken.stdout)
        self.write("docs/components/x.md", "# Spec\n")
        self.assertNotIn("broken-link: `../../docs/components/x.md`", self.run_check().stdout)

    def test_22_duplicate_stdin_document(self):
        self.write("docs/overview.md", OVERVIEW)
        duplicate = self.run_check("--doc", "Slice", "-", "--doc", "Slice", "-",
                                   stdin="# S\n## Outcome\nx\n")
        self.assertEqual(duplicate.returncode, 2)
        self.assertIn("only one --doc may read stdin", duplicate.stderr)
        self.assert_clean(self.run_check("--doc", "Slice", "-",
                                         stdin="# S\n## Outcome\nx\n"))


if __name__ == "__main__":
    unittest.main()
