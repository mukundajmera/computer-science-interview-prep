import java.util.List;
import java.util.Map;
import java.util.concurrent.*;

public class AlertEngine {
    private final Map<String, List<AlertRule>> rulesBySymbol = new ConcurrentHashMap<>();
    private final Map<String, Long> lastAlertTimes = new ConcurrentHashMap<>();
    
    private final BlockingQueue<Tick> tickQueue;
    private final ExecutorService sinkExecutor;
    private final Thread workerThread;
    private volatile boolean isRunning = true;
    
    // Poison pill to stop the worker safely
    private static final Tick POISON_PILL = new Tick("POISON", 0, 0, 0);

    public AlertEngine() {
        // High capacity bounded queue to absorb spikes
        this.tickQueue = new ArrayBlockingQueue<>(100000);
        
        // Dispatch threads to send notifications asynchronously
        this.sinkExecutor = Executors.newFixedThreadPool(4);
        
        this.workerThread = new Thread(this::workerLoop);
        this.workerThread.setDaemon(true);
        this.workerThread.start();
    }

    public void addRule(AlertRule rule) {
        rulesBySymbol.computeIfAbsent(rule.getSymbol(), k -> new CopyOnWriteArrayList<>()).add(rule);
    }

    // O(1) lock-free non-blocking ingestion
    public void processTick(Tick tick) {
        // offer returns false immediately if full, doesn't block.
        // For strict requirements we could drop, log, or use put() which blocks.
        tickQueue.offer(tick); 
    }
    
    public void stop() {
        try {
            tickQueue.put(POISON_PILL);
            workerThread.join(); // wait for worker to process all including poison pill
            sinkExecutor.shutdown();
            sinkExecutor.awaitTermination(5000, TimeUnit.MILLISECONDS);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        } finally {
            isRunning = false;
        }
    }

    private void workerLoop() {
        while (isRunning) {
            try {
                Tick tick = tickQueue.take();
                if (tick == POISON_PILL) {
                    break;
                }
                processTickInternal(tick);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
        }
    }

    private void processTickInternal(Tick tick) {
        List<AlertRule> rules = rulesBySymbol.get(tick.getSymbol());
        if (rules == null) return;

        for (AlertRule rule : rules) {
            if (rule.getCondition().evaluate(tick)) {
                String cooldownKey = rule.getRuleId() + "-" + tick.getSymbol();
                
                lastAlertTimes.compute(cooldownKey, (key, lastTime) -> {
                    long currentTime = tick.getTimestamp();
                    if (lastTime == null || (currentTime - lastTime >= rule.getCooldownMs())) {
                        dispatchAlert(rule, tick);
                        return currentTime;
                    }
                    return lastTime; // Suppressed
                });
            }
        }
    }

    private void dispatchAlert(AlertRule rule, Tick tick) {
        // Dispatch to the thread pool to execute sinks asynchronously, not blocking worker loop
        sinkExecutor.submit(() -> {
            for (Sink sink : rule.getSinks()) {
                sink.send(rule, tick);
            }
        });
    }
}
