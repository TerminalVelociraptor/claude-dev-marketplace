"""Shared helpers for the learning-toolkit bin scripts.

Importable because a script's own bin/ directory is placed on sys.path when it
runs. Centralizes the XDG config-dir resolver (previously copied into several
tools), the living edge/lang vocabulary, and skill-name derivation.
"""

import json
import os
import sys
import tempfile
from pathlib import Path

# Seed vocabulary. These are DEFAULTS written into vocab.json on first use, not a
# frozen list: once seeded, vocab.json is the source of truth and grows via
# `learn-vocab add`. `none` is a validator sentinel, never stored here.
DEFAULT_EDGES = {"internals", "hpc", "concurrency"}
DEFAULT_LANGS = {"c", "cpp", "python", "java"}

PLUGIN_ROOT = Path(__file__).resolve().parent.parent

# A session marker older than this belongs to a session that ended without cleanup (crash,
# closed terminal). learn-session sweeps such markers; the re-injection hook ignores them.
SESSION_STALE_SECONDS = 24 * 3600


class VocabError(Exception):
    """vocab.json exists but cannot be used; the message names the file and the reason."""


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


def _seeds() -> dict:
    return {"edges": set(DEFAULT_EDGES), "langs": set(DEFAULT_LANGS)}


def _read_vocab_file(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise VocabError(f"{path} is not valid JSON ({exc})") from None
    except OSError as exc:
        raise VocabError(f"{path} could not be read ({exc})") from None
    if not isinstance(data, dict):
        raise VocabError(f"{path} must hold a JSON object with 'edges' and 'langs' lists")
    vocab = {}
    for key in ("edges", "langs"):
        values = data.get(key, [])
        if not isinstance(values, list) or not all(isinstance(v, str) for v in values):
            raise VocabError(f"{path}: '{key}' must be a list of strings")
        vocab[key] = set(values)
    return vocab


def load_vocab(strict: bool = False, seed: bool = True) -> dict:
    """Return {"edges": set, "langs": set}.

    A missing vocab.json is seeded with the defaults (written to disk unless seed=False).
    A malformed one is never rewritten automatically, because it may hold the only copy of
    the user's custom values: with strict=True it raises VocabError so mutations refuse;
    otherwise it warns loudly on stderr and falls back to the seeds so logging is not blocked.
    """
    path = vocab_path()
    if not path.exists():
        vocab = _seeds()
        if seed:
            save_vocab(vocab)
        return vocab
    try:
        return _read_vocab_file(path)
    except VocabError as exc:
        if strict:
            raise
        print(f"learning-toolkit: WARNING: {exc}.\n"
              f"  Using the seed vocabulary for now; the file was not changed.\n"
              f"  Fix it, or move it aside to start a fresh one.", file=sys.stderr)
        return _seeds()


def save_vocab(vocab: dict) -> None:
    """Write vocab.json atomically (temp file + rename) with sorted lists.

    Refuses (VocabError) to replace an existing malformed file rather than clobber it.
    """
    path = vocab_path()
    if path.exists():
        _read_vocab_file(path)
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
