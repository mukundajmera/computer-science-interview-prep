import os
import subprocess
import sys

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    success = True
    
    # Python tests
    for item in os.listdir(root_dir):
        pattern_dir = os.path.join(root_dir, item)
        if os.path.isdir(pattern_dir) and not item.startswith('.') and item not in ['problem-bank', 'collections']:
            py_dir = os.path.join(pattern_dir, 'python')
            if os.path.isdir(py_dir):
                print(f"Running Python tests in {py_dir}...")
                result = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', py_dir, '-p', 'test_*.py'])
                if result.returncode != 0 and result.returncode != 5:
                    success = False
            
            java_dir = os.path.join(pattern_dir, 'java')
            if os.path.isdir(java_dir):
                print(f"Running Java tests in {java_dir}...")
                compile_res = subprocess.run(['javac', 'Solutions.java', 'SolutionsTest.java'], cwd=java_dir)
                if compile_res.returncode == 0:
                    run_res = subprocess.run(['java', '-ea', 'SolutionsTest'], cwd=java_dir)
                    if run_res.returncode != 0:
                        success = False
                else:
                    success = False
                    
    if not success:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == '__main__':
    main()
