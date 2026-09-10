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
        [sys.executable, str(BIN / "learn-vocab"), *args],
        capture_output=True, text=True, env=env,
    )


class LearnVocabTest(unittest.TestCase):
    def setUp(self):
        self._tmp = TemporaryDirectory()
        self.env = dict(os.environ, XDG_CONFIG_HOME=self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_list_edges_seeds_and_prints_defaults(self):
        r = run(["list", "--edges"], self.env)
        self.assertEqual(r.returncode, 0, r.stderr)
        lines = set(r.stdout.split())
        self.assertEqual(lines, {"internals", "hpc", "concurrency"})

    def test_add_lang_then_it_appears(self):
        self.assertEqual(run(["add", "--langs", "rust"], self.env).returncode, 0)
        r = run(["list", "--langs"], self.env)
        self.assertIn("rust", r.stdout.split())

    def test_add_rejects_non_kebab(self):
        r = run(["add", "--edges", "Bad Edge"], self.env)
        self.assertEqual(r.returncode, 2)
        self.assertIn("kebab-case", r.stderr)

    def test_add_rejects_reserved_none(self):
        r = run(["add", "--edges", "none"], self.env)
        self.assertEqual(r.returncode, 2)
        self.assertIn("reserved", r.stderr)

    def test_remove_reports_not_present(self):
        r = run(["remove", "--edges", "ghost"], self.env)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("was not present", r.stdout)

    def test_remove_namespace_negative_lang_only(self):
        """NEGATIVE: If a slug appears ONLY as a lang in the log, removing it as
        an edge should NOT report lingering. This proves the namespace fix — the
        old buggy flatten code would wrongly report it as lingering.
        """
        # Seed log with "rust" appearing ONLY as a lang, never as an edge
        log_path = Path(self.env["XDG_CONFIG_HOME"]) / "learning-toolkit" / "learning-log.jsonl"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("w") as f:
            f.write(json.dumps({"type": "taught", "concept": "x", "lang": "rust", "edge": "none"}) + "\n")

        # Add rust as an edge (not a lang, to keep it isolated)
        self.assertEqual(run(["add", "--edges", "rust"], self.env).returncode, 0)

        # Remove rust as an edge. It does NOT appear as an edge in the log,
        # only as a lang, so the "still present" note should NOT fire.
        # (The buggy flatten code would fire it anyway.)
        r = run(["remove", "--edges", "rust"], self.env)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("removed edge rust", r.stdout)
        self.assertNotIn("still present in existing log entries", r.stdout)

    def test_remove_namespace_positive_edge_in_log(self):
        """POSITIVE: If a slug appears as an edge in the log, removing it as an
        edge SHOULD report lingering. Sanity check that the namespace-aware code
        still detects genuine lingering.
        """
        # Seed log with "hpc" appearing as an edge
        log_path = Path(self.env["XDG_CONFIG_HOME"]) / "learning-toolkit" / "learning-log.jsonl"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("w") as f:
            f.write(json.dumps({"type": "taught", "concept": "y", "edge": "hpc", "lang": "none"}) + "\n")

        # Add hpc as an edge
        self.assertEqual(run(["add", "--edges", "hpc"], self.env).returncode, 0)

        # Remove hpc as an edge. It appears as an edge in the log,
        # so the "still present" note SHOULD fire.
        r = run(["remove", "--edges", "hpc"], self.env)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("removed edge hpc", r.stdout)
        self.assertIn("still present in existing log entries", r.stdout)
        self.assertIn("hpc", r.stdout)


if __name__ == "__main__":
    unittest.main()
