"""Shared helpers for the learning-toolkit bin scripts.

Importable because a script's own bin/ directory is placed on sys.path when it
runs. Centralizes the XDG config-dir resolver (previously copied into several
tools), the living edge/lang vocabulary, and skill-name derivation.
"""

import json
import os
import tempfile
from pathlib import Path

# Seed vocabulary. These are DEFAULTS written into vocab.json on first use, not a
# frozen list: once seeded, vocab.json is the source of truth and grows via
# `learn-vocab add`. `none` is a validator sentinel, never stored here.
DEFAULT_EDGES = {"internals", "hpc", "concurrency"}
DEFAULT_LANGS = {"c", "cpp", "python", "java"}

PLUGIN_ROOT = Path(__file__).resolve().parent.parent


def config_dir() -> Path:
    """The single global toolkit directory every tool must agree on."""
    base = os.environ.get("XDG_CONFIG_HOME") or os.path.join(
        os.path.expanduser("~"), ".config")
    return Path(base) / "learning-toolkit"


def vocab_path() -> Path:
    return config_dir() / "vocab.json"


def plugin_skills() -> set:
    """Skill names under <plugin>/skills/*/. `skill` is derived, not stored."""
    skills_dir = PLUGIN_ROOT / "skills"
    if not skills_dir.is_dir():
        return set()
    return {p.name for p in skills_dir.iterdir()
            if p.is_dir() and (p / "SKILL.md").exists()}


def load_vocab() -> dict:
    """Return {"edges": set, "langs": set}, seeding vocab.json on first use."""
    path = vocab_path()
    if not path.exists():
        vocab = {"edges": set(DEFAULT_EDGES), "langs": set(DEFAULT_LANGS)}
        save_vocab(vocab)
        return vocab
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError, UnicodeDecodeError):
        # A damaged vocab file must not brick logging; fall back to seeds.
        return {"edges": set(DEFAULT_EDGES), "langs": set(DEFAULT_LANGS)}
    return {
        "edges": set(data.get("edges", [])),
        "langs": set(data.get("langs", [])),
    }


def save_vocab(vocab: dict) -> None:
    """Write vocab.json atomically (temp file + rename) with sorted lists."""
    path = vocab_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "edges": sorted(vocab.get("edges", [])),
        "langs": sorted(vocab.get("langs", [])),
    }
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
