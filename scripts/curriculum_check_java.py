import json
import os
import subprocess
import tempfile
import shutil
import re
from pathlib import Path
from typing import Dict, Any, List

try:
    from scripts.check_curriculum_task import ProfileExtensionInterface
except ImportError:
    class ProfileExtensionInterface:
        def validate(self, task_def: Dict[str, Any], target_dir: Path) -> Dict[str, Any]:
            raise NotImplementedError()

class JavaProfile(ProfileExtensionInterface):
    """
    Java checker profile for curriculum tasks.
    Compiles with javac --release 11 to unique isolated outputs.
    Executes JUnit standalone console runner.
    """
    
    def validate(self, task_def: Dict[str, Any], target_dir: Path) -> Dict[str, Any]:
        tools = task_def.get("tools", {})
        junit_jar = tools.get("junit_jar")
        if not junit_jar or not os.path.isfile(junit_jar):
            return {"status": "BLOCKED", "reason": "Missing or invalid operator-supplied JUnit jar"}
            
        case_mappings = task_def.get("case_mappings", {})
        if not case_mappings:
            return {"status": "BLOCKED", "reason": "Missing version mapping"}
            
        tests = task_def.get("tests", [])
        if not tests:
            return {"status": "BLOCKED", "reason": "Zero required tests specified"}
            
        timeout = task_def.get("timeout", 60)
            
        # Overall state
        all_metrics = {}
        all_evidence = []
        
        # We need an isolated temp dir to hold all version outputs
        base_temp = tempfile.mkdtemp(prefix="java_checker_")
        
        try:
            for version_name, component_subpath in case_mappings.items():
                version_dir = target_dir / component_subpath
                if not version_dir.exists():
                    return {"status": "BLOCKED", "reason": f"Version mapping target does not exist: {component_subpath}"}
                
                # Find all .java files recursively
                java_files = list(version_dir.rglob("*.java"))
                if not java_files:
                    return {"status": "BLOCKED", "reason": f"No Java files found for version mapping: {version_name}"}
                    
                # Setup unique isolated output directory
                out_dir = Path(base_temp) / version_name
                out_dir.mkdir(parents=True, exist_ok=True)
                
                # Compile
                java_file_strs = [str(f.absolute()) for f in java_files]
                compile_cmd = ["javac", "--release", "11", "-d", str(out_dir)] + java_file_strs
                
                try:
                    comp_res = subprocess.run(compile_cmd, capture_output=True, text=True, timeout=timeout)
                    if comp_res.returncode != 0:
                        return {
                            "status": "FAIL",
                            "reason": f"Compile failure in {version_name}",
                            "details": comp_res.stderr
                        }
                except subprocess.TimeoutExpired:
                    return {"status": "BLOCKED", "reason": f"Compilation timeout in {version_name}"}
                except Exception as e:
                    return {"status": "BLOCKED", "reason": f"Unexpected compile error: {str(e)}"}
                    
                # Run JUnit tests
                # Ensure we run exactly the tests required
                test_cmd = [
                    "java", "-jar", junit_jar,
                    "execute",
                    "--class-path", str(out_dir),
                    "--details=summary"
                ]
                
                for t in tests:
                    test_cmd.extend(["-c", t])
                
                try:
                    test_res = subprocess.run(test_cmd, capture_output=True, text=True, timeout=timeout)
                    
                    if test_res.returncode != 0:
                        return {
                            "status": "FAIL",
                            "reason": f"Test failure in {version_name}",
                            "details": test_res.stdout + test_res.stderr
                        }
                        
                    tests_found = 0
                    tests_skipped = 0
                    tests_successful = 0
                    
                    for line in test_res.stdout.splitlines():
                        line = line.strip()
                        if "tests found" in line:
                            m = re.search(r'\[\s*(\d+)\s+tests found', line)
                            if m: tests_found = int(m.group(1))
                        elif "tests skipped" in line:
                            m = re.search(r'\[\s*(\d+)\s+tests skipped', line)
                            if m: tests_skipped = int(m.group(1))
                        elif "tests successful" in line:
                            m = re.search(r'\[\s*(\d+)\s+tests successful', line)
                            if m: tests_successful = int(m.group(1))
                            
                    if tests_found == 0:
                        return {"status": "FAIL", "reason": f"Zero tests discovered in {version_name}"}
                    if tests_skipped > 0:
                        return {"status": "FAIL", "reason": f"Skipped tests detected in {version_name}"}
                    
                    # Instead of a weak check, we mandate that every requested case ran successfully
                    if tests_successful < len(tests):
                        return {"status": "FAIL", "reason": f"Not all required tests passed in {version_name}. Expected at least {len(tests)}, got {tests_successful}"}
                        
                    all_evidence.append({
                        "version": version_name,
                        "tests_passed": tests_successful
                    })
                    
                except subprocess.TimeoutExpired:
                    return {"status": "BLOCKED", "reason": f"Test execution timeout in {version_name}"}
                    
        finally:
            shutil.rmtree(base_temp, ignore_errors=True)
            
        return {
            "status": "PASS",
            "reason": "All Java checks passed",
            "evidence": all_evidence
        }
