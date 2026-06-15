#!/usr/bin/env python3
"""Install repository skills into a Codex skill directory."""

from __future__ import annotations

import argparse
import os
import shutil
import sys
import tempfile
from pathlib import Path

from _skilllib import repository_root, skill_directories


def default_destination() -> Path:
    codex_home = os.environ.get("CODEX_HOME")
    return (
        Path(codex_home).expanduser() / "skills"
        if codex_home
        else Path.home() / ".codex" / "skills"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skills", nargs="*", help="Skill names to install")
    parser.add_argument("--all", action="store_true", help="Install all skills")
    parser.add_argument("--list", action="store_true", help="List available skills")
    parser.add_argument(
        "--dest",
        type=Path,
        default=default_destination(),
        help="Destination skills directory",
    )
    parser.add_argument(
        "--mode",
        choices=("copy", "symlink"),
        default="copy",
        help="Install by atomic copy or symlink",
    )
    parser.add_argument("--force", action="store_true", help="Replace existing target")
    return parser.parse_args()


def remove_target(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def install_copy(source: Path, target: Path) -> None:
    temp_parent = target.parent
    temp_path = Path(
        tempfile.mkdtemp(prefix=f".{target.name}-", dir=temp_parent)
    )
    try:
        staged = temp_path / target.name
        shutil.copytree(
            source,
            staged,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"),
        )
        os.replace(staged, target)
    finally:
        shutil.rmtree(temp_path, ignore_errors=True)


def main() -> int:
    args = parse_args()
    root = repository_root(__file__)
    available = {path.name: path for path in skill_directories(root)}
    if args.list:
        for name in sorted(available):
            print(name)
        return 0

    if args.all and args.skills:
        print("ERROR: use either named skills or --all", file=sys.stderr)
        return 2
    selected = sorted(available) if args.all else args.skills
    if not selected:
        print("ERROR: specify skill names, --all, or --list", file=sys.stderr)
        return 2
    unknown = sorted(set(selected) - set(available))
    if unknown:
        print(f"ERROR: unknown skills: {', '.join(unknown)}", file=sys.stderr)
        return 2

    destination = args.dest.expanduser().resolve()
    destination.mkdir(parents=True, exist_ok=True)
    for name in selected:
        source = available[name].resolve()
        target = destination / name
        if target.exists() or target.is_symlink():
            if target.resolve() == source:
                print(f"already-linked {name}: {target}")
                continue
            if not args.force:
                print(
                    f"ERROR: target exists for {name}: {target}; use --force",
                    file=sys.stderr,
                )
                return 1
            remove_target(target)
        if args.mode == "symlink":
            target.symlink_to(source, target_is_directory=True)
        else:
            install_copy(source, target)
        print(f"installed {name}: {target} ({args.mode})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
