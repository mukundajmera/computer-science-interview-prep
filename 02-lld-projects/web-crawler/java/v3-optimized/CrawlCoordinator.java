package v3_optimized;

import java.util.ArrayList;
import java.util.List;
import java.util.Collections;

public class CrawlCoordinator {
    private final ShardQueue queue;
    private final BackpressureController backpressure;
    private final List<String> completed = Collections.synchronizedList(new ArrayList<>());
    private volatile boolean running = true;

    public CrawlCoordinator(ShardQueue queue, BackpressureController backpressure) {
        this.queue = queue;
        this.backpressure = backpressure;
    }
    
    public void cancel() {
        this.running = false;
    }

    public void runConcurrently(String host, int numTasks, int numThreads) {
        List<Thread> threads = new ArrayList<>();
        int tasksPerThread = numTasks / numThreads;
        
        for (int i = 0; i < numThreads; i++) {
            Thread t = new Thread(() -> {
                int tasksDone = 0;
                while (tasksDone < tasksPerThread && running) {
                    if (backpressure.acquire()) {
                        try {
                            v1_basic.CrawlRequest req = queue.dequeue(host);
                            if (req != null) {
                                completed.add(req.getUrl());
                                tasksDone++;
                            } else {
                                try { Thread.sleep(10); } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
                            }
                        } finally {
                            backpressure.release();
                        }
                    } else {
                        try { Thread.sleep(10); } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
                    }
                }
            });
            threads.add(t);
            t.start();
        }
        
        for (Thread t : threads) {
            try {
                t.join();
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
    }
    
    public List<String> getCompleted() {
        return completed;
    }
}
