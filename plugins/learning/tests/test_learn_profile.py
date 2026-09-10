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


if __name__ == "__main__":
    unittest.main()
