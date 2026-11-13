# Fresh-install transcript: focus-block-planner v1.0.1

Captured by a script on 2026-11-13 (UTC) with a brand-new `HOME` and `~/.hermes`: no prior configuration, skills, logins or GitHub token. Paths under that sandbox home are shown as `~`. Nothing else is edited out.

- Skill commit under test: `f2a34b38b678e29d4f905069361e5cfa8fc6f785` (tag `v1.0.1`).
- Hermes Agent: v0.22.7 (`b200f5bc60e3`).

```text
# Fresh-install transcript: focus-block-planner via Hermes skill tap
# date -u: 2026-11-13T20:14:52Z
# host: macOS 26.5 arm64; brand-new HOME and HERMES_HOME (~/.hermes), no prior config, skills, auth or GitHub token

$ curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --commit b200f5bc60e31588ba2cb60e288029c4a54ba5fa --non-interactive --skip-browser --skip-computer-use
✓ prerequisites ok (git, curl)
✓ Hermes Agent cloned
✓ uv ready (uv 0.13.5 (46776a95d 2026-10-21 aarch64-apple-darwin))
✓ bootstrap Python ready; PM prepares the dependency environment
✓ uv ready (uv 0.13.5 (46776a95d 2026-10-21 aarch64-apple-darwin))
  ✓ Installing Python dependencies
✓ ffmpeg
✓ node
✓ npm
✓ python
✓ ripgrep
  ✓ Installing Python dependencies
✓ venv
✓ dependencies installed
✓ config prepared in ~/.hermes
✓ uv ready (uv 0.13.5 (46776a95d 2026-10-21 aarch64-apple-darwin))
  ✓ Installing Python dependencies
  ✓ Preparing Node dependencies
  ✓ Building the TUI
  ✓ Building the web UI
  ✓ Model catalog cache refreshed from checkout
  ✓ Configuration is up to date
✓ Install complete! [detached @ b200f5bc60]
✓ added ~/.local/bin to PATH in ~/.zshrc
✓ added ~/.local/bin to PATH in ~/.zprofile
✓ app products and hermes command ready
✓ Hermes Agent install complete. Run: hermes

$ hermes --version
Hermes Agent v0.22.7 (2026.9.24) · stable · local b200f5bc60e3
Install directory: ~/.hermes/hermes-agent
Install method: git
Python: 3.14.9
OpenAI SDK: 2.54.0
Update available — run 'hermes update'

$ hermes skills list --source hub
              Installed Skills               
┏━━━━━━┳━━━━━━━━━━┳━━━━━━━━┳━━━━━━━┳━━━━━━━━┓
┃ Name ┃ Category ┃ Source ┃ Trust ┃ Status ┃
┡━━━━━━╇━━━━━━━━━━╇━━━━━━━━╇━━━━━━━╇━━━━━━━━┩
└──────┴──────────┴────────┴───────┴────────┘
0 hub-installed, 0 builtin, 0 local — 0 enabled, 0 disabled


$ hermes skills tap add sauravcodes-dotcom/hermes-focus-block-planner
Added tap: sauravcodes-dotcom/hermes-focus-block-planner


$ hermes skills tap list
                      Configured Taps                      
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┓
┃ Repo                                          ┃ Path    ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━┩
│ sauravcodes-dotcom/hermes-focus-block-planner │ skills/ │
└───────────────────────────────────────────────┴─────────┘


$ hermes skills search focus-block-planner

Searching for: focus-block-planner
No skills found matching your query.


$ hermes skills inspect sauravcodes-dotcom/hermes-focus-block-planner/skills/focus-block-planner

╭───────────────────────── Skill: focus-block-planner ─────────────────────────╮
│ Name: focus-block-planner                                                    │
│ Description: Plan deep-work focus blocks from an .ics calendar export: busy  │
│ times, conflicts, free slots, deadline-aware task scheduling.                │
│ Source: skills.sh                                                            │
│ Trust: community                                                             │
│ Identifier:                                                                  │
│ skills-sh/sauravcodes-dotcom/hermes-focus-block-planner/skills/focus-block-p │
│ lanner                                                                       │
│ Tags: Calendar, Planning, Productivity, Scheduling, ICS                      │
│ Repo: https://github.com/sauravcodes-dotcom/hermes-focus-block-planner       │
│ Detail Page:                                                                 │
│ https://skills.sh/sauravcodes-dotcom/hermes-focus-block-planner/skills/focus │
│ -block-planner                                                               │
╰──────────────────────────────────────────────────────────────────────────────╯
╭────────────────────────────── SKILL.md Preview ──────────────────────────────╮
│ ---                                                                          │
│ name: focus-block-planner                                                    │
│ description: "Plan deep-work focus blocks from an .ics calendar export: busy │
│ times, conflicts, free slots, deadline-aware task scheduling."               │
│ version: 1.0.1                                                               │
│ author: Saurav Sharma (sauravcodes-dotcom)                                   │
│ license: MIT                                                                 │
│ platforms:                                                                   │
│ metadata:                                                                    │
│   hermes:                                                                    │
│     tags: [Calendar, Planning, Productivity, Scheduling, ICS]                │
│     related_skills:                                                          │
│ ---                                                                          │
│                                                                              │
│ # Focus Block Planner                                                        │
│                                                                              │
│ Turn a calendar export (`.ics`) and a to-do list into a concrete plan of     │
│ focus blocks. The work is done by a small, deterministic Python script       │
│ (standard library only), so times and overlaps are calculated exactly, not   │
│ guessed by the model.                                                        │
│                                                                              │
│ ## When to Use                                                               │
│                                                                              │
│ - "When am I free this week?" or "Find me two hours tomorrow afternoon."     │
│ - "Do I have any double-booked meetings?"                                    │
│ - "Schedule time for these tasks before their deadlines."                    │
│ - A morning briefing or weekly review needs free slots or a focus plan.      │
│                                                                              │
│ Don't use it to create, move or delete calendar events: this skill only      │
│ reads an export and proposes a plan. Don't use it for recurring-event        │
│ expansion. Export a concrete date range instead, because `RRULE` is not      │
│ expanded.                                                                    │
│                                                                              │
│ ## Inputs                                                                    │
│                                                                              │
│ - An `.ics` file path, or `-` to read the calendar from stdin. Google        │
│ Calendar, Outlook and Apple Calendar can all export `.ics`. If the user has  │
│ no file, ask for one; never invent events.                                   │
│ - `--tz`: the user's IANA timezone, e.g. `America/Los_Angeles`. All output   │
│ uses it.                                                                     │
│ - Optional: `--work 09:00-17:00`, `--days 5`, `--start YYYY-MM-DD`,          │
│ `--min-minutes 30`, `--include-weekends`.                                    │
│ - For planning: one `--task "Name:minutes[:YYYY-MM-DD]"` per task. The date  │
│ is a deadline (end of that day).                                             │
│                                                                              │
│ ## Procedure                                                                 │
│                                                                              │
│ The script is `scripts/focus_planner.py` inside this skill's directory. A    │
│ hub install puts that directory under `$HERMES_HOME/skills/` (default        │
│ `~/.hermes/skills/`), so resolve the script path with `find` instead of      │
│ guessing, and keep `$(...)` exactly as written. The script prints JSON.      │
│                                                                              │
│ ```bash                                                                      │
│ FBP="$(find "${HERMES_HOME:-$HOME/.hermes}/skills" -path                     │
│ '*/focus-block-planner/scripts/focus_planner.py' | head -1)"; echo "$FBP"    │
│ ```                                                                          │
│                                                                              │
│ Every command below starts with that lookup, so each one also works on its   │
│ own in a fresh shell.                                                        │
│                                                                              │
│ 1. **Busy times and conflicts**                                              │
│    ```bash                                                                   │
│    python3 "$(find "${HERMES_HOME:-$HOME/.hermes}/skills" -path              │
│ '*/focus-block-planner/scripts/focus_planner.py' | head -1)" busy --ics      │
│ calendar.ics --start 2026-11-16 --days 5 --tz America/Los_Angeles            │
│    ```                                                                       │
│    Report `conflicts` first (pairs of overlapping events with the overlap in │
│ minutes).                                                                    │
│ 2. **Free slots inside working hours**                                       │
│    ```bash                                                                   │
│                                                                              │
│ ... (21 more lines)                                                          │
╰─────────────────── hermes skills install <id> to install ────────────────────╯


$ hermes skills install sauravcodes-dotcom/hermes-focus-block-planner/skills/focus-block-planner --yes

Fetching: 
sauravcodes-dotcom/hermes-focus-block-planner/skills/focus-block-planner
Quarantined to .hub/quarantine/focus-block-planner
Running security scan...
Scan: focus-block-planner 
(skills-sh/sauravcodes-dotcom/hermes-focus-block-planner/skills/focus-block-plan
ner/community)  Verdict: SAFE
  MEDIUM   execution      SKILL.md:36                    "The script is 
`scripts/focus_planner.py` inside this skill's"
  MEDIUM   execution      SKILL.md:70                    "`python3 "$(dirname 
"$(dirname "$FBP")")/tests/test_focus_pl"

Decision: ALLOWED — Allowed (community source, safe verdict)
Scan provenance: fresh; scanner skills-guard-v10; hash 
sha256:cdc8e9a8ba6d53d0202139fdabb01f12c35f9a920f1406201c6a79e85c008bc2
Source: 
https://github.com/sauravcodes-dotcom/hermes-focus-block-planner/tree/f2a34b38b6
78e29d4f905069361e5cfa8fc6f785/skills/focus-block-planner; scanned 
2026-11-13T20:17:14.694111+00:00; rules: backtick_subshell
╭───────────────────────────── Upstream Metadata ──────────────────────────────╮
│ Repo: https://github.com/sauravcodes-dotcom/hermes-focus-block-planner       │
│ Detail Page:                                                                 │
│ https://skills.sh/sauravcodes-dotcom/hermes-focus-block-planner/skills/focus │
│ -block-planner                                                               │
╰──────────────────────────────────────────────────────────────────────────────╯
Installed: focus-block-planner
Files: SKILL.md, examples/sample_week.ics, scripts/focus_planner.py, 
tests/test_focus_planner.py


$ hermes skills list --source hub
                          Installed Skills                          
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━┓
┃ Name                ┃ Category ┃ Source    ┃ Trust     ┃ Status  ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━┩
│ focus-block-planner │          │ skills.sh │ community │ enabled │
└─────────────────────┴──────────┴───────────┴───────────┴─────────┘
1 hub-installed, 0 builtin, 0 local — 1 enabled, 0 disabled


$ find ~/.hermes/skills -path '*/focus-block-planner/*' -type f | sort
~/.hermes/skills/focus-block-planner/SKILL.md
~/.hermes/skills/focus-block-planner/examples/sample_week.ics
~/.hermes/skills/focus-block-planner/scripts/focus_planner.py
~/.hermes/skills/focus-block-planner/tests/test_focus_planner.py

$ python3 ~/.hermes/skills/focus-block-planner/tests/test_focus_planner.py
test_all_day_event_does_not_block_working_hours (__main__.FreeSlotTests.test_all_day_event_does_not_block_working_hours) ... ok
test_min_minutes_filter_and_weekends_skipped (__main__.FreeSlotTests.test_min_minutes_filter_and_weekends_skipped) ... ok
test_monday_free_slots (__main__.FreeSlotTests.test_monday_free_slots) ... ok
test_conflict_detected_with_overlap_minutes (__main__.ParseTests.test_conflict_detected_with_overlap_minutes) ... ok
test_parses_tzid_utc_duration_folding_and_filters (__main__.ParseTests.test_parses_tzid_utc_duration_folding_and_filters) ... ok
test_bad_input_is_json_error (__main__.PlanTests.test_bad_input_is_json_error) ... ok
test_deadline_first_split_and_buffer (__main__.PlanTests.test_deadline_first_split_and_buffer) ... ok
test_unplaceable_task_reported (__main__.PlanTests.test_unplaceable_task_reported) ... ok

----------------------------------------------------------------------
Ran 8 tests in 0.008s

OK

# Configure a model for the agent run: local Gemma 4 E2B on Ollama (no cloud credentials in this sandbox)
$ hermes config set model.provider custom
✓ Set model.provider = custom in ~/.hermes/config.yaml

$ hermes config set model.base_url http://127.0.0.1:11434/v1
✓ Set model.base_url = http://127.0.0.1:11434/v1 in ~/.hermes/config.yaml

$ hermes config set model.default gemma4-a3:e2b
✓ Set model.default = gemma4-a3:e2b in ~/.hermes/config.yaml

$ hermes config set model.context_length 65536
✓ Set model.context_length = 65536 in ~/.hermes/config.yaml

$ hermes chat -Q --oneshot -s focus-block-planner -t terminal,skills -q Use the focus-block-planner skill on the calendar file week.ics in the current directory (timezone America/Los_Angeles, start 2026-11-16, 5 days). Run its script to report any double-booked meetings, then plan focus time for the task 'Write project report' (150 minutes, due 2026-11-17). Show the results.
Conflicts found:
One conflict exists. The "Advisor meeting" overlaps with the "Lab sync" for 30 minutes starting at 2026-11-16T13:30:00-08:00.

Focus plan for 'Write project report' (150 minutes, due 2026-11-17):
The task is planned across three blocks on 2026-11-16:
1. 09:00 to 09:30 (30 minutes)
2. 10:00 to 11:30 (90 minutes)
3. 11:40 to 12:10 (30 minutes)

No unscheduled tasks were identified.

session_id: local-24e0cc1d5ea189c3f1822477084f4a44110a4559c830000068a026f4b84ae756

# Tool calls the agent made in that session (from ~/.hermes/state.db):
  terminal>  python3 "$(find "${HERMES_HOME:-$HOME/.hermes}/skills" -path '*/focus-block-planner/scripts/focus_planner.py' | head -1)" busy --ics week.ics --start 2026-11-16 --days 5 --tz America/Los_Angeles
  terminal>  python3 "$(find "${HERMES_HOME:-$HOME/.hermes}/skills" -path '*/focus-block-planner/scripts/focus_planner.py' | head -1)" plan --ics week.ics --start 2026-11-16 --days 5 --tz America/Los_Angeles --task "Write project report:150:2026-11-17"
  result : {"output": "{\n  \"ok\": true,\n  \"timezone\": \"America/Los_Angeles\",\n  \"window\": [\n    \"2026-11-16T00:00:00-08:00\",\n    \"2026-11-21T00:00:00-08:00\"\n  ],\n  \"busy\": [\n    {\n      \"summary\": \"Team standup\",\n      \"start\": \"2026-11-16T09:30:00-08:00\",\n      \"end\": \"2026-11-16T10:00:00-08:00\",\n      \"all_day\": false\n    },\n    {\n      \"summary\": \"Advisor meetin
  result : {"output": "{\n  \"ok\": true,\n  \"timezone\": \"America/Los_Angeles\",\n  \"window\": [\n    \"2026-11-16T00:00:00-08:00\",\n    \"2026-11-21T00:00:00-08:00\"\n  ],\n  \"scheduled\": [\n    {\n      \"task\": \"Write project report\",\n      \"requested_minutes\": 150,\n      \"deadline\": \"2026-11-17\",\n      \"blocks\": [\n        {\n          \"start\": \"2026-11-16T09:00:00-08:00\",\n     
# end 2026-11-13T20:17:57Z
```
