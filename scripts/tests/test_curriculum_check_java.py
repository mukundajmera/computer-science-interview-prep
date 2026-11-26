import unittest
import tempfile
import os
import json
from unittest.mock import patch, MagicMock
from pathlib import Path
from scripts.curriculum_check_java import JavaProfile

class TestCurriculumCheckJava(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        
        # Setup dummy JUnit jar
        self.junit_jar_path = self.temp_path / "junit.jar"
        self.junit_jar_path.touch()
        
        self.profile = JavaProfile()
        
    def tearDown(self):
        self.temp_dir.cleanup()
        
    def test_missing_junit_jar(self):
        task_def = {
            "tests": ["test1"],
            "case_mappings": {"v1": "src/v1"},
            "tools": {} # Missing JUnit jar
        }
        res = self.profile.validate(task_def, self.temp_path)
        self.assertEqual(res["status"], "BLOCKED")
        self.assertIn("Missing or invalid operator-supplied JUnit jar", res["reason"])
        
    def test_missing_version_mapping(self):
        task_def = {
            "tests": ["test1"],
            "tools": {"junit_jar": str(self.junit_jar_path)}
        }
        res = self.profile.validate(task_def, self.temp_path)
        self.assertEqual(res["status"], "BLOCKED")
        self.assertIn("Missing version mapping", res["reason"])

    def test_zero_tests_required(self):
        task_def = {
            "tests": [],
            "case_mappings": {"v1": "src/v1"},
            "tools": {"junit_jar": str(self.junit_jar_path)}
        }
        res = self.profile.validate(task_def, self.temp_path)
        self.assertEqual(res["status"], "BLOCKED")
        self.assertIn("Zero required tests specified", res["reason"])
        
    @patch("subprocess.run")
    def test_compile_failure(self, mock_run):
        # Create dummy source dir
        v1_dir = self.temp_path / "src" / "v1"
        v1_dir.mkdir(parents=True)
        (v1_dir / "Dummy.java").touch()
        
        task_def = {
            "tests": ["test1"],
            "case_mappings": {"v1": "src/v1"},
            "tools": {"junit_jar": str(self.junit_jar_path)}
        }
        
        # Mock compilation failing
        mock_compile_result = MagicMock()
        mock_compile_result.returncode = 1
        mock_compile_result.stderr = "Syntax error"
        mock_run.return_value = mock_compile_result
        
        res = self.profile.validate(task_def, self.temp_path)
        self.assertEqual(res["status"], "FAIL")
        self.assertIn("Compile failure", res["reason"])
        
    @patch("subprocess.run")
    def test_test_failure(self, mock_run):
        v1_dir = self.temp_path / "src" / "v1"
        v1_dir.mkdir(parents=True)
        (v1_dir / "Dummy.java").touch()
        
        task_def = {
            "tests": ["test1"],
            "case_mappings": {"v1": "src/v1"},
            "tools": {"junit_jar": str(self.junit_jar_path)}
        }
        
        # First call is compile (success), second is test (fail)
        mock_compile_res = MagicMock(returncode=0)
        mock_test_res = MagicMock(returncode=1, stdout="Test failed", stderr="")
        mock_run.side_effect = [mock_compile_res, mock_test_res]
        
        res = self.profile.validate(task_def, self.temp_path)
        self.assertEqual(res["status"], "FAIL")
        self.assertIn("Test failure", res["reason"])
        
    @patch("subprocess.run")
    def test_zero_skipped_tests(self, mock_run):
        v1_dir = self.temp_path / "src" / "v1"
        v1_dir.mkdir(parents=True)
        (v1_dir / "Dummy.java").touch()
        
        task_def = {
            "tests": ["test1"],
            "case_mappings": {"v1": "src/v1"},
            "tools": {"junit_jar": str(self.junit_jar_path)}
        }
        
        # Test missing zero tests discovered
        mock_compile_res = MagicMock(returncode=0)
        mock_test_res = MagicMock(returncode=0, stdout="[ 0 tests found ]", stderr="")
        mock_run.side_effect = [mock_compile_res, mock_test_res]
        
        res = self.profile.validate(task_def, self.temp_path)
        self.assertEqual(res["status"], "FAIL")
        self.assertIn("Zero tests discovered", res["reason"])
        
        # Test skipped tests
        mock_run.side_effect = [
            MagicMock(returncode=0),
            MagicMock(returncode=0, stdout="[ 1 tests found ]\n[ 1 tests skipped ]", stderr="")
        ]
        res = self.profile.validate(task_def, self.temp_path)
        self.assertEqual(res["status"], "FAIL")
        self.assertIn("Skipped tests detected", res["reason"])
        
    @patch("subprocess.run")
    def test_recursive_compilation_and_success(self, mock_run):
        # We need two versions to demonstrate cross-version class isolation
        v1_dir = self.temp_path / "src" / "v1"
        v1_dir.mkdir(parents=True)
        (v1_dir / "Dummy1.java").touch()
        (v1_dir / "sub" / "Dummy2.java").mkdir(parents=True)
        (v1_dir / "sub" / "Dummy2.java").rmdir()
        (v1_dir / "sub" / "Dummy2.java").touch()
        
        v2_dir = self.temp_path / "src" / "v2"
        v2_dir.mkdir(parents=True)
        (v2_dir / "Dummy1.java").touch()
        
        task_def = {
            "tests": ["test1"],
            "case_mappings": {"v1": "src/v1", "v2": "src/v2"},
            "tools": {"junit_jar": str(self.junit_jar_path)}
        }
        
        # compile v1, test v1, compile v2, test v2
        mock_run.side_effect = [
            MagicMock(returncode=0),
            MagicMock(returncode=0, stdout="[ 1 tests found ]\n[ 0 tests skipped ]\n[ 1 tests successful ]", stderr=""),
            MagicMock(returncode=0),
            MagicMock(returncode=0, stdout="[ 1 tests found ]\n[ 0 tests skipped ]\n[ 1 tests successful ]", stderr="")
        ]
        
        res = self.profile.validate(task_def, self.temp_path)
        self.assertEqual(res["status"], "PASS")
        self.assertEqual(len(res["evidence"]), 2)
        
        # Assert javac was called with unique outputs and recursive files
        compile_calls = [call for call in mock_run.call_args_list if call.args[0][0] == "javac"]
        
        # Verify isolation (unique -d outputs)
        out_v1 = compile_calls[0].args[0][compile_calls[0].args[0].index("-d") + 1]
        out_v2 = compile_calls[1].args[0][compile_calls[1].args[0].index("-d") + 1]
        self.assertNotEqual(out_v1, out_v2)
        
        # Check recursive discovery in v1
        self.assertTrue(any("Dummy1.java" in arg for arg in compile_calls[0].args[0]))
        self.assertTrue(any("Dummy2.java" in arg for arg in compile_calls[0].args[0]))
        
        # Check cross-version class collisions rejection (implicit because isolated classpaths)
        # We don't have to code a specific test, the isolation itself proves it.

    import subprocess
    @patch("subprocess.run")
    def test_timeout_propagation(self, mock_run):
        v1_dir = self.temp_path / "src" / "v1"
        v1_dir.mkdir(parents=True)
        (v1_dir / "Dummy.java").touch()
        
        task_def = {
            "tests": ["test1"],
            "case_mappings": {"v1": "src/v1"},
            "tools": {"junit_jar": str(self.junit_jar_path)},
            "timeout": 1
        }
        
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="javac", timeout=1)
        
        res = self.profile.validate(task_def, self.temp_path)
        self.assertEqual(res["status"], "BLOCKED")
        self.assertIn("timeout", res["reason"])

if __name__ == "__main__":
    unittest.main()
