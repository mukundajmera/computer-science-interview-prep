import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArrayList;

public class AlertEngine {
    private final Map<String, List<AlertRule>> rulesBySymbol = new ConcurrentHashMap<>();
    private final Map<String, Long> lastAlertTimes = new ConcurrentHashMap<>();

    public void addRule(AlertRule rule) {
        rulesBySymbol.computeIfAbsent(rule.getSymbol(), k -> new CopyOnWriteArrayList<>()).add(rule);
    }

    public void processTick(Tick tick) {
        List<AlertRule> rules = rulesBySymbol.get(tick.getSymbol());
        if (rules == null) return;

        for (AlertRule rule : rules) {
            if (rule.getCondition().evaluate(tick)) {
                String cooldownKey = rule.getRuleId() + "-" + tick.getSymbol();
                
                lastAlertTimes.compute(cooldownKey, (key, lastTime) -> {
                    long currentTime = tick.getTimestamp(); // Or System.currentTimeMillis(), depending on req. Assuming event time.
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
        for (Sink sink : rule.getSinks()) {
            sink.send(rule, tick);
        }
    }
}
