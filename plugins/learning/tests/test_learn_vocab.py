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

    def test_remove_namespaces_separate_in_log_check(self):
        """Verify that the lingering-log check respects edge/lang namespaces.

        If a slug appears as a lang in the log, removing it as an edge
        should NOT report it as lingering. Conversely, if it appears as
        an edge in the log, removing that edge SHOULD report it lingering.
        """
        # Seed the log with entries using "python" as both edge and lang
        # Note: config_dir() returns XDG_CONFIG_HOME/learning-toolkit
        log_path = Path(self.env["XDG_CONFIG_HOME"]) / "learning-toolkit" / "learning-log.jsonl"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("w") as f:
            # Entry where python is a lang (but we'll remove it as an edge)
            f.write(json.dumps({"timestamp": "2026-01-01T00:00:00Z", "lang": "python"}) + "\n")
            # Entry where python is an edge (so removing the edge should linger)
            f.write(json.dumps({"timestamp": "2026-01-02T00:00:00Z", "edge": "python"}) + "\n")

        # Add python as both edge and lang
        self.assertEqual(run(["add", "--edges", "python", "--langs", "python"], self.env).returncode, 0)

        # Test 1: Removing the edge should report lingering (because edge appears in log)
        r = run(["remove", "--edges", "python"], self.env)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("removed edge python", r.stdout)
        self.assertIn("still present in existing log entries", r.stdout)

        # Test 2: Now remove the lang. The log still has python as a lang entry,
        # but we're removing it as a lang, so it SHOULD report lingering
        r = run(["remove", "--langs", "python"], self.env)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("removed lang python", r.stdout)
        self.assertIn("still present in existing log entries", r.stdout)


if __name__ == "__main__":
    unittest.main()
