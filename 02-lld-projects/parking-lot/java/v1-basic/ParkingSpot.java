package v1_basic;

/**
 * Parking Lot System - V1 Basic
 * 
 * ParkingSpot class representing an individual parking position.
 */

/**
 * Enumeration of parking spot types.
 */
enum SpotType {
    MOTORCYCLE_SPOT,  // Fits: Motorcycle only
    COMPACT_SPOT,     // Fits: Motorcycle, Car
    LARGE_SPOT        // Fits: Motorcycle, Car, Truck
}

/**
 * Represents an individual parking spot in the lot.
 */
class ParkingSpot {
    private final String spotId;
    private final SpotType spotType;
    private final int floorNumber;
    private Vehicle vehicle;
    private boolean isOccupied;

    public ParkingSpot(String spotId, SpotType spotType, int floorNumber) {
        this.spotId = spotId;
        this.spotType = spotType;
        this.floorNumber = floorNumber;
        this.vehicle = null;
        this.isOccupied = false;
    }

    /**
     * Check if this spot can fit the given vehicle type.
     */
    public boolean canFit(Vehicle vehicle) {
        if (vehicle == null) {
            return false;
        }
        
        VehicleType vehicleType = vehicle.getType();
        
        switch (spotType) {
            case MOTORCYCLE_SPOT:
                return vehicleType == VehicleType.MOTORCYCLE;
            case COMPACT_SPOT:
                return vehicleType == VehicleType.MOTORCYCLE || 
                       vehicleType == VehicleType.CAR;
            case LARGE_SPOT:
                return true; // Fits all vehicle types
            default:
                return false;
        }
    }

    /**
     * Park a vehicle in this spot.
     * Returns true if successful, false otherwise.
     */
    public boolean park(Vehicle vehicle) {
        if (isOccupied || !canFit(vehicle)) {
            return false;
        }
        this.vehicle = vehicle;
        this.isOccupied = true;
        return true;
    }

    /**
     * Remove the vehicle from this spot.
     * Returns the vehicle that was parked, or null if empty.
     */
    public Vehicle unpark() {
        if (!isOccupied) {
            return null;
        }
        Vehicle parkedVehicle = this.vehicle;
        this.vehicle = null;
        this.isOccupied = false;
        return parkedVehicle;
    }

    // Getters
    public String getSpotId() {
        return spotId;
    }

    public SpotType getSpotType() {
        return spotType;
    }

    public int getFloorNumber() {
        return floorNumber;
    }

    public Vehicle getVehicle() {
        return vehicle;
    }

    public boolean isAvailable() {
        return !isOccupied;
    }

    public boolean isOccupied() {
        return isOccupied;
    }

    @Override
    public String toString() {
        return "Spot[" + spotId + ", " + spotType + ", " + 
               (isOccupied ? "Occupied by " + vehicle : "Available") + "]";
    }
}
