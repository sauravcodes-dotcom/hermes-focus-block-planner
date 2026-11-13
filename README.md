# focus-block-planner: a Hermes Agent skill

Plan deep-work focus blocks from a calendar export. Given an `.ics` file and a list of tasks, the skill:
- reports busy times and **double-booked meetings**
- finds **free slots** inside your working hours
- schedules tasks into those slots **earliest deadline first**, splitting long tasks into blocks with breaks between them

The calculation is done by a deterministic, standard-library Python script (`scripts/focus_planner.py`), so times and overlaps are exact rather than estimated by the model. It reads a local file only: no network, no credentials, and no calendar writes.

Written for **Atlas**, a CSCI 599 (USC, Fall 2026) personal-assistant project built on [Hermes Agent](https://github.com/NousResearch/hermes-agent). Tested with Hermes Agent v0.22.7.

## Install (Hermes skill tap)

This repository is a Hermes **skill tap**: skills live under `skills/<name>/SKILL.md`.

```bash
hermes skills tap add sauravcodes-dotcom/hermes-focus-block-planner
hermes skills search focus-block-planner
hermes skills install sauravcodes-dotcom/hermes-focus-block-planner/skills/focus-block-planner
hermes skills list | grep focus-block-planner
```

To pin a version, check out the tagged release (`v1.0.1`). The install transcript in `docs/INSTALL_TRANSCRIPT.md` records the exact commit that was tested.

## Use

Ask your agent, for example:
- "Here is my calendar export at ~/Downloads/week.ics. When am I free for 2 hours this week?"
- "Any double-booked meetings in that calendar?"
- "Plan focus time for 'Write report, 150 min, due Wednesday' and 'Review PRs, 45 min'."

Or run the script directly:

```bash
S=skills/focus-block-planner
python3 $S/scripts/focus_planner.py busy --ics $S/examples/sample_week.ics --start 2026-11-16 --days 5 --tz America/Los_Angeles
python3 $S/scripts/focus_planner.py free --ics $S/examples/sample_week.ics --start 2026-11-16 --days 5 --tz America/Los_Angeles --min-minutes 45
python3 $S/scripts/focus_planner.py plan --ics $S/examples/sample_week.ics --start 2026-11-16 --days 5 --tz America/Los_Angeles \
  --task "Write report:150:2026-11-18" --task "Review pull requests:45"
```

Options:
- `--work HH:MM-HH:MM` sets working hours (default 09:00-17:00).
- `--include-weekends` also plans Saturday and Sunday.
- `--max-block N` sets the longest single focus block in minutes (default 90).
- `--buffer N` sets the break after each block in minutes (default 10).

Output is JSON. Invalid input returns `{"ok": false, "error": "..."}` with exit code 2.

## Supported iCalendar features

| Feature | Supported |
|---|---|
| `DTSTART`/`DTEND` with `TZID`, UTC `Z` times, floating times | ✅ (floating times use `--tz`) |
| `DURATION` | ✅ |
| All-day events (`VALUE=DATE`) | ✅ reported as busy; they don't block working hours |
| Line folding | ✅ |
| `STATUS:CANCELLED`, `TRANSP:TRANSPARENT` | ✅ ignored |
| `RRULE` recurrence | ❌ export a concrete date range instead |

## Tests

```bash
python3 skills/focus-block-planner/tests/test_focus_planner.py
```

These are 8 unit tests against the synthetic `examples/sample_week.ics`. It contains a TZID event, a UTC event, a folded line, `DURATION`, a cancelled event, a transparent event and an all-day event.

## License

MIT. See `LICENSE`.
