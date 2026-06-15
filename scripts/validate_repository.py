#!/usr/bin/env python3
"""Validate skill structure, registry metadata, references, and scripts."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from _skilllib import (
    ALLOWED_CATEGORIES,
    ALLOWED_MATURITY,
    DATE_PATTERN,
    NAME_PATTERN,
    TAG_PATTERN,
    VERSION_PATTERN,
    load_registry,
    local_markdown_links,
    parse_frontmatter,
    parse_openai_interface,
    repository_root,
    skill_directories,
)

FORBIDDEN_DIRECTORIES = {"checkpoints", "runs"}
PRIVATE_KEY_MARKERS = (
    "-----BEGIN " + "OPENSSH PRIVATE KEY-----",
    "-----BEGIN " + "RSA PRIVATE KEY-----",
    "-----BEGIN " + "EC PRIVATE KEY-----",
)
MAX_FILE_BYTES = 10 * 1024 * 1024


def validate_python(path: Path, errors: list[str]) -> None:
    try:
        source = path.read_text(encoding="utf-8")
        compile(source, str(path), "exec")
    except (OSError, SyntaxError, UnicodeDecodeError) as error:
        errors.append(f"Invalid Python script {path}: {error}")


def main() -> int:
    root = repository_root(__file__)
    errors: list[str] = []
    try:
        registry = load_registry(root)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}")
        return 1

    skill_dirs = skill_directories(root)
    folder_names = {path.name for path in skill_dirs}
    registry_names = set(registry)
    if folder_names != registry_names:
        errors.append(
            "Skill folders and registry entries differ: "
            f"folders={sorted(folder_names)}, registry={sorted(registry_names)}"
        )

    for path in root.rglob("*"):
        if ".git" in path.parts:
            continue
        relative = path.relative_to(root)
        if path.is_dir() and path.name in FORBIDDEN_DIRECTORIES:
            errors.append(f"Forbidden repository directory: {relative}")
        if not path.is_file():
            continue
        try:
            if path.stat().st_size > MAX_FILE_BYTES:
                errors.append(f"File exceeds 10 MiB: {relative}")
            if path.suffix.lower() in {
                ".md", ".py", ".sh", ".txt", ".yaml", ".yml", ".json"
            }:
                text = path.read_text(encoding="utf-8")
                for marker in PRIVATE_KEY_MARKERS:
                    if marker in text:
                        errors.append(f"Private key material detected: {relative}")
        except (OSError, UnicodeDecodeError) as error:
            errors.append(f"Cannot inspect {relative}: {error}")

    for skill_dir in skill_dirs:
        name = skill_dir.name
        skill_path = skill_dir / "SKILL.md"
        agent_path = skill_dir / "agents" / "openai.yaml"
        if not NAME_PATTERN.fullmatch(name) or len(name) > 64:
            errors.append(f"Invalid skill directory name: {name}")
        if not skill_path.is_file():
            errors.append(f"Missing SKILL.md: {name}")
            continue
        if not agent_path.is_file():
            errors.append(f"Missing agents/openai.yaml: {name}")
            continue

        try:
            metadata, _ = parse_frontmatter(skill_path)
        except (OSError, ValueError, UnicodeDecodeError) as error:
            errors.append(str(error))
            continue
        if set(metadata) != {"name", "description"}:
            errors.append(
                f"{name}: frontmatter must contain only name and description"
            )
        if metadata.get("name") != name:
            errors.append(f"{name}: frontmatter name does not match directory")
        if len(metadata.get("description", "")) < 40:
            errors.append(f"{name}: description is too short for reliable triggering")
        if len(skill_path.read_text(encoding="utf-8").splitlines()) > 500:
            errors.append(f"{name}: SKILL.md exceeds 500 lines")

        interface = parse_openai_interface(agent_path)
        required_interface = {
            "display_name",
            "short_description",
            "default_prompt",
        }
        if set(interface) != required_interface:
            errors.append(f"{name}: incomplete or unquoted agents/openai.yaml")
        short_description = interface.get("short_description", "")
        if not 25 <= len(short_description) <= 64:
            errors.append(f"{name}: short_description must be 25-64 characters")
        if f"${name}" not in interface.get("default_prompt", ""):
            errors.append(f"{name}: default_prompt must mention ${name}")

        entry = registry.get(name)
        if not isinstance(entry, dict):
            errors.append(f"{name}: missing registry metadata")
        else:
            required_registry = {
                "category",
                "maturity",
                "version",
                "tags",
                "source",
                "updated",
            }
            if set(entry) != required_registry:
                errors.append(
                    f"{name}: registry fields must be {sorted(required_registry)}"
                )
            if entry.get("category") not in ALLOWED_CATEGORIES:
                errors.append(f"{name}: unknown category {entry.get('category')!r}")
            if entry.get("maturity") not in ALLOWED_MATURITY:
                errors.append(f"{name}: unknown maturity {entry.get('maturity')!r}")
            if not VERSION_PATTERN.fullmatch(str(entry.get("version", ""))):
                errors.append(f"{name}: version must use semantic x.y.z form")
            if not DATE_PATTERN.fullmatch(str(entry.get("updated", ""))):
                errors.append(f"{name}: updated must use YYYY-MM-DD")
            tags = entry.get("tags")
            if not isinstance(tags, list) or not tags:
                errors.append(f"{name}: tags must be a non-empty list")
            elif any(not TAG_PATTERN.fullmatch(str(tag)) for tag in tags):
                errors.append(f"{name}: tags must use lowercase hyphen-case")
            elif len(tags) != len(set(tags)):
                errors.append(f"{name}: duplicate tags")

        for markdown in skill_dir.rglob("*.md"):
            text = markdown.read_text(encoding="utf-8")
            if "TODO" in text or "[TODO" in text:
                errors.append(
                    f"{name}: unresolved TODO in "
                    f"{markdown.relative_to(skill_dir)}"
                )
            for link in local_markdown_links(markdown):
                if not link.exists():
                    errors.append(f"{name}: broken local link {link}")

        for path in skill_dir.rglob("*"):
            if path.is_dir() and path.name == "__pycache__":
                errors.append(f"{name}: committed __pycache__ directory")
            if path.is_file() and path.suffix == ".py":
                validate_python(path, errors)

    for path in (root / "scripts").glob("*.py"):
        validate_python(path, errors)

    for markdown in [root / "README.md", root / "CONTRIBUTING.md", *(root / "docs").glob("*.md")]:
        if markdown.is_file():
            for link in local_markdown_links(markdown):
                if not link.exists():
                    errors.append(f"Broken repository link in {markdown}: {link}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"validation_failed={len(errors)}")
        return 1
    print(f"validated_skills={len(skill_dirs)}")
    print("validation_passed=true")
    return 0


if __name__ == "__main__":
    sys.exit(main())
