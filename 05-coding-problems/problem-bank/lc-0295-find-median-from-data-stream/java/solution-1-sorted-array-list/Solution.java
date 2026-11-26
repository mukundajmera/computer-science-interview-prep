import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

class MedianFinder {
    private final List<Integer> values = new ArrayList<>();

    public void addNum(int num) {
        int index = Collections.binarySearch(values, num);
        if (index < 0) {
            index = -index - 1;
        }
        values.add(index, num);
    }

    public double findMedian() {
        int size = values.size();
        int middle = size / 2;
        if (size % 2 == 1) {
            return values.get(middle);
        }
        return ((long) values.get(middle - 1) + values.get(middle)) / 2.0;
    }
}
