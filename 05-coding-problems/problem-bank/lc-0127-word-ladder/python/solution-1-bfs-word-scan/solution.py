from __future__ import annotations

from collections import deque


class Solution:
    def ladderLength(self, beginWord: str, endWord: str, wordList: list[str]) -> int:
        unvisited = set(wordList)
        if endWord not in unvisited:
            return 0

        queue = deque([beginWord])
        distance = 1
        while queue:
            for _ in range(len(queue)):
                word = queue.popleft()
                if word == endWord:
                    return distance
                for candidate in list(unvisited):
                    if self._differs_by_one(word, candidate):
                        unvisited.remove(candidate)
                        queue.append(candidate)
            distance += 1
        return 0

    def _differs_by_one(self, a: str, b: str) -> bool:
        return sum(left != right for left, right in zip(a, b)) == 1
