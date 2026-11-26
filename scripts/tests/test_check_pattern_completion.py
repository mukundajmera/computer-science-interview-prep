import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "check_pattern_completion.py"


def write_file(path: Path, content: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_pattern(root: Path, category: str, slug: str, with_tests: bool = False, with_v2: bool = False) -> None:
    base = root / "01-design-patterns" / category / slug
    write_file(base / "README.md", "# Pattern\n")
    write_file(base / "java" / "v1-basic" / "Demo.java", "class Demo {}\n")
    write_file(base / "python" / "v1-basic" / "demo.py", "class Demo:\n    pass\n")
    if with_tests:
        write_file(base / "java" / "tests" / "DemoTest.java", "class DemoTest {}\n")
        write_file(base / "python" / "tests" / "test_demo.py", "def test_demo():\n    pass\n")
    if with_v2:
        write_file(base / "java" / "v2-extended" / "Demo.java", "class Demo {}\n")
        write_file(base / "python" / "v2-extended" / "demo.py", "class Demo:\n    pass\n")


def write_matrix(root: Path, rows: str) -> None:
    write_file(
        root / "01-design-patterns" / "COMPLETION-MATRIX.md",
        "# Matrix\n\n"
        "| Pattern | Category | Theory | Java v1 | Python v1 | Java tests | Python tests | v2/v3 progression |\n"
        "|---------|----------|--------|---------|-----------|------------|--------------|-------------------|\n"
        f"{rows}",
    )


class PatternCompletionCheckerTest(unittest.TestCase):
    def run_script(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(root)],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def test_passes_when_matrix_matches_discovered_pattern_coverage(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_pattern(root, "creational", "factory-method", with_tests=True)
            write_matrix(
                root,
                "| [Factory Method](./creational/factory-method/) | Creational | Yes | Yes | Yes | Yes | Yes | Planned |\n",
            )

            result = self.run_script(root)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("summary: patterns=1", result.stdout)
        self.assertIn("pattern-completion: ok", result.stdout)

    def test_reports_missing_pattern_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_pattern(root, "structural", "adapter")
            write_matrix(root, "")

            result = self.run_script(root)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("missing-matrix-row", result.stdout)
        self.assertIn("structural/adapter", result.stdout)

    def test_reports_stale_matrix_cells(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_pattern(root, "behavioral", "observer", with_v2=True)
            write_matrix(
                root,
                "| [Observer](./behavioral/observer/) | Behavioral | Yes | Yes | Yes | Yes | No | Planned |\n",
            )

            result = self.run_script(root)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("stale-matrix-cell", result.stdout)
        self.assertIn("java_tests", result.stdout)
        self.assertIn("v2_v3", result.stdout)

    def test_reports_extra_and_duplicate_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_pattern(root, "behavioral", "strategy")
            write_matrix(
                root,
                "| [Strategy](./behavioral/strategy/) | Behavioral | Yes | Yes | Yes | No | No | Planned |\n"
                "| [Strategy](./behavioral/strategy/) | Behavioral | Yes | Yes | Yes | No | No | Planned |\n"
                "| [Ghost](./behavioral/ghost/) | Behavioral | Yes | Yes | Yes | No | No | Planned |\n",
            )

            result = self.run_script(root)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("duplicate-matrix-row", result.stdout)
        self.assertIn("extra-matrix-row", result.stdout)



    def test_evidence_plan_reports_structural_presence_and_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_pattern(root, "creational", "factory-method", with_tests=True, with_v2=True)
            # Make v2 empty to simulate missing version
            (root / "01-design-patterns" / "creational" / "factory-method" / "java" / "v2-extended" / "Demo.java").unlink()
            
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--root", str(root), "--evidence-plan"],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            
            self.assertEqual(result.returncode, 0)
            self.assertIn("pattern-evidence: creational/factory-method/java/v1-basic: structural-presence/not-run", result.stdout)
            self.assertIn("pattern-evidence: creational/factory-method/python/v1-basic: structural-presence/not-run", result.stdout)
            self.assertIn("pattern-evidence: creational/factory-method/java/v2-extended: failed (missing version)", result.stdout)

    def test_evidence_report_rejects_wrong_version_test_provenance(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_pattern(root, "structural", "adapter", with_tests=True, with_v2=True)
            test_file = root / "01-design-patterns" / "structural" / "adapter" / "python" / "tests" / "test_demo.py"
            test_file.write_text("import sys\nsys.path.insert(0, '../v1-basic')\n\ndef test_demo():\n    pass\n")
            
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--root", str(root), "--evidence-report"],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            
            self.assertEqual(result.returncode, 0)
            self.assertIn("pattern-evidence: structural/adapter/python/v2-extended: failed (wrong-version test provenance)", result.stdout)

    def test_evidence_report_detects_fabrication_and_count_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_pattern(root, "behavioral", "observer", with_tests=True)
            # Write a failing test for v1
            test_file = root / "01-design-patterns" / "behavioral" / "observer" / "python" / "tests" / "test_demo.py"
            test_file.write_text("import unittest\nclass TestDemo(unittest.TestCase):\n    def test_fail(self):\n        self.assertTrue(False)\n")
            
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--root", str(root), "--evidence-report"],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            
            self.assertEqual(result.returncode, 0)
            self.assertIn("pattern-evidence: behavioral/observer/python/v1-basic: failed (test execution error)", result.stdout)
            
            # Now change to pass, checking the count is reported
            test_file.write_text("import unittest\nclass TestDemo(unittest.TestCase):\n    def test_pass(self):\n        self.assertTrue(True)\n    def test_pass2(self):\n        self.assertTrue(True)\n")
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--root", str(root), "--evidence-report"],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            
            self.assertEqual(result.returncode, 0)
            self.assertIn("pattern-evidence: behavioral/observer/python/v1-basic: passed with command/test count 2", result.stdout)


if __name__ == "__main__":
    unittest.main()
