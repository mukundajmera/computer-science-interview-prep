import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "check_lld_project_coverage.py"


def write_file(path: Path, content: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_project(root: Path, slug: str, with_rubric_pack: bool = False, with_nested_java_test: bool = False) -> None:
    base = root / "02-lld-projects" / slug
    for doc in ("PROBLEM.md", "APPROACH.md", "DESIGN.md", "CODE-WALKTHROUGH.md"):
        write_file(base / doc, f"# {doc}\n")
    if with_rubric_pack:
        for doc in ("RUBRIC.md", "PITFALLS.md", "FOLLOW-UPS.md"):
            write_file(base / doc, f"# {doc}\n")
    for version in ("v1-basic", "v2-extended", "v3-optimized"):
        write_file(base / "java" / version / "Demo.java", "class Demo {}\n")
        write_file(base / "python" / version / "demo.py", "class Demo:\n    pass\n")
    java_test_path = base / "java" / "tests" / "v1_basic" / "DemoTest.java" if with_nested_java_test else base / "java" / "tests" / "DemoTest.java"
    write_file(java_test_path, "class DemoTest {}\n")
    write_file(base / "python" / "tests" / "test_demo.py", "def test_demo():\n    pass\n")


def write_matrix(root: Path, rows: str) -> None:
    write_file(
        root / "02-lld-projects" / "lld-doc-coverage-matrix.md",
        "# Matrix\n\n"
        "| Project | Core docs | Rubric | Pitfalls | Follow-ups | Java v1 | Java v2 | Java v3 | Java tests | Python v1 | Python v2 | Python v3 | Python tests |\n"
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|\n"
        f"{rows}",
    )


def write_readme(root: Path, content: str) -> None:
    write_file(
        root / "02-lld-projects" / "README.md",
        content,
    )


class LldProjectCoverageCheckerTest(unittest.TestCase):
    def run_script(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(root)],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def test_passes_when_matrix_matches_discovered_project_coverage(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project(root, "parking-lot", with_rubric_pack=True, with_nested_java_test=True)
            write_matrix(
                root,
                "| [parking-lot](./parking-lot/) | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes |\n",
            )
            write_readme(
                root,
                "- **Total projects:** 1\n\n"
                "| [parking-lot](./parking-lot/) | ⭐⭐ | ✅ |\n",
            )

            result = self.run_script(root)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("summary: lld-projects=1", result.stdout)
        self.assertIn("lld-project-coverage: ok", result.stdout)

    def test_reports_missing_project_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project(root, "splitwise")
            write_matrix(root, "")
            write_readme(
                root,
                "- **Total projects:** 1\n\n"
                "| [splitwise](./splitwise/) | ⭐⭐ | ✅ |\n",
            )

            result = self.run_script(root)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("missing-matrix-row", result.stdout)
        self.assertIn("02-lld-projects/splitwise", result.stdout)

    def test_reports_stale_cells(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project(root, "payment-system", with_rubric_pack=False)
            write_matrix(
                root,
                "| [payment-system](./payment-system/) | Yes | Yes | No | No | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes |\n",
            )
            write_readme(
                root,
                "- **Total projects:** 1\n\n"
                "| [payment-system](./payment-system/) | ⭐⭐ | ✅ |\n",
            )

            result = self.run_script(root)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("stale-matrix-cell", result.stdout)
        self.assertIn("rubric", result.stdout)
        self.assertIn("expected 'No'", result.stdout)

    def test_reports_extra_duplicate_and_malformed_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project(root, "web-crawler")
            write_matrix(
                root,
                "| [web-crawler](./web-crawler/) | Yes | No | No | No | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes |\n"
                "| [web-crawler](./web-crawler/) | Yes | No | No | No | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes |\n"
                "| [ghost](./ghost/) | Yes | No | No | No | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes |\n"
                "| [bad](./bad/) | Yes | No |\n",
            )
            write_readme(
                root,
                "- **Total projects:** 1\n\n"
                "| [web-crawler](./web-crawler/) | ⭐⭐ | ✅ |\n",
            )

            result = self.run_script(root)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("duplicate-matrix-row", result.stdout)
        self.assertIn("extra-matrix-row", result.stdout)
        self.assertIn("malformed-matrix-row", result.stdout)

    def test_reports_stale_readme_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project(root, "parking-lot", with_rubric_pack=True, with_nested_java_test=True)
            write_matrix(
                root,
                "| [parking-lot](./parking-lot/) | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes |\n",
            )
            write_readme(
                root,
                "- **Total projects:** 99\n\n"
                "| [parking-lot](./parking-lot/) | ⭐⭐ | ✅ |\n",
            )

            result = self.run_script(root)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("stale-readme-count", result.stdout)
        self.assertIn("expected 1", result.stdout)

    def test_reports_missing_readme_row(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project(root, "splitwise")
            write_matrix(
                root,
                "| [splitwise](./splitwise/) | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes |\n",
            )
            write_readme(
                root,
                "- **Total projects:** 1\n\n",
            )

            result = self.run_script(root)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("missing-readme-row", result.stdout)
        self.assertIn("splitwise", result.stdout)

    def test_reports_extra_and_duplicate_readme_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project(root, "web-crawler")
            write_matrix(
                root,
                "| [web-crawler](./web-crawler/) | Yes | No | No | No | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes |\n",
            )
            write_readme(
                root,
                "- **Total projects:** 1\n\n"
                "| [web-crawler](./web-crawler/) | ⭐⭐ | ✅ |\n"
                "| [web-crawler](./web-crawler/) | ⭐⭐ | ✅ |\n"
                "| [ghost](./ghost/) | ⭐⭐ | ✅ |\n",
            )

            result = self.run_script(root)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("duplicate-readme-row", result.stdout)
        self.assertIn("extra-readme-row", result.stdout)


if __name__ == "__main__":
    unittest.main()
