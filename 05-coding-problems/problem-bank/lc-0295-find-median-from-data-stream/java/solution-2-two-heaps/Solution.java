import java.util.Collections;
import java.util.PriorityQueue;

class MedianFinder {
    private final PriorityQueue<Integer> lower = new PriorityQueue<>(Collections.reverseOrder());
    private final PriorityQueue<Integer> upper = new PriorityQueue<>();

    public void addNum(int num) {
        if (lower.isEmpty() || num <= lower.peek()) {
            lower.add(num);
        } else {
            upper.add(num);
        }
        rebalance();
    }

    public double findMedian() {
        if (lower.size() > upper.size()) {
            return lower.peek();
        }
        return ((long) lower.peek() + upper.peek()) / 2.0;
    }

    private void rebalance() {
        if (lower.size() > upper.size() + 1) {
            upper.add(lower.remove());
        } else if (upper.size() > lower.size()) {
            lower.add(upper.remove());
        }
    }
}
