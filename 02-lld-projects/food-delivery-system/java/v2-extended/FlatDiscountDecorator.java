package v2_extended;

/** Takes a flat amount off, never driving the price below zero. */
public class FlatDiscountDecorator implements PricingStrategyV2 {
    private final PricingStrategyV2 inner;
    private final double amount;

    public FlatDiscountDecorator(PricingStrategyV2 inner, double amount) {
        this.inner = inner;
        this.amount = amount;
    }

    @Override
    public double calculatePrice(OrderV2 order) {
        return Math.max(0.0, inner.calculatePrice(order) - amount);
    }
}
