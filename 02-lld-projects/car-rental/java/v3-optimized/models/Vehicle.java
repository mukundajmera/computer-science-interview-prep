package models;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.*;

public class Vehicle {
    private final String vehicleId;
    private final String licensePlate;
    private final String make;
    private final String model;
    private final VehicleType type;
    private VehicleStatus status;
    private double basePrice;
    private int mileage;
    private final List<DamageReport> damageReports;
    private Branch currentBranch;
    private final List<MaintenanceWindow> maintenanceWindows;

    public Vehicle(String vehicleId, String licensePlate, String make, 
                   String model, VehicleType type, double basePrice) {
        this.vehicleId = vehicleId;
        this.licensePlate = licensePlate;
        this.make = make;
        this.model = model;
        this.type = type;
        this.basePrice = basePrice * type.getMultiplier();
        this.status = VehicleStatus.AVAILABLE;
        this.mileage = 0;
        this.damageReports = new ArrayList<>();
        this.maintenanceWindows = new ArrayList<>();
    }

    public boolean isAvailable() {
        return status == VehicleStatus.AVAILABLE;
    }

    public Branch getCurrentBranch() { return currentBranch; }
    public void setCurrentBranch(Branch branch) { this.currentBranch = branch; }
    
    public void scheduleMaintenance(MaintenanceWindow window) {
        maintenanceWindows.add(window);
    }
    
    public List<MaintenanceWindow> getMaintenanceWindows() {
        return new ArrayList<>(maintenanceWindows);
    }
    
    public boolean isAvailableForDates(LocalDate start, LocalDate end) {
        if (!isAvailable()) return false;
        
        for (MaintenanceWindow window : maintenanceWindows) {
            if (window.overlaps(start, end)) {
                return false;
            }
        }
        return true;
    }


    public void reserve() {
        if (status == VehicleStatus.AVAILABLE) {
            status = VehicleStatus.RESERVED;
        }
    }

    public void startRental() {
        if (status == VehicleStatus.RESERVED) {
            status = VehicleStatus.RENTED;
        }
    }

    public void completeRental() {
        status = VehicleStatus.AVAILABLE;
    }

    public void release() {
        status = VehicleStatus.AVAILABLE;
    }

    public void setMaintenance() {
        status = VehicleStatus.MAINTENANCE;
    }

    public void addDamageReport(DamageReport report) {
        damageReports.add(report);
        if (report.getSeverity() == DamageSeverity.SEVERE) {
            status = VehicleStatus.MAINTENANCE;
        }
    }

    public void updateMileage(int miles) {
        this.mileage += miles;
    }

    // Getters
    public String getVehicleId() { return vehicleId; }
    public String getLicensePlate() { return licensePlate; }
    public String getMake() { return make; }
    public String getModel() { return model; }
    public VehicleType getType() { return type; }
    public VehicleStatus getStatus() { return status; }
    public double getBasePrice() { return basePrice; }
    public int getMileage() { return mileage; }
    public List<DamageReport> getDamageReports() { return new ArrayList<>(damageReports); }

    @Override
    public String toString() {
        return String.format("%s %s (%s) - $%.2f/day", make, model, type, basePrice);
    }
}
