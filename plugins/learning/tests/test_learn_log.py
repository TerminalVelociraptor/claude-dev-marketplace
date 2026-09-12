import importlib.util
import io
import json
import os
import subprocess
import sys
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

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


class LearnLogWriteTest(unittest.TestCase):
    def setUp(self):
        self._tmp = TemporaryDirectory()
        self.env = dict(os.environ, XDG_CONFIG_HOME=self._tmp.name, PYTHONDONTWRITEBYTECODE="1")
        self.cfg = Path(self._tmp.name) / "learning-toolkit"

    def tearDown(self):
        self._tmp.cleanup()

    def log(self, *args):
        return run("learn-log", [*args, "--project", "proj"], self.env)

    def test_append_writes_jsonl_and_marks_new_concept(self):
        first = self.log("--type", "to-cover", "--concept", "false-sharing", "--edge", "hpc")
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertIn("logged to-cover/false-sharing  [new concept]", first.stdout)
        second = self.log("--type", "hit", "--concept", "false-sharing", "--edge", "hpc")
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertNotIn("[new concept]", second.stdout)
        lines = (self.cfg / "learning-log.jsonl").read_text(encoding="utf-8").splitlines()
        entries = [json.loads(line) for line in lines]
        self.assertEqual([e["type"] for e in entries], ["to-cover", "hit"])
        self.assertEqual({e["project"] for e in entries}, {"proj"})

    def test_signal_required_for_signal_bearing_types(self):
        for type_ in ("calibration", "self-assessment"):
            r = self.log("--type", type_, "--concept", "x", "--dry-run")
            self.assertEqual(r.returncode, 2, type_)
            self.assertIn("--signal is required", r.stderr)
        ok = self.log("--type", "calibration", "--concept", "x", "--signal", "above-level",
                      "--dry-run")
        self.assertEqual(ok.returncode, 0, ok.stderr)

    def test_help_signals_works_alone(self):
        r = run("learn-log", ["--help-signals"], self.env)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("above-level", r.stdout)

    def test_type_and_concept_still_required(self):
        r = run("learn-log", ["--concept", "x", "--dry-run"], self.env)
        self.assertEqual(r.returncode, 2)
        self.assertIn("--type", r.stderr)

    def test_note_when_concept_moves_to_a_new_edge(self):
        self.log("--type", "to-cover", "--concept", "x", "--edge", "hpc")
        moved = self.log("--type", "hit", "--concept", "x", "--edge", "concurrency")
        self.assertEqual(moved.returncode, 0, moved.stderr)
        self.assertIn("note: first time x is logged under edge concurrency", moved.stdout)
        again = self.log("--type", "hit", "--concept", "x", "--edge", "hpc")
        self.assertNotIn("note:", again.stdout)

    def test_corrupt_vocab_warns_but_does_not_block_logging(self):
        self.cfg.mkdir(parents=True)
        vocab = self.cfg / "vocab.json"
        vocab.write_text("{not json", encoding="utf-8")
        r = self.log("--type", "taught", "--concept", "x", "--edge", "hpc", "--dry-run")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("WARNING", r.stderr)
        self.assertIn(str(vocab), r.stderr)
        self.assertEqual(vocab.read_text(encoding="utf-8"), "{not json")


def load_learn_log():
    sys.dont_write_bytecode = True
    if str(BIN) not in sys.path:
        sys.path.insert(0, str(BIN))
    loader = SourceFileLoader("learn_log", str(BIN / "learn-log"))
    spec = importlib.util.spec_from_loader("learn_log", loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


class LearnLogShortWriteTest(unittest.TestCase):
    def test_short_write_is_closed_off_and_reported(self):
        module = load_learn_log()
        real_write = os.write
        attempts = []

        def short_write(fd, data):
            attempts.append(bytes(data))
            return real_write(fd, data[:10] if len(attempts) == 1 else data)

        argv = ["learn-log", "--type", "taught", "--concept", "x", "--project", "proj"]
        err = io.StringIO()
        with TemporaryDirectory() as tmp, \
                mock.patch.dict(os.environ, {"XDG_CONFIG_HOME": tmp}), \
                mock.patch.object(sys, "argv", argv), \
                mock.patch.object(sys, "stderr", err), \
                mock.patch.object(module.os, "write", short_write):
            with self.assertRaises(SystemExit) as cm:
                module.main()
            log = (Path(tmp) / "learning-toolkit" / "learning-log.jsonl").read_bytes()
        self.assertEqual(cm.exception.code, 2)
        self.assertEqual(log, attempts[0][:10] + b"\n")
        self.assertIn("NOT logged", err.getvalue())


if __name__ == "__main__":
    unittest.main()
