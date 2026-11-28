from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "check_repo_smoke.py"


class RepoSmokeCommandSurfaceTest(unittest.TestCase):
    def run_script(self, *args: str, env: dict[str, str] | None = None, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            cwd=cwd or REPO_ROOT,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def test_lists_stable_named_checks(self):
        result = self.run_script("--list")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for check_name in [
            "check_scripts",
            "check_portal",
            "check_python_smoke",
            "check_python_failing",
            "check_java_smoke",
            "check_markdown_links",
            "check_content_inventory",
            "check_coding_problem_catalog",
            "check_coding_problem_driver_generation",
            "check_coding_problem_python_drivers",
            "check_coding_problem_artifacts",
            "check_coding_problem_java_drivers",
            "check_readability_style",
            "check_hld_concept_catalog",
            "check_genai_currentness",
            "check_assessment_coverage",
            "check_pattern_completion",
            "check_lld_project_coverage",
            "check_executable_sample_inventory",
            "check_secret_artifacts",
            "check_checkpoint_boundary",
            "check_mermaid",
        ]:
            self.assertIn(check_name, result.stdout)

    def test_dry_run_prints_commands_without_executing_them(self):
        result = self.run_script("--dry-run", "--only", "check_secret_artifacts")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("DRY-RUN check_secret_artifacts:", result.stdout)
        self.assertIn("scripts/check_tracked_secret_artifacts.py", result.stdout)
        self.assertNotIn("tracked-secret-artifacts: ok", result.stdout)
        self.assertNotIn("PASS", result.stdout)
        self.assertNotIn("FAIL", result.stdout)

    def test_dry_run_can_select_multiple_checks_without_execution(self):
        result = self.run_script(
            "--dry-run",
            "--only",
            "check_portal",
            "check_python_smoke",
            "check_java_smoke",
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("DRY-RUN check_portal:", result.stdout)
        self.assertIn("DRY-RUN check_python_smoke:", result.stdout)
        self.assertIn("DRY-RUN check_java_smoke:", result.stdout)
        self.assertIn("scripts/check_java_smoke.py", result.stdout)
        self.assertNotIn("PASS", result.stdout)
        self.assertNotIn("FAIL", result.stdout)
        self.assertNotIn("npm WARN", result.stdout)
        self.assertEqual(result.stderr, "")

    def test_default_dry_run_includes_release_protection_checks(self):
        result = self.run_script("--dry-run")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("DRY-RUN check_scripts:", result.stdout)
        self.assertIn("DRY-RUN check_secret_artifacts:", result.stdout)
        self.assertIn("DRY-RUN check_readability_style:", result.stdout)
        self.assertIn("DRY-RUN check_coding_problem_driver_generation:", result.stdout)
        self.assertNotIn("check_checkpoint_boundary", result.stdout)
        self.assertNotIn("check_java_smoke", result.stdout)
        self.assertNotIn("check_coding_problem_python_drivers", result.stdout)
        self.assertNotIn("check_coding_problem_java_drivers", result.stdout)
        self.assertNotIn("check_python_failing", result.stdout)
        self.assertNotIn("check_mermaid", result.stdout)

    def test_checkpoint_profile_dry_run_adds_boundary_checks(self):
        result = self.run_script("--dry-run", "--profile", "checkpoint")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("DRY-RUN check_scripts:", result.stdout)
        self.assertIn("DRY-RUN check_checkpoint_boundary:", result.stdout)
        self.assertNotIn("check_java_smoke", result.stdout)
        self.assertNotIn("check_python_failing", result.stdout)
        self.assertNotIn("check_mermaid", result.stdout)

    def test_release_profile_dry_run_adds_boundary_checks(self):
        result = self.run_script("--dry-run", "--profile", "release")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("DRY-RUN check_scripts:", result.stdout)
        self.assertIn("DRY-RUN check_checkpoint_boundary:", result.stdout)
        self.assertNotIn("check_java_smoke", result.stdout)
        self.assertNotIn("check_python_failing", result.stdout)
        self.assertNotIn("check_mermaid", result.stdout)

    def test_only_overrides_release_profile_selection(self):
        result = self.run_script("--dry-run", "--profile", "release", "--only", "check_secret_artifacts")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("DRY-RUN check_secret_artifacts:", result.stdout)
        self.assertNotIn("DRY-RUN check_checkpoint_boundary:", result.stdout)

    def test_checkpoint_boundary_check_is_optional_but_selectable(self):
        result = self.run_script("--dry-run", "--only", "check_checkpoint_boundary")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("DRY-RUN check_checkpoint_boundary:", result.stdout)
        self.assertIn("scripts/check_checkpoint_boundary.py", result.stdout)
        self.assertNotIn("PASS", result.stdout)

    def test_unknown_check_exits_with_usage_error(self):
        result = self.run_script("--only", "missing_check")

        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("unknown check: missing_check", result.stderr)
        self.assertEqual(result.stdout, "")

    def test_unknown_check_does_not_run_prior_valid_check(self):
        result = self.run_script("--only", "check_secret_artifacts", "missing_check")

        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("unknown check: missing_check", result.stderr)
        self.assertNotIn("tracked-secret-artifacts: ok", result.stdout)
        self.assertNotIn("PASS check_secret_artifacts", result.stdout)

    def test_blocked_tool_check_reports_actionable_skip(self):
        result = self.run_script("--only", "check_mermaid")

        if result.returncode == 0:
            self.assertIn("PASS check_mermaid", result.stdout)
        else:
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("BLOCKED check_mermaid", result.stdout)
        self.assertIn("mmdc", result.stdout)

    def test_java_runtime_shim_failure_reports_blocked(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            fake_java = Path(temp_dir) / "java"
            fake_java.write_text(
                "#!/bin/sh\n"
                "echo 'openjdk version \"17.0.10\"' >&2\n"
                "exit 0\n",
                encoding="utf-8",
            )
            fake_java.chmod(0o755)
            fake_javac = Path(temp_dir) / "javac"
            fake_javac.write_text(
                "#!/bin/sh\n"
                "echo 'Unable to locate a Java Runtime that supports javac.'\n"
                "exit 1\n",
                encoding="utf-8",
            )
            fake_javac.chmod(0o755)
            env = os.environ.copy()
            env["PATH"] = temp_dir + os.pathsep + env.get("PATH", "")
            result = self.run_script("--only", "check_java_smoke", env=env)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("BLOCKED check_java_smoke", result.stdout)
        self.assertIn("BLOCKED javac", result.stdout)
        self.assertIn("javac", result.stdout)

    def test_coding_problem_java_driver_blocker_reports_blocked(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            fake_java = Path(temp_dir) / "java"
            fake_java.write_text(
                "#!/bin/sh\n"
                "echo 'java version \"1.8.0_491\"' >&2\n"
                "exit 0\n",
                encoding="utf-8",
            )
            fake_java.chmod(0o755)
            fake_javac = Path(temp_dir) / "javac"
            fake_javac.write_text(
                "#!/bin/sh\n"
                "echo 'javac 1.8.0_491'\n"
                "exit 0\n",
                encoding="utf-8",
            )
            fake_javac.chmod(0o755)
            env = os.environ.copy()
            env["PATH"] = temp_dir + os.pathsep + env.get("PATH", "")
            result = self.run_script(
                "--only",
                "check_coding_problem_java_drivers",
                "--allow-unsafe-driver-execution",
                env=env,
            )

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("BLOCKED check_coding_problem_java_drivers", result.stdout)
        self.assertIn("Java toolchain must be Java 11+", result.stdout)

    def test_coding_problem_driver_checks_require_smoke_level_unsafe_ack(self):
        for check_name in ("check_coding_problem_python_drivers", "check_coding_problem_java_drivers"):
            with self.subTest(check_name=check_name):
                result = self.run_script("--only", check_name)

                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn(f"BLOCKED {check_name}: requires --allow-unsafe-driver-execution", result.stdout)
                self.assertEqual(result.stderr, "")

    def test_missing_mermaid_reports_blocked_with_temp_path(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            env = {"PATH": temp_dir}
            result = self.run_script("--only", "check_mermaid", env=env)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("BLOCKED check_mermaid", result.stdout)
        self.assertIn("mmdc", result.stdout)

    def test_dry_run_from_other_cwd_is_repo_independent(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.run_script(
                "--dry-run",
                "--only",
                "check_markdown_links",
                cwd=Path(temp_dir),
            )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("DRY-RUN check_markdown_links:", result.stdout)
        self.assertIn("scripts/check_markdown_links.py", result.stdout)


if __name__ == "__main__":
    unittest.main()
