class Solution:
    def minDistance(self, word1: str, word2: str) -> int:
        if len(word2) > len(word1):
            word1, word2 = word2, word1
        previous = list(range(len(word2) + 1))
        for i, first_char in enumerate(word1, start=1):
            current = [i] + [0] * len(word2)
            for j, second_char in enumerate(word2, start=1):
                if first_char == second_char:
                    current[j] = previous[j - 1]
                else:
                    current[j] = 1 + min(previous[j - 1], previous[j], current[j - 1])
            previous = current
        return previous[-1]
