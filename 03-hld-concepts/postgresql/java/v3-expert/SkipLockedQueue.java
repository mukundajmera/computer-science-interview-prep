import java.util.LinkedList;
import java.util.Queue;
public class SkipLockedQueue {
    private Queue<Integer> queue = new LinkedList<>();
    public void enqueue(int item) { queue.add(item); }
    public Integer dequeue() { return queue.poll(); }
}
