import json
import os
import re
import subprocess
import sys
import time
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

HOOK = Path(__file__).resolve().parent.parent / "hooks" / "reinject.py"


class ReinjectHookTest(unittest.TestCase):
    def setUp(self):
        self._tmp = TemporaryDirectory()
        self.env = dict(os.environ, XDG_CONFIG_HOME=self._tmp.name, PYTHONDONTWRITEBYTECODE="1")
        self.cfg = Path(self._tmp.name) / "learning-toolkit"
        (self.cfg / "sessions").mkdir(parents=True)

    def tearDown(self):
        self._tmp.cleanup()

    def hook(self, stdin=json.dumps({"session_id": "s1"})):
        r = subprocess.run([sys.executable, str(HOOK)], input=stdin,
                           capture_output=True, text=True, env=self.env)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout

    def mark(self, age_hours=0.0):
        marker = self.cfg / "sessions" / "s1.active"
        marker.write_text(json.dumps({"mode": "pair"}), encoding="utf-8")
        t = time.time() - age_hours * 3600
        os.utime(marker, (t, t))

    def reinject(self, value):
        (self.cfg / "config.json").write_text(json.dumps({"reinject": value}), encoding="utf-8")

    def test_silent_without_marker(self):
        self.reinject(True)
        self.assertEqual(self.hook(), "")

    def test_silent_when_marker_but_disabled_or_unconfigured(self):
        self.mark()
        self.assertEqual(self.hook(), "")
        self.reinject(False)
        self.assertEqual(self.hook(), "")

    def test_emits_when_marker_and_enabled(self):
        self.mark()
        self.reinject(True)
        self.assertIn("<learning-session-active>", self.hook())

    def test_bad_stdin_exits_zero_silently(self):
        self.mark()
        self.reinject(True)
        for stdin in ("not json", "", "[]", json.dumps({"other": 1})):
            self.assertEqual(self.hook(stdin), "", stdin)

    def test_stale_marker_is_silent_and_left_in_place(self):
        self.mark(age_hours=25)
        self.reinject(True)
        self.assertEqual(self.hook(), "")
        self.assertTrue((self.cfg / "sessions" / "s1.active").exists())

    def test_reminder_is_generic(self):
        self.mark()
        self.reinject(True)
        out = self.hook()
        self.assertIn("growth edge in the loaded profile", out)
        for word in ("hpc", "internals", "him", "his", "he", "bench"):
            self.assertIsNone(re.search(rf"\b{word}\b", out, re.IGNORECASE), word)

    def test_docstring_names_the_real_enable_command(self):
        self.assertIn("learn-session config reinject on", HOOK.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
