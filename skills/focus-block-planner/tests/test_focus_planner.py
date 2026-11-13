#!/usr/bin/env python3
"""Unit tests for focus_planner.py (stdlib unittest; run: python3 tests/test_focus_planner.py)."""
import io
import json
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
import focus_planner as fp  # noqa: E402

SAMPLE = str(HERE.parent / "examples" / "sample_week.ics")
BASE = ["--ics", SAMPLE, "--start", "2026-11-16", "--days", "5", "--tz", "America/Los_Angeles"]


def run(*args):
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = fp.main(list(args))
    return code, json.loads(buf.getvalue())


class ParseTests(unittest.TestCase):
    def test_parses_tzid_utc_duration_folding_and_filters(self):
        code, out = run("busy", *BASE)
        self.assertEqual(code, 0)
        names = [b["summary"] for b in out["busy"]]
        self.assertIn("Lab sync (overlaps advisor meeting)", names)          # folded line joined
        self.assertNotIn("Cancelled coffee chat", names)                     # STATUS:CANCELLED dropped
        self.assertNotIn("Office hours (free/transparent)", names)           # TRANSP:TRANSPARENT dropped
        lab = next(b for b in out["busy"] if b["summary"].startswith("Lab sync"))
        self.assertEqual(lab["start"], "2026-11-16T13:30:00-08:00")          # UTC converted to PST
        lecture = next(b for b in out["busy"] if b["summary"] == "Lecture")
        self.assertEqual(lecture["end"], "2026-11-17T11:50:00-08:00")        # DURATION applied
        holiday = next(b for b in out["busy"] if b["all_day"])
        self.assertEqual(holiday["summary"], "Campus holiday banner")

    def test_conflict_detected_with_overlap_minutes(self):
        _, out = run("busy", *BASE)
        self.assertEqual(len(out["conflicts"]), 1)
        c = out["conflicts"][0]
        self.assertEqual({c["a"], c["b"]}, {"Advisor meeting", "Lab sync (overlaps advisor meeting)"})
        self.assertEqual(c["overlap_minutes"], 30)


class FreeSlotTests(unittest.TestCase):
    def test_monday_free_slots(self):
        _, out = run("free", *BASE)
        monday = [(s["start"][11:16], s["end"][11:16]) for s in out["free_slots"] if s["start"].startswith("2026-11-16")]
        self.assertEqual(monday, [("09:00", "09:30"), ("10:00", "13:00"), ("14:30", "17:00")])

    def test_all_day_event_does_not_block_working_hours(self):
        _, out = run("free", *BASE)
        wed = [s for s in out["free_slots"] if s["start"].startswith("2026-11-18")]
        self.assertEqual(wed[0]["minutes"], 480)

    def test_min_minutes_filter_and_weekends_skipped(self):
        _, out = run("free", *BASE, "--min-minutes", "60")
        self.assertFalse(any(s["minutes"] < 60 for s in out["free_slots"]))
        _, out = run("free", "--ics", SAMPLE, "--start", "2026-11-21", "--days", "2", "--tz", "America/Los_Angeles")
        self.assertEqual(out["free_slots"], [])                              # Sat + Sun


class PlanTests(unittest.TestCase):
    def test_deadline_first_split_and_buffer(self):
        _, out = run("plan", *BASE, "--task", "Report:150:2026-11-16", "--task", "Reading:60",
                     "--max-block", "90", "--buffer", "10")
        sched = {t["task"]: t for t in out["scheduled"]}
        report = sched["Report"]["blocks"]
        self.assertEqual(sum(b["minutes"] for b in report), 150)
        self.assertTrue(all(b["minutes"] <= 90 for b in report))
        self.assertTrue(all(b["start"].startswith("2026-11-16") for b in report))  # before its deadline
        self.assertEqual(report[0]["start"][11:16], "09:00")
        self.assertEqual(out["unscheduled"], [])

    def test_unplaceable_task_reported(self):
        _, out = run("plan", *BASE, "--task", "Huge:5000:2026-11-16")
        self.assertEqual(out["scheduled"], [])
        self.assertGreater(out["unscheduled"][0]["unscheduled_minutes"], 0)

    def test_bad_input_is_json_error(self):
        code, out = run("plan", *BASE, "--task", "NoMinutes:abc")
        self.assertEqual(code, 2)
        self.assertFalse(out["ok"])
        code, out = run("busy", "--ics", "/nonexistent.ics")
        self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
