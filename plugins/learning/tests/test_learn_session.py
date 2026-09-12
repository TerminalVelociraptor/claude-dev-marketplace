import json
import os
import subprocess
import sys
import time
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

BIN = Path(__file__).resolve().parent.parent / "bin"


class LearnSessionTest(unittest.TestCase):
    def setUp(self):
        self._tmp = TemporaryDirectory()
        self.env = dict(os.environ, XDG_CONFIG_HOME=self._tmp.name, PYTHONDONTWRITEBYTECODE="1")
        self.cfg = Path(self._tmp.name) / "learning-toolkit"

    def tearDown(self):
        self._tmp.cleanup()

    def session(self, *args):
        return subprocess.run([sys.executable, str(BIN / "learn-session"), *args],
                              capture_output=True, text=True, env=self.env)

    def test_start_marks_session_and_end_clears_it(self):
        r = self.session("start", "s1", "--mode", "pair")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("mode=pair", r.stdout)
        self.assertIn("re-injection off", r.stdout)
        marker = self.cfg / "sessions" / "s1.active"
        self.assertEqual(json.loads(marker.read_text())["mode"], "pair")
        self.assertIn("session ended", self.session("end", "s1").stdout)
        self.assertFalse(marker.exists())
        self.assertIn("no active session to end", self.session("end", "s1").stdout)

    def test_start_sweeps_stale_markers(self):
        stale = self.cfg / "sessions" / "old.active"
        stale.parent.mkdir(parents=True)
        stale.write_text("{}")
        t = time.time() - 25 * 3600
        os.utime(stale, (t, t))
        self.session("start", "s1", "--mode", "guided")
        self.assertFalse(stale.exists())

    def test_status_lists_every_config_file(self):
        self.session("start", "s1")
        out = self.session("status").stdout
        for name in ("learning-log.jsonl", "config.json", "vocab.json", "learning-profile.md"):
            self.assertIn(name, out)
        self.assertNotIn("compilers.json", out)
        self.assertIn("sessions    1 active", out)

    def test_config_round_trip_and_validation(self):
        self.assertEqual(self.session("config", "reinject", "on").returncode, 0)
        self.assertTrue(json.loads((self.cfg / "config.json").read_text())["reinject"])
        self.assertEqual(self.session("config", "reinject").stdout.strip(), "True")
        self.assertEqual(self.session("config", "nope", "on").returncode, 2)
        self.assertEqual(self.session("config", "reinject", "maybe").returncode, 2)


if __name__ == "__main__":
    unittest.main()
