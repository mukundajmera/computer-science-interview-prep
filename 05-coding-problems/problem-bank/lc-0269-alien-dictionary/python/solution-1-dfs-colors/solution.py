from collections import defaultdict
from typing import Dict, List, Set


class Solution:
    def alienOrder(self, words: List[str]) -> str:
        graph: Dict[str, Set[str]] = {char: set() for word in words for char in word}
        for first, second in zip(words, words[1:]):
            limit = min(len(first), len(second))
            index = 0
            while index < limit and first[index] == second[index]:
                index += 1
            if index == limit:
                if len(first) > len(second):
                    return ""
            else:
                graph[first[index]].add(second[index])

        color: Dict[str, int] = defaultdict(int)
        order = []

        def dfs(char: str) -> bool:
            color[char] = 1
            for nxt in sorted(graph[char]):
                if color[nxt] == 1 or (color[nxt] == 0 and dfs(nxt)):
                    return True
            color[char] = 2
            order.append(char)
            return False

        for char in sorted(graph):
            if color[char] == 0 and dfs(char):
                return ""
        return "".join(reversed(order))
