import java.util.concurrent.atomic.AtomicInteger;

public class Bucket {
    public final long startTime;
    public final AtomicInteger successCount = new AtomicInteger(0);
    public final AtomicInteger failureCount = new AtomicInteger(0);

    public Bucket(long startTime) {
        this.startTime = startTime;
    }
}
