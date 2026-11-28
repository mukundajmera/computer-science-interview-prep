package v2_extended;

/** Takes `percent` off whatever the wrapped strategy charges. */
public class PercentDiscountDecorator implements PricingStrategyV2 {
    private final PricingStrategyV2 inner;
    private final double percent;

    public PercentDiscountDecorator(PricingStrategyV2 inner, double percent) {
        this.inner = inner;
        this.percent = percent;
    }

    @Override
    public double calculatePrice(OrderV2 order) {
        return inner.calculatePrice(order) * (1.0 - percent / 100.0);
    }
}
