package v3_optimized;

/**
 * Interview-oriented extension points for parking-lot pricing decisions.
 *
 * This file is intentionally lightweight and focuses on contracts rather
 * than production logic.
 */
public interface ParkingPricingPolicy {
    double calculateFee(Ticket ticket);
}

interface TicketLifecycleHook {
    void onTicketOpened(Ticket ticket);

    void onTicketClosed(Ticket ticket, double finalFee);
}

interface VehicleFitPolicy {
    boolean canAssign(Vehicle vehicle, ParkingSpot spot);
}
