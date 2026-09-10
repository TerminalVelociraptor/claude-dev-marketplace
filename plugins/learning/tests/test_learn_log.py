import os
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

BIN = Path(__file__).resolve().parent.parent / "bin"


def run(script, args, env):
    return subprocess.run(
        [sys.executable, str(BIN / script), *args],
        capture_output=True, text=True, env=env,
    )


class LearnLogVocabTest(unittest.TestCase):
    def setUp(self):
        self._tmp = TemporaryDirectory()
        self.env = dict(os.environ, XDG_CONFIG_HOME=self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_default_lang_still_accepted(self):
        r = run("learn-log",
                ["--type", "taught", "--concept", "ownership",
                 "--lang", "cpp", "--edge", "hpc", "--skill", "pair", "--dry-run"],
                self.env)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_unknown_lang_rejected_with_vocab_hint(self):
        r = run("learn-log",
                ["--type", "taught", "--concept", "ownership",
                 "--lang", "rust", "--skill", "pair", "--dry-run"],
                self.env)
        self.assertEqual(r.returncode, 2)
        self.assertIn("learn-vocab add --langs rust", r.stderr)

    def test_lang_accepted_after_vocab_add(self):
        add = run("learn-vocab", ["add", "--langs", "rust"], self.env)
        self.assertEqual(add.returncode, 0, add.stderr)
        r = run("learn-log",
                ["--type", "taught", "--concept", "ownership",
                 "--lang", "rust", "--skill", "pair", "--dry-run"],
                self.env)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_skill_derived_from_directory(self):
        ok = run("learn-log",
                 ["--type", "taught", "--concept", "x", "--skill", "pair", "--dry-run"],
                 self.env)
        self.assertEqual(ok.returncode, 0, ok.stderr)
        bad = run("learn-log",
                  ["--type", "taught", "--concept", "x", "--skill", "nope", "--dry-run"],
                  self.env)
        self.assertEqual(bad.returncode, 2)


if __name__ == "__main__":
    unittest.main()
