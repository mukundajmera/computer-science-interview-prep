package enums;

/**
 * RoomType.java - Types of hotel rooms with pricing.
 */
public enum RoomType {
    SINGLE(1, 80.0),
    DOUBLE(2, 120.0),
    DELUXE(3, 200.0),
    SUITE(4, 350.0);

    private final int maxOccupancy;
    private final double basePrice;

    RoomType(int maxOccupancy, double basePrice) {
        this.maxOccupancy = maxOccupancy;
        this.basePrice = basePrice;
    }

    public int getMaxOccupancy() {
        return maxOccupancy;
    }

    public double getBasePrice() {
        return basePrice;
    }
}
