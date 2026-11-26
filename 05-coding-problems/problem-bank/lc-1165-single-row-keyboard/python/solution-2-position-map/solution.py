class Solution:
    def calculateTime(self, keyboard: str, word: str) -> int:
        positions = {char: index for index, char in enumerate(keyboard)}
        current = 0
        total = 0
        for char in word:
            nxt = positions[char]
            total += abs(nxt - current)
            current = nxt
        return total
