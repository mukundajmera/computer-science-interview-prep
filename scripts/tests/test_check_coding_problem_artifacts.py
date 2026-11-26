import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "check_coding_problem_artifacts.py"


class CodingProblemArtifactCheckerTest(unittest.TestCase):
    def run_script(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), str(root)],
            cwd=REPO_ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def test_passes_when_support_paths_have_no_generated_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "05-coding-problems" / "problem-bank").mkdir(parents=True)
            (root / "resources" / "source-intake").mkdir(parents=True)
            (root / "scripts" / "coding_catalog").mkdir(parents=True)

            result = self.run_script(root)

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("coding-problem-artifacts: ok", result.stdout)

    def test_reports_cache_class_and_driver_payload_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            files = [
                root / "scripts" / "tests" / "__pycache__" / "test_x.pyc",
                root / "scripts" / "coding_catalog" / "__pycache__" / "driver.pyc",
                root / "05-coding-problems" / "problem-bank" / "lc-0001-two-sum" / "Driver.java",
                root / "05-coding-problems" / "problem-bank" / "lc-0001-two-sum" / "Solution.class",
                root / "05-coding-problems" / "problem-bank" / "lc-0001-two-sum" / "payload.json",
                root / "05-coding-problems" / "problem-bank" / "lc-0001-two-sum" / "result.json",
            ]
            for path in files:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("generated", encoding="utf-8")

            result = self.run_script(root)

            self.assertEqual(1, result.returncode)
            for path in files:
                self.assertIn(str(path.relative_to(root)), result.stdout)

    def test_reports_problem_readme_indented_as_code_block(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            readme = root / "05-coding-problems" / "problem-bank" / "lc-0001-two-sum" / "README.md"
            readme.parent.mkdir(parents=True, exist_ok=True)
            readme.write_text(
                "    # Two Sum\n\n    | Input | Output |\n    | --- | --- |\n",
                encoding="utf-8",
            )

            result = self.run_script(root)

            self.assertEqual(1, result.returncode)
            self.assertIn(str(readme.relative_to(root)), result.stdout)
            self.assertIn("problem README appears accidentally indented as a code block", result.stdout)


if __name__ == "__main__":
    unittest.main()
