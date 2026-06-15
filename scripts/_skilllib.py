#!/usr/bin/env python3
"""Shared repository helpers for skill catalog and validation scripts."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
TAG_PATTERN = NAME_PATTERN
VERSION_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
LOCAL_LINK_PATTERN = re.compile(r"\[[^]]+\]\(([^)]+)\)")
ALLOWED_CATEGORIES = {
    "experiment-analysis",
    "optimization-systems",
    "repository-operations",
    "research-communication",
    "research-engineering",
    "software-engineering",
    "tooling",
}
ALLOWED_MATURITY = {"draft", "validated", "stable", "deprecated"}


@dataclass(frozen=True)
class SkillRecord:
    name: str
    description: str
    display_name: str
    short_description: str
    default_prompt: str
    category: str
    maturity: str
    version: str
    tags: tuple[str, ...]
    source: str
    updated: str
    path: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "short_description": self.short_description,
            "default_prompt": self.default_prompt,
            "category": self.category,
            "maturity": self.maturity,
            "version": self.version,
            "tags": list(self.tags),
            "source": self.source,
            "updated": self.updated,
            "path": self.path,
        }


def repository_root(script_file: str) -> Path:
    return Path(script_file).resolve().parents[1]


def parse_frontmatter(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError(f"Missing YAML frontmatter: {path}")
    try:
        end = next(
            index
            for index, line in enumerate(lines[1:], start=1)
            if line.strip() == "---"
        )
    except StopIteration as error:
        raise ValueError(f"Unterminated YAML frontmatter: {path}") from error

    metadata: dict[str, str] = {}
    for line in lines[1:end]:
        if not line.strip():
            continue
        key, separator, value = line.partition(":")
        if not separator or not key.strip() or not value.strip():
            raise ValueError(f"Unsupported frontmatter line in {path}: {line}")
        key = key.strip()
        if key in metadata:
            raise ValueError(f"Duplicate frontmatter key {key!r}: {path}")
        metadata[key] = value.strip().strip('"').strip("'")
    return metadata, "\n".join(lines[end + 1 :])


def parse_openai_interface(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    values: dict[str, str] = {}
    for key in ("display_name", "short_description", "default_prompt"):
        match = re.search(
            rf"^\s{{2}}{key}:\s*([\"'])(.*?)\1\s*$",
            text,
            flags=re.MULTILINE,
        )
        if match:
            values[key] = match.group(2)
    return values


def load_registry(root: Path) -> dict[str, dict[str, Any]]:
    path = root / "catalog" / "registry.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("catalog/registry.json must contain a JSON object")
    return data


def skill_directories(root: Path) -> list[Path]:
    skills_root = root / "skills"
    if not skills_root.is_dir():
        return []
    return sorted(
        path
        for path in skills_root.iterdir()
        if path.is_dir() and not path.name.startswith(".")
    )


def load_records(root: Path) -> list[SkillRecord]:
    registry = load_registry(root)
    records: list[SkillRecord] = []
    for skill_dir in skill_directories(root):
        metadata, _ = parse_frontmatter(skill_dir / "SKILL.md")
        interface = parse_openai_interface(skill_dir / "agents" / "openai.yaml")
        name = metadata["name"]
        entry = registry[name]
        records.append(
            SkillRecord(
                name=name,
                description=metadata["description"],
                display_name=interface["display_name"],
                short_description=interface["short_description"],
                default_prompt=interface["default_prompt"],
                category=str(entry["category"]),
                maturity=str(entry["maturity"]),
                version=str(entry["version"]),
                tags=tuple(sorted(str(tag) for tag in entry["tags"])),
                source=str(entry["source"]),
                updated=str(entry["updated"]),
                path=skill_dir.relative_to(root).as_posix(),
            )
        )
    return sorted(records, key=lambda item: item.name)


def local_markdown_links(path: Path) -> list[Path]:
    text = path.read_text(encoding="utf-8")
    links: list[Path] = []
    for target in LOCAL_LINK_PATTERN.findall(text):
        target = target.split("#", 1)[0]
        if not target or "://" in target or target.startswith("mailto:"):
            continue
        links.append((path.parent / target).resolve())
    return links
