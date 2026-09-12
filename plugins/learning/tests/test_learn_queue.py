import json
import os
import subprocess
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

BIN = Path(__file__).resolve().parent.parent / "bin"

# One reference instant for every synthetic timestamp. Offsets below keep >= 6h away from any
# scheduling boundary (1/7/30-day spacing, the 14-day signal window) so the second or two between
# building the log and running the subprocess can never flip a result.
NOW = datetime.now(timezone.utc)


def ago(days: float) -> str:
    return (NOW - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")


def ev(type_, concept, days_ago, edge="none", lang="none", **extra):
    e = {"ts": ago(days_ago), "type": type_, "concept": concept, "edge": edge, "lang": lang,
         "project": "proj", "skill": "none"}
    e.update(extra)
    return e


def graduated(concept, first_days_ago, edge="none"):
    """Three successes spaced 2 and 13 days apart: graduates, last counted 13 days after the first."""
    return [ev("hit", concept, first_days_ago, edge),
            ev("hit", concept, first_days_ago - 2, edge),
            ev("hit", concept, first_days_ago - 15, edge)]


class QueueTestBase(unittest.TestCase):
    def setUp(self):
        self._tmp = TemporaryDirectory()
        self.env = dict(os.environ, XDG_CONFIG_HOME=self._tmp.name, PYTHONDONTWRITEBYTECODE="1")
        self.log = Path(self._tmp.name) / "learning-toolkit" / "learning-log.jsonl"

    def tearDown(self):
        self._tmp.cleanup()

    def write_log(self, events):
        self.log.parent.mkdir(parents=True, exist_ok=True)
        self.log.write_text("".join(json.dumps(e) + "\n" for e in events), encoding="utf-8")

    def queue(self, *args):
        return subprocess.run([sys.executable, str(BIN / "learn-queue"), *args],
                              capture_output=True, text=True, env=self.env)

    def rows(self, *args):
        r = self.queue(*args, "--json")
        self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads(r.stdout)

    def row(self, concept, *args):
        return {r["concept"]: r for r in self.rows(*args)}[concept]

    def concepts(self, *args):
        return [r["concept"] for r in self.rows(*args)]


class CurrentBehaviorTest(QueueTestBase):
    """Pins scheduling behavior that was already correct before the 0.5.0 changes."""

    def test_success_within_a_day_does_not_advance(self):
        self.write_log([ev("hit", "x", 3), ev("hit", "x", 2.9)])
        self.assertEqual(self.row("x")["stage"], 1)

    def test_spaced_successes_graduate_at_three(self):
        self.write_log([ev("hit", "two", 10), ev("hit", "two", 8)] + graduated("three", 40))
        two, three = self.row("two"), self.row("three")
        self.assertEqual((two["stage"], two["graduated"]), (2, False))
        self.assertEqual((three["stage"], three["graduated"]), (3, True))

    def test_miss_resets_and_counts_reactivation(self):
        self.write_log(graduated("x", 40) + [ev("miss", "x", 10)])
        r = self.row("x")
        self.assertEqual((r["stage"], r["graduated"], r["reactivations"]), (0, False, 1))

    def test_two_misses_make_next_easier(self):
        self.write_log([ev("hit", "x", 5), ev("miss", "x", 4), ev("miss", "x", 3)])
        self.assertEqual(self.row("x")["difficulty"], "easier")

    def test_one_hit_makes_next_harder(self):
        self.write_log([ev("hit", "x", 5)])
        self.assertEqual(self.row("x")["difficulty"], "harder")

    def test_pick_spreads_across_edges(self):
        self.write_log([ev("to-cover", "a1", 5, "a"), ev("to-cover", "a2", 5, "a"),
                        ev("to-cover", "a3", 5, "a"), ev("to-cover", "b1", 5, "b"),
                        ev("to-cover", "c1", 5, "c")])
        self.assertEqual({r["edge"] for r in self.rows("--pick", "3")}, {"a", "b", "c"})

    def test_pick_clamps_to_interleave_bounds(self):
        self.write_log([ev("to-cover", f"k{i}", 5, f"e{i}") for i in range(6)])
        self.assertEqual(len(self.rows("--pick", "1")), 2)
        self.assertEqual(len(self.rows("--pick", "9")), 4)


class MaintenanceTest(QueueTestBase):
    def test_due_maintenance_listed_after_active_due_and_labeled(self):
        self.write_log(graduated("m", 60) + graduated("g", 40) + [ev("to-cover", "x", 1)])
        self.assertEqual(self.concepts("--due"), ["x", "m"])
        self.assertTrue(self.row("m", "--due")["maint_due"])
        text = self.queue("--due").stdout
        m_line = next(line for line in text.splitlines() if line.startswith("m "))
        self.assertIn("maint", m_line)

    def test_maintenance_hit_schedules_next_check(self):
        self.write_log(graduated("m", 60) + [ev("hit", "m", 10)])
        self.assertNotIn("m", self.concepts("--due"))
        r = self.row("m")
        self.assertTrue(r["graduated"])
        self.assertFalse(r["maint_due"])

    def test_maintenance_miss_reactivates(self):
        self.write_log(graduated("m", 60) + [ev("miss", "m", 10)])
        r = self.row("m")
        self.assertEqual((r["graduated"], r["reactivations"], r["is_due"]), (False, 1, True))
        self.assertIn("m", self.concepts("--due"))

    def test_pick_adds_at_most_one_maintenance_after_active(self):
        self.write_log(graduated("m1", 60) + graduated("m2", 70) + [ev("to-cover", "x", 1)])
        picked = self.rows("--pick", "4")
        self.assertEqual(len(picked), 2)
        self.assertEqual(picked[0]["concept"], "x")
        self.assertTrue(picked[1]["maint_due"])

    def test_pick_leaves_maintenance_out_when_active_fills_it(self):
        self.write_log(graduated("m", 60, "e")
                       + [ev("to-cover", f"k{i}", 1, edge) for i, edge in enumerate("abcd")])
        self.assertNotIn("m", [r["concept"] for r in self.rows("--pick", "4")])

    def test_pick_practises_ahead_when_only_maintenance_is_due(self):
        self.write_log(graduated("m", 60, "c")
                       + [ev("hit", "a", 0.5, "a"), ev("hit", "b", 0.5, "b")])
        picked = self.rows("--pick", "4")
        self.assertEqual([r["concept"] for r in picked], ["m", "a", "b"])
        self.assertTrue(picked[0]["maint_due"])

    def test_due_does_not_narrow_pick(self):
        self.write_log([ev("hit", "a", 0.5, "a"), ev("hit", "b", 0.5, "b")])
        self.assertEqual(self.concepts("--due"), [])
        self.assertEqual(self.concepts("--due", "--pick", "2"), ["a", "b"])
        self.assertEqual(self.concepts("--due", "--pick", "2"), self.concepts("--pick", "2"))


class EligibilityTest(QueueTestBase):
    def test_only_queued_or_scored_concepts_are_due_or_picked(self):
        self.write_log([
            ev("calibration", "cal", 3, signal="already-known"),
            ev("skipped", "skip", 3), ev("taught", "tau", 3), ev("escape", "esc", 3),
            ev("to-cover", "q", 3), ev("hit", "h", 3),
        ])
        self.assertEqual(set(self.concepts("--due")), {"q", "h"})
        self.assertEqual(set(self.concepts("--pick", "4")), {"q", "h"})
        self.assertEqual(len(self.rows()), 6)
        self.assertFalse(self.row("cal")["eligible"])

    def test_pick_does_not_fall_back_to_ineligible(self):
        self.write_log([ev("calibration", "cal", 3, signal="already-known")])
        self.assertEqual(self.rows("--pick", "2"), [])
        self.assertIn("no concepts match the filter", self.queue("--pick", "2").stdout)


class DifficultyTest(QueueTestBase):
    def test_escapes_without_outcomes_make_next_easier(self):
        self.write_log([ev("to-cover", "x", 5), ev("escape", "x", 4), ev("escape", "x", 3)])
        self.assertEqual(self.row("x")["difficulty"], "easier")

    def test_two_escapes_override_a_perfect_hit_rate(self):
        self.write_log([ev("hit", "x", 5), ev("escape", "x", 4), ev("escape", "x", 3)])
        self.assertEqual(self.row("x")["difficulty"], "easier")

    def test_single_escape_does_not_ease(self):
        self.write_log([ev("escape", "x", 5), ev("hit", "x", 4)])
        self.assertEqual(self.row("x")["difficulty"], "harder")


class FilterTest(QueueTestBase):
    def setUp(self):
        super().setUp()
        self.write_log([
            ev("to-cover", "multi", 5, "a", "rust"), ev("hit", "multi", 4, "a", "rust"),
            ev("taught", "multi", 3, "b", "python"),
            ev("to-cover", "tie", 5, "a"), ev("taught", "tie", 4, "b"),
            ev("to-cover", "keep", 5, "a"), ev("taught", "keep", 1, "none"),
        ])

    def test_attribution_uses_every_edge_seen(self):
        multi = self.row("multi")
        self.assertEqual((multi["edge"], multi["edges"]), ("a", ["a", "b"]))
        self.assertEqual(multi["langs"], ["python", "rust"])
        self.assertEqual(self.row("tie")["edge"], "b")  # tie goes to the latest
        keep = self.row("keep")
        self.assertEqual((keep["edge"], keep["edges"]), ("a", ["a"]))  # `none` never displaces

    def test_edge_filter_matches_any_seen_edge(self):
        self.assertIn("multi", self.concepts("--edge", "b"))
        self.assertIn("multi", self.concepts("--edge", "x,b"))
        self.assertIn("multi", self.concepts("--edge", "x", "--edge", "b"))
        self.assertEqual(self.rows("--edge", "x"), [])
        self.assertIn("no concepts match the filter", self.queue("--edge", "x").stdout)

    def test_lang_filter_applies_before_due(self):
        self.assertEqual(self.concepts("--lang", "python", "--due"), ["multi"])
        self.assertIn("no concepts match the filter", self.queue("--lang", "go", "--due").stdout)

    def test_stats_respects_filters(self):
        self.write_log([ev("hit", "ha", 3, "a"), ev("miss", "mb", 3, "b")])
        glob = json.loads(self.queue("--stats", "--json").stdout)
        only_a = json.loads(self.queue("--stats", "--edge", "a", "--json").stdout)
        self.assertEqual(glob["outcomes"], 2)
        self.assertEqual((only_a["outcomes"], only_a["success_rate"]), (1, 1.0))
        self.assertEqual(set(only_a["per_edge"]), {"a"})
        self.assertIn("maintenance_due", only_a)

    def test_stats_outcomes_are_scoped_to_the_filter(self):
        self.write_log([ev("hit", "x", 3, "a", "rust"), ev("miss", "x", 2, "b", "python"),
                        ev("escape", "x", 1, "a", "rust")])
        by_edge = json.loads(self.queue("--stats", "--edge", "b", "--json").stdout)
        self.assertEqual((by_edge["outcomes"], by_edge["success_rate"], by_edge["escapes"]),
                         (1, 0.0, 0))
        self.assertEqual(by_edge["per_edge"], {"b": {"hits": 0, "misses": 1, "success_rate": 0.0}})
        by_lang = json.loads(self.queue("--stats", "--lang", "rust", "--json").stdout)
        self.assertEqual((by_lang["outcomes"], by_lang["success_rate"], by_lang["escapes"]),
                         (1, 1.0, 1))

    def test_empty_log_message_differs_from_filtered(self):
        self.log.unlink()
        self.assertIn("nothing logged yet", self.queue("--edge", "a").stdout)


class SignalsTest(QueueTestBase):
    def signals(self, *args):
        r = self.queue("--signals", *args)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout

    def test_repeated_already_known_suggests_higher_baseline(self):
        self.write_log([ev("calibration", "c1", 3, "a", signal="already-known"),
                        ev("calibration", "c2", 2, "a", signal="below-level")])
        self.assertIn("a: baseline may be higher", self.signals())

    def test_single_signal_or_old_signal_crosses_nothing(self):
        self.write_log([ev("calibration", "c1", 20, "a", signal="already-known"),
                        ev("calibration", "c2", 2, "a", signal="already-known")])
        out = self.signals()
        self.assertNotIn("baseline may be higher", out)
        self.assertIn("no calibration thresholds crossed", out)
        self.assertIn("baseline may be higher", self.signals("--days", "30"))

    def test_above_level_or_escapes_mean_pitched_too_high(self):
        self.write_log([ev("calibration", "c1", 3, "a", signal="above-level"),
                        ev("calibration", "c2", 2, "a", signal="above-level"),
                        ev("escape", "e1", 3, "b"), ev("escape", "e2", 2, "b"),
                        ev("escape", "e3", 1, "b"),
                        ev("escape", "e4", 3, "c"), ev("escape", "e5", 2, "c")])
        out = self.signals()
        self.assertIn("a: pitched too high", out)
        self.assertIn("b: pitched too high", out)
        self.assertNotIn("c:", out)

    def test_clean_hits_across_concepts_suggest_raising(self):
        self.write_log([ev("hit", "h1", 3, "a"), ev("hit", "h2", 2, "a"), ev("hit", "h1", 1, "a"),
                        ev("hit", "s1", 3, "b"), ev("hit", "s1", 2, "b"), ev("hit", "s1", 1, "b"),
                        ev("hit", "m1", 3, "c"), ev("hit", "m2", 2, "c"), ev("hit", "m1", 1.5, "c"),
                        ev("miss", "m2", 1, "c")])
        out = self.signals()
        self.assertIn("a: consider raising level", out)
        self.assertNotIn("b:", out)  # one concept only
        self.assertNotIn("c:", out)  # a miss in the window

    def test_filters_all_and_none_edge(self):
        self.write_log([ev("escape", f"e{i}", 2, edge) for i, edge in enumerate("aaabbb")]
                       + [ev("escape", f"n{i}", 2, "none") for i in range(3)]
                       + [ev("hit", "lone", 2, "d")])
        only_b = self.signals("--edge", "b")
        self.assertIn("b: pitched too high", only_b)
        self.assertNotIn("a:", only_b)
        self.assertNotIn("none", self.signals())
        self.assertIn("d", self.signals("--all"))

    def test_signals_are_read_only(self):
        self.write_log([ev("hit", "h1", 3, "a")])
        before = self.log.read_bytes()
        self.signals("--all")
        self.assertEqual(self.log.read_bytes(), before)


class TableTest(QueueTestBase):
    def test_columns_widen_to_fit_values(self):
        long_concept = "a-concept-name-well-past-the-old-thirty-two-char-column"
        self.write_log([ev("to-cover", long_concept, 1, "a-very-long-edge-name")])
        head, _, row = self.queue().stdout.splitlines()[:3]
        self.assertTrue(row.startswith(long_concept + " "))
        self.assertEqual(head.index("edge"), row.index("a-very-long-edge-name"))


if __name__ == "__main__":
    unittest.main()
