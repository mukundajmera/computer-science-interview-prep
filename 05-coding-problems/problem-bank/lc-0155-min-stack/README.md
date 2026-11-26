# Min Stack

## Clean-Room Summary

Build a last-in-first-out container that can report the smallest active value without scanning the stored elements.

## Driver Signature

```java
class MinStack {
    public MinStack() {}
    public void push(int val) {}
    public void pop() {}
    public int top() { return 0; }
    public int getMin() { return 0; }
}
```

```python
class MinStack:
    def __init__(self) -> None:
        pass
    def push(self, val: int) -> None:
        pass
    def pop(self) -> None:
        pass
    def top(self) -> int:
        return 0
    def getMin(self) -> int:
        return 0
```

## Repo-Authored Examples

| Operations | Results |
| --- | --- |
| `MinStack(), push(5), push(2), push(7), getMin(), pop(), top(), getMin()` | `null, null, null, null, 2, null, 2, 2` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Value stack plus minimum stack | `O(1)` per operation. Each operation does a constant number of stack reads/writes. | `O(n)`. The value stack stores all values and the minimum stack stores every active minimum occurrence. |
| 2 | Encoded minimum in one stack | `O(1)` per operation. Encoded markers restore the previous minimum with constant arithmetic. | `O(n)`. One stack stores either raw values or encoded minimum markers. |

## Pitfalls

- Duplicate minimum values must be tracked separately; one pop should not remove every equal minimum.
- `top()` must decode marker values when the stored top represents a new minimum.
- The encoded tier should use a wider numeric type to avoid overflow when computing marker values.
