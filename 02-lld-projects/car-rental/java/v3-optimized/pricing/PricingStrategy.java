public interface PricingStrategy {
    double calculatePrice(Vehicle vehicle, long durationHours, double surgeMultiplier);
}
