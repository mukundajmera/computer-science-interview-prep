import sys
import os
import ast
import subprocess
import tempfile
import json
import re
from pathlib import Path
from typing import Dict, Any, List, Set

try:
    from .check_curriculum_task import ProfileExtensionInterface
except ImportError:
    class ProfileExtensionInterface:
        def validate(self, task_def: Dict[str, Any], target_dir: Path) -> Dict[str, Any]:
            raise NotImplementedError()

def check_python_runtime() -> bool:
    return sys.version_info >= (3, 8)

def extract_imported_names(file_path: Path) -> Set[str]:
    imported = set()
    try:
        content = file_path.read_text(encoding='utf-8')
        tree = ast.parse(content, filename=str(file_path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported.add(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imported.add(node.module.split('.')[0])
    except Exception:
        pass
    return imported

class PythonProfile(ProfileExtensionInterface):
    """Profile extension for isolated Python testing."""
    
    def validate(self, task_def: Dict[str, Any], target_dir: Path) -> Dict[str, Any]:
        if not check_python_runtime():
            return {
                "status": "BLOCKED", 
                "reason": "Missing Python3.8 runtime as a limitation"
            }
            
        tests = task_def.get("tests", [])
        mappings = task_def.get("case_mappings", {})
        
        if not tests:
            return {"status": "FAIL", "reason": "Zero tests requested"}
            
        if not mappings:
            return {"status": "FAIL", "reason": "Missing semantic case mapping"}
            
        test_paths = []
        for test_name in tests:
            test_path = target_dir / test_name
            if not test_path.exists():
                return {"status": "FAIL", "reason": f"Test not found: {test_name}"}
            test_paths.append(str(test_path))

        # Check imports for "wrong-version collection" or "accidental v1-only pass".
        # We can detect this by examining imports in tests. If a test file in v2 imports a v1 module,
        # it might be accidentally testing the v1 implementation instead of v2.
        # But this implies we need to know the 'current' version and the 'disallowed' version.
        # We can extract the target version from the target_dir or the test module path.
        for test_path in test_paths:
            p = Path(test_path)
            rel_path = p.relative_to(target_dir).parts
            
            # Simple heuristic: if 'v2' in path/name, reject 'v1' imports
            # If 'v3' in path/name, reject 'v1' and 'v2' imports
            version_match = re.search(r'v([0-9]+)', str(p))
            if version_match:
                curr_version = int(version_match.group(1))
                imported = extract_imported_names(p)
                for imp in imported:
                    imp_v_match = re.search(r'v([0-9]+)', imp)
                    if imp_v_match:
                        imp_version = int(imp_v_match.group(1))
                        if imp_version < curr_version:
                            return {"status": "FAIL", "reason": f"Wrong-version collection: test {p.name} imports older version module {imp}"}

        # Check that we don't import task-provided module names in the checker process
        # (This is already satisfied by running tests in a subprocess)
        
        runner_script = """
import unittest
import sys
import json
import os

if __name__ == '__main__':
    target_dir = sys.argv[1]
    test_files = sys.argv[2].split(',')
    
    if target_dir not in sys.path:
        sys.path.insert(0, target_dir)
        
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    
    for test_file in test_files:
        rel_path = os.path.relpath(test_file, target_dir)
        module_name = rel_path.replace('.py', '').replace(os.sep, '.')
        try:
            loaded = loader.loadTestsFromName(module_name)
            suite.addTests(loaded)
        except Exception as e:
            print(json.dumps({"error": f"Failed to load {module_name}: {str(e)}"}))
            sys.exit(1)
            
    runner = unittest.TextTestRunner(verbosity=0, stream=open(os.devnull, 'w'))
    result = runner.run(suite)
    
    results = {
        "testsRun": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped)
    }
    
    print(json.dumps(results))
    sys.exit(0 if result.wasSuccessful() else 1)
"""
        
        with tempfile.NamedTemporaryFile('w', suffix='.py', delete=False) as f:
            f.write(runner_script)
            runner_path = f.name
            
        env = os.environ.copy()
        env['PYTHONDONTWRITEBYTECODE'] = '1'
        
        try:
            cmd = [sys.executable, "-B", runner_path, str(target_dir), ",".join(test_paths)]
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                env=env,
                timeout=60
            )
            
            try:
                out_lines = res.stdout.strip().split('\n')
                result_data = json.loads(out_lines[-1])
            except (json.JSONDecodeError, IndexError):
                return {"status": "FAIL", "reason": f"Test runner failed or returned malformed output: {res.stderr} {res.stdout}"}
                
            if "error" in result_data:
                return {"status": "FAIL", "reason": result_data["error"]}
                
            testsRun = result_data.get("testsRun", 0)
            failures = result_data.get("failures", 0)
            errors = result_data.get("errors", 0)
            skipped = result_data.get("skipped", 0)
            
            if testsRun == 0:
                return {"status": "FAIL", "reason": "Zero tests executed"}
            if skipped > 0:
                return {"status": "FAIL", "reason": f"Skipped tests are not allowed. Skipped: {skipped}"}
            if failures > 0 or errors > 0:
                return {"status": "FAIL", "reason": f"Test failures ({failures}) or errors ({errors}) present"}
                
        finally:
            os.remove(runner_path)
            
        return {
            "status": "PASS",
            "metrics": {
                "tests_executed": testsRun,
                "skipped": skipped
            },
            "evidence": {
                "runner_exit_code": res.returncode,
                "stdout_summary": out_lines[-1]
            }
        }
