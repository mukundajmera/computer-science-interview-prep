public class DailyPricing implements PricingStrategy {
    @Override
    public double calculatePrice(Vehicle vehicle, long durationHours, double surgeMultiplier) {
        long days = Math.max(1, durationHours / 24);
        return vehicle.getBasePrice() * days * surgeMultiplier;
    }
}
