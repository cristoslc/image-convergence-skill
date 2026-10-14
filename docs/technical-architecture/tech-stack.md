# Tech Stack

- **Skill protocol:** agent SKILL.md (YAML frontmatter: `name`, `description`; markdown body).
- **Engine + tests:** Python 3.12+, stdlib only (`dataclasses`, `typing`, `unittest`).
- **Staging scripts:** POSIX bash, `set -euo pipefail`, no external commands beyond `git`, `diff`, `cp`, `mkdir`.
- **CI:** none wired yet; the suite is offline and fast (`python3 -m unittest discover -s tests`).
