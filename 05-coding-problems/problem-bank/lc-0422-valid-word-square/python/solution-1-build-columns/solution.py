from typing import List


class Solution:
    def validWordSquare(self, words: List[str]) -> bool:
        if max((len(word) for word in words), default=0) != len(words):
            return False
        for col in range(len(words)):
            column = ''.join(word[col] for word in words if col < len(word))
            if column != words[col]:
                return False
        return True
