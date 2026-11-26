import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.TimeUnit;
import java.util.function.Consumer;

public class WriteBatcher<T> implements AutoCloseable {
    private final int batchSizeThreshold;
    private final long maxWaitDurationMs;
    private final BlockingQueue<T> buffer;
    private final Consumer<List<T>> batchCommitter;
    private final Thread workerThread;
    private volatile boolean running = true;

    public WriteBatcher(int capacity, int batchSizeThreshold, long maxWaitDurationMs, Consumer<List<T>> batchCommitter) {
        if (capacity < batchSizeThreshold) {
            throw new IllegalArgumentException("Capacity must be >= batchSizeThreshold");
        }
        this.batchSizeThreshold = batchSizeThreshold;
        this.maxWaitDurationMs = maxWaitDurationMs;
        this.buffer = new ArrayBlockingQueue<>(capacity);
        this.batchCommitter = batchCommitter;

        this.workerThread = new Thread(this::flushLoop);
        this.workerThread.setDaemon(true);
        this.workerThread.start();
    }

    /**
     * Adds an item to the buffer.
     * @return true if added, false if buffer is full (backpressure)
     */
    public boolean write(T item) {
        if (!running) {
            throw new IllegalStateException("Batcher is closed");
        }
        return buffer.offer(item);
    }

    private void flushLoop() {
        List<T> currentBatch = new ArrayList<>(batchSizeThreshold);
        long batchStartTime = System.currentTimeMillis();

        while (running) {
            try {
                T item;
                if (currentBatch.isEmpty()) {
                    // Block indefinitely if empty to avoid busy spinning
                    item = buffer.take();
                } else {
                    long timeLeft = maxWaitDurationMs - (System.currentTimeMillis() - batchStartTime);
                    if (timeLeft <= 0) {
                        commitBatch(currentBatch);
                        batchStartTime = System.currentTimeMillis();
                        continue;
                    }
                    item = buffer.poll(timeLeft, TimeUnit.MILLISECONDS);
                }

                if (item != null) {
                    currentBatch.add(item);
                    if (currentBatch.size() == 1) {
                        // Reset start time on first item in new batch
                        batchStartTime = System.currentTimeMillis();
                    }
                } else if (!currentBatch.isEmpty()) {
                    // Timeout occurred
                    commitBatch(currentBatch);
                    batchStartTime = System.currentTimeMillis();
                }

                if (currentBatch.size() >= batchSizeThreshold) {
                    commitBatch(currentBatch);
                    batchStartTime = System.currentTimeMillis();
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                // If interrupted and no longer running, break to drain
                if (!running) {
                    break;
                }
            }
        }

        // Drain remaining items from buffer
        List<T> remaining = new ArrayList<>();
        buffer.drainTo(remaining);
        currentBatch.addAll(remaining);

        // Commit any remaining in batches
        for (int i = 0; i < currentBatch.size(); i += batchSizeThreshold) {
            int end = Math.min(i + batchSizeThreshold, currentBatch.size());
            commitBatch(new ArrayList<>(currentBatch.subList(i, end)));
        }
    }

    private void commitBatch(List<T> batch) {
        if (batch.isEmpty()) return;
        try {
            batchCommitter.accept(new ArrayList<>(batch)); // Copy to ensure safe sharing
        } catch (Exception e) {
            System.err.println("Error committing batch: " + e.getMessage());
        } finally {
            batch.clear();
        }
    }

    @Override
    public void close() throws Exception {
        running = false;
        workerThread.interrupt();
        workerThread.join();
    }
}
