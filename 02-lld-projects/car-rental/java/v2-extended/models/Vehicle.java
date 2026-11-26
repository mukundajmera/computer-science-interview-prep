package models;

import enums.VehicleType;

/**
 * Vehicle.java - Rental vehicle entity.
 */
public class Vehicle {
    private final String id;
    private final String licensePlate;
    private final VehicleType type;
    private final String make;
    private final String model;
    private boolean isAvailable;

    public Vehicle(String id, String licensePlate, VehicleType type, String make, String model) {
        this.id = id;
        this.licensePlate = licensePlate;
        this.type = type;
        this.make = make;
        this.model = model;
        this.isAvailable = true;
    }

    public String getId() {
        return id;
    }

    public String getLicensePlate() {
        return licensePlate;
    }

    public VehicleType getType() {
        return type;
    }

    public String getMake() {
        return make;
    }

    public String getModel() {
        return model;
    }

    public boolean isAvailable() {
        return isAvailable;
    }

    public void setAvailable(boolean a) {
        this.isAvailable = a;
    }

    public double getDailyRate() {
        return type.getDailyRate();
    }

    @Override
    public String toString() {
        return String.format("%s %s (%s) - $%.2f/day", make, model, type, getDailyRate());
    }
}
