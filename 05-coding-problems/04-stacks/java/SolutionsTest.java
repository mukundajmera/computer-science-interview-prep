import java.util.*;

public class SolutionsTest {
    public static void main(String[] args) {
        Solutions sol = new Solutions();

        // 1. Valid Parentheses
        assert sol.isValid("()") == true : "Test 1 Failed";
        assert sol.isValid("()[]{}") == true : "Test 2 Failed";
        assert sol.isValid("(]") == false : "Test 3 Failed";

        // 2. Min Stack
        Solutions.MinStack minStack = new Solutions.MinStack();
        minStack.push(-2);
        minStack.push(0);
        minStack.push(-3);
        assert minStack.getMin() == -3 : "Test 4 Failed";
        minStack.pop();
        assert minStack.top() == 0 : "Test 5 Failed";
        assert minStack.getMin() == -2 : "Test 6 Failed";

        // 3. Evaluate Reverse Polish Notation
        assert sol.evalRPN(new String[]{"2","1","+","3","*"}) == 9 : "Test 7 Failed";
        assert sol.evalRPN(new String[]{"4","13","5","/","+"}) == 6 : "Test 8 Failed";

        // 4. Generate Parentheses
        List<String> expected4 = Arrays.asList("((()))", "(()())", "(())()", "()(())", "()()()");
        assert sol.generateParenthesis(3).equals(expected4) : "Test 9 Failed";

        // 5. Daily Temperatures
        int[] expected5 = {1, 1, 4, 2, 1, 1, 0, 0};
        assert Arrays.equals(sol.dailyTemperatures(new int[]{73, 74, 75, 71, 69, 72, 76, 73}), expected5) : "Test 10 Failed";

        // 6. Car Fleet
        assert sol.carFleet(12, new int[]{10, 8, 0, 5, 3}, new int[]{2, 4, 1, 1, 3}) == 3 : "Test 11 Failed";

        // 7. Largest Rectangle in Histogram
        assert sol.largestRectangleArea(new int[]{2, 1, 5, 6, 2, 3}) == 10 : "Test 12 Failed";
        assert sol.largestRectangleArea(new int[]{2, 4}) == 4 : "Test 13 Failed";
        
        System.out.println("All Java tests passed.");
    }
}
