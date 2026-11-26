from collections import Counter, defaultdict
from typing import List


class Solution:
    def findSubstring(self, s: str, words: List[str]) -> List[int]:
        if not words:
            return []
        word_length = len(words[0])
        total_words = len(words)
        required = Counter(words)
        result: List[int] = []
        for offset in range(word_length):
            window = defaultdict(int)
            left = offset
            used = 0
            for right in range(offset, len(s) - word_length + 1, word_length):
                word = s[right:right + word_length]
                if word not in required:
                    window.clear()
                    used = 0
                    left = right + word_length
                    continue
                window[word] += 1
                used += 1
                while window[word] > required[word]:
                    removed = s[left:left + word_length]
                    window[removed] -= 1
                    used -= 1
                    left += word_length
                if used == total_words:
                    result.append(left)
                    removed = s[left:left + word_length]
                    window[removed] -= 1
                    used -= 1
                    left += word_length
        return sorted(result)
