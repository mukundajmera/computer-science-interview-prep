from typing import List


class Solution:
    def generateParenthesis(self, n: int) -> List[str]:
        result: List[str] = []
        path: List[str] = []

        def build(open_count: int, close_count: int) -> None:
            if len(path) == 2 * n:
                result.append("".join(path))
                return
            if open_count < n:
                path.append("(")
                build(open_count + 1, close_count)
                path.pop()
            if close_count < open_count:
                path.append(")")
                build(open_count, close_count + 1)
                path.pop()

        build(0, 0)
        return result
