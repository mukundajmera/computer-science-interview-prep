import unittest
import os
import tempfile
import json
from pathlib import Path
from scripts.curriculum_check_docs import DocsProfile

class TestDocsProfile(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        
    def tearDown(self):
        self.temp_dir.cleanup()
        
    def test_missing_artifact(self):
        profile = DocsProfile()
        task_def = {"required_artifacts": ["missing.md"]}
        res = profile.validate(task_def, self.temp_path)
        self.assertEqual(res["status"], "FAIL")
        self.assertIn("Missing required artifact", res["reason"])
        
    def test_broken_link(self):
        profile = DocsProfile()
        md_file = self.temp_path / "test.md"
        with open(md_file, "w") as f:
            f.write("Here is a [broken link](does_not_exist.md).")
            
        task_def = {"required_artifacts": ["test.md"]}
        res = profile.validate(task_def, self.temp_path)
        self.assertEqual(res["status"], "FAIL")
        self.assertIn("Broken local link", res["reason"])
        
    def test_valid_link(self):
        profile = DocsProfile()
        md_file = self.temp_path / "test.md"
        target_file = self.temp_path / "target.md"
        with open(md_file, "w") as f:
            f.write("Here is a [valid link](target.md).")
        target_file.touch()
            
        task_def = {"required_artifacts": ["test.md"]}
        res = profile.validate(task_def, self.temp_path)
        self.assertEqual(res["status"], "PASS")
        self.assertEqual(res["metrics"]["checked_links"], 1)

    def test_missing_records_if_required(self):
        profile = DocsProfile()
        md_file = self.temp_path / "test.md"
        with open(md_file, "w") as f:
            f.write("Some text here.")
            
        task_def = {"required_artifacts": ["test.md"], "require_records": True}
        res = profile.validate(task_def, self.temp_path)
        self.assertEqual(res["status"], "FAIL")
        self.assertIn("Missing structured primary-source/units/worked-trace records", res["reason"])
        
    def test_valid_records(self):
        profile = DocsProfile()
        md_file = self.temp_path / "test.md"
        with open(md_file, "w") as f:
            f.write("We have a primary-source and a worked-trace. Also some units.")
            
        task_def = {"required_artifacts": ["test.md"], "require_records": True}
        res = profile.validate(task_def, self.temp_path)
        self.assertEqual(res["status"], "PASS")
        
    def test_fenced_probe_success(self):
        profile = DocsProfile()
        md_file = self.temp_path / "test.md"
        with open(md_file, "w") as f:
            f.write("```python\n# probe-opt-in\nprint('hello')\n```")
            
        task_def = {"required_artifacts": ["test.md"]}
        res = profile.validate(task_def, self.temp_path)
        self.assertEqual(res["status"], "PASS")
        self.assertEqual(res["metrics"]["fenced_probes"], 1)

    def test_fenced_probe_fail(self):
        profile = DocsProfile()
        md_file = self.temp_path / "test.md"
        with open(md_file, "w") as f:
            f.write("```python\n# probe-opt-in\nimport sys; sys.exit(1)\n```")
            
        task_def = {"required_artifacts": ["test.md"]}
        res = profile.validate(task_def, self.temp_path)
        self.assertEqual(res["status"], "FAIL")
        self.assertIn("Fenced probe failed", res["reason"])

    def test_unsupported_language_probe_fail(self):
        profile = DocsProfile()
        md_file = self.temp_path / "test.md"
        with open(md_file, "w") as f:
            f.write("```bash\n# probe-opt-in\necho 'hello'\n```")
            
        task_def = {"required_artifacts": ["test.md"]}
        res = profile.validate(task_def, self.temp_path)
        self.assertEqual(res["status"], "FAIL")
        self.assertIn("Unsupported fenced-language probe (bash)", res["reason"])

    def test_mermaid_missing_cli(self):
        # We need to simulate missing mmdc. By default, it will probably fail if mmdc is not installed.
        profile = DocsProfile()
        # Override PATH to ensure mmdc is not found, or use a fake mmdc_cmd
        os.environ["MMDC_PATH"] = "mmdc_fake_command_that_does_not_exist"
        mmd_file = self.temp_path / "test.mmd"
        mmd_file.touch()
        
        task_def = {"required_artifacts": ["test.mmd"]}
        res = profile.validate(task_def, self.temp_path)
        self.assertEqual(res["status"], "FAIL")
        self.assertIn("Missing Mermaid CLI", res["reason"])

if __name__ == "__main__":
    unittest.main()
