import java.util.ArrayDeque;
import java.util.Deque;

class MinStack {
    private final Deque<Long> values = new ArrayDeque<>();
    private long minimum;

    public void push(int val) {
        long value = val;
        if (values.isEmpty()) {
            values.push(value);
            minimum = value;
        } else if (value < minimum) {
            values.push(2 * value - minimum);
            minimum = value;
        } else {
            values.push(value);
        }
    }

    public void pop() {
        long removed = values.pop();
        if (removed < minimum) {
            minimum = 2 * minimum - removed;
        }
    }

    public int top() {
        long value = values.peek();
        if (value < minimum) {
            return (int) minimum;
        }
        return (int) value;
    }

    public int getMin() {
        return (int) minimum;
    }
}
