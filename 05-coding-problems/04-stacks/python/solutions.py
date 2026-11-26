class Solutions:
    # 1. Valid Parentheses
    def isValid(self, s: str) -> bool:
        stack = []
        mapping = {')': '(', '}': '{', ']': '['}
        for char in s:
            if char in mapping:
                top = stack.pop() if stack else '#'
                if mapping[char] != top:
                    return False
            else:
                stack.append(char)
        return not stack

    # 2. Min Stack
    class MinStack:
        def __init__(self):
            self.stack = []
            self.min_stack = []

        def push(self, val: int) -> None:
            self.stack.append(val)
            if not self.min_stack or val <= self.min_stack[-1]:
                self.min_stack.append(val)

        def pop(self) -> None:
            if self.stack:
                if self.stack[-1] == self.min_stack[-1]:
                    self.min_stack.pop()
                self.stack.pop()

        def top(self) -> int:
            return self.stack[-1] if self.stack else 0

        def getMin(self) -> int:
            return self.min_stack[-1] if self.min_stack else 0

    # 3. Evaluate Reverse Polish Notation
    def evalRPN(self, tokens: list[str]) -> int:
        stack = []
        for token in tokens:
            if token in "+-*/":
                b, a = stack.pop(), stack.pop()
                if token == "+":
                    stack.append(a + b)
                elif token == "-":
                    stack.append(a - b)
                elif token == "*":
                    stack.append(a * b)
                else:
                    stack.append(int(a / b))
            else:
                stack.append(int(token))
        return stack[0]

    # 4. Generate Parentheses
    def generateParenthesis(self, n: int) -> list[str]:
        res = []
        def backtrack(S, left, right):
            if len(S) == 2 * n:
                res.append("".join(S))
                return
            if left < n:
                S.append("(")
                backtrack(S, left + 1, right)
                S.pop()
            if right < left:
                S.append(")")
                backtrack(S, left, right + 1)
                S.pop()
        backtrack([], 0, 0)
        return res

    # 5. Daily Temperatures
    def dailyTemperatures(self, temperatures: list[int]) -> list[int]:
        res = [0] * len(temperatures)
        stack = []
        for i, t in enumerate(temperatures):
            while stack and temperatures[stack[-1]] < t:
                idx = stack.pop()
                res[idx] = i - idx
            stack.append(i)
        return res

    # 6. Car Fleet
    def carFleet(self, target: int, position: list[int], speed: list[int]) -> int:
        cars = sorted(zip(position, speed))
        stack = []
        for p, s in cars[::-1]:
            time = (target - p) / s
            if not stack or time > stack[-1]:
                stack.append(time)
        return len(stack)

    # 7. Largest Rectangle in Histogram
    def largestRectangleArea(self, heights: list[int]) -> int:
        stack = []
        max_area = 0
        for i, h in enumerate(heights):
            start = i
            while stack and stack[-1][1] > h:
                idx, height = stack.pop()
                max_area = max(max_area, height * (i - idx))
                start = idx
            stack.append((start, h))
        for i, h in stack:
            max_area = max(max_area, h * (len(heights) - i))
        return max_area
