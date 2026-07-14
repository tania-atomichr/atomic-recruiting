# Install — candidate-fit-score skill

A self-contained Claude Code skill: score a candidate against a role brief with the atomic-HR
7-dimension rubric. The assistant applies the rubric in chat; a no-API script computes the exact
score. No API key or network needed for normal use.

## Install

Unzip so the folder lands at one of these locations:

- **Per-user (all your projects):** `~/.claude/skills/candidate-fit-score/`
- **Per-project (this repo only):** `<project>/.claude/skills/candidate-fit-score/`

```bash
# per-user
mkdir -p ~/.claude/skills
unzip candidate-fit-score.zip -d ~/.claude/skills/
```

The final layout must be:
```
candidate-fit-score/
  SKILL.md
  RUBRIC.md
  scripts/compute_score.py
```

Start a new Claude Code session (or reload) and the skill registers automatically — you'll see
`candidate-fit-score` in the skills list. Then just paste a **role brief + a candidate profile**
and ask to score/evaluate fit.

## Requirements
- Python 3 (standard library only — `compute_score.py` needs no pip installs).
- `scripts/score.py` is an **optional** fully-automated variant that calls the Claude API
  (`pip install anthropic`, `ANTHROPIC_API_KEY`). Not needed for in-chat scoring.

## Keeping it in sync with the app
`scripts/build_skill.py` re-extracts the rubric + scoring math from the atomic-HR `ranking.py`.
It has a hardcoded path to that repo, so it only runs on a machine that has the app checked out —
it's a maintenance tool, not required to use the skill.
