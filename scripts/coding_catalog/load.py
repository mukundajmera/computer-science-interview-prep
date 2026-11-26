"""Load coding problem catalog files from the repository."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_catalog(root: Path) -> list[dict[str, Any]]:
    """Load canonical problem folders under 05-coding-problems/problem-bank."""

    bank = root / "05-coding-problems" / "problem-bank"
    if not bank.is_dir() or bank.is_symlink():
        return []

    records: list[dict[str, Any]] = []
    for problem_dir in sorted(child for child in bank.iterdir() if child.is_dir() and not child.is_symlink()):
        record: dict[str, Any] = {
            "dir": problem_dir,
            "problem": None,
            "cases": None,
            "solutions": None,
        }
        for key, filename in (
            ("problem", "problem.json"),
            ("cases", "cases.json"),
            ("solutions", "solutions.json"),
        ):
            path = problem_dir / filename
            if path.is_file() and not path.is_symlink():
                try:
                    record[key] = load_json(path)
                except json.JSONDecodeError as exc:
                    record.setdefault("errors", []).append(
                        {
                            "path": path,
                            "message": f"invalid JSON at line {exc.lineno} column {exc.colno}: {exc.msg}",
                        }
                    )
        records.append(record)
    return records


def load_source_manifests(root: Path, collection: str | None = None) -> list[dict[str, Any]]:
    """Load coding-list source manifests."""

    source_dir = root / "resources" / "source-intake" / "coding-lists"
    if not source_dir.is_dir() or source_dir.is_symlink():
        return []

    manifests: list[dict[str, Any]] = []
    for path in sorted(source_dir.glob("*.json")):
        if collection and path.stem != collection:
            continue
        if path.is_file() and not path.is_symlink():
            try:
                payload = load_json(path)
            except json.JSONDecodeError as exc:
                manifests.append(
                    {
                        "path": path,
                        "payload": None,
                        "error": f"{exc.msg} at line {exc.lineno} column {exc.colno}",
                    }
                )
                continue
            manifests.append({"path": path, "payload": payload})
    return manifests
