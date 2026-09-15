"""Tests for bin/check-handoff.

Briefs are built from the real template, and section-specific tests pick their section by its
template flags rather than by name, so adding or renaming a template section needs no test edits.
"""

import importlib.util
import os
import subprocess
import sys
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "bin" / "check-handoff"
TEMPLATE = ROOT / "templates" / "brief.md"


def load_script():
    sys.dont_write_bytecode = True
    loader = SourceFileLoader("check_handoff", str(SCRIPT))
    spec = importlib.util.spec_from_loader("check_handoff", loader)
    module = importlib.util.module_from_spec(spec)
    sys.modules["check_handoff"] = module
    loader.exec_module(module)
    return module


CH = load_script()


class Brief:
    """A valid brief built from a template, with sections editable before it is written."""

    def __init__(self, base_dir, template=TEMPLATE, optional=True):
        self.base_dir = base_dir
        (base_dir / "key.txt").write_text("one\ntwo\nthree\n")
        parsed = CH.load_template(template)
        self.title = self.fill(parsed.title)
        self.preamble = [self.fill(line) for line in parsed.preamble]
        self.sections = {}
        for rule in parsed.sections:
            if rule.optional and not optional:
                continue
            if rule.steps:
                labels = "\n".join(f"**{label}:** Something." for label in rule.labels)
                body = f"### Step 1: Example\n{labels}"
            elif rule.paths_exist:
                body = "- `key.txt:1-3`: An example file."
            else:
                body = "Some content."
            self.sections[rule.name] = body

    def fill(self, line):
        def value(match):
            return str(self.base_dir) if match.group(1) == CH.BASE_DIR_PLACEHOLDER else "example"

        return CH.PLACEHOLDER_RE.sub(value, line)

    def write(self):
        lines = [self.title, "", *self.preamble, ""]
        for name, body in self.sections.items():
            lines += [f"## {name}", body, ""]
        path = self.base_dir / "brief.md"
        path.write_text("\n".join(lines))
        return path


class CheckHandoffTest(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.template = CH.load_template(TEMPLATE)

    def tearDown(self):
        self.tmp.cleanup()

    def run_check(self, brief, *args, cwd=None):
        return subprocess.run(
            [sys.executable, str(SCRIPT), str(brief.write()), *args],
            capture_output=True, text=True, cwd=cwd,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )

    def assertPasses(self, result):
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def assertFinding(self, result, check):
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(f"[{check}]", result.stdout)

    def rule(self, predicate):
        rules = [rule for rule in self.template.sections if predicate(rule)]
        if not rules:
            self.skipTest("the template has no section of this kind")
        return rules[0]

    def plain_required(self):
        return self.rule(lambda r: not (r.optional or r.steps or r.paths_exist))

    def test_script_is_executable(self):
        self.assertTrue(os.access(SCRIPT, os.X_OK))

    def test_valid_brief_passes(self):
        result = self.run_check(Brief(self.dir))
        self.assertPasses(result)
        self.assertIn("OK", result.stdout)

    def test_optional_sections_can_be_omitted(self):
        self.rule(lambda r: r.optional)
        self.assertPasses(self.run_check(Brief(self.dir, optional=False)))

    def test_missing_required_section(self):
        brief = Brief(self.dir)
        del brief.sections[self.plain_required().name]
        self.assertFinding(self.run_check(brief), "missing-section")

    def test_unknown_section(self):
        brief = Brief(self.dir)
        brief.sections["Not in the template"] = "Content."
        self.assertFinding(self.run_check(brief), "unknown-section")

    def test_sections_out_of_order(self):
        brief = Brief(self.dir, optional=False)
        names = list(brief.sections)
        names[0], names[1] = names[1], names[0]
        brief.sections = {name: brief.sections[name] for name in names}
        self.assertFinding(self.run_check(brief), "section-order")

    def test_empty_section_must_say_none(self):
        brief = Brief(self.dir)
        name = self.plain_required().name
        brief.sections[name] = ""
        self.assertFinding(self.run_check(brief), "empty-section")
        brief.sections[name] = "None"
        self.assertPasses(self.run_check(brief))

    def test_section_with_only_a_comment_is_empty(self):
        brief = Brief(self.dir)
        brief.sections[self.plain_required().name] = "<!-- guidance left in -->"
        self.assertFinding(self.run_check(brief), "empty-section")

    def test_title_and_preamble_lines(self):
        brief = Brief(self.dir)
        brief.title = "# Notes"
        self.assertFinding(self.run_check(brief), "title")
        brief = Brief(self.dir)
        brief.preamble = []
        self.assertFinding(self.run_check(brief), "preamble")

    def test_working_directory_can_be_followed_by_a_note(self):
        brief = Brief(self.dir)
        brief.preamble = [line.rstrip(".") + " (cwd was a subdirectory)." for line in brief.preamble]
        self.assertPasses(self.run_check(brief, cwd="/"))

    def test_working_directory_keeps_inner_dots(self):
        dotted = self.dir / ".config"
        dotted.mkdir()
        brief = Brief(dotted)
        self.assertPasses(self.run_check(brief, cwd="/"))

    def test_relative_paths_are_skipped_without_a_working_directory(self):
        brief = Brief(self.dir)
        brief.preamble = []
        result = self.run_check(brief, cwd="/")
        self.assertFinding(result, "preamble")
        self.assertNotIn("[missing-path]", result.stdout)

    def test_step_missing_a_label(self):
        rule = self.rule(lambda r: r.steps)
        brief = Brief(self.dir)
        brief.sections[rule.name] = brief.sections[rule.name].replace(f"**{rule.labels[-1]}:**", "")
        self.assertFinding(self.run_check(brief), "step-labels")

    def test_steps_section_without_steps(self):
        rule = self.rule(lambda r: r.steps)
        brief = Brief(self.dir)
        brief.sections[rule.name] = "A plan with no steps."
        self.assertFinding(self.run_check(brief), "plan-steps")

    def test_key_file_must_exist(self):
        rule = self.rule(lambda r: r.paths_exist)
        brief = Brief(self.dir)
        brief.sections[rule.name] = "- `not-built-yet.py`: A planned file."
        self.assertFinding(self.run_check(brief), "missing-path")

    def test_key_file_needs_a_path_in_backticks(self):
        rule = self.rule(lambda r: r.paths_exist)
        brief = Brief(self.dir)
        brief.sections[rule.name] = "- key.txt: No backticks."
        self.assertFinding(self.run_check(brief), "path-format")

    def test_key_file_line_range(self):
        rule = self.rule(lambda r: r.paths_exist)
        brief = Brief(self.dir)
        brief.sections[rule.name] = "- `key.txt:2-9`: Past the end."
        self.assertFinding(self.run_check(brief), "line-range")

    def test_line_reference_anywhere_is_checked(self):
        brief = Brief(self.dir)
        brief.sections[self.plain_required().name] = "See `key.txt:9`."
        self.assertFinding(self.run_check(brief), "line-range")

    def test_planned_paths_and_non_file_values_are_ignored(self):
        brief = Brief(self.dir)
        brief.sections[self.plain_required().name] = (
            "Build `bin/not-yet`, serve on `localhost:8080` at `12:30`, see `key.txt:3`."
        )
        self.assertPasses(self.run_check(brief))

    def test_relative_paths_resolve_against_written_directory(self):
        self.assertPasses(self.run_check(Brief(self.dir), cwd="/"))

    def test_headings_inside_code_fences_are_ignored(self):
        brief = Brief(self.dir)
        name = self.plain_required().name
        brief.sections[name] = "```bash\n# a shell comment\n## not a section\n```"
        self.assertPasses(self.run_check(brief))

    def test_secret_is_flagged_without_echoing_it(self):
        secret = "sk-" + "a1B2" * 8
        brief = Brief(self.dir)
        brief.sections[self.plain_required().name] = f"Token: {secret}"
        result = self.run_check(brief)
        self.assertFinding(result, "secret")
        self.assertNotIn(secret, result.stdout)

    def test_long_brief_warns_unless_it_has_a_plan(self):
        if not self.template.max_lines:
            self.skipTest("the template sets no line target")
        long_body = "\n".join("A line." for _ in range(self.template.max_lines))
        brief = Brief(self.dir, optional=False)
        brief.sections[self.plain_required().name] = long_body
        result = self.run_check(brief)
        self.assertPasses(result)
        self.assertIn("warning [length]", result.stdout)

        self.rule(lambda r: r.steps)
        brief = Brief(self.dir)
        brief.sections[self.plain_required().name] = long_body
        result = self.run_check(brief)
        self.assertPasses(result)
        self.assertNotIn("[length]", result.stdout)

    def test_template_is_the_source_of_truth(self):
        edited = self.dir / "edited-template.md"
        edited.write_text(TEMPLATE.read_text() + "\n## Added section\nGuidance.\n")
        result = self.run_check(Brief(self.dir), "--template", str(edited))
        self.assertFinding(result, "missing-section")
        self.assertIn("Added section", result.stdout)
        self.assertPasses(self.run_check(Brief(self.dir, template=edited), "--template", str(edited)))

    def test_broken_template_exits_2(self):
        broken = self.dir / "broken-template.md"
        broken.write_text("# Handoff: <short title>\n\nNo sections here.\n")
        result = self.run_check(Brief(self.dir), "--template", str(broken))
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("template problem", result.stderr)


if __name__ == "__main__":
    unittest.main()
