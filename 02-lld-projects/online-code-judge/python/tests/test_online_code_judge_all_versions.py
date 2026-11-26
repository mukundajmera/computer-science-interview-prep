import unittest
import time
import sys
import os

class TestOnlineCodeJudge(unittest.TestCase):
    def test_terminal_verdict_does_not_change_v2(self):
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../v2-extended')))
        
        online_code_judge = __import__('judge')
        
        judge = online_code_judge.CodeJudge()
        tc = online_code_judge.TestCase("in", "out")
        problem = online_code_judge.Problem("p1", [tc], 1000, 100000)
        judge.add_problem(problem)

        submission = online_code_judge.Submission("s1", "u1", "p1", "PYTHON", "TLE")
        judge.submit(submission)
        
        self.assertEqual(submission.verdict, online_code_judge.Verdict.TLE)
        
        updated = submission.update_verdict(online_code_judge.Verdict.AC)
        self.assertFalse(updated)
        self.assertEqual(submission.verdict, online_code_judge.Verdict.TLE)
        
        sys.path.pop(0)

    def test_terminal_verdict_does_not_change_v3(self):
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../v3-optimized')))
        
        online_code_judge = __import__('online_code_judge')
        
        judge = online_code_judge.OnlineCodeJudge(2)
        tc = online_code_judge.TestCase("in", "out")
        problem = online_code_judge.Problem("p1", [tc], 1000, 100000)
        judge.add_problem(problem)

        submission = online_code_judge.Submission("s1", "u1", "p1", "PYTHON", "TLE")
        judge.submit(submission)
        
        time.sleep(0.5)
        
        self.assertEqual(submission.get_verdict(), online_code_judge.Verdict.TLE)
        
        updated = submission.update_verdict(online_code_judge.Verdict.AC)
        self.assertFalse(updated)
        self.assertEqual(submission.get_verdict(), online_code_judge.Verdict.TLE)
        
        judge.stop()
        
        sys.path.pop(0)

if __name__ == '__main__':
    unittest.main()
