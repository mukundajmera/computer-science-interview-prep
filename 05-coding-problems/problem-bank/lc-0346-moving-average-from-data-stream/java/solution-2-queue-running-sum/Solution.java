import java.util.ArrayDeque;
import java.util.Queue;

class MovingAverage {
    private final int size;
    private final Queue<Integer> window = new ArrayDeque<>();
    private int sum = 0;
    public MovingAverage(int size) { this.size = size; }
    public double next(int val) {
        window.add(val);
        sum += val;
        if (window.size() > size) sum -= window.remove();
        return (double) sum / window.size();
    }
}
