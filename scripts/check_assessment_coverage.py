#!/usr/bin/env python3
"""Validate and render assessment coverage across quizzes, flashcards, and interviews."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Sequence


MATRIX_PATH = Path("resources/ASSESSMENT-COVERAGE-MATRIX.md")
INTERVIEW_DATA = Path("apps/portal/src/components/interview/interview-data.ts")
DERIVATIVE_REVIEW_LEDGER = Path("resources/source-intake/temp-upload/derivative-review-ledger.csv")
IGNORED_FLASHCARDS = {"README.md", "AGENTS.md"}
BLOCKING_REVIEW_STATUSES = {"blocked", "needs-review"}
CODING_PACK_ORDER = [
    "two-pointers",
    "sliding-window",
    "binary-search",
    "bfs-dfs",
    "dynamic-programming",
    "greedy",
    "backtracking",
    "heap-priority-queue",
    "trie",
    "union-find",
]
CODING_PACK_TITLES = {
    "bfs-dfs": "BFS/DFS",
    "heap-priority-queue": "Heap / Priority Queue",
    "union-find": "Union-Find",
}

QUESTION_RE = re.compile(r"^#{2,3} Question\s+\d+\b", re.MULTILINE)
TABLE_ANSWER_RE = re.compile(r"^\|\s*\d+\s*\|\s*(?:\*\*)?[A-D](?:\*\*)?", re.MULTILINE)
NUMBERED_ANSWER_RE = re.compile(r"^\s*\d+\s*[-.)]\s*(?:\*\*)?[A-D](?:\*\*)?\b", re.MULTILINE)
ANSWER_MARKER_RE = re.compile(r"^\*\*Answer:", re.MULTILINE | re.IGNORECASE)
CARD_RE = re.compile(r"^### Card\s+\d+\b", re.MULTILINE)
FRONT_RE = re.compile(r"^\s*(?:\*\*)?Front:(?:\*\*)?", re.MULTILINE)

MATRIX_COLUMNS = [
    "section",
    "family",
    "slug",
    "title",
    "source_path",
    "portal_visible",
    "portal_route",
    "quiz_path",
    "quiz_questions",
    "answer_path",
    "answer_rows",
    "answer_reveal_route",
    "flashcard_path",
    "flashcards",
    "solution_path",
    "interview_type",
    "interview_route",
    "solution_reveal_route",
    "status",
    "findings",
]


@dataclass(frozen=True)
class Finding:
    kind: str
    slug: str
    path: str
    message: str


@dataclass(frozen=True)
class QuizAsset:
    slug: str
    path: str
    questions: int


@dataclass(frozen=True)
class AnswerAsset:
    slug: str
    path: str
    rows: int


@dataclass(frozen=True)
class FlashcardAsset:
    slug: str
    path: str
    cards: int
    fronts: int


@dataclass(frozen=True)
class InterviewAsset:
    slug: str
    coverage_slug: str
    title: str
    interview_type: str
    solution_path: str
    interview_route: str
    solution_reveal_route: str


@dataclass(frozen=True)
class MatrixRow:
    section: str
    family: str
    slug: str
    title: str
    source_path: str
    portal_visible: str
    portal_route: str
    quiz_path: str
    quiz_questions: str
    answer_path: str
    answer_rows: str
    answer_reveal_route: str
    flashcard_path: str
    flashcards: str
    solution_path: str
    interview_type: str
    interview_route: str
    solution_reveal_route: str
    status: str
    findings: str

    def cells(self) -> list[str]:
        return [str(getattr(self, column)) for column in MATRIX_COLUMNS]


def visible_file(path: Path) -> bool:
    return path.is_file() and not path.is_symlink() and not path.name.startswith(".")


def relative_path(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def strip_suffix(value: str, suffix: str) -> str:
    return value[: -len(suffix)] if value.endswith(suffix) else value


def strip_prefix(value: str, prefix: str) -> str:
    return value[len(prefix) :] if value.startswith(prefix) else value


def title_from_slug(slug: str) -> str:
    if slug in CODING_PACK_TITLES:
        return CODING_PACK_TITLES[slug]
    return " ".join(word.capitalize() for word in slug.split("-"))


def normalize_source_path(candidate: str) -> str | None:
    if not candidate or "\0" in candidate or "\\" in candidate:
        return None
    path = Path(candidate)
    if path.is_absolute():
        return None
    parts = candidate.replace("//", "/").strip("/").split("/")
    if any(part in {"", ".", ".."} for part in parts):
        return None
    return "/".join(parts)


def blocked_source_paths(root: Path) -> list[tuple[str, bool]]:
    path = root / DERIVATIVE_REVIEW_LEDGER
    if not visible_file(path):
        return []
    rows: list[tuple[str, bool]] = []
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if "artifact_path" not in (reader.fieldnames or []) or "review_status" not in (reader.fieldnames or []):
            return []
        for row in reader:
            status = (row.get("review_status") or "").strip().lower()
            if status not in BLOCKING_REVIEW_STATUSES:
                continue
            raw_path = (row.get("artifact_path") or "").strip()
            is_prefix = raw_path.endswith("/")
            normalized = normalize_source_path(raw_path)
            if normalized:
                rows.append((f"{normalized.rstrip('/')}/" if is_prefix else normalized, is_prefix))
    return rows


def is_blocked(relative: str, blocked_paths: list[tuple[str, bool]]) -> bool:
    normalized = normalize_source_path(relative)
    if normalized is None:
        return True
    return any(
        normalized.startswith(blocked_path) if is_prefix else normalized == blocked_path
        for blocked_path, is_prefix in blocked_paths
    )


def count_answer_rows(text: str) -> int:
    table_rows = len(TABLE_ANSWER_RE.findall(text))
    if table_rows:
        return table_rows
    question_headings = len(QUESTION_RE.findall(text))
    answer_markers = len(ANSWER_MARKER_RE.findall(text))
    if question_headings and answer_markers:
        return min(question_headings, answer_markers)
    match = re.search(r"^## Answers\s*$", text, re.MULTILINE)
    answer_text = text
    if match:
        answer_text = text[match.end() :]
        boundary = re.search(r"^## (?!Answers|Question)", answer_text, re.MULTILINE)
        if boundary:
            answer_text = answer_text[: boundary.start()]
    return len(NUMBERED_ANSWER_RE.findall(answer_text))


def discover_quizzes(root: Path, blocked_paths: list[tuple[str, bool]]) -> dict[str, QuizAsset]:
    directory = root / "quizzes"
    if not directory.is_dir() or directory.is_symlink():
        return {}
    assets: dict[str, QuizAsset] = {}
    for path in sorted(directory.glob("*-quiz.md")):
        if not visible_file(path):
            continue
        relative = relative_path(root, path)
        if is_blocked(relative, blocked_paths):
            continue
        slug = strip_suffix(path.name, "-quiz.md")
        text = path.read_text(encoding="utf-8")
        assets[slug] = QuizAsset(slug, relative, len(QUESTION_RE.findall(text)))
    return assets


def discover_answers(root: Path, blocked_paths: list[tuple[str, bool]]) -> dict[str, AnswerAsset]:
    directory = root / "quizzes" / "answers"
    if not directory.is_dir() or directory.is_symlink():
        return {}
    assets: dict[str, AnswerAsset] = {}
    for path in sorted(directory.glob("*-answers.md")):
        if not visible_file(path):
            continue
        relative = relative_path(root, path)
        if is_blocked(relative, blocked_paths):
            continue
        slug = strip_suffix(path.name, "-answers.md")
        text = path.read_text(encoding="utf-8")
        assets[slug] = AnswerAsset(slug, relative, count_answer_rows(text))
    return assets


def discover_flashcards(root: Path) -> dict[str, FlashcardAsset]:
    directory = root / "flashcards"
    if not directory.is_dir() or directory.is_symlink():
        return {}
    assets: dict[str, FlashcardAsset] = {}
    for path in sorted(directory.glob("*.md")):
        if not visible_file(path) or path.name in IGNORED_FLASHCARDS:
            continue
        slug = strip_suffix(path.name, ".md")
        text = path.read_text(encoding="utf-8")
        assets[slug] = FlashcardAsset(slug, relative_path(root, path), len(CARD_RE.findall(text)), len(FRONT_RE.findall(text)))
    return assets


def interview_array_text(text: str) -> str:
    match = re.search(
        r"export\s+const\s+INTERVIEW_PROBLEMS[^=]*=\s*\[(?P<body>.*?)\]\s*;",
        text,
        re.DOTALL,
    )
    return match.group("body") if match else ""


def static_interview_entries(root: Path, blocked_paths: list[tuple[str, bool]]) -> list[dict[str, str]]:
    path = root / INTERVIEW_DATA
    if not visible_file(path):
        return []
    entries: list[dict[str, str]] = []
    for object_match in re.finditer(r"\{(?P<object>.*?)\}", interview_array_text(path.read_text(encoding="utf-8")), re.DOTALL):
        fields = dict(
            re.findall(
                r"\b(slug|title|type|solutionPath)\s*:\s*[\"']([^\"']+)[\"']",
                object_match.group("object"),
            )
        )
        if not fields or fields.get("type") == "coding":
            continue
        solution_path = fields.get("solutionPath", "")
        if solution_path and not is_blocked(solution_path, blocked_paths):
            entries.append(fields)
    return entries


def coding_solution_entries(root: Path, blocked_paths: list[tuple[str, bool]]) -> list[dict[str, str]]:
    directory = root / "solutions"
    if not directory.is_dir() or directory.is_symlink():
        return []
    entries = []
    for path in sorted(directory.glob("coding-*.md")):
        if not visible_file(path):
            continue
        solution_path = relative_path(root, path)
        if is_blocked(solution_path, blocked_paths):
            continue
        slug = strip_suffix(strip_prefix(path.name, "coding-"), ".md")
        entries.append(
            {
                "slug": f"{slug}-pack",
                "title": f"{title_from_slug(slug)} Pack",
                "type": "coding",
                "solutionPath": solution_path,
            }
        )
    return sorted(entries, key=lambda entry: coding_sort_key(strip_suffix(entry["slug"], "-pack")))


def coding_sort_key(slug: str) -> tuple[int, str]:
    try:
        return (CODING_PACK_ORDER.index(slug), slug)
    except ValueError:
        return (len(CODING_PACK_ORDER), slug)


def discover_interviews(root: Path, blocked_paths: list[tuple[str, bool]]) -> dict[str, InterviewAsset]:
    assets: dict[str, InterviewAsset] = {}
    for entry in [*static_interview_entries(root, blocked_paths), *coding_solution_entries(root, blocked_paths)]:
        slug = entry["slug"]
        interview_type = entry["type"]
        coverage_slug = strip_suffix(slug, "-pack") if interview_type == "coding" else slug
        assets[coverage_slug] = InterviewAsset(
            slug=slug,
            coverage_slug=coverage_slug,
            title=entry.get("title") or title_from_slug(coverage_slug),
            interview_type=interview_type,
            solution_path=entry.get("solutionPath", ""),
            interview_route=f"/interview/{interview_type}/{slug}",
            solution_reveal_route=f"/reveal/solution/{interview_type}/{slug}",
        )
    return assets


def family_for_slug(slug: str, interview: InterviewAsset | None) -> str:
    if interview:
        return interview.interview_type
    if slug in CODING_PACK_ORDER:
        return "coding"
    if slug.startswith("genai-"):
        return "genai"
    if slug.startswith("hld-"):
        return "hld"
    if slug.startswith("lld-"):
        return "lld"
    if slug.startswith("ai-coding"):
        return "ai-coding"
    if slug in {"behavioral-interviews", "salary-negotiation"}:
        return "career"
    if slug in {"design-patterns", "infra-technologies"}:
        return "fundamentals"
    return "assessment"


def section_for_assets(quiz: QuizAsset | None, flashcard: FlashcardAsset | None, interview: InterviewAsset | None, answer: AnswerAsset | None) -> str:
    sections = []
    if quiz or answer:
        sections.append("quiz")
    if flashcard:
        sections.append("flashcard")
    if interview:
        sections.append("interview-mode")
    return "+".join(sections) if sections else "missing"


def portal_visibility(quiz: QuizAsset | None, answer: AnswerAsset | None, interview: InterviewAsset | None, flashcard: FlashcardAsset | None) -> str:
    if quiz or interview:
        return "yes"
    if answer:
        return "missing"
    if flashcard:
        return "no"
    return "missing"


def source_path_for(quiz: QuizAsset | None, flashcard: FlashcardAsset | None, interview: InterviewAsset | None, answer: AnswerAsset | None) -> str:
    for asset in (quiz, flashcard, interview, answer):
        if asset is None:
            continue
        path = getattr(asset, "path", None) or getattr(asset, "solution_path", None)
        if path:
            return path
    return "-"


def family_sort(slug: str, interview: InterviewAsset | None) -> tuple[int, int, str]:
    family_order = {
        "coding": 0,
        "lld": 1,
        "hld": 2,
        "genai-hld": 3,
        "behavioral": 4,
        "career": 5,
        "fundamentals": 6,
        "genai": 7,
        "ai-coding": 8,
        "assessment": 9,
    }
    family = family_for_slug(slug, interview)
    coding_index = CODING_PACK_ORDER.index(slug) if slug in CODING_PACK_ORDER else len(CODING_PACK_ORDER)
    return (family_order.get(family, 99), coding_index, slug)


def build_rows(root: Path) -> tuple[list[MatrixRow], list[Finding]]:
    blocked_paths = blocked_source_paths(root)
    findings: list[Finding] = []
    quizzes = discover_quizzes(root, blocked_paths)
    answers = discover_answers(root, blocked_paths)
    flashcards = discover_flashcards(root)
    interviews = discover_interviews(root, blocked_paths)
    slugs = sorted(set(quizzes) | set(answers) | set(flashcards) | set(interviews), key=lambda slug: family_sort(slug, interviews.get(slug)))

    rows: list[MatrixRow] = []
    for slug in slugs:
        quiz = quizzes.get(slug)
        answer = answers.get(slug)
        flashcard = flashcards.get(slug)
        interview = interviews.get(slug)
        row_findings: list[str] = []
        if quiz and quiz.questions == 0:
            row_findings.append("quiz has no counted questions")
            findings.append(Finding("empty-quiz", slug, quiz.path, "quiz has no counted questions"))
        if quiz and answer is None:
            row_findings.append("missing answer key")
            findings.append(Finding("missing-answer-key", slug, f"quizzes/answers/{slug}-answers.md", "quiz is missing answer key"))
        if answer and quiz is None:
            row_findings.append("answer has no quiz")
            findings.append(Finding("orphan-answer-key", slug, answer.path, "answer key has no matching quiz"))
        if quiz and answer and quiz.questions != answer.rows:
            row_findings.append(f"answer rows {answer.rows} != quiz questions {quiz.questions}")
            findings.append(Finding("answer-count-mismatch", slug, answer.path, "answer row count does not match quiz question count"))
        if flashcard and flashcard.cards == 0:
            row_findings.append("flashcard deck has no cards")
            findings.append(Finding("empty-flashcard-deck", slug, flashcard.path, "flashcard deck has no counted cards"))
        if flashcard and flashcard.cards != flashcard.fronts:
            row_findings.append(f"fronts {flashcard.fronts} != cards {flashcard.cards}")
            findings.append(Finding("flashcard-front-mismatch", slug, flashcard.path, "flashcard front count does not match card count"))
        if interview and not visible_file(root / interview.solution_path):
            row_findings.append("missing interview solution")
            findings.append(Finding("missing-interview-solution", slug, interview.solution_path, "interview solution file is missing"))
        rows.append(
            MatrixRow(
                section=section_for_assets(quiz, flashcard, interview, answer),
                family=family_for_slug(slug, interview),
                slug=slug,
                title=interview.title if interview else title_from_slug(slug),
                source_path=source_path_for(quiz, flashcard, interview, answer),
                portal_visible=portal_visibility(quiz, answer, interview, flashcard),
                portal_route=f"/quizzes/{slug}" if quiz else (interview.interview_route if interview else "-"),
                quiz_path=quiz.path if quiz else "-",
                quiz_questions=str(quiz.questions) if quiz else "0",
                answer_path=answer.path if answer else "-",
                answer_rows=str(answer.rows) if answer else "0",
                answer_reveal_route=f"/reveal/quiz-answer/{slug}" if quiz and answer else "-",
                flashcard_path=flashcard.path if flashcard else "-",
                flashcards=str(flashcard.cards) if flashcard else "0",
                solution_path=interview.solution_path if interview else "-",
                interview_type=interview.interview_type if interview else "-",
                interview_route=interview.interview_route if interview else "-",
                solution_reveal_route=interview.solution_reveal_route if interview else "-",
                status="validated" if not row_findings else "issue",
                findings="; ".join(row_findings) if row_findings else "-",
            )
        )
    return rows, findings


def escape_cell(value: str) -> str:
    return value.replace("\n", " ").replace("|", "\\|").strip()


def render_matrix(rows: list[MatrixRow]) -> str:
    lines = [
        "# Assessment Coverage Matrix",
        "",
        "Generated by `python3 -B scripts/check_assessment_coverage.py --write`.",
        "",
        "| " + " | ".join(MATRIX_COLUMNS) + " |",
        "|" + "|".join("---" for _ in MATRIX_COLUMNS) + "|",
    ]
    for row in rows:
        lines.append("| " + " | ".join(escape_cell(cell) for cell in row.cells()) + " |")
    lines.append("")
    return "\n".join(lines)


def check_matrix(root: Path, rows: list[MatrixRow], write: bool) -> list[Finding]:
    expected = render_matrix(rows)
    path = root / MATRIX_PATH
    if write:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(expected, encoding="utf-8")
        return []
    if not visible_file(path):
        return [Finding("missing-assessment-matrix", "assessment", MATRIX_PATH.as_posix(), "run with --write to create the matrix")]
    if path.read_text(encoding="utf-8") != expected:
        return [Finding("stale-assessment-matrix", "assessment", MATRIX_PATH.as_posix(), "run with --write to refresh the matrix")]
    return []


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Repository root to scan.")
    parser.add_argument("--write", action="store_true", help=f"Write {MATRIX_PATH}.")
    parser.add_argument("--format", choices=("text", "json"), default="text", help="Output format.")
    return parser.parse_args(argv)


def main(argv: Sequence[str]) -> int:
    args = parse_args(argv)
    root = args.root.resolve()
    rows, findings = build_rows(root)
    findings.extend(check_matrix(root, rows, args.write))
    findings = sorted(findings, key=lambda finding: (finding.kind, finding.slug, finding.path))
    blocked_paths = blocked_source_paths(root)
    summary = {
        "assessment_rows": len(rows),
        "issue_rows": sum(1 for row in rows if row.status == "issue"),
        "quizzes": len(discover_quizzes(root, blocked_paths)),
        "answers": len(discover_answers(root, blocked_paths)),
        "flashcards": len(discover_flashcards(root)),
        "interviews": len(discover_interviews(root, blocked_paths)),
    }
    if args.format == "json":
        print(json.dumps({"ok": not findings, "summary": summary, "findings": [asdict(finding) for finding in findings]}, indent=2))
    else:
        print(
            "summary: "
            f"assessment-rows={summary['assessment_rows']} "
            f"issue-rows={summary['issue_rows']} "
            f"quizzes={summary['quizzes']} "
            f"answers={summary['answers']} "
            f"flashcards={summary['flashcards']} "
            f"interviews={summary['interviews']}"
        )
        if args.write:
            print(f"wrote {MATRIX_PATH}")
        for finding in findings:
            print(f"{finding.kind}: {finding.slug}: {finding.path}: {finding.message}")
        if not findings:
            print("assessment-coverage: ok")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
