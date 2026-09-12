"""Static checks on skill and shared prompt text: references resolve, documented commands are
pre-approved and complete, required shared blocks are present, and removed tools stay removed."""

import importlib.util
import re
import sys
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = sorted((ROOT / "skills").glob("*/SKILL.md"))
PROMPT_FILES = SKILLS + sorted((ROOT / "shared").glob("*.md"))

ALLOWED_TOOL_RE = re.compile(r"Bash\(\$\{CLAUDE_SKILL_DIR\}/\.\./\.\./bin/([\w-]+) \*\)")
# A learn-log invocation: flags up to the end of the line or inline-code span, following `\`
# line continuations.
LEARN_LOG_RE = re.compile(r"learn-log[ \t]+(--(?:[^\n`\\]|\\\n)*)")
# Phrases in the generic verification rule that legitimately contain the removed tools' words.
ALLOWED_PHRASES = ("drill it in", "cargo bench")
REMOVED_RE = re.compile(r"\bdrill\b|\bbench\b|BenchHarness|compilers\.json", re.IGNORECASE)


def split_frontmatter(text: str):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    fields = {}
    for line in m.group(1).splitlines():
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip()
    return fields, text[m.end():]


def load_sync_shared():
    sys.dont_write_bytecode = True
    loader = SourceFileLoader("sync_shared", str(ROOT / "bin" / "sync-shared"))
    spec = importlib.util.spec_from_loader("sync_shared", loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


class SkillLintTest(unittest.TestCase):
    def test_referenced_shared_and_template_files_exist(self):
        for path in PROMPT_FILES:
            for ref in re.findall(r"\b(?:shared|templates)/[\w.-]*\w", path.read_text()):
                self.assertTrue((ROOT / ref).exists(), f"{path.relative_to(ROOT)} -> {ref}")

    def test_bin_commands_are_pre_approved(self):
        for path in SKILLS:
            fields, body = split_frontmatter(path.read_text())
            body = re.sub(r"<!--.*?-->", "", body, flags=re.DOTALL)  # splice markers name bin/sync-shared
            allowed = set(ALLOWED_TOOL_RE.findall(fields.get("allowed-tools", "")))
            used = set(re.findall(r"\bbin/([\w-]+)", body))
            for tool in used | allowed:
                self.assertTrue((ROOT / "bin" / tool).exists(), f"{path.parent.name}: {tool}")
            self.assertEqual(used - allowed, set(), f"{path.parent.name} lacks allowed-tools")

    def test_learn_log_examples_name_type_and_concept(self):
        found = 0
        for path in PROMPT_FILES:
            for m in LEARN_LOG_RE.finditer(path.read_text()):
                found += 1
                for flag in ("--type", "--concept"):
                    self.assertIn(flag, m.group(1), f"{path.relative_to(ROOT)}: {m.group(0)!r}")
        self.assertGreater(found, 0)

    def test_required_shared_blocks_present(self):
        required = load_sync_shared().REQUIRED
        self.assertEqual(set(required), {"pair", "guided"})
        for skill, names in required.items():
            text = (ROOT / "skills" / skill / "SKILL.md").read_text()
            for name in names:
                self.assertIn(f"<!-- BEGIN shared:{name} ", text, skill)
                self.assertIn(f"<!-- END shared:{name} -->", text, skill)

    def test_no_references_to_removed_tools(self):
        files = PROMPT_FILES + sorted((ROOT / "hooks").iterdir())
        for path in files:
            text = path.read_text()
            for phrase in ALLOWED_PHRASES:
                text = text.replace(phrase, "")
            hits = sorted({m.group(0) for m in REMOVED_RE.finditer(text)})
            self.assertEqual(hits, [], str(path.relative_to(ROOT)))


if __name__ == "__main__":
    unittest.main()
