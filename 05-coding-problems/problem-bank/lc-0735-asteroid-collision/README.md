# Asteroid Collision

## Clean-Room Summary

Simulate one-dimensional asteroid movement and return the survivors after all opposing-direction collisions are resolved.

## Driver Signature

```java
class Solution {
    public int[] asteroidCollision(int[] asteroids) {
        // implement
    }
}
```

```python
class Solution:
    def asteroidCollision(self, asteroids: List[int]) -> List[int]:
        # implement
```

## Repo-Authored Cases

- `small asteroid destroyed`
- `equal asteroids destroy both`
- `chain collision`
- `no opposing collisions`
- `incoming negative survives all`
- `late large negative clears stack`

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Repeated adjacent simulation | `O(n^2)`. A chain of collisions can require repeated passes over the survivor list. | `O(n)`. A working survivor list is rebuilt per pass. |
| 2 | Stack simulation | `O(n)`. Each asteroid is pushed once and popped at most once. | `O(n)`. The survivor stack can hold every asteroid. |

## Pitfalls

- Only a positive asteroid to the left and a negative asteroid to the right can collide.
- Equal magnitudes remove both asteroids and the incoming asteroid should not be pushed.
