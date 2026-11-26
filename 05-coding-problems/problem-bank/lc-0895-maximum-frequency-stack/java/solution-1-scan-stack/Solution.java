import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

class FreqStack {
    private final List<Integer> stack = new ArrayList<>();
    private final Map<Integer, Integer> frequency = new HashMap<>();

    public void push(int val) {
        stack.add(val);
        frequency.put(val, frequency.getOrDefault(val, 0) + 1);
    }

    public int pop() {
        int bestFrequency = 0;
        for (int count : frequency.values()) {
            bestFrequency = Math.max(bestFrequency, count);
        }
        for (int i = stack.size() - 1; i >= 0; i--) {
            int value = stack.get(i);
            if (frequency.get(value) == bestFrequency) {
                stack.remove(i);
                int next = frequency.get(value) - 1;
                if (next == 0) {
                    frequency.remove(value);
                } else {
                    frequency.put(value, next);
                }
                return value;
            }
        }
        throw new IllegalStateException("empty stack");
    }
}
