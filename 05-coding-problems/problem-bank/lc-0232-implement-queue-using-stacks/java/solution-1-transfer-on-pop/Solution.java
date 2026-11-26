import java.util.ArrayDeque;
import java.util.Deque;

class MyQueue {
    private final Deque<Integer> input = new ArrayDeque<>();
    private final Deque<Integer> output = new ArrayDeque<>();

    public void push(int x) {
        input.push(x);
    }

    public int pop() {
        moveIfNeeded();
        return output.pop();
    }

    public int peek() {
        moveIfNeeded();
        return output.peek();
    }

    public boolean empty() {
        return input.isEmpty() && output.isEmpty();
    }

    private void moveIfNeeded() {
        if (!output.isEmpty()) {
            return;
        }
        while (!input.isEmpty()) {
            output.push(input.pop());
        }
    }
}
