#!/usr/bin/env python3
"""Validate portal content inventory counts against CONTENT-UI-MAP.md."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, Sequence


CONTENT_MAP = Path("resources/CONTENT-UI-MAP.md")
VALID_PATTERN_CATEGORIES = {"creational", "structural", "behavioral"}
IGNORED_FLASHCARD_FILES = {"README.md", "AGENTS.md"}
IGNORED_PROMPT_FILES = {"README.md"}
CODING_SUPPORT_DIRS = {"problem-bank", "collections"}
PUBLIC_RESOURCE_CATEGORIES = (
    "study-plans",
    "cheatsheets",
    "interview-tips",
    "templates",
)
EXECUTABLE_SAMPLE_ROOTS = (
    Path("00-theory"),
    Path("03-hld-concepts"),
    Path("06-genai-systems/00-concepts"),
)


@dataclass(frozen=True)
class Section:
    key: str
    inventory_label: str
    portal_label: str | None
    discover: Callable[[Path], int]


@dataclass(frozen=True)
class Finding:
    kind: str
    section: str
    path: str
    expected: int | None = None
    discovered: int | None = None
    message: str = ""


def is_visible_dir(path: Path) -> bool:
    return path.is_dir() and not path.is_symlink() and not path.name.startswith(".")


def is_visible_file(path: Path) -> bool:
    return path.is_file() and not path.is_symlink() and not path.name.startswith(".")


def child_dirs(root: Path, relative: str) -> list[Path]:
    path = root / relative
    if not path.is_dir() or path.is_symlink():
        return []
    return sorted(child for child in path.iterdir() if is_visible_dir(child))


def child_files(root: Path, relative: str, pattern: str = "*.md") -> list[Path]:
    path = root / relative
    if not path.is_dir() or path.is_symlink():
        return []
    return sorted(child for child in path.glob(pattern) if is_visible_file(child))


def count_theory(root: Path) -> int:
    return sum(len(child_files(root, f"00-theory/{area.name}")) for area in child_dirs(root, "00-theory"))


def count_patterns(root: Path) -> int:
    total = 0
    for category in sorted(VALID_PATTERN_CATEGORIES):
        total += len(child_dirs(root, f"01-design-patterns/{category}"))
    return total


def count_dirs(relative: str) -> Callable[[Path], int]:
    return lambda root: len(child_dirs(root, relative))


def coding_pack_slugs(root: Path) -> list[str]:
    return [
        directory.name
        for directory in child_dirs(root, "05-coding-problems")
        if directory.name not in CODING_SUPPORT_DIRS
    ]


def count_coding_pattern_packs(root: Path) -> int:
    return len(coding_pack_slugs(root))


def count_project_dirs(relative: str, required_file: str) -> Callable[[Path], int]:
    def discover(root: Path) -> int:
        return sum(
            1
            for directory in child_dirs(root, relative)
            if (directory / required_file).is_file()
            and not (directory / required_file).is_symlink()
        )

    return discover


def count_quizzes(root: Path) -> int:
    return len(child_files(root, "quizzes", "*-quiz.md"))


def count_flashcards(root: Path) -> int:
    return len(
        [
            deck
            for deck in child_files(root, "flashcards")
            if deck.name not in IGNORED_FLASHCARD_FILES
        ]
    )


def count_prompts(root: Path) -> int:
    return len(
        [
            prompt
            for prompt in child_files(root, "prompts")
            if prompt.name not in IGNORED_PROMPT_FILES
        ]
    )


def count_public_resources(root: Path) -> int:
    total = 0
    for category in PUBLIC_RESOURCE_CATEGORIES:
        directory = root / "resources" / category
        if not directory.is_dir() or directory.is_symlink():
            continue
        if not (directory / "README.md").is_file() or (directory / "README.md").is_symlink():
            continue
        total += len(
            [
                resource
                for resource in child_files(root, f"resources/{category}")
                if resource.name != "README.md"
            ]
        )
    return total


def count_interview_problems(root: Path) -> int:
    return len(interview_problem_entries(root))


def static_interview_problem_entries(root: Path) -> list[dict[str, str]]:
    source = root / "apps/portal/src/components/interview/interview-data.ts"
    if not source.is_file() or source.is_symlink():
        return []
    text = source.read_text(encoding="utf-8")
    match = re.search(
        r"export\s+const\s+INTERVIEW_PROBLEMS[^=]*=\s*\[(?P<body>.*?)\]\s*;",
        text,
        re.DOTALL,
    )
    if not match:
        return []

    entries: list[dict[str, str]] = []
    for object_match in re.finditer(r"\{(?P<object>.*?)\}", match.group("body"), re.DOTALL):
        fields = dict(
            re.findall(
                r"\b(slug|title|type|solutionPath)\s*:\s*[\"']([^\"']+)[\"']",
                object_match.group("object"),
            )
        )
        if fields:
            entries.append(fields)
    return entries


def coding_solution_entries(root: Path) -> list[dict[str, str]]:
    solutions_root = root / "solutions"
    if not solutions_root.is_dir() or solutions_root.is_symlink():
        return []

    entries = []
    for path in sorted(solutions_root.glob("coding-*.md")):
        if not path.is_file() or path.is_symlink():
            continue
        slug = path.name.replace("coding-", "").replace(".md", "")
        entries.append(
            {
                "slug": f"{slug}-pack",
                "title": f"{title_from_slug(slug)} Pack",
                "type": "coding",
                "solutionPath": f"solutions/{path.name}",
            }
        )
    return entries


def interview_problem_entries(root: Path) -> list[dict[str, str]]:
    static_entries = [
        entry
        for entry in static_interview_problem_entries(root)
        if entry.get("type") != "coding"
    ]
    return [*static_entries, *coding_solution_entries(root)]


def title_from_slug(slug: str) -> str:
    special = {
        "bfs-dfs": "BFS/DFS",
        "heap-priority-queue": "Heap / Priority Queue",
        "union-find": "Union-Find",
    }
    if slug in special:
        return special[slug]
    return " ".join(word.capitalize() for word in slug.split("-"))


def count_executable_samples(root: Path) -> int:
    total = 0
    for relative_root in EXECUTABLE_SAMPLE_ROOTS:
        directory = root / relative_root
        if not directory.is_dir() or directory.is_symlink():
            continue
        for path in directory.rglob("*"):
            if (
                path.is_file()
                and path.suffix in {".java", ".py"}
                and "tests" not in path.parts
                and "__pycache__" not in path.parts
                and path.name != "__init__.py"
            ):
                total += 1
    return total


SECTIONS = [
    Section("theory", "Theory articles", "Theory", count_theory),
    Section("patterns", "Design Patterns", "Design Patterns", count_patterns),
    Section(
        "lld-projects",
        "LLD Projects",
        "LLD Projects",
        count_project_dirs("02-lld-projects", "PROBLEM.md"),
    ),
    Section("hld-concepts", "HLD Concepts", "HLD Concepts", count_dirs("03-hld-concepts")),
    Section("hld-projects", "HLD Projects", "HLD Projects", count_dirs("04-hld-projects")),
    Section(
        "genai-concepts",
        "GenAI Concepts",
        "GenAI Concepts",
        count_dirs("06-genai-systems/00-concepts"),
    ),
    Section(
        "genai-lld",
        "GenAI LLD Projects",
        "GenAI LLD",
        count_dirs("06-genai-systems/01-llm-lld-projects"),
    ),
    Section(
        "genai-hld",
        "GenAI HLD Projects",
        "GenAI HLD",
        count_dirs("06-genai-systems/02-llm-hld-projects"),
    ),
    Section("coding", "Coding Pattern Packs", "Coding Patterns", count_coding_pattern_packs),
    Section("case-studies", "Case Studies", "Case Studies", count_dirs("case-studies")),
    Section("quizzes", "Quizzes", "Quizzes", count_quizzes),
    Section("interview-mode", "Interview Problems", "Interview Mode", count_interview_problems),
    Section("resources", "Resources", "Resources", count_public_resources),
    Section("flashcards", "Flashcard Decks", None, count_flashcards),
    Section("prompts", "Prompt Workflow Files", None, count_prompts),
    Section("executable-samples", "Executable Sample Files", None, count_executable_samples),
]
SECTION_BY_KEY = {section.key: section for section in SECTIONS}


def parse_markdown_table(markdown: str, heading: str) -> list[list[str]]:
    heading_match = re.search(rf"^## {re.escape(heading)}\s*$", markdown, re.MULTILINE)
    if not heading_match:
        return []

    lines = markdown[heading_match.end() :].splitlines()
    table_lines = []
    in_table = False
    for line in lines:
        if line.startswith("## "):
            break
        if line.strip().startswith("|"):
            table_lines.append(line.strip())
            in_table = True
        elif in_table and line.strip():
            break

    rows: list[list[str]] = []
    for line in table_lines:
        cells = split_table_row(line)
        if all(set(cell) <= {"-"} for cell in cells):
            continue
        rows.append(cells)
    return rows[1:] if rows else []


def split_table_row(line: str) -> list[str]:
    cells = []
    current = []
    escaped = False
    for char in line.strip().strip("|"):
        if char == "|" and not escaped:
            cells.append("".join(current).replace("\\|", "|").strip())
            current = []
        else:
            current.append(char)
        escaped = char == "\\" and not escaped
        if char != "\\":
            escaped = False
    cells.append("".join(current).replace("\\|", "|").strip())
    return cells


def parse_int(value: str) -> int | None:
    match = re.search(r"\d+", value)
    return int(match.group(0)) if match else None


def content_map_counts(root: Path) -> tuple[dict[str, int], dict[str, int]]:
    path = root / CONTENT_MAP
    if not path.is_file() or path.is_symlink():
        return {}, {}

    markdown = path.read_text(encoding="utf-8")
    inventory_counts = {}
    for row in parse_markdown_table(markdown, "Content Inventory"):
        if len(row) < 2:
            continue
        count = parse_int(row[1])
        if count is not None:
            inventory_counts[row[0]] = count

    portal_counts = {}
    for row in parse_markdown_table(markdown, "Portal-Covered Categories"):
        if len(row) < 9:
            continue
        count = parse_int(row[8])
        if count is not None:
            portal_counts[row[1]] = count

    return inventory_counts, portal_counts


def selected_sections(keys: Sequence[str] | None) -> list[Section]:
    if not keys:
        return SECTIONS
    sections = []
    for key in keys:
        if key not in SECTION_BY_KEY:
            raise ValueError(f"unknown section: {key}")
        sections.append(SECTION_BY_KEY[key])
    return sections


def check_inventory(root: Path, sections: list[Section]) -> tuple[dict[str, int], list[Finding], int, int]:
    inventory_counts, portal_counts = content_map_counts(root)
    discovered = {section.key: section.discover(root) for section in sections}
    findings: list[Finding] = []
    selected_keys = {section.key for section in sections}

    for section in sections:
        actual = discovered[section.key]
        expected = inventory_counts.get(section.inventory_label)
        if expected is None:
            findings.append(
                Finding(
                    "missing-catalog-row",
                    section.inventory_label,
                    CONTENT_MAP.as_posix(),
                    discovered=actual,
                    message="inventory row is missing",
                )
            )
        elif expected != actual:
            findings.append(
                Finding(
                    "stale-count",
                    section.inventory_label,
                    CONTENT_MAP.as_posix(),
                    expected=expected,
                    discovered=actual,
                    message="inventory count differs from discovery",
                )
            )

        if section.portal_label is None:
            continue
        portal_expected = portal_counts.get(section.portal_label)
        if portal_expected is None:
            findings.append(
                Finding(
                    "missing-catalog-row",
                    section.portal_label,
                    CONTENT_MAP.as_posix(),
                    discovered=actual,
                    message="portal category row is missing",
                )
            )
        elif portal_expected != actual:
            findings.append(
                Finding(
                    "stale-count",
                    section.portal_label,
                    CONTENT_MAP.as_posix(),
                    expected=portal_expected,
                    discovered=actual,
                    message="portal category count differs from discovery",
                )
            )

    if {"coding", "interview-mode"}.issubset(selected_keys):
        entries = interview_problem_entries(root)
        by_solution_path = {
            entry.get("solutionPath", ""): entry for entry in entries if entry.get("solutionPath")
        }
        for slug in sorted(coding_pack_slugs(root)):
            expected_solution = f"solutions/coding-{slug}.md"
            expected_slug = f"{slug}-pack"
            expected_title = f"{title_from_slug(slug)} Pack"
            entry = by_solution_path.get(expected_solution)
            if entry is None:
                findings.append(
                    Finding(
                        "missing-interview-coding-pack",
                        "Interview Mode",
                        "apps/portal/src/components/interview/interview-data.ts",
                        message=(
                            f"coding pack {slug} is missing a "
                            f"{expected_solution} Interview Mode entry"
                        ),
                    )
                )
                continue

            for field, expected in (
                ("type", "coding"),
                ("slug", expected_slug),
                ("title", expected_title),
            ):
                actual = entry.get(field)
                if actual != expected:
                    findings.append(
                        Finding(
                            "invalid-interview-coding-pack",
                            "Interview Mode",
                            "apps/portal/src/components/interview/interview-data.ts",
                            message=(
                                f"coding pack {slug} has {field}={actual!r}; "
                                f"expected {expected!r}"
                            ),
                        )
                    )

            solution_path = root / expected_solution
            if not solution_path.is_file() or solution_path.is_symlink():
                findings.append(
                    Finding(
                        "missing-interview-solution-file",
                        "Interview Mode",
                        expected_solution,
                        message=f"coding pack {slug} solution file is missing",
                    )
                )

        for solution_path in sorted(
            path
            for path in by_solution_path
            if path.startswith("solutions/coding-") and path.endswith(".md")
        ):
            slug = solution_path[len("solutions/coding-") : -len(".md")]
            if slug not in set(coding_pack_slugs(root)):
                findings.append(
                    Finding(
                        "stale-interview-coding-pack",
                        "Interview Mode",
                        "apps/portal/src/components/interview/interview-data.ts",
                        message=f"Interview Mode references missing coding pack {slug}",
                    )
                )

    return (
        discovered,
        sorted(findings, key=lambda item: (item.kind, item.section)),
        len(sections),
        len([section for section in sections if section.portal_label is not None]),
    )


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate portal content inventory counts against CONTENT-UI-MAP.md."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Repository root to scan.")
    parser.add_argument(
        "--sections",
        nargs="+",
        choices=sorted(SECTION_BY_KEY),
        help="Optional section keys to scan.",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format.",
    )
    return parser.parse_args(argv)


def print_text(summary: dict[str, int], findings: list[Finding], rows: tuple[int, int]) -> None:
    for finding in findings:
        if finding.kind == "stale-count":
            print(
                f"{finding.kind}: {finding.section} expected {finding.expected} "
                f"discovered {finding.discovered} ({finding.path}; {finding.message})"
            )
        else:
            print(f"{finding.kind}: {finding.section} ({finding.path}; {finding.message})")

    print("summary: " + " ".join(f"{key}={summary[key]}" for key in sorted(summary)))
    print(f"checked {rows[0]} inventory rows")
    print(f"checked {rows[1]} portal rows")
    if findings:
        print(f"found {len(findings)} inventory issue{'s' if len(findings) != 1 else ''}")
    else:
        print("content-inventory: ok")


def main(argv: Sequence[str] | None = None) -> int:
    try:
        args = parse_args(argv or sys.argv[1:])
        root = args.root.resolve()
        sections = selected_sections(args.sections)
        summary, findings, inventory_row_count, portal_row_count = check_inventory(root, sections)
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return 2

    if args.format == "json":
        print(
            json.dumps(
                {
                    "ok": not findings,
                    "summary": summary,
                    "findings": [asdict(finding) for finding in findings],
                },
                sort_keys=True,
            )
        )
    else:
        print_text(summary, findings, (inventory_row_count, portal_row_count))

    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
