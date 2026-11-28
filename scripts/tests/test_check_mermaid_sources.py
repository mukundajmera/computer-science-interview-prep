import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "check_mermaid_sources.py"


def init_repo(root: Path) -> None:
    subprocess.run(["git", "init", "-q"], cwd=str(root), check=True)


def stage_file(root: Path, relative: str, content: bytes) -> None:
    target = root / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(content)
    subprocess.run(["git", "add", relative], cwd=str(root), check=True)


class MermaidSourcesCheckerTest(unittest.TestCase):
    def run_script(self, root: Path) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(root)],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def test_valid_file_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_repo(root)
            stage_file(root, "diagrams/a.mmd", b"flowchart TD\n    A --> B\n")

            result = self.run_script(root)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("mermaid-sources: ok (1 files)", result.stdout)

    def test_fenced_file_reported_at_line_1_only_as_fenced(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_repo(root)
            stage_file(root, "a.mmd", b"```mermaid\nflowchart TD\n```\n")

            result = self.run_script(root)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("a.mmd:1: fenced:", result.stdout)
        self.assertNotIn("no-diagram-keyword", result.stdout)

    def test_empty_file_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_repo(root)
            stage_file(root, "a.mmd", b"%% only a comment\n\n")

            result = self.run_script(root)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("a.mmd:1: empty:", result.stdout)

    def test_unknown_first_keyword_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_repo(root)
            stage_file(root, "a.mmd", b"notadiagram TD\n    A --> B\n")

            result = self.run_script(root)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("a.mmd:1: no-diagram-keyword:", result.stdout)

    def test_crlf_file_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_repo(root)
            stage_file(root, "a.mmd", b"flowchart TD\r\n    A --> B\r\n")

            result = self.run_script(root)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("a.mmd:1: crlf:", result.stdout)

    def test_repo_without_mmd_files_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_repo(root)
            stage_file(root, "README.md", b"# readme\n")

            result = self.run_script(root)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("mermaid-sources: ok (0 files)", result.stdout)

    def test_front_matter_with_valid_keyword_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_repo(root)
            stage_file(root, "a.mmd", b"---\ntitle: Example\n---\nsequenceDiagram\n    A->>B: hi\n")

            result = self.run_script(root)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("mermaid-sources: ok (1 files)", result.stdout)


if __name__ == "__main__":
    unittest.main()
