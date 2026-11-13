---
name: focus-block-planner
description: "Plan deep-work focus blocks from an .ics calendar export: busy times, conflicts, free slots, deadline-aware task scheduling."
version: 1.0.1
author: Saurav Sharma (sauravcodes-dotcom)
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [Calendar, Planning, Productivity, Scheduling, ICS]
    related_skills: [google-workspace, weekly-review-planning]
---

# Focus Block Planner

Turn a calendar export (`.ics`) and a to-do list into a concrete plan of focus blocks. The work is done by a small, deterministic Python script (standard library only), so times and overlaps are calculated exactly, not guessed by the model.

## When to Use

- "When am I free this week?" or "Find me two hours tomorrow afternoon."
- "Do I have any double-booked meetings?"
- "Schedule time for these tasks before their deadlines."
- A morning briefing or weekly review needs free slots or a focus plan.

Don't use it to create, move or delete calendar events: this skill only reads an export and proposes a plan. Don't use it for recurring-event expansion. Export a concrete date range instead, because `RRULE` is not expanded.

## Inputs

- An `.ics` file path, or `-` to read the calendar from stdin. Google Calendar, Outlook and Apple Calendar can all export `.ics`. If the user has no file, ask for one; never invent events.
- `--tz`: the user's IANA timezone, e.g. `America/Los_Angeles`. All output uses it.
- Optional: `--work 09:00-17:00`, `--days 5`, `--start YYYY-MM-DD`, `--min-minutes 30`, `--include-weekends`.
- For planning: one `--task "Name:minutes[:YYYY-MM-DD]"` per task. The date is a deadline (end of that day).

## Procedure

The script is `scripts/focus_planner.py` inside this skill's directory. A hub install puts that directory under `$HERMES_HOME/skills/` (default `~/.hermes/skills/`), so resolve the script path with `find` instead of guessing, and keep `$(...)` exactly as written. The script prints JSON.

```bash
FBP="$(find "${HERMES_HOME:-$HOME/.hermes}/skills" -path '*/focus-block-planner/scripts/focus_planner.py' | head -1)"; echo "$FBP"
```

Every command below starts with that lookup, so each one also works on its own in a fresh shell.

1. **Busy times and conflicts**
   ```bash
   python3 "$(find "${HERMES_HOME:-$HOME/.hermes}/skills" -path '*/focus-block-planner/scripts/focus_planner.py' | head -1)" busy --ics calendar.ics --start 2026-11-16 --days 5 --tz America/Los_Angeles
   ```
   Report `conflicts` first (pairs of overlapping events with the overlap in minutes).
2. **Free slots inside working hours**
   ```bash
   python3 "$(find "${HERMES_HOME:-$HOME/.hermes}/skills" -path '*/focus-block-planner/scripts/focus_planner.py' | head -1)" free --ics calendar.ics --start 2026-11-16 --days 5 --tz America/Los_Angeles --work 09:00-17:00 --min-minutes 45
   ```
3. **Focus plan for tasks** (earliest deadline first; long tasks split into blocks of at most `--max-block` minutes, with a `--buffer` break after each block)
   ```bash
   python3 "$(find "${HERMES_HOME:-$HOME/.hermes}/skills" -path '*/focus-block-planner/scripts/focus_planner.py' | head -1)" plan --ics calendar.ics --start 2026-11-16 --days 5 --tz America/Los_Angeles \
     --task "Write project report:150:2026-11-18" --task "Review pull requests:45" --max-block 90 --buffer 10
   ```
4. Present the result as a short list: day, time range, task. Mention every entry in `unscheduled` with its `unscheduled_minutes`, and suggest a fix, such as extending working hours, adding days, or moving the deadline.
5. If the script returns `"ok": false`, show the `error` and ask the user for the corrected input. Don't retry with guessed values.

## Pitfalls

- All-day events are reported as busy, but they don't block working hours (e.g. "Holiday" banners). Mention them.
- Events marked free (`TRANSP:TRANSPARENT`) and cancelled events are ignored.
- Floating times (no timezone in the file) are read in `--tz`.
- The plan is a proposal. Never claim it was added to the user's calendar.

## Verification

`python3 "$(dirname "$(dirname "$FBP")")/tests/test_focus_planner.py"` runs the bundled unit tests against `examples/sample_week.ics`.
