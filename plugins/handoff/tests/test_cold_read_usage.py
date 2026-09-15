"""Tests for bin/cold-read-usage."""

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

SCRIPT = Path(__file__).resolve().parent.parent / "bin" / "cold-read-usage"


def usage(input_tokens, cache_write, cache_read, output):
    return {
        "input_tokens": input_tokens,
        "cache_creation_input_tokens": cache_write,
        "cache_read_input_tokens": cache_read,
        "output_tokens": output,
        "cache_creation": {"ephemeral_5m_input_tokens": cache_write, "ephemeral_1h_input_tokens": 0},
    }


def entry(timestamp, message=None):
    line = {"timestamp": timestamp, "agentId": "abc123", "type": "assistant" if message else "user"}
    if message:
        line["message"] = message
    return line


def assistant(message_id, model, counts):
    return {"id": message_id, "model": model, "usage": counts}


# Modeled on a real cold read: two requests, 2m17s. msg_1 appears twice, first with partial usage
# from streaming; only its last line counts. The synthetic message is not a real request.
TRANSCRIPT = [
    entry("2026-09-15T00:31:29.000Z"),
    entry("2026-09-15T00:31:40.000Z", assistant("msg_1", "claude-sonnet-5", usage(2, 0, 0, 0))),
    entry("2026-09-15T00:31:41.000Z", assistant("msg_1", "claude-sonnet-5", usage(2, 36380, 0, 2))),
    entry("2026-09-15T00:33:40.000Z", assistant("msg_2", "claude-sonnet-5", usage(2, 10754, 36380, 12051))),
    entry("2026-09-15T00:33:41.000Z", assistant("msg_3", "<synthetic>", usage(0, 0, 0, 999))),
    entry("2026-09-15T00:33:46.000Z"),
]


class ColdReadUsageTest(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.log = self.dir / "usage.jsonl"
        self.brief = self.dir / "brief.md"
        self.brief.write_text("line\n" * 300)

    def tearDown(self):
        self.tmp.cleanup()

    def write_transcript(self, path, lines=TRANSCRIPT):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(json.dumps(line) for line in lines) + "\n")
        return path

    def run_script(self, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *map(str, args), "--log", str(self.log)],
            capture_output=True, text=True, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )

    def record(self, *source):
        return self.run_script(*source, "--brief", self.brief, "--filled", 2, "--undecided", 1)

    def logged(self):
        return [json.loads(line) for line in self.log.read_text().splitlines()]

    def test_script_is_executable(self):
        self.assertTrue(os.access(SCRIPT, os.X_OK))

    def test_records_deduplicated_usage(self):
        transcript = self.write_transcript(self.dir / "agent-abc123.jsonl")
        result = self.record(transcript)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Cold read: 2 gaps filled, 1 added as undecided.", result.stdout)
        self.assertIn("95.6k tokens over 2 requests", result.stdout)
        self.assertIn("47.1k cache write, 36.4k cache read, 12.1k output, 4 uncached input", result.stdout)
        self.assertIn("claude-sonnet-5, 2m17s.", result.stdout)

        [record] = self.logged()
        expected = {
            "input": 4, "cache_write": 47134, "cache_write_5m": 47134, "cache_write_1h": 0,
            "cache_read": 36380, "output": 12053, "total": 95571, "requests": 2,
            "model": "claude-sonnet-5", "duration_s": 137.0, "agent_id": "abc123",
            "brief_lines": 300, "gaps_filled": 2, "gaps_undecided": 1, "error": None,
        }
        self.assertEqual({key: record[key] for key in expected}, expected)

    def test_each_run_appends_a_record(self):
        transcript = self.write_transcript(self.dir / "agent-abc123.jsonl")
        self.record(transcript)
        self.record(transcript)
        self.assertEqual(len(self.logged()), 2)

    def test_finds_transcript_by_agent_id(self):
        projects = self.dir / "projects"
        self.write_transcript(projects / "-proj" / "session" / "subagents" / "agent-abc123.jsonl")
        result = self.record("--agent-id", "abc123", "--projects-dir", projects)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("95.6k tokens", result.stdout)

    def test_falls_back_to_agent_id_when_path_is_missing(self):
        projects = self.dir / "projects"
        self.write_transcript(projects / "-proj" / "session" / "subagents" / "agent-abc123.jsonl")
        result = self.record(self.dir / "gone.jsonl", "--agent-id", "abc123", "--projects-dir", projects)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_missing_transcript_still_reports_and_logs(self):
        result = self.record(self.dir / "gone.jsonl")
        self.assertEqual(result.returncode, 1)
        self.assertIn("Cold read: 2 gaps filled, 1 added as undecided. Usage unavailable", result.stdout)
        [record] = self.logged()
        self.assertIn("transcript not found", record["error"])

    def test_transcript_without_usage_is_unavailable(self):
        transcript = self.write_transcript(self.dir / "agent-abc123.jsonl", [TRANSCRIPT[0]])
        result = self.record(transcript)
        self.assertEqual(result.returncode, 1)
        self.assertIn("no usage in transcript", result.stdout)

    def test_recording_requires_brief_and_counts(self):
        transcript = self.write_transcript(self.dir / "agent-abc123.jsonl")
        result = self.run_script(transcript)
        self.assertEqual(result.returncode, 2)
        self.assertIn("--brief", result.stderr)

    def test_summary(self):
        self.assertIn("No cold reads logged yet", self.run_script("--summary").stdout)
        transcript = self.write_transcript(self.dir / "agent-abc123.jsonl")
        self.record(transcript)
        self.record(self.dir / "gone.jsonl")
        result = self.run_script("--summary")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("2 cold read(s) logged", result.stdout)
        self.assertIn("1 without usage", result.stdout)
        self.assertRegex(result.stdout, r"total\s+95\.6k\s+95\.6k")
        self.assertRegex(result.stdout, r"duration_s\s+2m17s\s+2m17s")


if __name__ == "__main__":
    unittest.main()
