from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "check_python38_syntax.py"


def run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def init_repo(root: Path, files: dict[str, str]) -> None:
    run(["git", "init", "-q"], root)
    for relative_path, content in files.items():
        write_file(root / relative_path, content)
    run(["git", "add", "-f", "."], root)


class Python38SyntaxCheckTest(unittest.TestCase):
    def run_check(self, root: Path) -> subprocess.CompletedProcess[str]:
        return run([sys.executable, str(SCRIPT), "--root", str(root)], REPO_ROOT)

    def test_valid_files_pass(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            init_repo(root, {"ok.py": "x = {'a': 1}\n", "pkg/mod.py": "def f():\n    return 42\n"})

            result = self.run_check(root)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("python38-syntax: ok", result.stdout)
        self.assertIn("(2 files)", result.stdout)

    def test_match_statement_fails_with_path_and_line(self):
        source = "def f(x):\n    match x:\n        case 1:\n            return 1\n"
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            init_repo(root, {"bad.py": source})

            result = self.run_check(root)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertRegex(result.stdout, r"bad\.py:\d+: ")

    def test_ordinary_syntax_error_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            init_repo(root, {"broken.py": "def broken(:\n"})

            result = self.run_check(root)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("broken.py:1:", result.stdout)

    def test_empty_repo_passes(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            init_repo(root, {})

            result = self.run_check(root)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("python38-syntax: ok", result.stdout)
        self.assertIn("(0 files)", result.stdout)


if __name__ == "__main__":
    unittest.main()
