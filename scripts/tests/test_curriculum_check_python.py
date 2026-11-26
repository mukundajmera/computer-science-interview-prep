import unittest
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

# Add repo root to path
repo_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(repo_root))

from scripts.curriculum_check_python import PythonProfile

class TestCurriculumCheckPython(unittest.TestCase):
    def setUp(self):
        self.profile = PythonProfile()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        
    def tearDown(self):
        self.temp_dir.cleanup()
        
    @patch('scripts.curriculum_check_python.check_python_runtime', return_value=False)
    def test_01_missing_python38(self, mock_check):
        task_def = {}
        res = self.profile.validate(task_def, self.temp_path)
        self.assertEqual(res["status"], "BLOCKED")
        self.assertIn("Missing Python3.8 runtime", res["reason"])

    def test_02_zero_tests(self):
        task_def = {
            "tests": ["test_zero.py"],
            "case_mappings": {"test_zero.py": "c1"}
        }
        
        test_file = self.temp_path / "test_zero.py"
        with open(test_file, "w") as f:
            f.write("import unittest\nclass TestZero(unittest.TestCase):\n  pass\n")
            
        res = self.profile.validate(task_def, self.temp_path)
        self.assertEqual(res["status"], "FAIL")
        self.assertIn("Zero tests", res["reason"])
        
    def test_03_skipped_tests(self):
        task_def = {
            "tests": ["test_skip.py"],
            "case_mappings": {"test_skip.py": "c1"}
        }
        
        test_file = self.temp_path / "test_skip.py"
        with open(test_file, "w") as f:
            f.write("import unittest\nclass TestSkip(unittest.TestCase):\n  @unittest.skip('skip')\n  def test_a(self):\n    pass\n")
            
        res = self.profile.validate(task_def, self.temp_path)
        self.assertEqual(res["status"], "FAIL")
        self.assertIn("Skipped tests", res["reason"])
        
    def test_04_wrong_version_collection(self):
        task_def = {
            "tests": ["test_v2.py"],
            "case_mappings": {"test_v2.py": "c1"}
        }
        
        test_file = self.temp_path / "test_v2.py"
        with open(test_file, "w") as f:
            f.write("import v1_basic\nimport unittest\nclass TestV2(unittest.TestCase):\n  def test_a(self):\n    pass\n")
            
        res = self.profile.validate(task_def, self.temp_path)
        self.assertEqual(res["status"], "FAIL")
        self.assertIn("Wrong-version collection", res["reason"])

    def test_05_missing_case_mappings(self):
        task_def = {
            "tests": ["test_ok.py"]
        }
        test_file = self.temp_path / "test_ok.py"
        test_file.touch()
        
        res = self.profile.validate(task_def, self.temp_path)
        self.assertEqual(res["status"], "FAIL")
        self.assertIn("Missing semantic case mapping", res["reason"])
        
    def test_06_test_failure(self):
        task_def = {
            "tests": ["test_fail.py"],
            "case_mappings": {"test_fail.py": "c1"}
        }
        
        test_file = self.temp_path / "test_fail.py"
        with open(test_file, "w") as f:
            f.write("import unittest\nclass TestFail(unittest.TestCase):\n  def test_a(self):\n    self.assertTrue(False)\n")
            
        res = self.profile.validate(task_def, self.temp_path)
        self.assertEqual(res["status"], "FAIL")
        self.assertIn("Test failures", res["reason"])
        
    def test_07_success(self):
        task_def = {
            "tests": ["test_success.py"],
            "case_mappings": {"test_success.py": "c1"}
        }
        
        test_file = self.temp_path / "test_success.py"
        with open(test_file, "w") as f:
            f.write("import unittest\nclass TestSuccess(unittest.TestCase):\n  def test_a(self):\n    self.assertTrue(True)\n")
            
        res = self.profile.validate(task_def, self.temp_path)
        self.assertEqual(res["status"], "PASS")
        self.assertEqual(res["metrics"]["tests_executed"], 1)

if __name__ == "__main__":
    unittest.main()
