#!/usr/bin/env python3
"""focus_planner.py: find free time in an iCalendar (.ics) file and plan focus blocks for tasks.

Standard library only (Python 3.9+, uses zoneinfo). No network access and no credentials: it reads a
local .ics export, or stdin. It never writes to any calendar.

Subcommands (all print JSON to stdout):
  busy       busy intervals in the window, with overlapping events reported as conflicts
  free       free slots inside working hours, at least --min-minutes long
  plan       greedy earliest-deadline-first placement of tasks into free slots
             (tasks: "Name:minutes" or "Name:minutes:YYYY-MM-DD"; long tasks are split into
             blocks of at most --max-block minutes)

Examples:
  focus_planner.py free --ics week.ics --start 2026-11-16 --days 5 --tz America/Los_Angeles
  focus_planner.py plan --ics week.ics --start 2026-11-16 --days 5 \
      --task "Write report:120:2026-11-18" --task "Read paper:60"
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

__version__ = "1.0.1"


# ---------------------------------------------------------------- iCalendar parsing (RFC 5545 subset)
@dataclass
class Event:
    summary: str
    start: datetime  # timezone-aware
    end: datetime    # timezone-aware
    all_day: bool = False
    transparent: bool = False  # TRANSP:TRANSPARENT = does not block time


def _unfold(text: str) -> list[str]:
    """RFC 5545 §3.1: a line starting with space or tab continues the previous line."""
    lines: list[str] = []
    for raw in text.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        if raw[:1] in (" ", "\t") and lines:
            lines[-1] += raw[1:]
        else:
            lines.append(raw)
    return lines


def _parse_dt(value: str, params: dict[str, str], default_tz: ZoneInfo) -> tuple[datetime, bool]:
    """Return (aware datetime, is_all_day)."""
    if params.get("VALUE") == "DATE" or re.fullmatch(r"\d{8}", value):
        d = datetime.strptime(value, "%Y%m%d")
        return d.replace(tzinfo=default_tz), True
    if value.endswith("Z"):
        return datetime.strptime(value, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc), False
    tz = default_tz
    if "TZID" in params:
        try:
            tz = ZoneInfo(params["TZID"].strip('"'))
        except Exception:  # unknown TZID: fall back to the requested zone
            tz = default_tz
    return datetime.strptime(value, "%Y%m%dT%H%M%S").replace(tzinfo=tz), False


def _parse_duration(value: str) -> timedelta:
    m = re.fullmatch(r"([+-])?P(?:(\d+)W)?(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?)?", value)
    if not m:
        raise ValueError(f"unsupported DURATION {value!r}")
    sign, w, d, h, mi, s = m.groups()
    delta = timedelta(weeks=int(w or 0), days=int(d or 0), hours=int(h or 0), minutes=int(mi or 0),
                      seconds=int(s or 0))
    return -delta if sign == "-" else delta


def parse_ics(text: str, default_tz: ZoneInfo) -> list[Event]:
    """Parse VEVENTs. Recurring rules (RRULE) are not expanded: export a concrete date range instead."""
    events: list[Event] = []
    cur: dict | None = None
    for line in _unfold(text):
        if line == "BEGIN:VEVENT":
            cur = {}
            continue
        if line == "END:VEVENT":
            if cur is not None and "DTSTART" in cur and cur.get("STATUS") != "CANCELLED":
                start, all_day = cur["DTSTART"]
                if "DTEND" in cur:
                    end = cur["DTEND"][0]
                elif "DURATION" in cur:
                    end = start + cur["DURATION"]
                else:
                    end = start + (timedelta(days=1) if all_day else timedelta(0))
                events.append(Event(cur.get("SUMMARY", "(no title)"), start, end, all_day,
                                    cur.get("TRANSP") == "TRANSPARENT"))
            cur = None
            continue
        if cur is None or ":" not in line:
            continue
        head, value = line.split(":", 1)
        name, *raw_params = head.split(";")
        params = dict(p.split("=", 1) for p in raw_params if "=" in p)
        name = name.upper()
        if name in ("DTSTART", "DTEND"):
            cur[name] = _parse_dt(value.strip(), params, default_tz)
        elif name == "DURATION":
            cur[name] = _parse_duration(value.strip())
        elif name == "SUMMARY":
            cur[name] = value.replace("\\,", ",").replace("\\;", ";").replace("\\n", " ").strip()
        elif name in ("STATUS", "TRANSP"):
            cur[name] = value.strip().upper()
    return events


# ---------------------------------------------------------------- scheduling logic
def window(start: date, days: int, tz: ZoneInfo) -> tuple[datetime, datetime]:
    lo = datetime.combine(start, time(0), tz)
    return lo, lo + timedelta(days=days)


def busy_intervals(events: list[Event], lo: datetime, hi: datetime) -> list[Event]:
    return sorted((e for e in events if not e.transparent and e.end > lo and e.start < hi),
                  key=lambda e: (e.start, e.end))


def conflicts(events: list[Event]) -> list[dict]:
    """Pairs of timed (non all-day) busy events that overlap."""
    timed = [e for e in events if not e.all_day]
    out = []
    for i, a in enumerate(timed):
        for b in timed[i + 1:]:
            if b.start >= a.end:
                break
            overlap = min(a.end, b.end) - b.start
            out.append({"a": a.summary, "b": b.summary, "overlap_minutes": int(overlap.total_seconds() // 60),
                        "at": b.start.isoformat()})
    return out


def free_slots(events: list[Event], start: date, days: int, tz: ZoneInfo, work_start: time, work_end: time,
               min_minutes: int, weekdays_only: bool) -> list[tuple[datetime, datetime]]:
    timed = [e for e in events if not e.all_day]
    slots: list[tuple[datetime, datetime]] = []
    for i in range(days):
        day = start + timedelta(days=i)
        if weekdays_only and day.weekday() >= 5:
            continue
        cursor = datetime.combine(day, work_start, tz)
        day_end = datetime.combine(day, work_end, tz)
        for e in timed:
            s, t = max(e.start, cursor), min(e.end, day_end)
            if t <= cursor or s >= day_end:
                continue
            if s > cursor:
                slots.append((cursor, s))
            cursor = max(cursor, t)
        if day_end > cursor:
            slots.append((cursor, day_end))
    return [(a, b) for a, b in slots if (b - a) >= timedelta(minutes=min_minutes)]


@dataclass
class Task:
    name: str
    minutes: int
    deadline: date | None


def parse_task(spec: str) -> Task:
    parts = spec.rsplit(":", 2)
    if len(parts) == 3 and re.fullmatch(r"\d{4}-\d{2}-\d{2}", parts[2]):
        name, minutes, deadline = parts[0], parts[1], date.fromisoformat(parts[2])
    else:
        name, minutes = spec.rsplit(":", 1)
        deadline = None
    if not minutes.isdigit() or int(minutes) <= 0:
        raise ValueError(f"task {spec!r}: minutes must be a positive integer")
    return Task(name.strip(), int(minutes), deadline)


def plan(tasks: list[Task], slots: list[tuple[datetime, datetime]], max_block: int, buffer: int) -> dict:
    """Earliest-deadline-first; each task is split into blocks <= max_block, placed in the earliest free time
    that ends before its deadline (end of the deadline day). A buffer is kept after every block."""
    free = [list(s) for s in slots]
    order = sorted(tasks, key=lambda t: (t.deadline or date.max, -t.minutes))
    placed, unplaced = [], []
    for task in order:
        remaining = task.minutes
        blocks = []
        for slot in free:
            while remaining > 0:
                a, b = slot
                cap = int((b - a).total_seconds() // 60)
                if cap < min(15, remaining):
                    break
                size = min(remaining, max_block, cap)
                end = a + timedelta(minutes=size)
                if task.deadline and end.date() > task.deadline:
                    break
                blocks.append({"start": a.isoformat(), "end": end.isoformat(), "minutes": size})
                remaining -= size
                slot[0] = min(end + timedelta(minutes=buffer), b)
            if remaining <= 0:
                break
        entry = {"task": task.name, "requested_minutes": task.minutes,
                 "deadline": task.deadline.isoformat() if task.deadline else None, "blocks": blocks}
        (placed if remaining <= 0 else unplaced).append(
            entry if remaining <= 0 else {**entry, "unscheduled_minutes": remaining})
    return {"scheduled": placed, "unscheduled": unplaced}


# ---------------------------------------------------------------- CLI
def _hm(value: str) -> time:
    return datetime.strptime(value, "%H:%M").time()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("command", choices=["busy", "free", "plan"])
    ap.add_argument("--ics", required=True, help="path to an .ics file, or - for stdin")
    ap.add_argument("--start", default=date.today().isoformat(), help="first day YYYY-MM-DD (default today)")
    ap.add_argument("--days", type=int, default=5)
    ap.add_argument("--tz", default="UTC", help="IANA zone for output and floating times, e.g. America/Los_Angeles")
    ap.add_argument("--work", default="09:00-17:00", help="working hours HH:MM-HH:MM")
    ap.add_argument("--min-minutes", type=int, default=30)
    ap.add_argument("--include-weekends", action="store_true")
    ap.add_argument("--task", action="append", default=[], help='"Name:minutes[:YYYY-MM-DD]" (repeatable)')
    ap.add_argument("--max-block", type=int, default=90, help="longest single focus block, minutes")
    ap.add_argument("--buffer", type=int, default=10, help="break after each block, minutes")
    args = ap.parse_args(argv)

    try:
        tz = ZoneInfo(args.tz)
        text = sys.stdin.read() if args.ics == "-" else Path(args.ics).read_text(encoding="utf-8")
        start = date.fromisoformat(args.start)
        ws, we = (_hm(x) for x in args.work.split("-"))
        if not (1 <= args.days <= 31):
            raise ValueError("--days must be 1..31")
        tasks = [parse_task(t) for t in args.task]
    except Exception as exc:  # noqa: BLE001 - report input errors as JSON, not tracebacks
        print(json.dumps({"ok": False, "error": f"{type(exc).__name__}: {exc}"}))
        return 2

    lo, hi = window(start, args.days, tz)
    parsed = parse_ics(text, tz)
    for e in parsed:  # normalize every instant to the output zone (UTC "Z" and TZID times alike)
        e.start, e.end = e.start.astimezone(tz), e.end.astimezone(tz)
    events = busy_intervals(parsed, lo, hi)
    out: dict = {"ok": True, "timezone": args.tz, "window": [lo.isoformat(), hi.isoformat()]}
    if args.command == "busy":
        out["busy"] = [{"summary": e.summary, "start": e.start.astimezone(tz).isoformat(),
                        "end": e.end.astimezone(tz).isoformat(), "all_day": e.all_day} for e in events]
        out["conflicts"] = conflicts(events)
    else:
        slots = free_slots(events, start, args.days, tz, ws, we, args.min_minutes, not args.include_weekends)
        out["free_slots"] = [{"start": a.isoformat(), "end": b.isoformat(),
                              "minutes": int((b - a).total_seconds() // 60)} for a, b in slots]
        if args.command == "plan":
            if not tasks:
                print(json.dumps({"ok": False, "error": "plan needs at least one --task"}))
                return 2
            out.update(plan(tasks, slots, args.max_block, args.buffer))
            out.pop("free_slots")
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
