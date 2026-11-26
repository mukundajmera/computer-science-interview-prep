package enums;

/**
 * VehicleType.java - Types of rental vehicles.
 */
public enum VehicleType {
    CAR(50.0),
    SUV(80.0),
    VAN(100.0),
    LUXURY(150.0);

    private final double dailyRate;

    VehicleType(double rate) {
        this.dailyRate = rate;
    }

    public double getDailyRate() {
        return dailyRate;
    }
}
