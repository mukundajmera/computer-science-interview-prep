package v3_optimized;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.TimeUnit;

public class AsyncLogProcessor {

    private static class LogTask {
        final LogEvent event;
        final List<Appender> appenders;

        LogTask(LogEvent event, List<Appender> appenders) {
            this.event = event;
            this.appenders = appenders;
        }
    }

    private final BlockingQueue<LogTask> queue;
    private volatile boolean isRunning;
    private final Thread workerThread;
    private final int batchSize;

    public AsyncLogProcessor(int capacity) {
        this(capacity, 100);
    }
    
    public AsyncLogProcessor(int capacity, int batchSize) {
        this.queue = new LinkedBlockingQueue<>(capacity);
        this.batchSize = batchSize;
        this.isRunning = true;
        this.workerThread = new Thread(this::processLogs, "AsyncLogWorker");
        this.workerThread.start();
    }

    public void submit(LogEvent event, List<Appender> appenders) {
        if (isRunning) {
            try {
                // Wait up to 1 second if queue is full
                queue.offer(new LogTask(event, appenders), 1, TimeUnit.SECONDS);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
    }

    private void processLogs() {
        while (isRunning || !queue.isEmpty()) {
            try {
                LogTask firstTask = queue.poll(100, TimeUnit.MILLISECONDS);
                if (firstTask != null) {
                    List<LogTask> batch = new ArrayList<>();
                    batch.add(firstTask);
                    queue.drainTo(batch, batchSize - 1);
                    
                    for (LogTask task : batch) {
                        for (Appender appender : task.appenders) {
                            try {
                                appender.append(task.event);
                            } catch (Exception e) {
                                System.err.println("Appender failed: " + e.getMessage());
                            }
                        }
                    }
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
        }
    }

    public void stop() {
        isRunning = false;
        try {
            workerThread.join(5000);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}
