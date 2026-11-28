package v2_extended;

/** Pricing as an interface so decorators can wrap any base strategy. */
public interface PricingStrategyV2 {
    double calculatePrice(OrderV2 order);
}
