class Solution:
    def appendCharacters(self, s: str, t: str) -> int:
        start = 0
        matched = 0
        for char in t:
            found = s.find(char, start)
            if found == -1:
                break
            matched += 1
            start = found + 1
        return len(t) - matched
