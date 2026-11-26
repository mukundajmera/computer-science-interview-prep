import unittest
import json
import os
import tempfile
from pathlib import Path

from scripts.check_curriculum_task import (
    validate_path_safety,
    parse_evidence,
    validate_task_definition,
    process_checker,
    main
)

class TestCurriculumCheckContract(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        
    def tearDown(self):
        self.temp_dir.cleanup()
        
    def test_01_reject_unsafe_paths(self):
        """1. Reject unsafe/absolute/traversal/symlink paths."""
        with self.assertRaises(ValueError) as ctx:
            validate_path_safety("/etc/passwd", allow_absolute_for_testing=False)
        self.assertIn("Absolute path not allowed", str(ctx.exception))
        
        with self.assertRaises(ValueError) as ctx:
            validate_path_safety("../some_dir", allow_absolute_for_testing=False)
        self.assertIn("Directory traversal not allowed", str(ctx.exception))
        
        # Test symlink
        os.symlink(self.temp_path / "target", self.temp_path / "link")
        # Change to temp dir to test symlink safely
        cwd = os.getcwd()
        os.chdir(self.temp_path)
        try:
            with self.assertRaises(ValueError) as ctx:
                validate_path_safety("link/file", allow_absolute_for_testing=False)
            self.assertIn("Symlinks not allowed", str(ctx.exception))
        finally:
            os.chdir(cwd)

    def test_02_unknown_task_profile(self):
        """2. Reject unknown task/profile."""
        catalog_data = {
            "tasks": {
                "known_task": {
                    "tests": ["test1"],
                    "case_mappings": {"t1": "c1"},
                    "allowed_components": ["comp"],
                    "required_artifacts": ["comp/file"],
                    "profile": "known_but_unimplemented"
                }
            }
        }
        cat_file = self.temp_path / "cat.json"
        with open(cat_file, "w") as f:
            json.dump(catalog_data, f)
            
        # Test unknown task
        res1 = process_checker(str(cat_file), "unknown_task", str(self.temp_path))
        self.assertEqual(res1["status"], "BLOCKED")
        self.assertIn("Unknown task", res1["reason"])
        
        # Test known task but unimplemented profile
        comp_dir = self.temp_path / "comp"
        comp_dir.mkdir()
        req_file = comp_dir / "file"
        req_file.touch()
        
        res2 = process_checker(str(cat_file), "known_task", str(self.temp_path))
        self.assertEqual(res2["status"], "BLOCKED")
        self.assertIn("Unimplemented profile", res2["reason"])

    def test_03_missing_required_files(self):
        """3. Reject missing required files."""
        task_def = {
            "tests": ["test1"],
            "case_mappings": {"t1": "c1"},
            "allowed_components": ["src"],
            "required_artifacts": ["src/missing.py"],
            "profile": "test"
        }
        res = validate_task_definition(task_def, self.temp_path)
        self.assertEqual(res["status"], "BLOCKED")
        self.assertIn("Missing required artifact", res["reason"])

    def test_04_missing_case_mappings(self):
        """4. Reject missing case mappings."""
        task_def = {
            "tests": ["test1"],
            "allowed_components": ["src"],
            "required_artifacts": ["src/exist.py"],
            "profile": "test"
        }
        res = validate_task_definition(task_def, self.temp_path)
        self.assertEqual(res["status"], "BLOCKED")
        self.assertIn("Missing explicit test/version/case mappings", res["reason"])

    def test_05_malformed_evidence(self):
        """5. Reject malformed evidence."""
        ev_file = self.temp_path / "ev.json"
        with open(ev_file, "w") as f:
            f.write("not json")
            
        with self.assertRaises(ValueError) as ctx:
            parse_evidence(str(ev_file))
        self.assertIn("invalid JSON", str(ctx.exception))
        
        with open(ev_file, "w") as f:
            json.dump({"foo": "bar"}, f)
            
        with self.assertRaises(ValueError) as ctx:
            parse_evidence(str(ev_file))
        self.assertIn("missing or invalid status", str(ctx.exception))
        
        with open(ev_file, "w") as f:
            json.dump({"status": "INVALID_STATE"}, f)
            
        with self.assertRaises(ValueError) as ctx:
            parse_evidence(str(ev_file))
        self.assertIn("missing or invalid status", str(ctx.exception))

    def test_06_empty_tests(self):
        """6. Reject empty tests."""
        task_def = {
            "tests": [],
            "case_mappings": {"t1": "c1"},
            "allowed_components": ["src"],
            "required_artifacts": ["src/exist.py"],
            "profile": "test"
        }
        res = validate_task_definition(task_def, self.temp_path)
        self.assertEqual(res["status"], "BLOCKED")
        self.assertIn("Empty tests are not allowed", res["reason"])

    def test_07_unimplemented_profiles_never_success(self):
        """7. Empty tests, unavailable tools and unimplemented profiles are never success."""
        task_def = {
            "tests": ["t1"],
            "case_mappings": {"t1": "c1"},
            "allowed_components": ["src"],
            "required_artifacts": ["src/exist.py"],
            "profile": "some_profile",
            "validation_command": "echo 'SUCCESS'"
        }
        src_dir = self.temp_path / "src"
        src_dir.mkdir()
        req_file = src_dir / "exist.py"
        req_file.touch()
        
        res = validate_task_definition(task_def, self.temp_path)
        self.assertEqual(res["status"], "BLOCKED")
        self.assertIn("Unimplemented profile", res["reason"])
        # ensure validation_command doesn't get evaluated implicitly

    def test_08_component_aware_whitelists(self):
        """8. Reject artifacts not in component-aware whitelists."""
        task_def = {
            "tests": ["t1"],
            "case_mappings": {"t1": "c1"},
            "allowed_components": ["src/whitelisted"],
            "required_artifacts": ["src/other/exist.py"],
            "profile": "some_profile"
        }
        src_dir = self.temp_path / "src" / "other"
        src_dir.mkdir(parents=True)
        req_file = src_dir / "exist.py"
        req_file.touch()
        
        res = validate_task_definition(task_def, self.temp_path)
        self.assertEqual(res["status"], "BLOCKED")
        self.assertIn("not in whitelisted components", res["reason"])

if __name__ == "__main__":
    unittest.main()
