"""Fail when a skill routes to a file that is not there, or ships a file nothing routes to.

- every relative Markdown link in the repo resolves to an existing file;
- every `references/...md` path named in a SKILL.md exists in that skill;
- every file under a skill's references/ is named in its SKILL.md, by path or by
  file name (the per-language files are routed by file name), so an agent that
  reads only the router can still reach it.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LINK = re.compile(r"\]\(([^)\s]+)\)")
ROUTE = re.compile(r"`(references/[^`\s]+\.md)`")
SCHEME = re.compile(r"^[a-z][a-z0-9+.-]*:", re.IGNORECASE)


def main() -> int:
    errors = []

    for md in sorted(ROOT.rglob("*.md")):
        if ".git" in md.parts or "node_modules" in md.parts:
            continue
        for target in LINK.findall(md.read_text(encoding="utf-8")):
            if target.startswith("#") or SCHEME.match(target):
                continue
            if not (md.parent / target.split("#", 1)[0]).exists():
                errors.append((md, f"broken link: {target}"))

    for skill_md in sorted(ROOT.glob("skills/*/SKILL.md")):
        skill = skill_md.parent
        router = skill_md.read_text(encoding="utf-8")
        for route in sorted(set(ROUTE.findall(router))):
            if not (skill / route).is_file():
                errors.append((skill_md, f"routes to a missing file: {route}"))
        references = skill / "references"
        if references.is_dir():
            for ref in sorted(references.rglob("*.md")):
                path = ref.relative_to(references).as_posix()
                if path not in router and ref.name not in router:
                    errors.append((skill_md, f"nothing routes to references/{path}"))

    for file, message in errors:
        print(f"::error file={file.relative_to(ROOT).as_posix()}::{message}")
    if errors:
        return 1
    print("All skill links and routes resolve.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
