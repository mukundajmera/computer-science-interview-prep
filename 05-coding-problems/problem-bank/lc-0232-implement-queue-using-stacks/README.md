# Implement Queue using Stacks

## Clean-Room Summary

Implement FIFO queue operations using stack primitives while preserving queue order across pushes, peeks, pops, and empty checks.

## Driver Signature

```java
class MyQueue {
    public MyQueue() {}
    public void push(int x) {}
    public int pop() { return 0; }
    public int peek() { return 0; }
    public boolean empty() { return true; }
}
```

```python
class MyQueue:
    def __init__(self) -> None: ...
    def push(self, x: int) -> None: ...
    def pop(self) -> int: ...
    def peek(self) -> int: ...
    def empty(self) -> bool: ...
```

## Repo-Authored Cases

- `basic fifo order`
- `interleaved pushes and pops`

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Two stacks with lazy transfer | `O(1) amortized per operation`. Each value moves from input to output at most once before being popped. | `O(n)`. Both stacks together store all queued values. |
| 2 | Costly push with front stack | `O(n) push, O(1) pop/peek/empty`. A push may move every queued item twice; reads and removals are direct. | `O(n)`. The queue contents live in one stack, with temporary movement during push. |

## Pitfalls

- Do not reverse the queue order on every pop if a transferred output stack is already available.
- Peek must not remove the element.
- The queue is considered empty only when both backing stacks are empty.
