import java.util.ArrayDeque;
import java.util.Queue;

class HitCounter {
    private final Queue<Integer> hits = new ArrayDeque<>();

    public void hit(int timestamp) {
        hits.add(timestamp);
    }

    public int getHits(int timestamp) {
        while (!hits.isEmpty() && hits.peek() <= timestamp - 300) {
            hits.remove();
        }
        return hits.size();
    }
}
