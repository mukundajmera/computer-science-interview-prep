import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "check_checkpoint_boundary.py"


class CheckpointBoundaryTest(unittest.TestCase):
    def init_repo(self, root: Path) -> None:
        subprocess.run(["git", "init"], cwd=root, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def commit_all(self, root: Path, message: str = "baseline") -> None:
        subprocess.run(["git", "add", "."], cwd=root, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.run(
            [
                "git",
                "-c",
                "user.name=Test User",
                "-c",
                "user.email=test@example.com",
                "commit",
                "-m",
                message,
            ],
            cwd=root,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def run_script(self, root: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(root), *args],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def test_passes_for_staged_only_checkpoint(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.init_repo(root)
            (root / "README.md").write_text("# Example\n", encoding="utf-8")
            subprocess.run(["git", "add", "README.md"], cwd=root, check=True)

            result = self.run_script(root)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("checkpoint-boundary: ok", result.stdout)
        self.assertEqual(result.stderr, "")

    def test_reports_checkpoint_boundary_hazards_without_reading_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.init_repo(root)
            (root / "tracked.md").write_text("baseline\n", encoding="utf-8")
            self.commit_all(root)

            (root / "tracked.md").write_text("unstaged private sentinel\n", encoding="utf-8")
            (root / "mixed.md").write_text("staged\n", encoding="utf-8")
            subprocess.run(["git", "add", "mixed.md"], cwd=root, check=True)
            (root / "mixed.md").write_text("unstaged after add\n", encoding="utf-8")
            (root / "untracked.md").write_text("untracked private sentinel\n", encoding="utf-8")
            temp_upload_file = root / "temp_upload" / "INTEGRATION-PLAN.md"
            temp_upload_file.parent.mkdir()
            temp_upload_file.write_text("raw source area sentinel\n", encoding="utf-8")

            result = self.run_script(root)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        combined = result.stdout + result.stderr
        self.assertIn("unstaged-change", combined)
        self.assertIn("mixed-index-worktree", combined)
        self.assertIn("untracked-file", combined)
        self.assertIn("raw-source-dirty", combined)
        self.assertIn("temp_upload/INTEGRATION-PLAN.md", combined)
        self.assertNotIn("private sentinel", combined)
        self.assertNotIn("raw source area sentinel", combined)

    def test_json_output_is_machine_readable(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.init_repo(root)
            (root / "untracked.md").write_text("do not print me\n", encoding="utf-8")

            result = self.run_script(root, "--format", "json")

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["finding_count"], 1)
        self.assertEqual(payload["findings"][0]["kind"], "untracked-file")
        self.assertEqual(result.stderr, "")
        self.assertNotIn("do not print me", result.stdout)


if __name__ == "__main__":
    unittest.main()
