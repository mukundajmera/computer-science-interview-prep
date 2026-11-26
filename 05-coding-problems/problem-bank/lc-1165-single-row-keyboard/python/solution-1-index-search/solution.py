class Solution:
    def calculateTime(self, keyboard: str, word: str) -> int:
        position = 0
        total = 0
        for char in word:
            nxt = keyboard.index(char)
            total += abs(nxt - position)
            position = nxt
        return total
