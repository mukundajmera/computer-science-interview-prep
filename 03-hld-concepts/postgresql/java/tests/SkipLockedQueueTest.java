public class SkipLockedQueueTest {
    public static void main(String[] args) {
        SkipLockedQueue q = new SkipLockedQueue();
        q.enqueue(1);
        assert q.dequeue() == 1;
        System.out.println("SkipLockedQueueTest passed");
    }
}
