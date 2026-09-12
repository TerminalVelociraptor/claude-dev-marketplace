import os
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

BIN = Path(__file__).resolve().parent.parent / "bin"


class LearnBaselineTest(unittest.TestCase):
    def setUp(self):
        self._tmp = TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        gitconfig = self.root / "gitconfig"
        gitconfig.write_text("", encoding="utf-8")
        ident = {"GIT_AUTHOR_NAME": "Test", "GIT_AUTHOR_EMAIL": "test@example.com",
                 "GIT_COMMITTER_NAME": "Test", "GIT_COMMITTER_EMAIL": "test@example.com"}
        # Isolate from the user's git config and from any repository above the temp dir.
        self.env = dict(os.environ, **ident, PYTHONDONTWRITEBYTECODE="1",
                        GIT_CONFIG_GLOBAL=str(gitconfig), GIT_CONFIG_NOSYSTEM="1",
                        GIT_CEILING_DIRECTORIES=str(self.root))

    def tearDown(self):
        self._tmp.cleanup()

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.repo, env=self.env, check=True,
                              capture_output=True, text=True).stdout.strip()

    def commit(self, message):
        (self.repo / "f.txt").write_text(message, encoding="utf-8")
        self.git("add", "f.txt")
        self.git("commit", "-q", "-m", message)

    def baseline(self, *args, cwd=None):
        return subprocess.run([sys.executable, str(BIN / "learn-baseline"), *args],
                              cwd=cwd or self.repo, env=self.env, capture_output=True, text=True)

    def test_outside_a_repository(self):
        elsewhere = self.root / "not-a-repo"
        elsewhere.mkdir()
        r = self.baseline("set", cwd=elsewhere)
        self.assertEqual(r.returncode, 2)
        self.assertIn("not inside a git repository", r.stderr)

    def test_repository_without_commits(self):
        self.git("init", "-q")
        r = self.baseline("set")
        self.assertEqual(r.returncode, 2)
        self.assertIn("no commits yet", r.stderr)

    def test_set_commits_advance_clear(self):
        self.git("init", "-q")
        self.commit("one")
        first = self.git("rev-parse", "HEAD")

        r = self.baseline("set")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn(first[:12], r.stdout)
        self.assertIn("no commits since the last check-in", self.baseline("commits").stdout)

        self.commit("two")
        self.commit("three")
        subjects = [line.split("\t")[-1] for line in self.baseline("commits").stdout.splitlines()]
        self.assertEqual(subjects, ["two", "three"])  # oldest first

        self.assertIn("baseline advanced", self.baseline("advance").stdout)
        self.assertEqual(self.baseline("get").stdout.strip(), self.git("rev-parse", "HEAD"))
        self.assertIn("no commits since the last check-in", self.baseline("commits").stdout)
        self.assertEqual(self.git("status", "--porcelain"), "")  # state lives inside .git/

        self.assertIn("baseline cleared", self.baseline("clear").stdout)
        self.assertFalse((self.repo / ".git" / "learning-baseline").exists())
        self.assertEqual(self.baseline("get").returncode, 1)
        self.assertIn("no baseline to clear", self.baseline("clear").stdout)


if __name__ == "__main__":
    unittest.main()
