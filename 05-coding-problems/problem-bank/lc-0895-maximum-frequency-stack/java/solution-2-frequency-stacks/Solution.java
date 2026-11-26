import java.util.ArrayDeque;
import java.util.Deque;
import java.util.HashMap;
import java.util.Map;

class FreqStack {
    private final Map<Integer, Integer> frequency = new HashMap<>();
    private final Map<Integer, Deque<Integer>> byFrequency = new HashMap<>();
    private int maxFrequency = 0;

    public void push(int val) {
        int next = frequency.getOrDefault(val, 0) + 1;
        frequency.put(val, next);
        maxFrequency = Math.max(maxFrequency, next);
        byFrequency.computeIfAbsent(next, ignored -> new ArrayDeque<>()).push(val);
    }

    public int pop() {
        Deque<Integer> stack = byFrequency.get(maxFrequency);
        int value = stack.pop();
        frequency.put(value, frequency.get(value) - 1);
        if (stack.isEmpty()) {
            byFrequency.remove(maxFrequency);
            maxFrequency--;
        }
        return value;
    }
}
