#!/usr/bin/env python3
"""Create a clean-room canonical coding problem stub from source metadata."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

from coding_catalog.load import load_source_manifests
from coding_catalog.schema import CANONICAL_ID_PATTERN


PROBLEM_BANK_DIR = Path("05-coding-problems/problem-bank")


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scaffold a canonical coding problem folder.")
    parser.add_argument("canonical_id", help="Canonical problem id, for example lc-0001-two-sum.")
    parser.add_argument("--root", default=".", help="Repository root. Defaults to current directory.")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    root = Path(args.root).resolve()
    if not CANONICAL_ID_PATTERN.fullmatch(args.canonical_id):
        print("canonical_id must match lc-<zero-padded-id>-<title-slug>", file=sys.stderr)
        return 1
    matches = source_items_for(root, args.canonical_id)
    if not matches:
        print(f"no source metadata found for {args.canonical_id}", file=sys.stderr)
        return 1

    problem_root = (root / PROBLEM_BANK_DIR).resolve()
    problem_dir = (problem_root / args.canonical_id).resolve()
    try:
        problem_dir.relative_to(problem_root)
    except ValueError:
        print("canonical_id resolves outside the problem bank", file=sys.stderr)
        return 1
    if problem_dir.exists():
        print(f"problem folder already exists: {problem_dir.relative_to(root)}", file=sys.stderr)
        return 1

    primary = matches[0]
    problem_dir.mkdir(parents=True)
    (problem_dir / "problem.json").write_text(
        json.dumps(problem_payload(args.canonical_id, primary, matches), indent=2) + "\n",
        encoding="utf-8",
    )
    (problem_dir / "README.md").write_text(readme_template(args.canonical_id, primary), encoding="utf-8")
    print(f"created {problem_dir.relative_to(root)}")
    return 0


def source_items_for(root: Path, canonical_id: str) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    for manifest in load_source_manifests(root):
        payload = manifest["payload"]
        if not isinstance(payload, dict):
            continue
        for item in payload.get("items", []):
            if isinstance(item, dict) and item.get("canonicalId") == canonical_id:
                matches.append(item)
    return sorted(matches, key=lambda item: (str(item.get("collectionId", "")), int(item.get("order", 0))))


def problem_payload(canonical_id: str, primary: dict[str, Any], matches: list[dict[str, Any]]) -> dict[str, Any]:
    source_id = str(primary["sourceId"])
    title_slug = str(primary["titleSlug"])
    groups = sorted({str(item.get("group", "")).strip() for item in matches if str(item.get("group", "")).strip()})
    leetcode = {
        "frontendId": source_id,
        "titleSlug": title_slug,
        "url": f"https://leetcode.com/problems/{title_slug}",
    }
    paid_only = next((item["paidOnly"] for item in matches if isinstance(item.get("paidOnly"), bool)), None)
    if paid_only is not None:
        leetcode["paidOnly"] = paid_only
    return {
        "id": canonical_id,
        "title": primary["title"],
        "difficulty": str(primary.get("difficulty", "")).lower(),
        "status": "stub",
        "patterns": groups,
        "collections": [
            {
                "id": item["collectionId"],
                "order": item["order"],
                "group": item.get("group", ""),
                "sourceUrl": item["sourceUrl"],
            }
            for item in matches
        ],
        "leetcode": leetcode,
    }


def readme_template(canonical_id: str, primary: dict[str, Any]) -> str:
    return "\n".join(
        [
            f"# {primary['title']}",
            "",
            f"- Canonical ID: `{canonical_id}`",
            "- Status: `stub`",
            "- Source metadata only. Author the prompt summary, examples, cases, and explanations independently.",
            "",
            "## Driver Signature",
            "",
            "Define Java and Python signatures in `problem.json` before adding solutions.",
            "",
            "## Clean-Room Problem Summary",
            "",
            "TODO: Write a repo-authored summary without copying external statements.",
            "",
            "## Solution Ladder",
            "",
            "TODO: Add one to five Java/Python solution tiers from brute force to best practical approach.",
            "",
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main())
