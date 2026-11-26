import sys
import json
import os
import argparse
import unittest
import subprocess
import tempfile
import re
from pathlib import Path
from typing import Dict, Any, List

class ProfileExtensionInterface:
    """Extension interface for later profile modules."""
    def validate(self, task_def: Dict[str, Any], target_dir: Path) -> Dict[str, Any]:
        raise NotImplementedError("Profile not implemented: MUST return BLOCKED")


class JavaProfile(ProfileExtensionInterface):
    def validate(self, task_def: Dict[str, Any], target_dir: Path) -> Dict[str, Any]:
        junit_jar = os.environ.get("JUNIT_JAR")
        if not junit_jar or not os.path.exists(junit_jar):
            return {"status": "BLOCKED", "reason": "Missing preloaded tools/artifacts: JUNIT_JAR"}
            
        versions = task_def.get("versions", [])
        if not versions:
            return {"status": "BLOCKED", "reason": "Missing versions in task definition"}
            
        env = os.environ.copy()
        for k in ["AWS_ACCESS_KEY_ID", "GITHUB_TOKEN", "HTTP_PROXY"]:
            env.pop(k, None)
            
        total_tests = 0
        seen_versions = set()
        
        for version in versions:
            if version in seen_versions:
                return {"status": "FAIL", "reason": f"Version collision detected: {version}"}
            seen_versions.add(version)
            
            ver_dir = target_dir / version
            if not ver_dir.exists():
                return {"status": "BLOCKED", "reason": f"Version directory {version} missing"}
            
            sources = []
            for root, _, files in os.walk(ver_dir):
                for f in files:
                    if f.endswith(".java"):
                        sources.append(os.path.join(root, f))
            
            if not sources:
                return {"status": "BLOCKED", "reason": f"No Java sources for {version}"}
                
            with tempfile.TemporaryDirectory() as tmpdir:
                cmd = ["javac", "--release", "11", "-cp", junit_jar, "-d", tmpdir] + sources
                res = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=30)
                if res.returncode != 0:
                    return {"status": "FAIL", "reason": f"Compilation failed: {res.stderr}"}
                
                test_cmd = ["java", "-jar", junit_jar, "--class-path", tmpdir, "--scan-class-path"]
                try:
                    tres = subprocess.run(test_cmd, env=env, capture_output=True, text=True, timeout=30)
                except subprocess.TimeoutExpired:
                    return {"status": "FAIL", "reason": "Test execution timeout"}
                
                if tres.returncode != 0:
                    return {"status": "FAIL", "reason": f"Tests failed: {tres.stderr}"}
                
                if "0 tests successful" in tres.stdout or "0 tests found" in tres.stdout or "0 tests executed" in tres.stdout:
                    return {"status": "FAIL", "reason": "Zero tests executed"}
                
                total_tests += 1
                
        if "regressions" in task_def:
            for reg in task_def["regressions"]:
                if not reg.get("found"):
                    return {"status": "FAIL", "reason": f"Missing requested regression evidence: {reg}"}
                
        return {"status": "PASS", "reason": "Java tests passed"}


class PythonProfile(ProfileExtensionInterface):
    def validate(self, task_def: Dict[str, Any], target_dir: Path) -> Dict[str, Any]:
        versions = task_def.get("versions", [])
        if not versions:
            return {"status": "BLOCKED", "reason": "Missing versions in task definition"}
            
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        for k in ["AWS_ACCESS_KEY_ID", "GITHUB_TOKEN", "HTTP_PROXY"]:
            env.pop(k, None)
            
        seen_versions = set()
        for version in versions:
            if version in seen_versions:
                return {"status": "FAIL", "reason": f"Version collision detected: {version}"}
            seen_versions.add(version)
            
            ver_dir = target_dir / version
            if not ver_dir.exists():
                return {"status": "BLOCKED", "reason": f"Version directory {version} missing"}
                
            cmd = [sys.executable, "-B", "-m", "pytest", str(ver_dir), "-v"]
            try:
                res = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=30)
            except subprocess.TimeoutExpired:
                return {"status": "FAIL", "reason": "Timeout during Python execution"}
                
            if res.returncode != 0:
                if res.returncode == 5:
                    return {"status": "FAIL", "reason": "Zero tests executed"}
                return {"status": "FAIL", "reason": f"Python tests failed: {res.stderr or res.stdout}"}
                
            if "collected 0 items" in res.stdout:
                return {"status": "FAIL", "reason": "Zero tests executed"}
                
        if "regressions" in task_def:
            for reg in task_def["regressions"]:
                if not reg.get("found"):
                    return {"status": "FAIL", "reason": f"Missing requested regression evidence: {reg}"}
                    
        return {"status": "PASS", "reason": "Python tests passed"}


class DocumentationProfile(ProfileExtensionInterface):
    def validate(self, task_def: Dict[str, Any], target_dir: Path) -> Dict[str, Any]:
        required_files = task_def.get("required_artifacts", [])
        
        for rf in required_files:
            fpath = target_dir / rf
            if not fpath.exists():
                return {"status": "BLOCKED", "reason": f"Missing doc file: {rf}"}
            
            with open(fpath, "r") as f:
                content = f.read()
                
                # Check for explicit worked calculations if required
                reqs = task_def.get("requirements", [])
                
                # We need to simulate checking executable fenced snippets by writing them to temp files and running them.
                snippets = re.findall(r'```python\n(.*?)\n```', content, re.DOTALL)
                for snippet in snippets:
                    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as temp_snippet:
                        temp_snippet.write(snippet)
                        temp_snippet_path = temp_snippet.name
                        
                    try:
                        env = os.environ.copy()
                        # Disable network
                        env.pop("HTTP_PROXY", None)
                        res = subprocess.run([sys.executable, temp_snippet_path], env=env, capture_output=True, text=True, timeout=10)
                        if res.returncode != 0:
                            os.remove(temp_snippet_path)
                            return {"status": "FAIL", "reason": f"Snippet execution failed: {res.stderr}"}
                    finally:
                        if os.path.exists(temp_snippet_path):
                            os.remove(temp_snippet_path)
                            
                # Check for links
                links = re.findall(r'\[([^\]]+)\]\(([^\)]+)\)', content)
                for label, url in links:
                    if url.startswith("http") or url.startswith("www"):
                        pass # Valid link
                    elif not (target_dir / url).exists():
                        return {"status": "FAIL", "reason": f"Broken link in doc: {url}"}
                        
                # Check for mermaid
                mermaid = re.findall(r'```mermaid\n(.*?)```', content, re.DOTALL)
                if "mermaid sources" in reqs and not mermaid:
                    return {"status": "FAIL", "reason": "Missing mermaid sources"}

        if "regressions" in task_def:
            for reg in task_def["regressions"]:
                if not reg.get("found"):
                    return {"status": "FAIL", "reason": f"Missing requested regression evidence: {reg}"}
                    
        return {"status": "PASS", "reason": "Documentation valid"}


class PortalProfile(ProfileExtensionInterface):
    def validate(self, task_def: Dict[str, Any], target_dir: Path) -> Dict[str, Any]:
        if not (target_dir / "package-lock.json").exists() and not (target_dir / "yarn.lock").exists():
            return {"status": "BLOCKED", "reason": "Missing lockfile"}
            
        if not (target_dir / "route-manifest.ts").exists() and task_def.get("require_manifest", False):
            return {"status": "FAIL", "reason": "Missing route-manifest contract"}
            
        env = os.environ.copy()
        env["npm_config_offline"] = "true"
        
        # Execute lint/build if required
        if task_def.get("require_lint", False):
            try:
                res = subprocess.run(["npm", "run", "lint"], cwd=target_dir, env=env, capture_output=True, text=True, timeout=60)
                if res.returncode != 0:
                    return {"status": "FAIL", "reason": f"Lint failed: {res.stderr}"}
            except Exception as e:
                return {"status": "FAIL", "reason": f"Lint execution failed: {e}"}
                
        if task_def.get("require_build", False):
            try:
                res = subprocess.run(["npm", "run", "build"], cwd=target_dir, env=env, capture_output=True, text=True, timeout=60)
                if res.returncode != 0:
                    return {"status": "FAIL", "reason": f"Build failed: {res.stderr}"}
            except Exception as e:
                return {"status": "FAIL", "reason": f"Build execution failed: {e}"}
        
        if "regressions" in task_def:
            for reg in task_def["regressions"]:
                if not reg.get("found"):
                    return {"status": "FAIL", "reason": f"Missing requested regression evidence: {reg}"}
                    
        return {"status": "PASS", "reason": "Portal valid"}


PROFILES = {
    "java": JavaProfile(),
    "python": PythonProfile(),
    "documentation": DocumentationProfile(),
    "portal": PortalProfile()
}


def validate_path_safety(p: str, base_dir: Path = None, allow_absolute_for_testing: bool = False) -> Path:
    if not p:
        raise ValueError("Empty path provided")
        
    path = Path(p)
    if os.path.isabs(p) and not allow_absolute_for_testing:
        raise ValueError(f"Absolute path not allowed: {p}")
    
    if ".." in path.parts:
        raise ValueError(f"Directory traversal not allowed: {p}")
        
    current = base_dir if base_dir else Path()
    if allow_absolute_for_testing and os.path.isabs(p):
        current = Path(path.anchor)
        parts = path.parts[1:]
    else:
        parts = path.parts

    for part in parts:
        current = current / part
        if current.is_symlink():
            raise ValueError(f"Symlinks not allowed: {current}")
            
    return path


def parse_evidence(evidence_path: str) -> Dict[str, Any]:
    path = validate_path_safety(evidence_path, allow_absolute_for_testing=True)
    if not path.exists():
        raise ValueError(f"Evidence file not found: {evidence_path}")
    with open(path, 'r') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            raise ValueError("Malformed evidence: invalid JSON")
            
    if not isinstance(data, dict):
        raise ValueError("Malformed evidence: must be a JSON object")
    if "status" not in data or data["status"] not in ["PASS", "FAIL", "BLOCKED"]:
        raise ValueError("Malformed evidence: missing or invalid status")
        
    return data


def validate_task_definition(task_def: Dict[str, Any], target_dir: Path) -> Dict[str, Any]:
    tests = task_def.get("tests", [])
    if not tests:
        return {"status": "BLOCKED", "reason": "Empty tests are not allowed"}
        
    mappings = task_def.get("case_mappings", {})
    if not mappings:
        return {"status": "BLOCKED", "reason": "Missing explicit test/version/case mappings"}
        
    allowed_components = task_def.get("allowed_components", [])
    if not allowed_components:
        return {"status": "BLOCKED", "reason": "Missing component-aware whitelists"}
        
    required_files = task_def.get("required_artifacts", [])
    if not required_files:
        return {"status": "BLOCKED", "reason": "Missing artifact requirements"}
        
    for req_file in required_files:
        try:
            validate_path_safety(req_file, base_dir=target_dir) 
            req_path = target_dir / req_file
        except ValueError as e:
            return {"status": "BLOCKED", "reason": str(e)}
            
        in_whitelist = False
        for comp in allowed_components:
            try:
                validate_path_safety(comp, base_dir=target_dir)
                req_path.relative_to(target_dir / comp)
                in_whitelist = True
                break
            except ValueError:
                pass
                
        if not in_whitelist:
            return {"status": "BLOCKED", "reason": f"Artifact {req_file} not in whitelisted components"}
            
        if not req_path.exists() or not req_path.is_file():
            return {"status": "BLOCKED", "reason": f"Missing required artifact: {req_file}"}

    profile_name = task_def.get("profile")
    if not profile_name:
        return {"status": "BLOCKED", "reason": "Unknown profile"}
        
    if "validation_command" in task_def:
        command = task_def["validation_command"]
        # Never shell-evaluate validation_command strings
        if "|" in command or ">" in command or "&" in command or ";" in command:
            return {"status": "BLOCKED", "reason": "Shell metadata refusal in validation_command"}

    profile = PROFILES.get(profile_name)
    if not profile:
        return {"status": "BLOCKED", "reason": f"Unimplemented profile: {profile_name}"}
        
    return profile.validate(task_def, target_dir)


def process_checker(catalog_path_str, task_id, target_dir_str):
    try:
        cat_path = validate_path_safety(catalog_path_str, allow_absolute_for_testing=True)
        tgt_dir = validate_path_safety(target_dir_str, allow_absolute_for_testing=True)
        
        if not cat_path.exists():
            return {"status": "BLOCKED", "reason": f"Catalog not found: {catalog_path_str}"}
        if not tgt_dir.is_dir():
            return {"status": "BLOCKED", "reason": f"Target is not a directory: {target_dir_str}"}
            
        with open(cat_path, "r") as f:
            try:
                catalog = json.load(f)
            except json.JSONDecodeError:
                return {"status": "BLOCKED", "reason": "Malformed catalog payload"}
                
        tasks = catalog.get("tasks", {})
        if task_id not in tasks:
            return {"status": "BLOCKED", "reason": f"Unknown task: {task_id}"}
            
        task_def = tasks[task_id]
        return validate_task_definition(task_def, tgt_dir)
        
    except ValueError as e:
        return {"status": "BLOCKED", "reason": str(e)}
    except Exception as e:
        return {"status": "BLOCKED", "reason": f"Unexpected error: {str(e)}"}


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
        
    if "--self-test" in argv:
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        if repo_root not in sys.path:
            sys.path.insert(0, repo_root)
            
        test_module = "scripts.tests.test_curriculum_check_contract"
        suite = unittest.defaultTestLoader.loadTestsFromName(test_module)
        
        test_count = suite.countTestCases()
        
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        if test_count < 15:
            print(f"Self-test failed: Only {test_count} tests discovered. Require >= 15.", file=sys.stderr)
            sys.exit(1)
            
        if not result.wasSuccessful() or result.skipped:
            sys.exit(1)
            
        sys.exit(0)
        
    parser = argparse.ArgumentParser(description="Fail-closed curriculum task checker")
    parser.add_argument("--catalog", type=str, help="Path to catalog file")
    parser.add_argument("--task", type=str, help="Task ID")
    parser.add_argument("--target", type=str, help="Target directory")
    parser.add_argument("--evidence", type=str, help="Evidence output path")
    parser.add_argument("--verify-evidence", type=str, help="Verify an existing evidence file")
    
    args, unknown = parser.parse_known_args(argv)
    if unknown:
        print(f"Unknown arguments rejected: {unknown}", file=sys.stderr)
        sys.exit(1)
        
    if args.verify_evidence:
        try:
            ev = parse_evidence(args.verify_evidence)
            print(json.dumps(ev))
            sys.exit(0 if ev["status"] == "PASS" else 1)
        except Exception as e:
            print(f"Evidence verification failed: {e}", file=sys.stderr)
            sys.exit(1)
            
    if not args.catalog or not args.task or not args.target or not args.evidence:
        print("Missing required arguments", file=sys.stderr)
        sys.exit(1)
            
    evidence_record = {
        "status": "BLOCKED",
        "task": args.task,
        "reason": "Unknown error"
    }
    
    result = process_checker(args.catalog, args.task, args.target)
    evidence_record.update(result)
    
    try:
        ev_path = validate_path_safety(args.evidence, allow_absolute_for_testing=True)
        ev_path.parent.mkdir(parents=True, exist_ok=True)
        with open(ev_path, "w") as f:
            json.dump(evidence_record, f, indent=2)
    except Exception as e:
        print(f"Failed to write evidence: {e}", file=sys.stderr)
        sys.exit(1)
        
    sys.exit(1 if evidence_record["status"] != "PASS" else 0)

if __name__ == "__main__":
    main()
