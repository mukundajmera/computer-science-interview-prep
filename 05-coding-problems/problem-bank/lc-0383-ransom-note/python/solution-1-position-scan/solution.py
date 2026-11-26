class Solution:
    def canConstruct(self, ransomNote: str, magazine: str) -> bool:
        used = [False] * len(magazine)
        for needed in ransomNote:
            matched = False
            for index, available in enumerate(magazine):
                if not used[index] and available == needed:
                    used[index] = True
                    matched = True
                    break
            if not matched:
                return False
        return True
