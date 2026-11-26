import unittest
from solutions import Solutions

class TestSolutions(unittest.TestCase):
    def setUp(self):
        self.sol = Solutions()

    def test_isValid(self):
        self.assertTrue(self.sol.isValid("()"))
        self.assertTrue(self.sol.isValid("()[]{}"))
        self.assertFalse(self.sol.isValid("(]"))

    def test_minStack(self):
        minStack = self.sol.MinStack()
        minStack.push(-2)
        minStack.push(0)
        minStack.push(-3)
        self.assertEqual(minStack.getMin(), -3)
        minStack.pop()
        self.assertEqual(minStack.top(), 0)
        self.assertEqual(minStack.getMin(), -2)

    def test_evalRPN(self):
        self.assertEqual(self.sol.evalRPN(["2","1","+","3","*"]), 9)
        self.assertEqual(self.sol.evalRPN(["4","13","5","/","+"]), 6)

    def test_generateParenthesis(self):
        self.assertEqual(self.sol.generateParenthesis(3), ["((()))","(()())","(())()","()(())","()()()"])

    def test_dailyTemperatures(self):
        self.assertEqual(self.sol.dailyTemperatures([73,74,75,71,69,72,76,73]), [1,1,4,2,1,1,0,0])

    def test_carFleet(self):
        self.assertEqual(self.sol.carFleet(12, [10,8,0,5,3], [2,4,1,1,3]), 3)

    def test_largestRectangleArea(self):
        self.assertEqual(self.sol.largestRectangleArea([2,1,5,6,2,3]), 10)
        self.assertEqual(self.sol.largestRectangleArea([2,4]), 4)

if __name__ == '__main__':
    unittest.main()
