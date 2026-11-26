public class PriceCondition implements Condition {
    private final double threshold;
    private final Operator operator;

    public PriceCondition(double threshold, Operator operator) {
        this.threshold = threshold;
        this.operator = operator;
    }

    @Override
    public boolean evaluate(Tick tick) {
        switch (operator) {
            case GREATER_THAN: return tick.getPrice() > threshold;
            case LESS_THAN: return tick.getPrice() < threshold;
            case EQUAL: return Double.compare(tick.getPrice(), threshold) == 0;
            default: return false;
        }
    }
}
