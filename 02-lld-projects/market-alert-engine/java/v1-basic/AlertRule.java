import java.util.ArrayList;
import java.util.List;

public class AlertRule {
    private final String ruleId;
    private final String symbol;
    private final Condition condition;
    private final long cooldownMs;
    private final List<Sink> sinks;

    public AlertRule(String ruleId, String symbol, Condition condition, long cooldownMs, List<Sink> sinks) {
        this.ruleId = ruleId;
        this.symbol = symbol;
        this.condition = condition;
        this.cooldownMs = cooldownMs;
        this.sinks = new ArrayList<>(sinks);
    }

    public String getRuleId() { return ruleId; }
    public String getSymbol() { return symbol; }
    public Condition getCondition() { return condition; }
    public long getCooldownMs() { return cooldownMs; }
    public List<Sink> getSinks() { return sinks; }
}
