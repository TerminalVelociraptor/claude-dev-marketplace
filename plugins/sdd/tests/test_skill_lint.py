"""Static checks on skill and shared prompt text: references resolve, used tools are pre-approved,
skills are user-invoked only, generators name a real document, and nothing restates sdd.md's
locations or Whys."""

import importlib.util
import re
import sys
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = sorted((ROOT / "skills").glob("*/SKILL.md"))
SHARED = sorted((ROOT / "shared").glob("*.md"))
# Files that must point to sdd.md rather than restate it.
POINTING_FILES = SKILLS + SHARED + [p for p in [ROOT / "README.md"] if p.exists()]

ROOT_REF_RE = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/([\w./-]*\w)")
SHARED_REF_RE = re.compile(r"\bshared/[\w.-]*\w")
BIN_RE = re.compile(r"\bbin/([\w-]+)")
DOCUMENT_RE = re.compile(r"^Document: `([^`]+)`$", re.MULTILINE)
WHY_RE = re.compile(r"^\s*\*Why[^*]*:\*\s*(.+)$", re.MULTILINE)
LOCATION_RE = re.compile(r"`([^`]+\.md)`")


def split_frontmatter(text: str):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    fields = {}
    for line in m.group(1).splitlines():
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip()
    return fields, text[m.end():]


def load_sdd_check():
    sys.dont_write_bytecode = True
    loader = SourceFileLoader("sdd_check", str(ROOT / "bin" / "sdd-check"))
    spec = importlib.util.spec_from_loader("sdd_check", loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


SDD_CHECK = load_sdd_check()
SDD_TEXT = (ROOT / "sdd.md").read_text()
ENTRIES = SDD_CHECK.parse_entries(SDD_TEXT)


def entry_patterns_as_written():
    """Each entry's location as sdd.md writes it, e.g. `docs/components/<name>.md`."""
    wanted = {entry.pattern for entry in ENTRIES.values() if entry.pattern}
    return sorted({span for span in LOCATION_RE.findall(SDD_TEXT)
                   if SDD_CHECK.PLACEHOLDER_RE.sub("*", span) in wanted})


class SkillLintTest(unittest.TestCase):
    def test_referenced_files_exist(self):
        for path in SKILLS:
            text = path.read_text()
            refs = set(ROOT_REF_RE.findall(text)) | set(SHARED_REF_RE.findall(text))
            for ref in refs:
                self.assertTrue((ROOT / ref).exists(), f"{path.parent.name}: {ref}")

    def test_bin_tools_are_pre_approved(self):
        for path in SKILLS:
            fields, body = split_frontmatter(path.read_text())
            allowed = fields.get("allowed-tools", "")
            for tool in set(BIN_RE.findall(body)):
                self.assertIn(f"Bash(${{CLAUDE_PLUGIN_ROOT}}/bin/{tool} *)", allowed,
                              f"{path.parent.name}: {tool}")

    def test_skills_are_user_invoked_only(self):
        self.assertGreater(len(SKILLS), 0)
        for path in SKILLS:
            fields, _ = split_frontmatter(path.read_text())
            self.assertEqual(fields.get("disable-model-invocation"), "true", path.parent.name)

    def test_generators_name_a_document_entry(self):
        generators = 0
        for path in SKILLS:
            text = path.read_text()
            if "shared/generate.md" not in text:
                continue
            generators += 1
            documents = DOCUMENT_RE.findall(text)
            self.assertEqual(len(documents), 1, f"{path.parent.name}: no Document line")
            # parse_entries drops a trailing "(...)" from the heading, so do the same here.
            name = re.sub(r"\s+\([^)]*\)$", "", documents[0]).casefold()
            self.assertTrue(name in ENTRIES, f"{path.parent.name}: {documents[0]}")
            self.assertFalse(ENTRIES[name].derived, f"{path.parent.name}: {documents[0]}")
        self.assertGreater(generators, 0)

    def test_locations_are_not_restated(self):
        patterns = entry_patterns_as_written()
        self.assertIn("docs/components/<name>.md", patterns)
        for path in POINTING_FILES:
            text = path.read_text()
            for pattern in patterns:
                self.assertFalse(pattern in text, f"{path.relative_to(ROOT)} restates {pattern}")

    def test_whys_are_not_restated(self):
        whys = [why[:40] for why in WHY_RE.findall(SDD_TEXT)]
        self.assertGreater(len(whys), 0)
        for path in POINTING_FILES:
            text = path.read_text()
            for why in whys:
                self.assertFalse(why in text, f"{path.relative_to(ROOT)} restates Why {why!r}")


if __name__ == "__main__":
    unittest.main()
