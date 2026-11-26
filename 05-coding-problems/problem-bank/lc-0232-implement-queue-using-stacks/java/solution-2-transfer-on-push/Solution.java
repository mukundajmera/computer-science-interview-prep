import java.util.ArrayDeque;
import java.util.Deque;

class MyQueue {
    private final Deque<Integer> stack = new ArrayDeque<>();

    public void push(int x) {
        Deque<Integer> temp = new ArrayDeque<>();
        while (!stack.isEmpty()) {
            temp.push(stack.pop());
        }
        stack.push(x);
        while (!temp.isEmpty()) {
            stack.push(temp.pop());
        }
    }

    public int pop() {
        return stack.pop();
    }

    public int peek() {
        return stack.peek();
    }

    public boolean empty() {
        return stack.isEmpty();
    }
}
