# Skill discovery transcript: `hermes skills search` for focus-block-planner

Isolated sandbox: the brand-new `HOME` and `~/.hermes` from [INSTALL_TRANSCRIPT.md](INSTALL_TRANSCRIPT.md), on the Mac. The production Cloud Run instance was not touched. A GitHub token was supplied only as the `GITHUB_TOKEN` environment variable of the commands in section B and D. Its value is not shown, and the final check confirms it was not written anywhere under `~/.hermes`.

```text
# Hermes GitHub skill discovery test (isolated sandbox: the fresh-install HOME/~/.hermes from the install transcript)
# date -u: 2026-11-13T21:56:38Z; Hermes Hermes Agent v0.22.7 (2026.9.24) · stable · local b200f5bc60e3

## A. Without GitHub authentication (60 req/h anonymous API quota)
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


## B. With GitHub authentication: GITHUB_TOKEN set in this shell only (from `gh auth token`, value not shown, not written to any config)
$ hermes skills search focus-block-planner

Searching for: focus-block-planner
No skills found matching your query.


$ hermes skills search focus block

Searching for: focus block
                            Skills Hub — 2 result(s)                            
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━┓
┃ Name                ┃ Description        ┃ Source  ┃ Trust     ┃ Identifier  ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━┩
│ FocusTimer Pomodoro │ Pomodoro-style     │ clawhub │ community │ focus-timer │
│ Timer via Agent     │ focus blocks       │         │           │             │
│                     │ managed by your    │         │           │             │
│                     │ agent. Start,      │         │           │             │
│                     │ pa...              │         │           │             │
│ focus-coach         │ Focus coach for AI │ clawhub │ community │ focus-coach │
│                     │ agents — diagnose  │         │           │             │
│                     │ focus blockers     │         │           │             │
│                     │ using BJ...        │         │           │             │
└─────────────────────┴────────────────────┴─────────┴───────────┴─────────────┘
Use: hermes skills inspect <identifier> to preview, hermes skills install 
<identifier> to install (--json for scripting)


$ hermes skills search planner --source github

Searching for: planner
No skills found matching your query.


$ hermes skills search focus-block-planner --json
[]

## C. Token not persisted: check the sandbox config and env files for it
$ grep -rl "<token>" ~/.hermes/config.yaml ~/.hermes/.env ~/.hermes/skills/.hub  (searched for the literal token value)
files containing the token: 0
## D. Search restricted to the GitHub source (custom taps), authenticated. In default mode Hermes skips the GitHub/tap source whenever its central index is reachable (tools/skills_hub_search.py: _select_active_sources skips API sources; _INDEX_MISS_FALLBACK_IDS excludes github), which explains B
# GitHub API quota with token: limit 5000 remaining 4892
$ hermes skills search focus-block-planner --source github

Searching for: focus-block-planner
No skills found matching your query.

(took 31 s)

$ hermes skills search focus-block-planner --source github

Searching for: focus-block-planner
No skills found matching your query.

(took 31 s)

$ hermes skills search planner --source github

Searching for: planner
No skills found matching your query.

(took 30 s)

## E. GitHub-source search again without a token (local tap cache now warm)
$ hermes skills search focus-block-planner --source github

Searching for: focus-block-planner
No skills found matching your query.

(took 31 s)

## Token persisted anywhere under ~/.hermes (grep for its literal value): 0 files
## F. Root cause, measured directly with Hermes' own GitHubSource (same sandbox, authenticated, outside the CLI's 30 s limit)
# GitHubSource has 28 taps: 27 built-in default repos (openai/skills, anthropics/skills, huggingface/skills, …) and ours LAST (index 27).
# A cold search walks every tap and inspects every skill directory through the GitHub API.
# direct GitHubSource.search("focus-block-planner"), cold: 310.1 s -> [('focus-block-planner', 'sauravcodes-dotcom/hermes-focus-block-planner/skills/focus-block-planner')]
# same call again, cache warm: 0.0 s -> same result
# The CLI's parallel search stops at overall_timeout=30 s (tools/skills_hub_search.py), long before our tap is reached on a cold cache.
## G. CLI search after the tap index was cached by step F (no token)
$ hermes skills search focus-block-planner --source github

Searching for: focus-block-planner
                            Skills Hub — 1 result(s)                            
┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┓
┃ Name             ┃ Description       ┃ Source ┃ Trust     ┃ Identifier       ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━┩
│ focus-block-pla… │ Plan deep-work    │ github │ community │ sauravcodes-dotc │
│                  │ focus blocks from │        │           │ om/hermes-focus- │
│                  │ an .ics calendar  │        │           │ block-planner/sk │
│                  │ export: bu...     │        │           │ ills/focus-block │
│                  │                   │        │           │ -planner         │
└──────────────────┴───────────────────┴────────┴───────────┴──────────────────┘
Use: hermes skills inspect <identifier> to preview, hermes skills install 
<identifier> to install (--json for scripting)

(took 1 s)

$ hermes skills search focus-block-planner

Searching for: focus-block-planner
No skills found matching your query.

(took 9 s)

$ hermes skills search focus planning --source github

Searching for: focus planning
No skills found matching your query.

(took 1 s)

```
