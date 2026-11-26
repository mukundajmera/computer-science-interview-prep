package v1_basic;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Parking Lot System - V1 Basic
 * 
 * Main ParkingLot class implementing Singleton pattern.
 * Manages floors, parking operations, and ticket tracking.
 */

/**
 * Main parking lot system using Singleton pattern.
 */
class ParkingLot {
    private static ParkingLot instance;
    
    private final String name;
    private final List<Floor> floors;
    private final Map<String, Ticket> activeTickets;      // ticketId -> Ticket
    private final Map<String, ParkingSpot> vehicleToSpot; // licensePlate -> Spot
    private final PricingStrategy pricingStrategy;

    /**
     * Private constructor for Singleton.
     */
    private ParkingLot(String name) {
        this.name = name;
        this.floors = new ArrayList<>();
        this.activeTickets = new HashMap<>();
        this.vehicleToSpot = new HashMap<>();
        this.pricingStrategy = new HourlyPricing();
    }

    /**
     * Get the singleton instance.
     */
    public static synchronized ParkingLot getInstance() {
        if (instance == null) {
            instance = new ParkingLot("Main Parking Lot");
        }
        return instance;
    }

    /**
     * Initialize with custom name (for testing).
     */
    public static synchronized ParkingLot getInstance(String name) {
        if (instance == null) {
            instance = new ParkingLot(name);
        }
        return instance;
    }

    /**
     * Reset the singleton (for testing only).
     */
    public static synchronized void resetInstance() {
        instance = null;
    }

    /**
     * Add a floor to the parking lot.
     */
    public void addFloor(int motorcycleSpots, int compactSpots, int largeSpots) {
        int floorNumber = floors.size() + 1;
        floors.add(new Floor(floorNumber, motorcycleSpots, compactSpots, largeSpots));
    }

    /**
     * Park a vehicle in the lot.
     * Returns a ticket if successful, null if lot is full.
     */
    public Ticket parkVehicle(Vehicle vehicle) {
        if (vehicle == null) {
            throw new IllegalArgumentException("Vehicle cannot be null");
        }

        // Check if vehicle is already parked
        if (vehicleToSpot.containsKey(vehicle.getLicensePlate())) {
            System.out.println("Vehicle " + vehicle.getLicensePlate() + " is already parked");
            return null;
        }

        // Try to find a spot on any floor
        for (Floor floor : floors) {
            ParkingSpot spot = floor.parkVehicle(vehicle);
            if (spot != null) {
                Ticket ticket = new Ticket(vehicle, spot);
                activeTickets.put(ticket.getTicketId(), ticket);
                vehicleToSpot.put(vehicle.getLicensePlate(), spot);
                
                System.out.println("Vehicle parked successfully at " + spot.getSpotId());
                return ticket;
            }
        }

        System.out.println("No available spot for " + vehicle.getType());
        return null;
    }

    /**
     * Unpark a vehicle using the ticket.
     * Returns the parking fee.
     */
    public double unparkVehicle(Ticket ticket) {
        if (ticket == null) {
            throw new IllegalArgumentException("Ticket cannot be null");
        }

        if (!activeTickets.containsKey(ticket.getTicketId())) {
            System.out.println("Invalid or already used ticket");
            return -1;
        }

        // Calculate fee
        ticket.setExitTime();
        double fee = pricingStrategy.calculateFee(ticket);

        // Free the spot
        ParkingSpot spot = ticket.getSpot();
        Vehicle vehicle = spot.unpark();

        // Remove from tracking
        activeTickets.remove(ticket.getTicketId());
        vehicleToSpot.remove(vehicle.getLicensePlate());

        ticket.markPaid();
        System.out.println("Vehicle unparked. Fee: $" + String.format("%.2f", fee));
        return fee;
    }

    /**
     * Get the number of available spots for a vehicle type.
     */
    public int getAvailableSpots(VehicleType vehicleType) {
        int total = 0;
        for (Floor floor : floors) {
            total += floor.getAvailableSpots(vehicleType);
        }
        return total;
    }

    /**
     * Find a vehicle by license plate.
     * Returns the parking spot if found.
     */
    public ParkingSpot findVehicle(String licensePlate) {
        return vehicleToSpot.get(licensePlate);
    }

    /**
     * Get the total capacity of the parking lot.
     */
    public int getTotalCapacity() {
        int total = 0;
        for (Floor floor : floors) {
            total += floor.getTotalCapacity();
        }
        return total;
    }

    /**
     * Check if the parking lot is full.
     */
    public boolean isFull() {
        for (Floor floor : floors) {
            if (!floor.isFull()) {
                return false;
            }
        }
        return true;
    }

    /**
     * Display the status of the parking lot.
     */
    public void displayStatus() {
        System.out.println("\n=== " + name + " Status ===");
        System.out.println("Total Floors: " + floors.size());
        System.out.println("Total Capacity: " + getTotalCapacity());
        System.out.println("Active Vehicles: " + activeTickets.size());
        System.out.println();
        
        for (Floor floor : floors) {
            floor.displayStatus();
        }
        
        System.out.println("\nAvailable by vehicle type:");
        System.out.println("  Motorcycles: " + getAvailableSpots(VehicleType.MOTORCYCLE));
        System.out.println("  Cars: " + getAvailableSpots(VehicleType.CAR));
        System.out.println("  Trucks: " + getAvailableSpots(VehicleType.TRUCK));
    }

    // Getters
    public String getName() {
        return name;
    }

    public int getFloorCount() {
        return floors.size();
    }

    public int getActiveVehicleCount() {
        return activeTickets.size();
    }
}

/**
 * Interface for pricing strategies.
 */
interface PricingStrategy {
    double calculateFee(Ticket ticket);
}

/**
 * Hourly pricing strategy - different rates for different vehicle types.
 */
class HourlyPricing implements PricingStrategy {
    private static final double MOTORCYCLE_RATE = 1.0;  // $1/hour
    private static final double CAR_RATE = 2.0;         // $2/hour
    private static final double TRUCK_RATE = 4.0;       // $4/hour

    @Override
    public double calculateFee(Ticket ticket) {
        long hours = ticket.getDurationHours();
        VehicleType type = ticket.getVehicle().getType();
        
        double rate;
        switch (type) {
            case MOTORCYCLE:
                rate = MOTORCYCLE_RATE;
                break;
            case CAR:
                rate = CAR_RATE;
                break;
            case TRUCK:
                rate = TRUCK_RATE;
                break;
            default:
                rate = CAR_RATE;
        }
        
        return hours * rate;
    }
}

/**
 * Flat rate pricing - same rate for all vehicles.
 */
class FlatRatePricing implements PricingStrategy {
    private final double dailyRate;

    public FlatRatePricing(double dailyRate) {
        this.dailyRate = dailyRate;
    }

    @Override
    public double calculateFee(Ticket ticket) {
        long hours = ticket.getDurationHours();
        int days = (int) Math.ceil(hours / 24.0);
        return days * dailyRate;
    }
}
