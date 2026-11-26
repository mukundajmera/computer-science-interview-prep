from typing import List


class Solution:
    def asteroidCollision(self, asteroids: List[int]) -> List[int]:
        current = asteroids[:]
        changed = True
        while changed:
            changed = False
            next_state: List[int] = []
            index = 0
            while index < len(current):
                if index + 1 < len(current) and current[index] > 0 and current[index + 1] < 0:
                    changed = True
                    left = current[index]
                    right = current[index + 1]
                    if abs(left) > abs(right):
                        next_state.append(left)
                    elif abs(left) < abs(right):
                        next_state.append(right)
                    index += 2
                else:
                    next_state.append(current[index])
                    index += 1
            current = next_state
        return current
