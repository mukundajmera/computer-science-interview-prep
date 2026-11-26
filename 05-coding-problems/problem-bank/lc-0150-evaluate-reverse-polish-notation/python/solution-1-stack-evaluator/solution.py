from typing import List


class Solution:
    def evalRPN(self, tokens: List[str]) -> int:
        stack: List[int] = []
        for token in tokens:
            if token in {'+', '-', '*', '/'}:
                right = stack.pop()
                left = stack.pop()
                stack.append(self._apply(left, right, token))
            else:
                stack.append(int(token))
        return stack[-1]

    def _apply(self, left: int, right: int, operator: str) -> int:
        if operator == '+':
            return left + right
        if operator == '-':
            return left - right
        if operator == '*':
            return left * right
        quotient = abs(left) // abs(right)
        return -quotient if (left < 0) ^ (right < 0) else quotient
