
import sys
import os
import time
import importlib.util

def load_module(version_dir, module_name):
    target = "online_code_judge" if version_dir == "v3-optimized" and module_name == "judge" else module_name
    path = os.path.join(os.path.dirname(__file__), "..", version_dir, f"{target}.py")
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    if hasattr(module, "OnlineCodeJudge") and not hasattr(module, "CodeJudge"):
        module.CodeJudge = module.OnlineCodeJudge
    return module

def run_tests(version_dir):
    module = load_module(version_dir, "judge")
    
    # Test AC
    judge = module.CodeJudge()
    p1 = module.Problem("p1", [module.TestCase("1 2", "1 2")], 1000, 256000)
    judge.add_problem(p1)
    s1 = module.Submission("s1", "u1", "p1", "PYTHON", "print('1 2')")
    judge.submit(s1)
    
    if version_dir == "v3-optimized":
        time.sleep(0.5)
        
    assert judge.get_verdict("s1") == module.Verdict.AC

    # Test WA
    s2 = module.Submission("s2", "u1", "p1", "PYTHON", "WA")
    judge.submit(s2)
    if version_dir == "v3-optimized":
        time.sleep(0.5)
    assert judge.get_verdict("s2") == module.Verdict.WA

    # Test TLE
    s3 = module.Submission("s3", "u1", "p1", "PYTHON", "TLE")
    judge.submit(s3)
    if version_dir == "v3-optimized":
        time.sleep(0.5)
    assert judge.get_verdict("s3") == module.Verdict.TLE
    
    # Test MLE
    s4 = module.Submission("s4", "u1", "p1", "PYTHON", "MLE")
    judge.submit(s4)
    if version_dir == "v3-optimized":
        time.sleep(0.5)
    assert judge.get_verdict("s4") == module.Verdict.MLE

    # Test RE
    s5 = module.Submission("s5", "u1", "p1", "PYTHON", "RE")
    judge.submit(s5)
    if version_dir == "v3-optimized":
        time.sleep(0.5)
    assert judge.get_verdict("s5") == module.Verdict.RE
    
    if version_dir == "v3-optimized":
        judge.stop()
        
    del sys.modules["judge"]

def test_v1_basic():
    run_tests("v1-basic")

def test_v2_extended():
    run_tests("v2-extended")

def test_v3_optimized():
    run_tests("v3-optimized")
    
def test_ce_verdict():
    # Test compilation error (no problem exists)
    module = load_module("v2-extended", "judge")
    judge = module.CodeJudge()
    s = module.Submission("s_ce", "u", "missing_problem", "PYTHON", "print('hi')")
    judge.submit(s)
    assert judge.get_verdict("s_ce") == module.Verdict.CE
    del sys.modules["judge"]

def test_missing_submission():
    # Test querying non-existent submission
    module = load_module("v1-basic", "judge")
    judge = module.CodeJudge()
    assert judge.get_verdict("none") is None
    del sys.modules["judge"]
