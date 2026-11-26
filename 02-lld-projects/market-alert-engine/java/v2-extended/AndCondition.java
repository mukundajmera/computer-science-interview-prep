public class AndCondition implements Condition {
    private final Condition left;
    private final Condition right;

    public AndCondition(Condition left, Condition right) {
        this.left = left;
        this.right = right;
    }

    @Override
    public boolean evaluate(Tick tick) {
        return left.evaluate(tick) && right.evaluate(tick);
    }
}
