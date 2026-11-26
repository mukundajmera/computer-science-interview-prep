package enums;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.*;

public enum VehicleType {
    CAR(1.0), SUV(1.3), TRUCK(1.4), VAN(1.2), LUXURY(2.0);
    
    private final double priceMultiplier;
    VehicleType(double multiplier) { this.priceMultiplier = multiplier; }
    public double getMultiplier() { return priceMultiplier; }
}
