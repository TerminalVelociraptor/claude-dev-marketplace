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


if __name__ == "__main__":
    unittest.main()
