package v2_extended;

import java.util.List;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.LinkedBlockingQueue;

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
    private final Thread worker;
    private volatile boolean isRunning;

    public AsyncLogProcessor(int capacity) {
        this.queue = new LinkedBlockingQueue<>(capacity);
        this.isRunning = true;
        this.worker = new Thread(this::processLogs, "AsyncLogWorker");
        this.worker.setDaemon(false);
        this.worker.start();
    }

    public void submit(LogEvent event, List<Appender> appenders) {
        if (isRunning) {
            try {
                // For simplicity, we just put and block if queue is full.
                queue.put(new LogTask(event, appenders));
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
    }

    private void processLogs() {
        while (isRunning || !queue.isEmpty()) {
            try {
                LogTask task = queue.poll(100, java.util.concurrent.TimeUnit.MILLISECONDS);
                if (task != null) {
                    for (Appender appender : task.appenders) {
                        try {
                            appender.append(task.event);
                        } catch (Exception e) {
                            System.err.println("Appender failed: " + e.getMessage());
                        }
                    }
                }
            } catch (InterruptedException e) {
                // During graceful shutdown, if interrupted, clear the interrupted flag and continue draining queue
                if (!isRunning) {
                    // Just clear the flag, we will continue draining because !queue.isEmpty() will be evaluated
                } else {
                    Thread.currentThread().interrupt();
                    break;
                }
            }
        }
    }

    public void stop() {
        isRunning = false;
        worker.interrupt();
        try {
            worker.join(5000); // Wait up to 5s for queue to flush
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}
