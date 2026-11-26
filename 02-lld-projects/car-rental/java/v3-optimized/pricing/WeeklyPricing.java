public class WeeklyPricing implements PricingStrategy {
    private static final double WEEKLY_DISCOUNT = 0.85; // 15% discount
    
    @Override
    public double calculatePrice(Vehicle vehicle, long durationHours, double surgeMultiplier) {
        long weeks = durationHours / (24 * 7);
        long remainingDays = (durationHours % (24 * 7)) / 24;
        
        double weeklyPrice = vehicle.getBasePrice() * 7 * WEEKLY_DISCOUNT * weeks;
        double dailyPrice = vehicle.getBasePrice() * remainingDays;
        
        return (weeklyPrice + dailyPrice) * surgeMultiplier;
    }
}
