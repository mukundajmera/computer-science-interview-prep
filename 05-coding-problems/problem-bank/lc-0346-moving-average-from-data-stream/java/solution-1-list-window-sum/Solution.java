import java.util.ArrayList;
import java.util.List;

class MovingAverage {
    private final int size;
    private final List<Integer> values = new ArrayList<>();
    public MovingAverage(int size) { this.size = size; }
    public double next(int val) {
        values.add(val);
        int start = Math.max(0, values.size() - size);
        int sum = 0;
        for (int i = start; i < values.size(); i++) sum += values.get(i);
        return (double) sum / (values.size() - start);
    }
}
