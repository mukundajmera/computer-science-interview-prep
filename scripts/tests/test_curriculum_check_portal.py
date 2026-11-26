import unittest
from pathlib import Path
import tempfile
import os
import subprocess
from unittest.mock import patch

from scripts.curriculum_check_portal import PortalProfile

class TestCurriculumCheckPortal(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.target_dir = Path(self.temp_dir.name)
        self.profile = PortalProfile()
        
        # Setup valid baseline
        (self.target_dir / "package.json").touch()
        (self.target_dir / "package-lock.json").touch()
        
        src_dir = self.target_dir / "src"
        (src_dir / "content").mkdir(parents=True)
        (src_dir / "lib").mkdir(parents=True)
        
        with open(src_dir / "content" / "route-manifest.ts", "w") as f:
            f.write("export const PUBLIC_ROUTE_ROOTS = new Set(['/portal/valid-route']);")
            
        with open(src_dir / "lib" / "sections.ts", "w") as f:
            f.write("export const PORTAL_SECTIONS = [{ path: '/portal/valid-route' }];")
            
        self.valid_task_def = {
            "validation_command": "npm run build",
            "expected_routes": ["/portal/valid-route"],
            "expected_interactions": ["click-login", "submit-form"],
            "test_ids": ["test-123", "test-456"]
        }

    def tearDown(self):
        self.temp_dir.cleanup()
        
    @patch('subprocess.run')
    def test_success_baseline(self, mock_run):
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "Build successful"
        mock_run.return_value.stderr = ""
        
        res = self.profile.validate(self.valid_task_def, self.target_dir)
        self.assertEqual(res["status"], "PASS")
        self.assertEqual(res["evidence"]["exit_code"], 0)
        self.assertEqual(res["evidence"]["test_ids"], ["test-123", "test-456"])
        
        # Verify it routes outputs to /tmp via NEXT_DIST_DIR
        env_args = mock_run.call_args[1].get('env', {})
        self.assertIn('NEXT_DIST_DIR', env_args)
        self.assertTrue(env_args['NEXT_DIST_DIR'].startswith('/tmp/'))
        
        # Verify call arguments are safely split
        cmd_args = mock_run.call_args[0][0]
        self.assertEqual(cmd_args, ["npm", "run", "build"])
        
    def test_missing_dependencies_rejected(self):
        # Remove lockfile
        os.remove(self.target_dir / "package-lock.json")
        res = self.profile.validate(self.valid_task_def, self.target_dir)
        self.assertEqual(res["status"], "FAIL")
        self.assertIn("Missing lockfile", res["reason"])
        
        # Remove package.json
        (self.target_dir / "package-lock.json").touch()
        os.remove(self.target_dir / "package.json")
        res = self.profile.validate(self.valid_task_def, self.target_dir)
        self.assertEqual(res["status"], "FAIL")
        self.assertIn("Missing package.json", res["reason"])
        
    def test_unapproved_shell_argv(self):
        task_def = dict(self.valid_task_def)
        task_def["validation_command"] = "npm install && npm run build"
        res = self.profile.validate(task_def, self.target_dir)
        self.assertEqual(res["status"], "FAIL")
        self.assertIn("Unapproved shell argv", res["reason"])
        
    def test_route_navigation_mismatch(self):
        task_def = dict(self.valid_task_def)
        task_def["expected_routes"] = ["/portal/invalid-route"]
        res = self.profile.validate(task_def, self.target_dir)
        self.assertEqual(res["status"], "FAIL")
        self.assertIn("Route/navigation mismatch", res["reason"])
        
    def test_missing_route_files(self):
        os.remove(self.target_dir / "src" / "content" / "route-manifest.ts")
        res = self.profile.validate(self.valid_task_def, self.target_dir)
        self.assertEqual(res["status"], "FAIL")
        self.assertIn("Route manifest or navigation file missing", res["reason"])
        
    def test_missing_interaction_regression(self):
        task_def = dict(self.valid_task_def)
        task_def["expected_interactions"] = []
        res = self.profile.validate(task_def, self.target_dir)
        self.assertEqual(res["status"], "FAIL")
        self.assertIn("Missing interaction regression test IDs", res["reason"])
        
    @patch('subprocess.run')
    def test_missing_test_ids(self, mock_run):
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "Build successful"
        mock_run.return_value.stderr = ""
        
        task_def = dict(self.valid_task_def)
        task_def["test_ids"] = []
        task_def["expected_interactions"] = []
        res = self.profile.validate(task_def, self.target_dir)
        self.assertEqual(res["status"], "FAIL")
        self.assertIn("Missing interaction regression test IDs", res["reason"])
        
    @patch('subprocess.run')
    def test_build_lint_failure(self, mock_run):
        mock_run.return_value.returncode = 1
        mock_run.return_value.stdout = "Error"
        mock_run.return_value.stderr = "Fatal error"
        
        task_def = dict(self.valid_task_def)
        res = self.profile.validate(task_def, self.target_dir)
        self.assertEqual(res["status"], "FAIL")
        self.assertIn("Build/lint or validation failure", res["reason"])
        
if __name__ == "__main__":
    unittest.main()
