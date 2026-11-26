package enums;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.*;

public enum DamageSeverity {
    MINOR(100), MODERATE(500), SEVERE(2000);
    
    private final double baseCost;
    DamageSeverity(double cost) { this.baseCost = cost; }
    public double getBaseCost() { return baseCost; }
}
