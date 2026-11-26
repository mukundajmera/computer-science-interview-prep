class Solution:
    def wordPattern(self, pattern: str, s: str) -> bool:
        words = s.split(" ")
        if len(words) != len(pattern):
            return False
        to_word = {}
        to_char = {}
        for key, word in zip(pattern, words):
            if key in to_word and to_word[key] != word:
                return False
            if word in to_char and to_char[word] != key:
                return False
            to_word[key] = word
            to_char[word] = key
        return True
