import subprocess
import sys
import tempfile
import unittest
import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "check_readability_style.py"
SPEC = importlib.util.spec_from_file_location("check_readability_style_module", SCRIPT)
CHECKER = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = CHECKER
SPEC.loader.exec_module(CHECKER)


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


class ReadabilityStyleCheckerTest(unittest.TestCase):
    def run_script(self, root: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(root), *args],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def test_interview_ready_markdown_passes(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_file(
                root / "ready.md",
                """# Ready Topic

## Mental Model

This topic explains the core idea with concrete scope and clear interview framing.

## Failure Modes

- Timeout recovery is explicit.
- Retry semantics are bounded.

## Strong Answer

Say: "I would start by clarifying requirements, then choose the simplest design that preserves correctness."
""",
            )

            result = self.run_script(root, "ready.md")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("readability-style: ok", result.stdout)

    def test_placeholder_and_generic_hld_language_fail(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_file(
                root / "weak.md",
                """# Weak Topic

## Requirements

TODO: Support core user workflow with High sustained load and p95 low-latency.
""",
            )

            result = self.run_script(root, "weak.md")

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("banned-phrase", result.stdout)
        self.assertIn("generic HLD requirement", result.stdout)

    def test_long_paragraph_fails(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            paragraph = " ".join(["word"] * 131)
            write_file(root / "wall.md", f"# Wall\n\n{paragraph}\n")

            result = self.run_script(root, "wall.md")

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("long-paragraph", result.stdout)

    def test_empty_section_fails(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_file(
                root / "empty.md",
                """# Empty

## Missing Body

## Next Section

This section has content.
""",
            )

            result = self.run_script(root, "empty.md")

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("empty-section", result.stdout)

    def test_directory_input_checks_nested_markdown(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            ready = """# Ready

## Mental Model

This nested file has concrete interview framing and a crisp explanation.

## Strong Answer

Say: "I would name the invariant, describe the state, and validate the failure path."
"""
            write_file(root / "pilot/a.md", ready)
            write_file(root / "pilot/nested/b.md", ready)

            result = self.run_script(root, "pilot")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("checked 2 markdown readability files", result.stdout)

    def test_temp_upload_paths_are_skipped(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_file(root / "temp_upload/private.md", "TODO DO-NOT-READ-THIS-PAYLOAD")

            result = self.run_script(root, "temp_upload/private.md")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("checked 0 markdown", result.stdout)
        self.assertNotIn("DO-NOT-READ-THIS-PAYLOAD", result.stdout)

    def test_default_paths_include_wave3_batch3_batch4_and_wave4_theory(self):
        defaults = set(CHECKER.DEFAULT_PATHS)

        for expected in [
            Path("00-theory/big-data-structures/merkle-tree.md"),
            Path("00-theory/big-data-structures/trie.md"),
            Path("05-coding-problems/backtracking"),
            Path("05-coding-problems/heap-priority-queue"),
            Path("05-coding-problems/trie"),
            Path("05-coding-problems/union-find"),
            Path("quizzes/backtracking-quiz.md"),
            Path("quizzes/heap-priority-queue-quiz.md"),
            Path("quizzes/trie-quiz.md"),
            Path("quizzes/union-find-quiz.md"),
            Path("flashcards/backtracking.md"),
            Path("flashcards/heap-priority-queue.md"),
            Path("flashcards/trie.md"),
            Path("flashcards/union-find.md"),
            Path("solutions/coding-backtracking.md"),
            Path("solutions/coding-heap-priority-queue.md"),
            Path("solutions/coding-trie.md"),
            Path("solutions/coding-union-find.md"),
        ]:
            self.assertIn(expected, defaults)


if __name__ == "__main__":
    unittest.main()
