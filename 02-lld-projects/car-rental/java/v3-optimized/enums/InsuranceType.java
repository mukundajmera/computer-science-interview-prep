package enums;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.*;

public enum InsuranceType {
    NONE(0, 0), BASIC(15, 0.5), PREMIUM(30, 1.0);
    
    private final double dailyCost;
    private final double damageCoverage;
    InsuranceType(double cost, double coverage) { 
        this.dailyCost = cost; 
        this.damageCoverage = coverage;
    }
    public double getDailyCost() { return dailyCost; }
    public double getCoverage() { return damageCoverage; }
}
