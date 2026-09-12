import json
import os
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

BIN = Path(__file__).resolve().parent.parent / "bin"


def run(args, env):
    return subprocess.run(
        [sys.executable, str(BIN / "learn-profile"), *args],
        capture_output=True, text=True, env=env,
    )


class LearnProfileTest(unittest.TestCase):
    def setUp(self):
        self._tmp = TemporaryDirectory()
        self.env = dict(os.environ, XDG_CONFIG_HOME=self._tmp.name)
        self.cfg = Path(self._tmp.name) / "learning-toolkit"

    def tearDown(self):
        self._tmp.cleanup()

    def test_path_prints_expected_location(self):
        r = run(["path"], self.env)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.strip(),
                         str(self.cfg / "learning-profile.md"))

    def test_path_ensure_dir_creates_config_dir(self):
        self.assertFalse(self.cfg.exists())
        run(["path", "--ensure-dir"], self.env)
        self.assertTrue(self.cfg.is_dir())

    def test_show_missing_exits_nonzero_with_sentinel(self):
        r = run(["show"], self.env)
        self.assertEqual(r.returncode, 1)
        self.assertIn("NO_PROFILE", r.stderr)

    def test_show_prints_existing_profile(self):
        self.cfg.mkdir(parents=True)
        (self.cfg / "learning-profile.md").write_text("# my profile\n")
        r = run(["show"], self.env)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("# my profile", r.stdout)


EDGES = """- **`concurrency`** — scope: threads and async. Level: proficient.
  Depth: conceptual: knows the models; hands-on: little.
- **`rust-fundamentals`** — scope: learning Rust from the ground up. Level: novice.
  Depth: patient and scaffolded."""

LANGS = """- `rust` (Rust) — role: learning. Proficiency: new; reads simple code.
- `cpp` (C++) — role: analogy. Proficiency: working, as of 2026-09."""


def make_profile(edges=EDGES, langs=LANGS, drop=None):
    parts = [("Who you are teaching", "A backend developer.\n\nPronoun: they/them."),
             ("Growth edges", edges),
             ("Languages in scope", langs),
             ("Per-edge goals (optional)", "- `concurrency`: reason about races unaided."),
             ("Preferences & learning styles", "- Brief theory, one compact example, then practice.")]
    body = "\n\n".join(f"## {h}\n\n{b}" for h, b in parts if h != drop)
    return f"# Learner profile — test\n\n{body}\n"


class LearnProfileCheckTest(unittest.TestCase):
    def setUp(self):
        self._tmp = TemporaryDirectory()
        self.env = dict(os.environ, XDG_CONFIG_HOME=self._tmp.name, PYTHONDONTWRITEBYTECODE="1")
        self.cfg = Path(self._tmp.name) / "learning-toolkit"
        self.cfg.mkdir(parents=True)
        self.vocab = self.cfg / "vocab.json"
        self.vocab.write_text(json.dumps({"edges": ["concurrency", "rust-fundamentals"],
                                          "langs": ["cpp", "python", "rust"]}))

    def tearDown(self):
        self._tmp.cleanup()

    def check(self, text, *args):
        (self.cfg / "learning-profile.md").write_text(text, encoding="utf-8")
        return run(["check", *args], self.env)

    def test_new_format_profile_is_clean(self):
        r = self.check(make_profile())
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("profile ok: no warnings", r.stdout)

    def test_old_flat_list_warns_but_passes(self):
        r = self.check(make_profile(langs="rust, cpp"))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("not in the one-line format", r.stdout)
        self.assertNotIn("not in the vocabulary", r.stdout)

    def test_old_classified_bullets_map_roles(self):
        langs = "- **Primary learning:** Rust, Python (basic)\n- **Analogy/reference:** C++"
        r = self.check(make_profile(langs=langs))
        self.assertIn("not in the one-line format", r.stdout)
        self.assertIn("`python` is role: learning but no growth edge covers it", r.stdout)
        self.assertNotIn("`rust` is role: learning", r.stdout)
        self.assertNotIn("cannot map", r.stdout)

    def test_missing_section(self):
        r = self.check(make_profile(drop="Preferences & learning styles"))
        self.assertEqual(r.returncode, 0)
        self.assertIn("missing section: ## Preferences", r.stdout)

    def test_unknown_or_missing_level_and_depth(self):
        edges = ("- **`concurrency`** — scope: threads. Level: guru. Depth: terse.\n"
                 "- **`rust-fundamentals`** — scope: Rust.")
        out = self.check(make_profile(edges=edges)).stdout
        self.assertIn("edge `concurrency` has unknown level `guru`", out)
        self.assertIn("edge `rust-fundamentals` has no `Level:`", out)
        self.assertIn("edge `rust-fundamentals` has no `Depth:` note", out)

    def test_unregistered_slugs(self):
        self.vocab.write_text(json.dumps({"edges": ["concurrency"], "langs": ["cpp"]}))
        out = self.check(make_profile()).stdout
        self.assertIn("edge `rust-fundamentals` is not in the vocabulary", out)
        self.assertIn("lang `rust` is not in the vocabulary", out)

    def test_learning_language_without_coverage(self):
        langs = LANGS + "\n- `python` (Python) — role: learning. Proficiency: basic."
        out = self.check(make_profile(langs=langs)).stdout
        self.assertIn("`python` is role: learning but no growth edge covers it", out)

    def test_ordinary_word_is_not_coverage(self):
        edges = EDGES.replace("threads and async.", "threads and async, as we go through it.")
        langs = LANGS + "\n- `go` (Go) — role: learning. Proficiency: new."
        out = self.check(make_profile(edges=edges, langs=langs)).stdout
        self.assertIn("`go` is role: learning but no growth edge covers it", out)

    def test_display_name_or_backticked_slug_is_coverage(self):
        langs = LANGS + "\n- `go` (Go) — role: learning. Proficiency: new."
        for note in ("Go material is pitched at novice.", "`go` material is pitched at novice."):
            edges = EDGES.replace("hands-on: little.", f"hands-on: little. {note}")
            out = self.check(make_profile(edges=edges, langs=langs)).stdout
            self.assertNotIn("`go` is role: learning", out, note)

    def test_undated_progress_markers(self):
        undated = EDGES.replace("patient and scaffolded.", "has read only chapter 1.")
        self.assertIn("undated progress marker", self.check(make_profile(edges=undated)).stdout)
        dated = EDGES.replace("patient and scaffolded.", "as of 2026-09, read chapter 1.")
        self.assertNotIn("undated progress marker", self.check(make_profile(edges=dated)).stdout)

    def test_strict_exits_nonzero_only_with_warnings(self):
        self.assertEqual(self.check(make_profile(), "--strict").returncode, 0)
        self.assertEqual(self.check(make_profile(langs="rust"), "--strict").returncode, 1)

    def test_no_profile_exits_one_with_sentinel(self):
        r = run(["check"], self.env)
        self.assertEqual(r.returncode, 1)
        self.assertIn("NO_PROFILE", r.stderr)

    def test_read_only_and_tolerates_corrupt_vocab(self):
        self.vocab.write_text("{broken")
        text = make_profile()
        r = self.check(text)
        self.assertEqual(r.returncode, 0)
        self.assertIn("WARNING", r.stderr)
        self.assertEqual((self.cfg / "learning-profile.md").read_text(encoding="utf-8"), text)
        self.assertEqual(self.vocab.read_text(), "{broken")
        self.vocab.unlink()
        self.check(text)
        self.assertFalse(self.vocab.exists())

    def test_example_template_has_no_structural_warnings(self):
        example = (BIN.parent / "templates" / "learning-profile.example.md").read_text()
        out = self.check(example).stdout
        for fragment in ("missing section", "Level:", "Depth:", "unknown level", "no role"):
            self.assertNotIn(fragment, out)

    def test_example_template_is_clean_with_seed_vocabulary(self):
        self.vocab.unlink()
        example = (BIN.parent / "templates" / "learning-profile.example.md").read_text()
        self.assertIn("profile ok: no warnings", self.check(example).stdout)


if __name__ == "__main__":
    unittest.main()
