import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "check_java_smoke.py"


class JavaSmokePreflightTest(unittest.TestCase):
    def write_tool(self, directory: Path, name: str, body: str) -> None:
        tool = directory / name
        tool.write_text("#!/bin/sh\n" + body, encoding="utf-8")
        tool.chmod(0o755)

    def run_script(
        self,
        *args: str,
        path_dir: Path,
        root: Path | None = None,
    ) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["PATH"] = str(path_dir)
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(root or REPO_ROOT), *args],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            check=False,
        )

    def test_java_8_is_blocked_before_compile(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            tools = Path(temp_dir)
            self.write_tool(tools, "java", "echo 'java version \"1.8.0_491\"' >&2\nexit 0\n")
            self.write_tool(tools, "javac", "echo 'javac 17.0.10'\nexit 0\n")

            result = self.run_script("--preflight-only", path_dir=tools)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("BLOCKED java_version", result.stdout)
        self.assertIn("Java 11+", result.stdout)

    def test_unusable_javac_shim_is_blocked(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            tools = Path(temp_dir)
            self.write_tool(tools, "java", "echo 'openjdk version \"17.0.10\"' >&2\nexit 0\n")
            self.write_tool(
                tools,
                "javac",
                "echo 'Unable to locate a Java Runtime that supports javac.'\nexit 1\n",
            )

            result = self.run_script("--preflight-only", path_dir=tools)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("BLOCKED javac", result.stdout)
        self.assertIn("required tool not usable", result.stdout)

    def test_missing_junit_jar_is_blocked(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            tools = Path(temp_dir)
            self.write_tool(tools, "java", "echo 'openjdk version \"17.0.10\"' >&2\nexit 0\n")
            self.write_tool(tools, "javac", "echo 'javac 17.0.10'\nexit 0\n")

            result = self.run_script("--preflight-only", "--junit-jar", str(tools / "missing.jar"), path_dir=tools)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("BLOCKED junit", result.stdout)
        self.assertIn("missing JUnit console jar", result.stdout)

    def test_compile_uses_output_dir_outside_repository(self):
        with tempfile.TemporaryDirectory() as temp_dir, tempfile.TemporaryDirectory() as repo_dir:
            tools = Path(temp_dir)
            root = Path(repo_dir)
            source_dir = root / "sample" / "java" / "v1-basic"
            output_dir = root / "classes"
            jar = root / "junit-platform-console-standalone.jar"
            source_dir.mkdir(parents=True)
            (source_dir / "Demo.java").write_text("class Demo {}\n", encoding="utf-8")
            jar.write_bytes(b"jar")
            self.write_tool(tools, "java", "echo 'openjdk version \"17.0.10\"' >&2\nexit 0\n")
            self.write_tool(tools, "javac", "echo 'javac 17.0.10'\nexit 0\n")

            result = self.run_script(
                "--compile-target",
                str(source_dir),
                "--output-dir",
                str(output_dir),
                "--junit-jar",
                str(jar),
                path_dir=tools,
                root=root,
            )

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("output directory must be outside repository", result.stderr)

    def test_preflight_and_compile_pass_with_fake_java_toolchain(self):
        with tempfile.TemporaryDirectory() as temp_dir, tempfile.TemporaryDirectory() as repo_dir:
            tools = Path(temp_dir)
            root = Path(repo_dir)
            source_dir = root / "sample" / "java" / "v1-basic"
            output_dir = Path(temp_dir) / "classes"
            jar = root / "junit-platform-console-standalone.jar"
            source_dir.mkdir(parents=True)
            (source_dir / "Demo.java").write_text("class Demo {}\n", encoding="utf-8")
            jar.write_bytes(b"jar")
            self.write_tool(tools, "java", "echo 'openjdk version \"17.0.10\"' >&2\nexit 0\n")
            self.write_tool(
                tools,
                "javac",
                "if [ \"$1\" = '-version' ]; then echo 'javac 17.0.10'; exit 0; fi\nexit 0\n",
            )

            result = self.run_script(
                "--compile-target",
                str(source_dir),
                "--output-dir",
                str(output_dir),
                "--junit-jar",
                str(jar),
                path_dir=tools,
                root=root,
            )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS java_version", result.stdout)
        self.assertIn("PASS javac", result.stdout)
        self.assertIn("PASS junit", result.stdout)
        self.assertIn("PASS compile", result.stdout)


if __name__ == "__main__":
    unittest.main()
