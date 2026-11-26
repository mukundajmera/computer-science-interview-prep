package v2_extended;

/**
 * Parking Lot System - V2 Extended
 * 
 * Pricing strategies with support for different rate types.
 */

/**
 * Interface for pricing strategies.
 */
interface PricingStrategy {
    double calculateFee(Ticket ticket);
    String getStrategyName();
}

/**
 * Hourly pricing - different rates per vehicle type.
 */
class HourlyPricing implements PricingStrategy {
    private final double motorcycleRate;
    private final double carRate;
    private final double truckRate;

    public HourlyPricing() {
        this(1.0, 2.0, 4.0);
    }

    public HourlyPricing(double motorcycleRate, double carRate, double truckRate) {
        this.motorcycleRate = motorcycleRate;
        this.carRate = carRate;
        this.truckRate = truckRate;
    }

    @Override
    public double calculateFee(Ticket ticket) {
        long hours = ticket.getDurationHours();
        VehicleType type = ticket.getVehicle().getType();
        
        double rate;
        switch (type) {
            case MOTORCYCLE:
                rate = motorcycleRate;
                break;
            case CAR:
                rate = carRate;
                break;
            case TRUCK:
                rate = truckRate;
                break;
            default:
                rate = carRate;
        }
        
        return hours * rate;
    }

    @Override
    public String getStrategyName() {
        return "Hourly";
    }
}

/**
 * Flat rate pricing - same daily rate for all.
 */
class FlatRatePricing implements PricingStrategy {
    private final double dailyRate;

    public FlatRatePricing(double dailyRate) {
        this.dailyRate = dailyRate;
    }

    @Override
    public double calculateFee(Ticket ticket) {
        long hours = ticket.getDurationHours();
        int days = (int) Math.ceil(hours / 24.0);
        return Math.max(1, days) * dailyRate;
    }

    @Override
    public String getStrategyName() {
        return "FlatRate";
    }
}

/**
 * Tiered pricing - rates decrease with longer duration.
 */
class TieredPricing implements PricingStrategy {
    private final double firstHourRate;
    private final double additionalHourRate;
    private final double dailyMaxRate;

    public TieredPricing(double firstHourRate, double additionalHourRate, double dailyMaxRate) {
        this.firstHourRate = firstHourRate;
        this.additionalHourRate = additionalHourRate;
        this.dailyMaxRate = dailyMaxRate;
    }

    @Override
    public double calculateFee(Ticket ticket) {
        long hours = ticket.getDurationHours();
        
        if (hours <= 0) {
            return firstHourRate;
        }
        
        double fee = firstHourRate;
        if (hours > 1) {
            fee += (hours - 1) * additionalHourRate;
        }
        
        // Cap at daily maximum
        int days = (int) Math.ceil(hours / 24.0);
        double maxFee = days * dailyMaxRate;
        
        return Math.min(fee, maxFee);
    }

    @Override
    public String getStrategyName() {
        return "Tiered";
    }
}

/**
 * Weekend pricing - higher rates on weekends.
 */
class WeekendPricing implements PricingStrategy {
    private final PricingStrategy weekdayStrategy;
    private final double weekendMultiplier;

    public WeekendPricing(PricingStrategy weekdayStrategy, double weekendMultiplier) {
        this.weekdayStrategy = weekdayStrategy;
        this.weekendMultiplier = weekendMultiplier;
    }

    @Override
    public double calculateFee(Ticket ticket) {
        double baseFee = weekdayStrategy.calculateFee(ticket);
        
        // Check if entry was on weekend
        int dayOfWeek = ticket.getEntryTime().getDayOfWeek().getValue();
        boolean isWeekend = (dayOfWeek == 6 || dayOfWeek == 7);
        
        return isWeekend ? baseFee * weekendMultiplier : baseFee;
    }

    @Override
    public String getStrategyName() {
        return "Weekend";
    }
}

/**
 * Lost ticket pricing - penalty rate.
 */
class LostTicketPricing implements PricingStrategy {
    private final double penaltyFee;

    public LostTicketPricing(double penaltyFee) {
        this.penaltyFee = penaltyFee;
    }

    @Override
    public double calculateFee(Ticket ticket) {
        // Assume full day charge plus penalty
        return penaltyFee;
    }

    @Override
    public String getStrategyName() {
        return "LostTicket";
    }
}
