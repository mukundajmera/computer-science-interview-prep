import os
import sys
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
import subprocess
import glob

def main():
    list_missing = '--list-missing' in sys.argv
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    packs = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d)) and d not in ('tools', 'diagrams', 'images', '__pycache__') and not d.startswith('.')]
    packs.sort()
    
    missing_packs = []
    results = []
    
    for p in packs:
        pack_dir = os.path.join(base_dir, p)
        tests_dir = os.path.join(pack_dir, 'python', 'tests')
        
        has_tests = False
        if os.path.isdir(tests_dir):
            test_files = glob.glob(os.path.join(tests_dir, 'test_*.py'))
            if test_files:
                has_tests = True
        
        if not has_tests:
            missing_packs.append(p)
            continue
            
        if not list_missing:
            # Run tests
            res = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'python/tests'], cwd=pack_dir, capture_output=True)
            rc = res.returncode
            if rc == 5:
                rc = 0 # NO TESTS RAN is considered non-failure per memory
            results.append((p, rc))
    
    if list_missing:
        for p in missing_packs:
            print(p)
        sys.exit(0)
    
    # Table output
    print(f"| {'Pack':<35} | {'Status':<10} |")
    print(f"|{'-'*37}|{'-'*12}|")
    all_passed = True
    for p, rc in results:
        status = 'PASS' if rc == 0 else 'FAIL'
        if rc != 0:
            all_passed = False
        print(f"| {p:<35} | {status:<10} |")
    for p in missing_packs:
        print(f"| {p:<35} | {'MISSING':<10} |")
        
    if not all_passed:
        sys.exit(1)

if __name__ == '__main__':
    main()
