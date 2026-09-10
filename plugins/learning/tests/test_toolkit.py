import json
import os
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

BIN = Path(__file__).resolve().parent.parent / "bin"
sys.path.insert(0, str(BIN))

import _toolkit  # noqa: E402


class ToolkitTest(unittest.TestCase):
    def setUp(self):
        self._tmp = TemporaryDirectory()
        self._old = os.environ.get("XDG_CONFIG_HOME")
        os.environ["XDG_CONFIG_HOME"] = self._tmp.name

    def tearDown(self):
        if self._old is None:
            os.environ.pop("XDG_CONFIG_HOME", None)
        else:
            os.environ["XDG_CONFIG_HOME"] = self._old
        self._tmp.cleanup()

    def test_config_dir_honors_xdg(self):
        self.assertEqual(
            _toolkit.config_dir(),
            Path(self._tmp.name) / "learning-toolkit",
        )

    def test_load_vocab_seeds_defaults_and_writes_file(self):
        vocab = _toolkit.load_vocab()
        self.assertEqual(vocab["edges"], set(_toolkit.DEFAULT_EDGES))
        self.assertEqual(vocab["langs"], set(_toolkit.DEFAULT_LANGS))
        self.assertTrue(_toolkit.vocab_path().exists())
        data = json.loads(_toolkit.vocab_path().read_text())
        self.assertEqual(set(data["edges"]), set(_toolkit.DEFAULT_EDGES))

    def test_save_then_load_round_trips_new_value(self):
        vocab = _toolkit.load_vocab()
        vocab["langs"].add("rust")
        _toolkit.save_vocab(vocab)
        self.assertIn("rust", _toolkit.load_vocab()["langs"])

    def test_plugin_skills_finds_real_skill_dirs(self):
        skills = _toolkit.plugin_skills()
        self.assertIn("pair", skills)
        self.assertIn("flag", skills)


if __name__ == "__main__":
    unittest.main()
