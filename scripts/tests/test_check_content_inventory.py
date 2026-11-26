import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "check_content_inventory.py"


CONTENT_MAP_TEMPLATE = """# Content Map

## Content Inventory

| Section | Items | Source |
|---------|-------|--------|
{inventory_rows}

## Portal-Covered Categories

| # | Category | Source Directory | File / Dir Pattern | Registry Key (`types.ts`) | Portal Route | Nav Link | Discovery Method | Items |
|---|----------|------------------|--------------------|--------------------------|--------------|----------|------------------|-------|
{portal_rows}
"""


def write_file(path: Path, content: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_minimal_repo(root: Path) -> None:
    write_file(root / "00-theory" / "oop" / "solid.md")
    write_file(root / "00-theory" / "oop" / "dry.md")
    (root / "01-design-patterns" / "creational" / "singleton").mkdir(parents=True)
    (root / "01-design-patterns" / "structural" / "adapter").mkdir(parents=True)
    write_file(root / "02-lld-projects" / "parking-lot" / "PROBLEM.md")
    (root / "03-hld-concepts" / "caching").mkdir(parents=True)
    (root / "04-hld-projects" / "url-shortener").mkdir(parents=True)
    (root / "05-coding-problems" / "two-pointers").mkdir(parents=True)
    write_file(root / "06-genai-systems" / "00-concepts" / "rag" / "README.md")
    (root / "06-genai-systems" / "01-llm-lld-projects" / "prompt-builder").mkdir(
        parents=True
    )
    (root / "06-genai-systems" / "02-llm-hld-projects" / "document-qa-rag").mkdir(
        parents=True
    )
    write_file(root / "case-studies" / "netflix-streaming" / "README.md")
    write_file(root / "quizzes" / "design-patterns-quiz.md")
    write_file(root / "quizzes" / "answers" / "design-patterns-answers.md")
    write_file(root / "flashcards" / "README.md")
    write_file(root / "flashcards" / "AGENTS.md")
    write_file(root / "flashcards" / "design-patterns.md")
    write_file(root / "prompts" / "README.md")
    write_file(root / "prompts" / "01-action-truth-sync.md")
    write_file(root / "prompts" / "01.1-verify-truth-sync.md")
    write_file(root / "resources" / "study-plans" / "README.md")
    write_file(root / "resources" / "study-plans" / "1-week-plan.md")
    write_file(root / "resources" / "source-intake" / "README.md")
    write_file(root / "solutions" / "hld-url-shortener.md")
    write_file(root / "solutions" / "coding-two-pointers.md")
    write_file(
        root / "apps" / "portal" / "src" / "components" / "interview" / "interview-data.ts",
        """
interface InterviewProblem {
  slug: string;
  title: string;
  type: string;
  solutionPath: string;
}

export const INTERVIEW_PROBLEMS = [
  {
    slug: "url-shortener",
    title: "URL Shortener",
    type: "hld",
    solutionPath: "solutions/hld-url-shortener.md",
  },
  {
    slug: "two-pointers-pack",
    title: "Two Pointers Pack",
    type: "coding",
    solutionPath: "solutions/coding-two-pointers.md",
  },
];
""",
    )


def content_map(inventory_counts: dict[str, int], portal_counts: dict[str, int]) -> str:
    inventory_labels = {
        "Theory articles": "00-theory/",
        "Design Patterns": "01-design-patterns/",
        "LLD Projects": "02-lld-projects/",
        "HLD Concepts": "03-hld-concepts/",
        "HLD Projects": "04-hld-projects/",
        "GenAI Concepts": "06-genai-systems/00-concepts/",
        "GenAI LLD Projects": "06-genai-systems/01-llm-lld-projects/",
        "GenAI HLD Projects": "06-genai-systems/02-llm-hld-projects/",
        "Coding Pattern Packs": "05-coding-problems/",
        "Case Studies": "case-studies/",
        "Quizzes": "quizzes/",
        "Interview Problems": "solutions/",
        "Resources": "resources/",
        "Flashcard Decks": "flashcards/",
        "Prompt Workflow Files": "prompts/",
        "Executable Sample Files": "03-hld-concepts/",
    }
    portal_labels = {
        "Theory": "00-theory/",
        "Design Patterns": "01-design-patterns/",
        "LLD Projects": "02-lld-projects/",
        "HLD Concepts": "03-hld-concepts/",
        "HLD Projects": "04-hld-projects/",
        "GenAI Concepts": "06-genai-systems/00-concepts/",
        "GenAI LLD": "06-genai-systems/01-llm-lld-projects/",
        "GenAI HLD": "06-genai-systems/02-llm-hld-projects/",
        "Coding Patterns": "05-coding-problems/",
        "Case Studies": "case-studies/",
        "Quizzes": "quizzes/",
        "Interview Mode": "solutions/",
        "Resources": "resources/",
    }
    inventory_rows = "\n".join(
        f"| {label} | {inventory_counts[label]} | `{source}` |"
        for label, source in inventory_labels.items()
    )
    def portal_pattern(label: str) -> str:
        if label == "Design Patterns":
            return "<creational\\|structural\\|behavioral>/<pattern>/"
        return "pattern"

    portal_rows = "\n".join(
        f"| 1 | {label} | `{source}` | {portal_pattern(label)} | key | route | ✅ | scan | {portal_counts[label]} |"
        for label, source in portal_labels.items()
        if label in portal_counts
    )
    return CONTENT_MAP_TEMPLATE.format(
        inventory_rows=inventory_rows,
        portal_rows=portal_rows,
    )


class ContentInventoryCheckerTest(unittest.TestCase):
    def matching_counts(self) -> tuple[dict[str, int], dict[str, int]]:
        return (
            {
                "Theory articles": 2,
                "Design Patterns": 2,
                "LLD Projects": 1,
                "HLD Concepts": 1,
                "HLD Projects": 1,
                "GenAI Concepts": 1,
                "GenAI LLD Projects": 1,
                "GenAI HLD Projects": 1,
                "Coding Pattern Packs": 1,
                "Case Studies": 1,
                "Quizzes": 1,
                "Interview Problems": 2,
                "Resources": 1,
                "Flashcard Decks": 1,
                "Prompt Workflow Files": 2,
                "Executable Sample Files": 0,
            },
            {
                "Theory": 2,
                "Design Patterns": 2,
                "LLD Projects": 1,
                "HLD Concepts": 1,
                "HLD Projects": 1,
                "GenAI Concepts": 1,
                "GenAI LLD": 1,
                "GenAI HLD": 1,
                "Coding Patterns": 1,
                "Case Studies": 1,
                "Quizzes": 1,
                "Interview Mode": 2,
                "Resources": 1,
            },
        )

    def test_passes_when_content_map_counts_match_discovery(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_repo(root)
            counts, portal_counts = self.matching_counts()
            write_file(
                root / "resources" / "CONTENT-UI-MAP.md",
                content_map(counts, portal_counts),
            )

            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--root", str(root)],
                cwd=root,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("checked 16 inventory rows", result.stdout)
        self.assertIn("checked 13 portal rows", result.stdout)

    def test_reports_stale_counts_and_missing_catalog_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_repo(root)
            counts, portal_counts = self.matching_counts()
            counts["Theory articles"] = 1
            counts["Flashcard Decks"] = 0
            portal_counts["Theory"] = 1
            del portal_counts["Case Studies"]
            write_file(
                root / "resources" / "CONTENT-UI-MAP.md",
                content_map(counts, portal_counts),
            )

            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--root", str(root)],
                cwd=root,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("stale-count: Theory articles expected 1 discovered 2", result.stdout)
        self.assertIn("stale-count: Flashcard Decks expected 0 discovered 1", result.stdout)
        self.assertIn("missing-catalog-row: Case Studies", result.stdout)

    def test_section_filter_excludes_root_level_template_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_repo(root)
            write_file(root / "04-hld-projects" / "DESIGN-TEMPLATE.md")
            counts, portal_counts = self.matching_counts()
            write_file(
                root / "resources" / "CONTENT-UI-MAP.md",
                content_map(counts, portal_counts),
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(root),
                    "--sections",
                    "hld-projects",
                ],
                cwd=root,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("hld-projects=1", result.stdout)
        self.assertNotIn("DESIGN-TEMPLATE.md", result.stdout)

    def test_coding_inventory_excludes_problem_bank_support_dirs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_repo(root)
            write_file(root / "05-coding-problems" / "problem-bank" / "README.md")
            write_file(root / "05-coding-problems" / "collections" / "README.md")
            counts, portal_counts = self.matching_counts()
            write_file(
                root / "resources" / "CONTENT-UI-MAP.md",
                content_map(counts, portal_counts),
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(root),
                    "--sections",
                    "coding",
                ],
                cwd=root,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("coding=1", result.stdout)

    def test_portal_registry_excludes_problem_bank_support_dirs(self):
        registry = (REPO_ROOT / "apps/portal/src/content/registry.ts").read_text(encoding="utf-8")
        coding_policy = (REPO_ROOT / "apps/portal/src/content/coding-policy.ts").read_text(encoding="utf-8")

        self.assertIn('"problem-bank"', coding_policy)
        self.assertIn('"collections"', coding_policy)
        self.assertIn("if (CODING_SUPPORT_DIRS.has(topic)) continue;", registry)

    def test_lld_inventory_excludes_helper_dirs_without_problem_docs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_repo(root)
            write_file(root / "02-lld-projects" / "test_helpers" / "imports.py")
            counts, portal_counts = self.matching_counts()
            write_file(
                root / "resources" / "CONTENT-UI-MAP.md",
                content_map(counts, portal_counts),
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(root),
                    "--sections",
                    "lld-projects",
                ],
                cwd=root,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("lld-projects=1", result.stdout)
        self.assertNotIn("test_helpers", result.stdout)

    def test_quizzes_count_only_quiz_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_repo(root)
            write_file(root / "quizzes" / "README.md")
            write_file(root / "quizzes" / "answers" / "extra-answers.md")
            counts, portal_counts = self.matching_counts()
            write_file(
                root / "resources" / "CONTENT-UI-MAP.md",
                content_map(counts, portal_counts),
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(root),
                    "--sections",
                    "quizzes",
                ],
                cwd=root,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("quizzes=1", result.stdout)

    def test_resources_count_only_public_resource_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_repo(root)
            write_file(root / "resources" / "study-plans" / "2-week-plan.md")
            write_file(root / "resources" / "source-intake" / "private.md")
            write_file(root / "resources" / "practice-labs" / "README.md")
            write_file(root / "resources" / "practice-labs" / "lab.md")
            counts, portal_counts = self.matching_counts()
            counts["Resources"] = 2
            portal_counts["Resources"] = 2
            write_file(
                root / "resources" / "CONTENT-UI-MAP.md",
                content_map(counts, portal_counts),
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(root),
                    "--sections",
                    "resources",
                ],
                cwd=root,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("resources=2", result.stdout)

    def test_interview_mode_discovers_coding_solutions_when_both_sections_checked(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_repo(root)
            interview_data = (
                root
                / "apps"
                / "portal"
                / "src"
                / "components"
                / "interview"
                / "interview-data.ts"
            )
            interview_data.write_text(
                """
export const INTERVIEW_PROBLEMS = [
  { slug: "url-shortener", solutionPath: "solutions/hld-url-shortener.md" },
];
""",
                encoding="utf-8",
            )
            counts, portal_counts = self.matching_counts()
            write_file(
                root / "resources" / "CONTENT-UI-MAP.md",
                content_map(counts, portal_counts),
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(root),
                    "--sections",
                    "coding",
                    "interview-mode",
                ],
                cwd=root,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("interview-mode=2", result.stdout)

    def test_interview_mode_rejects_coding_solution_without_pack(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_repo(root)
            write_file(root / "solutions" / "coding-orphan.md")
            counts, portal_counts = self.matching_counts()
            counts["Interview Problems"] = 3
            portal_counts["Interview Mode"] = 3
            write_file(
                root / "resources" / "CONTENT-UI-MAP.md",
                content_map(counts, portal_counts),
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(root),
                    "--sections",
                    "coding",
                    "interview-mode",
                ],
                cwd=root,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("stale-interview-coding-pack: Interview Mode", result.stdout)
        self.assertIn("missing coding pack orphan", result.stdout)

    def test_interview_mode_validates_coding_solution_file_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_repo(root)
            (root / "solutions" / "coding-two-pointers.md").unlink()
            counts, portal_counts = self.matching_counts()
            write_file(
                root / "resources" / "CONTENT-UI-MAP.md",
                content_map(counts, portal_counts),
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(root),
                    "--sections",
                    "coding",
                    "interview-mode",
                ],
                cwd=root,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("missing-interview-coding-pack: Interview Mode", result.stdout)
        self.assertIn("solutions/coding-two-pointers.md", result.stdout)

    def test_json_output_is_machine_readable_on_failures(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_repo(root)
            counts, portal_counts = self.matching_counts()
            counts["HLD Concepts"] = 2
            write_file(
                root / "resources" / "CONTENT-UI-MAP.md",
                content_map(counts, portal_counts),
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(root),
                    "--format",
                    "json",
                ],
                cwd=root,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(set(payload), {"ok", "summary", "findings"})
        self.assertFalse(payload["ok"])
        stale_hld = next(
            finding
            for finding in payload["findings"]
            if finding["kind"] == "stale-count" and finding["section"] == "HLD Concepts"
        )
        self.assertEqual(stale_hld["expected"], 2)
        self.assertEqual(stale_hld["discovered"], 1)
        self.assertEqual(stale_hld["path"], "resources/CONTENT-UI-MAP.md")


if __name__ == "__main__":
    unittest.main()
