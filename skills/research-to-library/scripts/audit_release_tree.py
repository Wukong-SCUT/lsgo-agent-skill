#!/usr/bin/env python3
"""Audit a candidate public release tree for boundary violations."""

from __future__ import annotations

import argparse
import json
import os
import sys
import zipfile
from pathlib import Path
from tarfile import open as open_tar


DEFAULT_IGNORED_DIRS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
}
TEXT_SUFFIXES = {
    ".c",
    ".cfg",
    ".cpp",
    ".h",
    ".ini",
    ".md",
    ".py",
    ".rst",
    ".sh",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit a clean public release tree and built archives."
    )
    parser.add_argument("root", type=Path, help="Candidate release root")
    parser.add_argument(
        "--package-dir",
        action="append",
        default=[],
        help="Relative core package directory to scan for forbidden tokens",
    )
    parser.add_argument(
        "--forbid-path",
        action="append",
        default=[],
        help="Case-insensitive substring forbidden in repository paths",
    )
    parser.add_argument(
        "--forbid-package-token",
        action="append",
        default=[],
        help="Case-insensitive token forbidden in core package text",
    )
    parser.add_argument(
        "--require",
        action="append",
        default=[],
        help="Relative path that must exist",
    )
    parser.add_argument(
        "--archive",
        action="append",
        default=[],
        help="Wheel, zip, tar.gz, or tgz archive to inspect",
    )
    parser.add_argument(
        "--max-file-mib",
        type=float,
        default=10.0,
        help="Fail on candidate files larger than this size (default: 10)",
    )
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def iter_candidate_files(root: Path):
    for current, dirs, files in os.walk(root):
        dirs[:] = [item for item in dirs if item not in DEFAULT_IGNORED_DIRS]
        current_path = Path(current)
        for name in files:
            yield current_path / name


def archive_members(path: Path) -> list[str]:
    lower = path.name.lower()
    if lower.endswith((".whl", ".zip")):
        with zipfile.ZipFile(path) as archive:
            return archive.namelist()
    if lower.endswith((".tar.gz", ".tgz")):
        with open_tar(path, "r:gz") as archive:
            return archive.getnames()
    raise ValueError(f"Unsupported archive format: {path}")


def text_contains(path: Path, tokens: list[str]) -> list[str]:
    if path.suffix.lower() not in TEXT_SUFFIXES:
        return []
    try:
        text = path.read_text(encoding="utf-8").lower()
    except (OSError, UnicodeDecodeError):
        return []
    return [token for token in tokens if token in text]


def main() -> int:
    args = parse_args()
    root = args.root.expanduser().resolve()
    errors: list[str] = []
    warnings: list[str] = []
    checked_files = 0

    if not root.is_dir():
        errors.append(f"Release root does not exist: {root}")
    else:
        forbidden_paths = [item.lower() for item in args.forbid_path]
        max_bytes = int(args.max_file_mib * 1024 * 1024)
        for path in iter_candidate_files(root):
            checked_files += 1
            relative = path.relative_to(root).as_posix()
            relative_lower = relative.lower()
            for token in forbidden_paths:
                if token in relative_lower:
                    errors.append(
                        f"Forbidden path token {token!r}: {relative}"
                    )
            try:
                size = path.stat().st_size
            except OSError as error:
                errors.append(f"Cannot stat {relative}: {error}")
                continue
            if size > max_bytes:
                errors.append(
                    f"Large file {relative}: {size / 1024 / 1024:.2f} MiB"
                )

        for required in args.require:
            if not (root / required).exists():
                errors.append(f"Missing required path: {required}")

        package_tokens = [
            item.lower() for item in args.forbid_package_token
        ]
        for package_dir in args.package_dir:
            package_root = root / package_dir
            if not package_root.is_dir():
                errors.append(f"Missing package directory: {package_dir}")
                continue
            for path in iter_candidate_files(package_root):
                relative = path.relative_to(root).as_posix()
                for token in text_contains(path, package_tokens):
                    errors.append(
                        f"Forbidden package token {token!r}: {relative}"
                    )

        for archive_arg in args.archive:
            archive_path = Path(archive_arg).expanduser()
            if not archive_path.is_absolute():
                archive_path = root / archive_path
            if not archive_path.is_file():
                errors.append(f"Missing archive: {archive_path}")
                continue
            try:
                members = archive_members(archive_path)
            except (OSError, ValueError, zipfile.BadZipFile) as error:
                errors.append(f"Cannot inspect {archive_path}: {error}")
                continue
            for member in members:
                member_lower = member.lower()
                for token in forbidden_paths:
                    if token in member_lower:
                        errors.append(
                            f"Forbidden archive member token {token!r}: "
                            f"{archive_path.name}:{member}"
                        )

    result = {
        "root": str(root),
        "checked_files": checked_files,
        "errors": errors,
        "warnings": warnings,
        "passed": not errors,
    }
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"release_root={root}")
        print(f"checked_files={checked_files}")
        for warning in warnings:
            print(f"WARNING: {warning}")
        for error in errors:
            print(f"ERROR: {error}")
        print(f"passed={str(not errors).lower()}")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
