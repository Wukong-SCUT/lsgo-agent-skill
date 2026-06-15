#!/usr/bin/env python3
"""Scaffold a new repository skill and its registry metadata."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date

from _skilllib import (
    ALLOWED_CATEGORIES,
    NAME_PATTERN,
    TAG_PATTERN,
    VERSION_PATTERN,
    load_registry,
    repository_root,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("name")
    parser.add_argument("--category", required=True, choices=sorted(ALLOWED_CATEGORIES))
    parser.add_argument("--description", required=True)
    parser.add_argument("--display-name")
    parser.add_argument("--short-description")
    parser.add_argument("--default-prompt")
    parser.add_argument("--tags", nargs="+", required=True)
    parser.add_argument("--source", required=True)
    parser.add_argument("--version", default="0.1.0")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not NAME_PATTERN.fullmatch(args.name) or len(args.name) > 64:
        print("ERROR: name must use lowercase hyphen-case and be <=64 chars", file=sys.stderr)
        return 2
    if len(args.description) < 40:
        print("ERROR: description must be at least 40 characters", file=sys.stderr)
        return 2
    if not VERSION_PATTERN.fullmatch(args.version):
        print("ERROR: version must use semantic x.y.z form", file=sys.stderr)
        return 2
    if any(not TAG_PATTERN.fullmatch(tag) for tag in args.tags):
        print("ERROR: tags must use lowercase hyphen-case", file=sys.stderr)
        return 2

    root = repository_root(__file__)
    skill_dir = root / "skills" / args.name
    if skill_dir.exists():
        print(f"ERROR: skill already exists: {skill_dir}", file=sys.stderr)
        return 1

    registry = load_registry(root)
    if args.name in registry:
        print(f"ERROR: registry entry already exists: {args.name}", file=sys.stderr)
        return 1

    display_name = args.display_name or args.name.replace("-", " ").title()
    short_description = args.short_description or args.description[:64].rstrip()
    default_prompt = args.default_prompt or (
        f"Use ${args.name} to apply this reusable workflow to the current task."
    )

    skill_template = (root / "templates" / "SKILL_TEMPLATE.md").read_text(
        encoding="utf-8"
    )
    skill_text = skill_template.replace("skill-name", args.name, 1)
    skill_text = skill_text.replace(
        "Describe what the skill does and the exact tasks or situations that should trigger it.",
        args.description,
        1,
    )
    skill_text = skill_text.replace("# Skill Name", f"# {display_name}", 1)

    skill_dir.mkdir(parents=True)
    (skill_dir / "agents").mkdir()
    (skill_dir / "scripts").mkdir()
    (skill_dir / "references").mkdir()
    (skill_dir / "SKILL.md").write_text(skill_text, encoding="utf-8")
    agent_text = (
        "interface:\n"
        f"  display_name: {json.dumps(display_name)}\n"
        f"  short_description: {json.dumps(short_description)}\n"
        f"  default_prompt: {json.dumps(default_prompt)}\n"
    )
    (skill_dir / "agents" / "openai.yaml").write_text(
        agent_text, encoding="utf-8"
    )

    registry[args.name] = {
        "category": args.category,
        "maturity": "draft",
        "version": args.version,
        "tags": sorted(set(args.tags)),
        "source": args.source,
        "updated": date.today().isoformat(),
    }
    registry_path = root / "catalog" / "registry.json"
    registry_path.write_text(
        json.dumps(registry, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"created {skill_dir}")
    print("next: complete TODOs, add resources, build catalog, validate")
    return 0


if __name__ == "__main__":
    sys.exit(main())
