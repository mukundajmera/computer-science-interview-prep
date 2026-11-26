class Solution:
    def confusingNumber(self, n: int) -> bool:
        mapping = {'0': '0', '1': '1', '6': '9', '8': '8', '9': '6'}
        value = str(n)
        rotated = []
        for digit in reversed(value):
            if digit not in mapping:
                return False
            rotated.append(mapping[digit])
        return ''.join(rotated) != value
