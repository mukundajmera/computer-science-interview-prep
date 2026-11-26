public class VolumeCondition implements Condition {
    private final int threshold;
    private final Operator operator;

    public VolumeCondition(int threshold, Operator operator) {
        this.threshold = threshold;
        this.operator = operator;
    }

    @Override
    public boolean evaluate(Tick tick) {
        switch (operator) {
            case GREATER_THAN: return tick.getVolume() > threshold;
            case LESS_THAN: return tick.getVolume() < threshold;
            case EQUAL: return tick.getVolume() == threshold;
            default: return false;
        }
    }
}
