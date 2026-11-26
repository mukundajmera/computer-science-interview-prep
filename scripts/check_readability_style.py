#!/usr/bin/env python3
"""Catch obvious placeholder, generic, and wall-of-text Markdown issues."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Sequence


DEFAULT_PATHS = [
    Path("resources/INTERVIEW-READY-CONTENT-RUBRIC.md"),
    Path("00-theory/big-data-structures/merkle-tree.md"),
    Path("00-theory/big-data-structures/trie.md"),
    Path("04-hld-projects/payment-system/PROBLEM.md"),
    Path("04-hld-projects/payment-system/APPROACH.md"),
    Path("04-hld-projects/payment-system/DESIGN.md"),
    Path("04-hld-projects/payment-system/RUBRIC.md"),
    Path("04-hld-projects/payment-system/PITFALLS.md"),
    Path("04-hld-projects/payment-system/FOLLOW-UPS.md"),
    Path("04-hld-projects/payment-system/COMPARISON.md"),
    Path("04-hld-projects/payment-system/STRONG-ANSWER.md"),
    Path("03-hld-concepts/caching/THEORY.md"),
    Path("02-lld-projects/elevator-system/PROBLEM.md"),
    Path("02-lld-projects/elevator-system/APPROACH.md"),
    Path("02-lld-projects/elevator-system/DESIGN.md"),
    Path("02-lld-projects/elevator-system/RUBRIC.md"),
    Path("02-lld-projects/elevator-system/PITFALLS.md"),
    Path("02-lld-projects/elevator-system/FOLLOW-UPS.md"),
    Path("05-coding-problems/sliding-window/README.md"),
    Path("05-coding-problems/sliding-window/01-overview.md"),
    Path("05-coding-problems/sliding-window/02-maximum-sum-subarray-size-k.md"),
    Path("05-coding-problems/sliding-window/03-minimum-size-subarray-sum.md"),
    Path("05-coding-problems/sliding-window/04-longest-substring-without-repeating.md"),
    Path("05-coding-problems/sliding-window/05-longest-substring-at-most-k-distinct.md"),
    Path("05-coding-problems/sliding-window/06-subarrays-with-exactly-k-distinct.md"),
    Path("05-coding-problems/sliding-window/07-permutation-in-string.md"),
    Path("05-coding-problems/sliding-window/08-sliding-window-maximum.md"),
    Path("05-coding-problems/bfs-dfs"),
    Path("05-coding-problems/dynamic-programming"),
    Path("05-coding-problems/greedy"),
    Path("05-coding-problems/backtracking"),
    Path("05-coding-problems/heap-priority-queue"),
    Path("05-coding-problems/trie"),
    Path("05-coding-problems/union-find"),
    Path("quizzes/bfs-dfs-quiz.md"),
    Path("quizzes/dynamic-programming-quiz.md"),
    Path("quizzes/greedy-quiz.md"),
    Path("quizzes/backtracking-quiz.md"),
    Path("quizzes/heap-priority-queue-quiz.md"),
    Path("quizzes/trie-quiz.md"),
    Path("quizzes/union-find-quiz.md"),
    Path("flashcards/bfs-dfs.md"),
    Path("flashcards/dynamic-programming.md"),
    Path("flashcards/greedy.md"),
    Path("flashcards/backtracking.md"),
    Path("flashcards/heap-priority-queue.md"),
    Path("flashcards/trie.md"),
    Path("flashcards/union-find.md"),
    Path("solutions/coding-bfs-dfs.md"),
    Path("solutions/coding-dynamic-programming.md"),
    Path("solutions/coding-greedy.md"),
    Path("solutions/coding-backtracking.md"),
    Path("solutions/coding-heap-priority-queue.md"),
    Path("solutions/coding-trie.md"),
    Path("solutions/coding-union-find.md"),
    Path("06-genai-systems/00-concepts/rag-architecture/README.md"),
]

SKIP_PARTS = {"temp_upload", ".git", "node_modules", ".next", "out", "__pycache__"}
FENCE_RE = re.compile(r"(^|\n)(```|~~~).*?(\n\2[ \t]*$)", re.MULTILINE | re.DOTALL)
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)

BANNED_PHRASES = {
    "TODO": "placeholder marker",
    "TBD": "placeholder marker",
    "Lorem ipsum": "placeholder text",
    "Support core user workflow": "generic HLD requirement",
    "High sustained load": "generic non-functional target",
    "p95 low-latency": "generic latency target",
    "Compute one throughput and one storage estimate": "generic strong-answer outline",
    "Walk write path": "generic strong-answer outline",
}


@dataclass(frozen=True)
class Finding:
    kind: str
    path: str
    line: int
    message: str


def is_within(root: Path, path: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def repository_relative(root: Path, path: Path) -> Path:
    return path.resolve().relative_to(root.resolve())


def should_skip(root: Path, path: Path) -> bool:
    try:
        parts = set(repository_relative(root, path).parts)
    except ValueError:
        return True
    return bool(parts & SKIP_PARTS)


def safe_path(root: Path, relative: Path) -> Path:
    candidate = (root / relative).resolve()
    if not is_within(root, candidate):
        raise ValueError(f"path escapes repository root: {relative}")
    return candidate


def strip_code_fences(markdown: str) -> str:
    return FENCE_RE.sub(lambda match: "\n" * match.group(0).count("\n"), markdown)


def line_for_offset(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def paragraph_blocks(markdown: str) -> list[tuple[int, str]]:
    blocks: list[tuple[int, str]] = []
    current: list[str] = []
    start_line = 1
    for line_number, line in enumerate(markdown.splitlines(), start=1):
        stripped = line.strip()
        is_list_item = stripped.startswith(("-", "*", ">", "```", "~~~")) or bool(
            re.match(r"\d+[.)]\s+", stripped)
        )
        if not stripped or stripped.startswith("#") or stripped.startswith("|") or is_list_item:
            if current:
                blocks.append((start_line, " ".join(current)))
                current = []
            continue
        if not current:
            start_line = line_number
        current.append(stripped)
    if current:
        blocks.append((start_line, " ".join(current)))
    return blocks


def check_empty_headings(markdown: str, path: Path) -> list[Finding]:
    findings: list[Finding] = []
    headings = list(HEADING_RE.finditer(markdown))
    for index, heading in enumerate(headings):
        level = len(heading.group(1))
        if index + 1 < len(headings) and len(headings[index + 1].group(1)) > level:
            continue
        start = heading.end()
        end = headings[index + 1].start() if index + 1 < len(headings) else len(markdown)
        body = markdown[start:end].strip()
        body_without_rules = "\n".join(
            line for line in body.splitlines() if set(line.strip()) != {"-"}
        ).strip()
        if not body_without_rules:
            findings.append(
                Finding(
                    "empty-section",
                    path.as_posix(),
                    line_for_offset(markdown, heading.start()),
                    f"section has no body: {heading.group(2).strip()}",
                )
            )
    return findings


def check_markdown(path: Path, markdown: str) -> list[Finding]:
    findings: list[Finding] = []
    stripped = strip_code_fences(markdown)

    for phrase, reason in BANNED_PHRASES.items():
        pattern = re.compile(re.escape(phrase), re.IGNORECASE)
        for match in pattern.finditer(stripped):
            findings.append(
                Finding(
                    "banned-phrase",
                    path.as_posix(),
                    line_for_offset(stripped, match.start()),
                    f"{reason}: {phrase}",
                )
            )

    for line, paragraph in paragraph_blocks(stripped):
        word_count = len(re.findall(r"\b\w+\b", paragraph))
        if word_count > 130:
            findings.append(
                Finding(
                    "long-paragraph",
                    path.as_posix(),
                    line,
                    f"paragraph has {word_count} words; split for scanability",
                )
            )

    findings.extend(check_empty_headings(markdown, path))

    if path.name == "STRONG-ANSWER.md" and "Say:" not in markdown:
        findings.append(
            Finding(
                "weak-strong-answer",
                path.as_posix(),
                1,
                "strong answer should include candidate-speakable 'Say:' lines",
            )
        )

    return findings


def selected_paths(args: argparse.Namespace) -> list[Path]:
    return [Path(path) for path in (args.paths or DEFAULT_PATHS)]


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate scoped Markdown readability.")
    parser.add_argument("paths", nargs="*", help="Markdown files or directories to check.")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Repository root.")
    parser.add_argument("--waves", nargs="+", help="Accepted for batch scripts; current checker uses scoped default files.")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    return parser.parse_args(argv)


def expand_paths(root: Path, paths: Sequence[Path]) -> list[Path]:
    expanded: list[Path] = []
    for relative in paths:
        path = safe_path(root, relative)
        if should_skip(root, path):
            continue
        if path.is_dir():
            for child in sorted(path.rglob("*.md")):
                if not should_skip(root, child) and child.is_file() and not child.is_symlink():
                    expanded.append(child)
        elif path.is_file() and not path.is_symlink():
            expanded.append(path)
        else:
            expanded.append(path)
    return expanded


def print_text(findings: list[Finding], checked_count: int) -> None:
    for finding in findings:
        print(f"{finding.kind}: {finding.path}:{finding.line} ({finding.message})")
    print(f"checked {checked_count} markdown readability file{'s' if checked_count != 1 else ''}")
    if findings:
        print(f"found {len(findings)} readability issue{'s' if len(findings) != 1 else ''}")
    else:
        print("readability-style: ok")


def main(argv: Sequence[str] | None = None) -> int:
    try:
        args = parse_args(argv or sys.argv[1:])
        root = args.root.resolve()
        paths = expand_paths(root, selected_paths(args))
        findings: list[Finding] = []
        checked = 0
        for path in paths:
            if should_skip(root, path):
                continue
            if not path.exists():
                findings.append(Finding("missing-file", path.as_posix(), 1, "file does not exist"))
                continue
            checked += 1
            relative = repository_relative(root, path)
            findings.extend(check_markdown(relative, path.read_text(encoding="utf-8")))
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return 2

    if args.format == "json":
        print(
            json.dumps(
                {
                    "ok": not findings,
                    "checked": checked,
                    "findings": [asdict(finding) for finding in findings],
                },
                sort_keys=True,
            )
        )
    else:
        print_text(findings, checked)
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
