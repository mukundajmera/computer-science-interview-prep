package v1_basic;

import java.util.ArrayList;
import java.util.List;

/**
 * Parking Lot System - V1 Basic
 * 
 * Floor class representing a parking floor with multiple spots.
 */

/**
 * Represents a single floor in the parking lot.
 */
class Floor {
    private final int floorNumber;
    private final List<ParkingSpot> spots;
    private int motorcycleSpotCount;
    private int compactSpotCount;
    private int largeSpotCount;

    /**
     * Create a floor with specified number of spots for each type.
     */
    public Floor(int floorNumber, int motorcycleSpots, int compactSpots, int largeSpots) {
        this.floorNumber = floorNumber;
        this.spots = new ArrayList<>();
        this.motorcycleSpotCount = motorcycleSpots;
        this.compactSpotCount = compactSpots;
        this.largeSpotCount = largeSpots;
        
        initializeSpots(motorcycleSpots, compactSpots, largeSpots);
    }

    /**
     * Initialize parking spots for this floor.
     */
    private void initializeSpots(int motorcycleSpots, int compactSpots, int largeSpots) {
        int spotNumber = 1;
        
        // Create motorcycle spots
        for (int i = 0; i < motorcycleSpots; i++) {
            String spotId = String.format("F%d-M%03d", floorNumber, spotNumber++);
            spots.add(new ParkingSpot(spotId, SpotType.MOTORCYCLE_SPOT, floorNumber));
        }
        
        // Create compact spots
        spotNumber = 1;
        for (int i = 0; i < compactSpots; i++) {
            String spotId = String.format("F%d-C%03d", floorNumber, spotNumber++);
            spots.add(new ParkingSpot(spotId, SpotType.COMPACT_SPOT, floorNumber));
        }
        
        // Create large spots
        spotNumber = 1;
        for (int i = 0; i < largeSpots; i++) {
            String spotId = String.format("F%d-L%03d", floorNumber, spotNumber++);
            spots.add(new ParkingSpot(spotId, SpotType.LARGE_SPOT, floorNumber));
        }
    }

    /**
     * Find an available spot for the given vehicle.
     * Returns null if no suitable spot is available.
     */
    public ParkingSpot findAvailableSpot(Vehicle vehicle) {
        // First try to find exact match spot type
        SpotType preferredType = getPreferredSpotType(vehicle.getType());
        
        for (ParkingSpot spot : spots) {
            if (spot.isAvailable() && spot.getSpotType() == preferredType) {
                return spot;
            }
        }
        
        // If no exact match, find any compatible spot
        for (ParkingSpot spot : spots) {
            if (spot.isAvailable() && spot.canFit(vehicle)) {
                return spot;
            }
        }
        
        return null;
    }

    /**
     * Get the preferred spot type for a vehicle type.
     */
    private SpotType getPreferredSpotType(VehicleType vehicleType) {
        switch (vehicleType) {
            case MOTORCYCLE:
                return SpotType.MOTORCYCLE_SPOT;
            case CAR:
                return SpotType.COMPACT_SPOT;
            case TRUCK:
                return SpotType.LARGE_SPOT;
            default:
                return SpotType.LARGE_SPOT;
        }
    }

    /**
     * Park a vehicle on this floor.
     * Returns the assigned spot, or null if no spot available.
     */
    public ParkingSpot parkVehicle(Vehicle vehicle) {
        ParkingSpot spot = findAvailableSpot(vehicle);
        if (spot != null && spot.park(vehicle)) {
            return spot;
        }
        return null;
    }

    /**
     * Unpark a vehicle from the given spot.
     */
    public Vehicle unparkVehicle(ParkingSpot spot) {
        return spot.unpark();
    }

    /**
     * Get the count of available spots for a vehicle type.
     */
    public int getAvailableSpots(VehicleType vehicleType) {
        int count = 0;
        for (ParkingSpot spot : spots) {
            if (spot.isAvailable()) {
                Vehicle tempVehicle = VehicleFactory.createVehicle(vehicleType, "TEMP");
                if (spot.canFit(tempVehicle)) {
                    count++;
                }
            }
        }
        return count;
    }

    /**
     * Check if the floor is full.
     */
    public boolean isFull() {
        for (ParkingSpot spot : spots) {
            if (spot.isAvailable()) {
                return false;
            }
        }
        return true;
    }

    /**
     * Get the total capacity of this floor.
     */
    public int getTotalCapacity() {
        return spots.size();
    }

    /**
     * Display floor status.
     */
    public void displayStatus() {
        System.out.println("Floor " + floorNumber + " Status:");
        System.out.println("  Total Spots: " + spots.size());
        System.out.println("  Available: " + getAvailableSpotsCount());
        System.out.println("  Occupied: " + getOccupiedSpotsCount());
    }

    private int getAvailableSpotsCount() {
        return (int) spots.stream().filter(ParkingSpot::isAvailable).count();
    }

    private int getOccupiedSpotsCount() {
        return (int) spots.stream().filter(ParkingSpot::isOccupied).count();
    }

    // Getters
    public int getFloorNumber() {
        return floorNumber;
    }

    public List<ParkingSpot> getSpots() {
        return new ArrayList<>(spots);
    }
}
