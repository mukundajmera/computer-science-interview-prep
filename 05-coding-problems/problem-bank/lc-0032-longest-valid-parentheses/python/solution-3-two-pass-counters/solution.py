class Solution:
    def longestValidParentheses(self, s: str) -> int:
        def scan(indexes: range, reset_on_more_closes: bool) -> int:
            opens = closes = best = 0
            for index in indexes:
                if s[index] == "(":
                    opens += 1
                else:
                    closes += 1
                if opens == closes:
                    best = max(best, 2 * min(opens, closes))
                elif (reset_on_more_closes and closes > opens) or (not reset_on_more_closes and opens > closes):
                    opens = closes = 0
            return best

        return max(scan(range(len(s)), True), scan(range(len(s) - 1, -1, -1), False))
