package models;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.*;

public class DamageReport {
    private static int counter = 0;
    
    private final String reportId;
    private final Vehicle vehicle;
    private final String description;
    private final DamageSeverity severity;
    private final double estimatedCost;
    private final LocalDateTime reportDate;

    public DamageReport(Vehicle vehicle, String description, DamageSeverity severity) {
        this.reportId = "DMG-" + (++counter);
        this.vehicle = vehicle;
        this.description = description;
        this.severity = severity;
        this.estimatedCost = severity.getBaseCost();
        this.reportDate = LocalDateTime.now();
    }

    public String getReportId() { return reportId; }
    public Vehicle getVehicle() { return vehicle; }
    public String getDescription() { return description; }
    public DamageSeverity getSeverity() { return severity; }
    public double getEstimatedCost() { return estimatedCost; }
    public LocalDateTime getReportDate() { return reportDate; }
}
