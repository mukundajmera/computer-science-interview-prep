import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "run_python_tests.py"

PASSING_TEST = b"""import unittest


class TrivialPassTest(unittest.TestCase):
    def test_passes(self):
        self.assertEqual(1 + 1, 2)
"""

FAILING_TEST = b"""import unittest


class TrivialFailTest(unittest.TestCase):
    def test_fails(self):
        self.assertEqual(1 + 1, 3)
"""


def build_repo(root: Path) -> None:
    subprocess.run(["git", "init", "-q"], cwd=str(root), check=True)
    for relative, content in (
        ("proj_alpha/python/tests/test_ok.py", PASSING_TEST),
        ("proj_beta/python/tests/test_bad.py", FAILING_TEST),
    ):
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        subprocess.run(["git", "add", relative], cwd=str(root), check=True)


class RunPythonTestsTest(unittest.TestCase):
    def run_script(self, root: Path, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(root), *args],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def test_list_prints_folders_and_runs_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            build_repo(root)

            result = self.run_script(root, "--list")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        lines = result.stdout.split()
        self.assertIn("proj_alpha/python/tests", lines)
        self.assertIn("proj_beta/python/tests", lines)
        self.assertNotIn("PASS", lines)
        self.assertNotIn("FAIL", lines)

    def test_only_filters_folders(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            build_repo(root)

            result = self.run_script(root, "--only", "alpha")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS proj_alpha/python/tests", result.stdout)
        self.assertNotIn("proj_beta", result.stdout)

    def test_failing_folder_gives_fail_line_and_exit_1(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            build_repo(root)

            result = self.run_script(root)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("PASS proj_alpha/python/tests", result.stdout)
        self.assertIn("FAIL proj_beta/python/tests", result.stdout)
        self.assertIn("1 passed, 1 failed, 2 folders", result.stdout)

    def test_only_matching_nothing_passes_vacuously(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            build_repo(root)

            result = self.run_script(root, "--only", "no-such-project")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("0 passed, 0 failed, 0 folders", result.stdout)


if __name__ == "__main__":
    unittest.main()
