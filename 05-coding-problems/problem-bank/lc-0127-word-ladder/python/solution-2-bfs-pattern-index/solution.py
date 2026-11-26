from __future__ import annotations

from collections import defaultdict, deque


class Solution:
    def ladderLength(self, beginWord: str, endWord: str, wordList: list[str]) -> int:
        if endWord not in set(wordList):
            return 0

        by_pattern: dict[str, list[str]] = defaultdict(list)
        for word in wordList:
            for pattern in self._patterns(word):
                by_pattern[pattern].append(word)

        queue = deque([beginWord])
        visited = {beginWord}
        distance = 1
        while queue:
            for _ in range(len(queue)):
                word = queue.popleft()
                if word == endWord:
                    return distance
                for pattern in self._patterns(word):
                    neighbors = by_pattern[pattern]
                    for neighbor in neighbors:
                        if neighbor not in visited:
                            visited.add(neighbor)
                            queue.append(neighbor)
                    neighbors.clear()
            distance += 1
        return 0

    def _patterns(self, word: str) -> list[str]:
        return [word[:i] + "*" + word[i + 1 :] for i in range(len(word))]
