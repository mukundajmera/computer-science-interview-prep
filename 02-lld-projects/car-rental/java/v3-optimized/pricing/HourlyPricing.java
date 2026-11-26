public class HourlyPricing implements PricingStrategy {
    private static final double HOURLY_RATE_FACTOR = 0.1; // 10% of daily rate
    
    @Override
    public double calculatePrice(Vehicle vehicle, long durationHours, double surgeMultiplier) {
        return vehicle.getBasePrice() * HOURLY_RATE_FACTOR * durationHours * surgeMultiplier;
    }
}
