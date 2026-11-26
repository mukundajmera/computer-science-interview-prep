import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "check_assessment_coverage.py"


def write_file(path: Path, content: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def minimal_interview_data() -> str:
    return """
export const INTERVIEW_PROBLEMS = [
  {
    slug: "url-shortener",
    title: "URL Shortener",
    type: "hld",
    difficulty: "advanced",
    solutionPath: "solutions/hld-url-shortener.md",
  },
  {
    slug: "legacy-static-coding",
    title: "Legacy Static Coding",
    type: "coding",
    difficulty: "intermediate",
    solutionPath: "solutions/coding-legacy.md",
  },
];
"""


def write_valid_repo(root: Path) -> None:
    write_file(
        root / "quizzes/design-patterns-quiz.md",
        "# Design Patterns Quiz\n\n### Question 1\n\nA\n\n### Question 2\n\nB\n",
    )
    write_file(
        root / "quizzes/answers/design-patterns-answers.md",
        "# Answers\n\n| Question | Answer | Why |\n|---|---|---|\n| 1 | A | one |\n| 2 | B | two |\n",
    )
    write_file(
        root / "flashcards/design-patterns.md",
        "# Cards\n\n### Card 1\n**Front:** one\n\n### Card 2\n**Front:** two\n",
    )
    write_file(root / "solutions/hld-url-shortener.md", "# Coach Answer\n")
    write_file(root / "solutions/coding-two-pointers.md", "# Coding Coach Answer\n")
    write_file(
        root / "resources/source-intake/temp-upload/derivative-review-ledger.csv",
        "artifact_path,review_status\n",
    )
    write_file(
        root / "apps/portal/src/components/interview/interview-data.ts",
        minimal_interview_data(),
    )


class AssessmentCoverageCheckerTest(unittest.TestCase):
    def run_script(self, root: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(root), *args],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def test_write_then_check_passes_for_valid_assets(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_valid_repo(root)

            write_result = self.run_script(root, "--write")
            check_result = self.run_script(root)

            matrix = (root / "resources/ASSESSMENT-COVERAGE-MATRIX.md").read_text(encoding="utf-8")

        self.assertEqual(write_result.returncode, 0, write_result.stdout + write_result.stderr)
        self.assertEqual(check_result.returncode, 0, check_result.stdout + check_result.stderr)
        self.assertIn("assessment-coverage: ok", check_result.stdout)
        self.assertIn("| quiz+flashcard | fundamentals | design-patterns |", matrix)
        self.assertIn("| interview-mode | coding | two-pointers | Two Pointers Pack |", matrix)
        self.assertIn("/reveal/solution/coding/two-pointers-pack", matrix)

    def test_reports_malformed_assessment_assets(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_valid_repo(root)
            write_file(
                root / "quizzes/answers/design-patterns-answers.md",
                "# Answers\n\n| Question | Answer | Why |\n|---|---|---|\n| 1 | A | one |\n",
            )
            write_file(
                root / "flashcards/design-patterns.md",
                "# Cards\n\n### Card 1\n**Front:** one\n\n### Card 2\n",
            )

            result = self.run_script(root, "--write")

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("answer-count-mismatch: design-patterns", result.stdout)
        self.assertIn("flashcard-front-mismatch: design-patterns", result.stdout)

    def test_missing_matrix_fails_without_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_valid_repo(root)

            result = self.run_script(root)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("missing-assessment-matrix", result.stdout)

    def test_provenance_blocked_quiz_and_answer_are_not_counted_as_public_routes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_valid_repo(root)
            write_file(
                root / "resources/source-intake/temp-upload/derivative-review-ledger.csv",
                "artifact_path,review_status\n"
                "quizzes/design-patterns-quiz.md,blocked\n"
                "quizzes/answers/design-patterns-answers.md,blocked\n",
            )

            result = self.run_script(root, "--write")
            matrix = (root / "resources/ASSESSMENT-COVERAGE-MATRIX.md").read_text(encoding="utf-8")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("/quizzes/design-patterns", matrix)
        self.assertNotIn("/reveal/quiz-answer/design-patterns", matrix)
        self.assertIn("| flashcard | fundamentals | design-patterns |", matrix)

    def test_json_output_is_machine_readable(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_valid_repo(root)

            result = self.run_script(root, "--format", "json")

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(set(payload), {"ok", "summary", "findings"})
        self.assertFalse(payload["ok"])
        self.assertTrue(any(finding["kind"] == "missing-assessment-matrix" for finding in payload["findings"]))


if __name__ == "__main__":
    unittest.main()
