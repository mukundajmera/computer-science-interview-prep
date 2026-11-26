from typing import Dict, List, Set


class Solution:
    def wordBreak(self, s: str, wordDict: List[str]) -> List[str]:
        words: Set[str] = set(wordDict)
        memo: Dict[int, List[str]] = {}

        def dfs(start: int) -> List[str]:
            if start in memo:
                return memo[start]
            if start == len(s):
                return [""]

            res: List[str] = []
            for end in range(start + 1, len(s) + 1):
                prefix = s[start:end]
                if prefix in words:
                    sub_sentences = dfs(end)
                    for sub in sub_sentences:
                        if sub:
                            res.append(f"{prefix} {sub}")
                        else:
                            res.append(prefix)

            memo[start] = res
            return res

        return dfs(0)
