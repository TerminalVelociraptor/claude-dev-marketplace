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
