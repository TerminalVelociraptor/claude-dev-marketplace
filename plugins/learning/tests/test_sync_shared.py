import os
import shutil
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parent.parent


def run(root, *args):
    return subprocess.run([sys.executable, str(root / "bin" / "sync-shared"), *args],
                          capture_output=True, text=True,
                          env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))


class SyncSharedTest(unittest.TestCase):
    def setUp(self):
        self._tmp = TemporaryDirectory()
        self.copy = Path(self._tmp.name) / "plugin"
        (self.copy / "bin").mkdir(parents=True)
        shutil.copy2(ROOT / "bin" / "sync-shared", self.copy / "bin" / "sync-shared")
        shutil.copytree(ROOT / "shared", self.copy / "shared")
        shutil.copytree(ROOT / "skills", self.copy / "skills")

    def tearDown(self):
        self._tmp.cleanup()

    def test_check_is_clean_on_the_real_tree(self):
        r = run(ROOT, "--check")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_check_is_clean_on_an_untouched_copy(self):
        r = run(self.copy, "--check")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_check_fails_when_a_required_block_is_removed(self):
        skill = self.copy / "skills" / "guided" / "SKILL.md"
        text = skill.read_text(encoding="utf-8")
        start = text.index("<!-- BEGIN shared:teaching-protocol")
        end_marker = "<!-- END shared:teaching-protocol -->"
        end = text.index(end_marker) + len(end_marker)
        skill.write_text(text[:start] + text[end:], encoding="utf-8")
        for args in (["--check"], []):
            r = run(self.copy, *args)
            self.assertEqual(r.returncode, 1, args)
            self.assertIn("skills/guided/SKILL.md: missing shared:teaching-protocol block", r.stdout)

    def test_check_fails_when_a_required_skill_is_missing(self):
        shutil.rmtree(self.copy / "skills" / "pair")
        r = run(self.copy, "--check")
        self.assertEqual(r.returncode, 1)
        self.assertIn("skills/pair/SKILL.md: required skill is missing", r.stdout)

    def test_drift_is_reported_then_fixed(self):
        core = self.copy / "shared" / "calibration-core.md"
        core.write_text(core.read_text(encoding="utf-8") + "\nextra line\n", encoding="utf-8")
        self.assertEqual(run(self.copy, "--check").returncode, 1)
        self.assertEqual(run(self.copy).returncode, 0)
        self.assertEqual(run(self.copy, "--check").returncode, 0)


if __name__ == "__main__":
    unittest.main()
