"""Render deduplicated coding-problem collection coverage pages."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .load import load_catalog, load_source_manifests
from .schema import CANONICAL_ID_PATTERN, COLLECTION_ID_PATTERN


COLLECTION_DIR = Path("05-coding-problems/collections")
PROBLEM_BANK_DIR = Path("05-coding-problems/problem-bank")


@dataclass(frozen=True)
class RenderedPage:
    path: Path
    content: str


def render_collection_pages(root: Path) -> list[RenderedPage]:
    catalog = catalog_by_id(root)
    manifests = load_source_manifests(root)
    manifests = [manifest for manifest in manifests if isinstance(manifest.get("payload"), dict)]
    manifests.sort(key=lambda manifest: manifest["payload"].get("collectionId", ""))

    pages = [
        RenderedPage(root / COLLECTION_DIR / "README.md", render_index(root, manifests, catalog)),
        RenderedPage(root / COLLECTION_DIR / "PENDING-COVERAGE.md", render_pending_coverage(manifests, catalog)),
    ]
    for manifest in manifests:
        payload = manifest["payload"]
        collection_id = payload["collectionId"]
        pages.append(
            RenderedPage(
                collection_page_path(root, collection_id),
                render_collection(root, payload, catalog),
            )
        )
    return pages


def catalog_by_id(root: Path) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    for record in load_catalog(root):
        problem = record.get("problem")
        if not isinstance(problem, dict):
            continue
        problem_id = problem.get("id")
        if isinstance(problem_id, str):
            records[problem_id] = {
                "title": problem.get("title", problem_id),
                "status": problem.get("status", "unknown"),
                "path": Path(record["dir"]),
                "paidOnly": problem.get("leetcode", {}).get("paidOnly")
                if isinstance(problem.get("leetcode"), dict)
                else None,
            }
    return records


def render_index(root: Path, manifests: list[dict[str, Any]], catalog: dict[str, dict[str, Any]]) -> str:
    membership_count = 0
    canonical_ids: set[str] = set()
    collection_rows = []
    memberships_by_problem: dict[str, list[str]] = {}

    for manifest in manifests:
        payload = manifest["payload"]
        collection_id = payload["collectionId"]
        items = payload.get("items", [])
        membership_count += len(items)
        for item in items:
            canonical_id = item.get("canonicalId")
            if isinstance(canonical_id, str):
                canonical_ids.add(canonical_id)
                memberships_by_problem.setdefault(canonical_id, []).append(collection_id)
        collection_rows.append(
            [
                collection_id,
                str(len(items)),
                str(sum(1 for item in items if item.get("canonicalId") in catalog)),
                markdown_link(f"{collection_id}.md", f"./{collection_id}.md"),
            ]
        )

    shared_count = sum(1 for memberships in memberships_by_problem.values() if len(set(memberships)) > 1)

    lines = [
        "# Coding Problem Collections",
        "",
        "Generated from metadata-only source manifests. Collection pages track list membership and order; canonical problem folders hold reusable details, drivers, and Java/Python solutions.",
        "",
        "## Coverage Summary",
        "",
        "| Metric | Count |",
        "|---|---:|",
        f"| Source-list memberships | {membership_count} |",
        f"| Unique canonical problems | {len(canonical_ids)} |",
        f"| Canonical folders present | {len(catalog)} |",
        f"| Problems appearing in multiple collections | {shared_count} |",
        "",
        "## Collections",
        "",
        "| Collection | Entries | Canonical folders present | Page |",
        "|---|---:|---:|---|",
    ]
    lines.extend(f"| {escape_cell(row[0])} | {row[1]} | {row[2]} | {row[3]} |" for row in collection_rows)

    if shared_count:
        lines.extend(
            [
                "",
                "## Shared Problem Examples",
                "",
                "| Canonical problem | Collections |",
                "|---|---|",
            ]
        )
        for canonical_id, memberships in sorted(memberships_by_problem.items()):
            unique_memberships = sorted(set(memberships))
            if len(unique_memberships) <= 1:
                continue
            lines.append(
                f"| {problem_link(root, canonical_id, catalog)} | {escape_cell(', '.join(unique_memberships))} |"
            )
            if len(lines) > 35:
                break

    lines.extend(
        [
            "",
            "## Maintenance",
            "",
            "Create or update one canonical folder under `../problem-bank/<canonical-id>/` for each real problem. Do not duplicate solution code in collection pages.",
            "",
        ]
    )
    return "\n".join(lines)


def render_collection(root: Path, payload: dict[str, Any], catalog: dict[str, dict[str, Any]]) -> str:
    collection_id = payload["collectionId"]
    source_url = payload.get("sourceUrl", "")
    items = payload.get("items", [])
    lines = [
        f"# {collection_id}",
        "",
        f"- Source: {source_url}",
        f"- Entries: {len(items)}",
        "- Generated from metadata-only source manifests.",
        "",
        "| # | Group | Canonical problem | Title | Difficulty | Access | Canonical status | Source |",
        "|---:|---|---|---|---|---|---|---|",
    ]
    for item in sorted(items, key=lambda value: value.get("order", 0)):
        canonical_id = item.get("canonicalId", "")
        catalog_entry = catalog.get(canonical_id, {})
        status = catalog_entry.get("status", "planned")
        title = catalog_entry.get("title", item.get("title", ""))
        lines.append(
            "| {order} | {group} | {problem} | {title} | {difficulty} | {access} | {status} | {source} |".format(
                order=item.get("order", ""),
                group=escape_cell(str(item.get("group", ""))),
                problem=problem_link(root, canonical_id, catalog),
                title=escape_cell(str(title)),
                difficulty=escape_cell(str(item.get("difficulty", ""))),
                access=access_label(item, catalog_entry),
                status=escape_cell(str(status)),
                source=markdown_link("source", str(item.get("sourceUrl", ""))),
            )
        )
    lines.append("")
    return "\n".join(lines)


def render_pending_coverage(manifests: list[dict[str, Any]], catalog: dict[str, dict[str, Any]]) -> str:
    all_items: list[tuple[str, dict[str, Any]]] = []
    for manifest in manifests:
        payload = manifest["payload"]
        collection_id = str(payload.get("collectionId", ""))
        for item in payload.get("items", []):
            if isinstance(item, dict):
                all_items.append((collection_id, item))

    unique_items: dict[str, dict[str, Any]] = {}
    for collection_id, item in all_items:
        canonical_id = item.get("canonicalId")
        if not isinstance(canonical_id, str):
            continue
        entry = unique_items.setdefault(
            canonical_id,
            {
                "title": item.get("title", ""),
                "difficulty": item.get("difficulty", ""),
                "sourceUrl": item.get("sourceUrl", ""),
                "collections": set(),
                "groups": set(),
            },
        )
        entry["collections"].add(collection_id)
        if item.get("group"):
            entry["groups"].add(str(item["group"]))

    remaining_unique = {
        canonical_id: metadata
        for canonical_id, metadata in unique_items.items()
        if canonical_id not in catalog
    }
    pending_memberships = [
        (collection_id, item)
        for collection_id, item in all_items
        if item.get("canonicalId") not in catalog
    ]

    lines = [
        "# Pending Coding Problem Coverage",
        "",
        "- Source: metadata-only manifests under `resources/source-intake/coding-lists/`",
        "- Scope: exact pending source-list memberships and unique canonical problems not yet implemented under `05-coding-problems/problem-bank/`",
        "- This file is generated by `python3 -B scripts/generate_coding_problem_collections.py`.",
        "",
        "## Summary",
        "",
        "| Metric | Count |",
        "|---|---:|",
        f"| Canonical folders present | {len(catalog)} |",
        f"| Unique canonical source problems | {len(unique_items)} |",
        f"| Unique canonical source problems remaining | {len(remaining_unique)} |",
        f"| Source-list memberships total | {len(all_items)} |",
        f"| Source-list memberships remaining | {len(pending_memberships)} |",
        "",
        "## Collection Counts",
        "",
        "| Collection | Verified memberships | Pending memberships | Total |",
        "|---|---:|---:|---:|",
    ]
    for manifest in manifests:
        payload = manifest["payload"]
        collection_id = payload["collectionId"]
        items = payload.get("items", [])
        verified = sum(1 for item in items if item.get("canonicalId") in catalog)
        pending = len(items) - verified
        lines.append(f"| {escape_cell(str(collection_id))} | {verified} | {pending} | {len(items)} |")

    lines.extend(
        [
            "",
            "## Estimated Execution Time",
            "",
            "These are planning estimates, not validation guarantees. A completed batch includes clean-room README/cases/solutions, Java and Python implementations, generated collection refresh, Python driver execution, Java driver execution, repo smoke, artifact checks, and at least one review/audit loop.",
            "",
            "| Scope | Remaining unique problems | Batch size | Estimated batches | Estimated focused engineering time |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    scoped_ids = [
        ("Finish LeetCode Top 150", pending_ids_for_collection(manifests, catalog, "leetcode-top-150")),
        ("Finish Grind 169 remaining beyond current bank", pending_ids_for_collection(manifests, catalog, "grind-169")),
        ("Finish NeetCode All remaining beyond current bank", pending_ids_for_collection(manifests, catalog, "neetcode-all")),
        ("Finish all unique source problems", set(remaining_unique)),
    ]
    for label, ids in scoped_ids:
        count = len(ids)
        batches = (count + 7) // 8
        low_hours = batches * 2.5
        high_hours = batches * 4
        lines.append(f"| {label} | {count} | 8 | {batches} | {low_hours:.1f}-{high_hours:.1f} hours |")

    lines.extend(
        [
            "",
            "## Pending Unique Canonical Problems",
            "",
            "| Canonical ID | Title | Difficulty | Collections | Groups | Source |",
            "|---|---|---|---|---|---|",
        ]
    )
    for canonical_id, metadata in sorted(remaining_unique.items()):
        collections = ", ".join(sorted(metadata["collections"]))
        groups = ", ".join(sorted(metadata["groups"]))
        lines.append(
            "| {canonical_id} | {title} | {difficulty} | {collections} | {groups} | {source} |".format(
                canonical_id=f"`{escape_cell(canonical_id)}`",
                title=escape_cell(str(metadata["title"])),
                difficulty=escape_cell(str(metadata["difficulty"])),
                collections=escape_cell(collections),
                groups=escape_cell(groups),
                source=markdown_link("source", str(metadata["sourceUrl"])),
            )
        )

    for manifest in manifests:
        payload = manifest["payload"]
        collection_id = payload["collectionId"]
        lines.extend(
            [
                "",
                f"## Pending Memberships: {collection_id}",
                "",
                "| Order | Group | Canonical ID | Title | Difficulty | Source |",
                "|---:|---|---|---|---|---|",
            ]
        )
        for item in sorted(payload.get("items", []), key=lambda value: value.get("order", 0)):
            if item.get("canonicalId") in catalog:
                continue
            lines.append(
                "| {order} | {group} | {canonical_id} | {title} | {difficulty} | {source} |".format(
                    order=item.get("order", ""),
                    group=escape_cell(str(item.get("group", ""))),
                    canonical_id=f"`{escape_cell(str(item.get('canonicalId', '')))}`",
                    title=escape_cell(str(item.get("title", ""))),
                    difficulty=escape_cell(str(item.get("difficulty", ""))),
                    source=markdown_link("source", str(item.get("sourceUrl", ""))),
                )
            )
    lines.append("")
    return "\n".join(lines)


def pending_ids_for_collection(
    manifests: list[dict[str, Any]],
    catalog: dict[str, dict[str, Any]],
    collection_id: str,
) -> set[str]:
    pending: set[str] = set()
    for manifest in manifests:
        payload = manifest["payload"]
        if payload.get("collectionId") != collection_id:
            continue
        for item in payload.get("items", []):
            canonical_id = item.get("canonicalId")
            if isinstance(canonical_id, str) and canonical_id not in catalog:
                pending.add(canonical_id)
    return pending


def access_label(item: dict[str, Any], catalog_entry: dict[str, Any] | None = None) -> str:
    canonical_paid_only = (catalog_entry or {}).get("paidOnly")
    if isinstance(canonical_paid_only, bool):
        return "paid" if canonical_paid_only else "free"
    if "paidOnly" not in item:
        return "unknown"
    return "paid" if item.get("paidOnly") is True else "free"


def collection_page_path(root: Path, collection_id: str) -> Path:
    if not COLLECTION_ID_PATTERN.fullmatch(collection_id):
        raise ValueError(f"unsafe collection id: {collection_id}")
    collection_root = (root / COLLECTION_DIR).resolve()
    output_path = (collection_root / f"{collection_id}.md").resolve()
    output_path.relative_to(collection_root)
    return output_path


def problem_link(
    root: Path,
    canonical_id: str,
    catalog: dict[str, dict[str, Any]],
    fallback: str | None = None,
) -> str:
    label = canonical_id
    if not CANONICAL_ID_PATTERN.fullmatch(canonical_id):
        return f"`{escape_cell(fallback or canonical_id)}`"
    if canonical_id in catalog:
        relative = relative_markdown_path(root / COLLECTION_DIR, root / PROBLEM_BANK_DIR / canonical_id)
        return markdown_link(label, relative)
    return f"`{escape_cell(label)}`"


def relative_markdown_path(from_dir: Path, target: Path) -> str:
    relative = Path(os.path.relpath(target, from_dir)).as_posix()
    return relative + "/"


def markdown_link(label: str, href: str) -> str:
    if not href:
        return ""
    return f"[{escape_cell(label)}]({href})"


def escape_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")
