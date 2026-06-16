#!/usr/bin/env python3
"""Summarize scalar metrics from a MetaBBO JSONL training log."""

from __future__ import annotations

import argparse
import json
import math
import statistics
from pathlib import Path
from typing import Any


def numeric_items(record: dict[str, Any]) -> dict[str, float]:
    items: dict[str, float] = {}
    for key, value in record.items():
        if isinstance(value, bool):
            continue
        if isinstance(value, (int, float)) and math.isfinite(float(value)):
            items[key] = float(value)
    return items


def load_records(path: Path) -> list[dict[str, float]]:
    records: list[dict[str, float]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as error:
                raise SystemExit(f"{path}:{line_number}: invalid JSON: {error}") from error
            if isinstance(value, dict):
                records.append(numeric_items(value))
    return records


def choose_keys(records: list[dict[str, float]], requested: list[str]) -> list[str]:
    if requested:
        return requested
    preferred_fragments = (
        "reward",
        "action",
        "return",
        "continue",
        "budget",
        "entropy",
        "kl",
        "clip",
        "grad",
        "loss",
        "best",
        "objective",
    )
    keys = sorted({key for record in records for key in record})
    selected = [key for key in keys if any(fragment in key.lower() for fragment in preferred_fragments)]
    return selected or keys


def summarize(values: list[float]) -> tuple[float, float, float, float]:
    if not values:
        return (float("nan"), float("nan"), float("nan"), float("nan"))
    mean = statistics.fmean(values)
    std = statistics.pstdev(values) if len(values) > 1 else 0.0
    return mean, std, min(values), max(values)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log_path", type=Path)
    parser.add_argument("--tail", type=int, default=10, help="Number of final records to summarize.")
    parser.add_argument("--keys", nargs="*", default=[], help="Metric keys to print. Defaults to common training keys.")
    args = parser.parse_args()

    records = load_records(args.log_path)
    if not records:
        raise SystemExit(f"no numeric records found: {args.log_path}")
    tail_records = records[-max(args.tail, 1) :]
    keys = choose_keys(tail_records, args.keys)

    print(f"path={args.log_path}")
    print(f"records={len(records)} tail={len(tail_records)}")
    print("metric\tlast\tmean\tstd\tmin\tmax")
    last = tail_records[-1]
    for key in keys:
        values = [record[key] for record in tail_records if key in record]
        if not values:
            continue
        mean, std, minimum, maximum = summarize(values)
        print(f"{key}\t{last.get(key, float('nan')):.6g}\t{mean:.6g}\t{std:.6g}\t{minimum:.6g}\t{maximum:.6g}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
