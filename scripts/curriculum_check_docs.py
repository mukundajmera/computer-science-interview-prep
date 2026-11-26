import json
import os
import re
import subprocess
import tempfile
import urllib.parse
from pathlib import Path
from typing import Dict, Any, List

from scripts.check_curriculum_task import ProfileExtensionInterface, validate_path_safety

FENCE_RE = re.compile(r"(^|\n)(```|~~~)([a-zA-Z0-9_+-]+)?.*?(\n\2[ \t]*$)", re.MULTILINE | re.DOTALL)
INLINE_LINK_RE = re.compile(r"(!?)\[([^\]\n]+)\]\(([^)\n]+)\)")

class DocsProfile(ProfileExtensionInterface):
    """
    Profile implementation for documentation.
    Validates Markdown files, links, mermaid renderings, fenced code blocks, and source/trace records.
    """
    def __init__(self):
        self.link_cache = set()
        
    def validate(self, task_def: Dict[str, Any], target_dir: Path) -> Dict[str, Any]:
        result = {
            "status": "PASS",
            "metrics": {"checked_files": 0, "checked_links": 0, "rendered_mermaid": 0, "fenced_probes": 0},
            "evidence": []
        }
        
        required_artifacts = task_def.get("required_artifacts", [])
        
        for art in required_artifacts:
            try:
                path = validate_path_safety(art, base_dir=target_dir)
                full_path = target_dir / path
            except ValueError as e:
                return self._fail(f"Invalid path {art}: {e}")
                
            if not full_path.exists():
                return self._fail(f"Missing required artifact: {art}")
                
            result["metrics"]["checked_files"] += 1
            
            if str(full_path).endswith('.md'):
                res = self._validate_markdown(full_path, target_dir)
                if res["status"] != "PASS":
                    return res
                result["metrics"]["checked_links"] += res["metrics"]["checked_links"]
                result["metrics"]["fenced_probes"] += res["metrics"]["fenced_probes"]
                result["evidence"].extend(res.get("evidence", []))
                
                # Check for primary-source/units/worked-trace records
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    content_lower = content.lower()
                    
                has_source = "primary-source" in content_lower
                has_trace = "worked-trace" in content_lower
                has_units = "units" in content_lower
                
                if task_def.get("require_records", False):
                    if not (has_source and has_trace and has_units):
                        return self._fail(f"Missing structured primary-source/units/worked-trace records in {art}")
                
            elif str(full_path).endswith('.mmd'):
                res = self._validate_mermaid(full_path, target_dir)
                if res["status"] != "PASS":
                    return res
                result["metrics"]["rendered_mermaid"] += 1
                result["evidence"].extend(res.get("evidence", []))
        
        return result

    def _fail(self, reason: str) -> Dict[str, Any]:
        return {"status": "FAIL", "reason": reason, "metrics": {}, "evidence": []}
    
    def _validate_markdown(self, path: Path, base_dir: Path) -> Dict[str, Any]:
        metrics = {"checked_links": 0, "fenced_probes": 0}
        evidence = []
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extract and validate local links
        for match in INLINE_LINK_RE.finditer(content):
            url = match.group(3).strip()
            # Basic external check
            if url.startswith(('http://', 'https://', 'mailto:', 'tel:')):
                continue
                
            # Internal link check
            url_no_frag = urllib.parse.urlparse(url).path
            if not url_no_frag:
                continue
                
            metrics["checked_links"] += 1
            try:
                target_path = validate_path_safety(url_no_frag, base_dir=path.parent)
                full_target = path.parent / target_path
                if not full_target.exists():
                    return self._fail(f"Broken local link in {path.name}: {url}")
            except ValueError:
                return self._fail(f"Invalid local link in {path.name}: {url}")
                
        # Opt-in fenced syntax probes
        for match in FENCE_RE.finditer(content):
            lang = match.group(3)
            if not lang:
                continue
            lang = lang.strip().lower()
            if lang in ['python', 'py']:
                code_block = content[match.start():match.end()]
                lines = code_block.split('\n')
                
                inner_lines = []
                in_code = False
                for line in lines:
                    if line.strip().startswith('```') or line.strip().startswith('~~~'):
                        in_code = not in_code
                    elif in_code:
                        inner_lines.append(line)
                        
                snippet = '\n'.join(inner_lines)
                
                if "probe-opt-in" in snippet:
                    metrics["fenced_probes"] += 1
                    # bounded offline subprocess
                    with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w') as temp_f:
                        temp_f.write(snippet)
                        temp_path = temp_f.name
                        
                    try:
                        # Using Python 3.8+ baseline, with timeout
                        subprocess.run(['python3', '-B', temp_path], check=True, timeout=5,
                                     capture_output=True, text=True)
                        evidence.append(f"Probe success: python {path.name}")
                    except subprocess.CalledProcessError as e:
                        os.remove(temp_path)
                        return self._fail(f"Fenced probe failed in {path.name}:\n{e.stderr}")
                    except subprocess.TimeoutExpired:
                        os.remove(temp_path)
                        return self._fail(f"Fenced probe timed out in {path.name}")
                        
                    os.remove(temp_path)
            else:
                code_block = content[match.start():match.end()]
                if "probe-opt-in" in code_block:
                    return self._fail(f"Unsupported fenced-language probe ({lang}) in {path.name}")
                        
        return {"status": "PASS", "metrics": metrics, "evidence": evidence}

    def _validate_mermaid(self, path: Path, base_dir: Path) -> Dict[str, Any]:
        evidence = []
        mmdc_cmd = os.environ.get("MMDC_PATH", "mmdc")
        
        try:
            subprocess.run([mmdc_cmd, '-V'], check=True, capture_output=True, text=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            return self._fail(f"Missing Mermaid CLI (mmdc)")
        
        # Build outputs go to unique /tmp directories, never the source tree
        temp_out = os.path.join("/tmp", f"mmd_out_{os.urandom(4).hex()}.svg")
        try:
            subprocess.run([mmdc_cmd, '-i', str(path), '-o', temp_out], check=True, capture_output=True, text=True)
            evidence.append(f"Rendered {path.name} to {temp_out}")
        except subprocess.CalledProcessError as e:
            return self._fail(f"Mermaid rendering failed for {path.name}: {e.stderr}")
            
        return {"status": "PASS", "evidence": evidence}
