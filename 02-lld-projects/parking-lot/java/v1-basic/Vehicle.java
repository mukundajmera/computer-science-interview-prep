package v1_basic;

/**
 * Parking Lot System - V1 Basic
 * 
 * Vehicle classes with Factory pattern for creation.
 * Supports Motorcycle, Car, and Truck types.
 */

/**
 * Enumeration of vehicle types supported by the parking lot.
 */
enum VehicleType {
    MOTORCYCLE,
    CAR,
    TRUCK
}

/**
 * Abstract base class for all vehicles.
 */
abstract class Vehicle {
    protected String licensePlate;
    protected VehicleType type;

    public Vehicle(String licensePlate, VehicleType type) {
        this.licensePlate = licensePlate;
        this.type = type;
    }

    public String getLicensePlate() {
        return licensePlate;
    }

    public VehicleType getType() {
        return type;
    }

    @Override
    public String toString() {
        return type + " [" + licensePlate + "]";
    }
}

/**
 * Motorcycle - smallest vehicle type.
 */
class Motorcycle extends Vehicle {
    public Motorcycle(String licensePlate) {
        super(licensePlate, VehicleType.MOTORCYCLE);
    }
}

/**
 * Car - medium-sized vehicle type.
 */
class Car extends Vehicle {
    public Car(String licensePlate) {
        super(licensePlate, VehicleType.CAR);
    }
}

/**
 * Truck - largest vehicle type.
 */
class Truck extends Vehicle {
    public Truck(String licensePlate) {
        super(licensePlate, VehicleType.TRUCK);
    }
}

/**
 * Factory for creating vehicles based on type.
 */
class VehicleFactory {
    public static Vehicle createVehicle(VehicleType type, String licensePlate) {
        switch (type) {
            case MOTORCYCLE:
                return new Motorcycle(licensePlate);
            case CAR:
                return new Car(licensePlate);
            case TRUCK:
                return new Truck(licensePlate);
            default:
                throw new IllegalArgumentException("Unknown vehicle type: " + type);
        }
    }
}
