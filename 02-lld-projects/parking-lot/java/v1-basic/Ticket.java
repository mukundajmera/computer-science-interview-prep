package v1_basic;

import java.time.LocalDateTime;
import java.time.Duration;
import java.util.UUID;

/**
 * Parking Lot System - V1 Basic
 * 
 * Ticket class representing a parking entry record.
 */

/**
 * Enumeration of ticket statuses.
 */
enum TicketStatus {
    ACTIVE,     // Vehicle is parked
    PAID,       // Fee has been paid
    LOST        // Ticket was lost
}

/**
 * Represents a parking ticket issued when a vehicle enters.
 */
class Ticket {
    private final String ticketId;
    private final Vehicle vehicle;
    private final ParkingSpot spot;
    private final LocalDateTime entryTime;
    private LocalDateTime exitTime;
    private TicketStatus status;

    public Ticket(Vehicle vehicle, ParkingSpot spot) {
        this.ticketId = generateTicketId();
        this.vehicle = vehicle;
        this.spot = spot;
        this.entryTime = LocalDateTime.now();
        this.exitTime = null;
        this.status = TicketStatus.ACTIVE;
    }

    /**
     * Generate a unique ticket ID.
     */
    private String generateTicketId() {
        return "TKT-" + UUID.randomUUID().toString().substring(0, 8).toUpperCase();
    }

    /**
     * Calculate the parking duration in hours (rounded up).
     */
    public long getDurationHours() {
        LocalDateTime end = (exitTime != null) ? exitTime : LocalDateTime.now();
        Duration duration = Duration.between(entryTime, end);
        long hours = duration.toHours();
        // Round up if there are any remaining minutes
        if (duration.toMinutesPart() > 0 || duration.toSecondsPart() > 0) {
            hours++;
        }
        return Math.max(1, hours); // Minimum 1 hour
    }

    /**
     * Mark the ticket as exited.
     */
    public void setExitTime() {
        this.exitTime = LocalDateTime.now();
    }

    /**
     * Mark the ticket as paid.
     */
    public void markPaid() {
        this.status = TicketStatus.PAID;
    }

    /**
     * Mark the ticket as lost.
     */
    public void markLost() {
        this.status = TicketStatus.LOST;
    }

    // Getters
    public String getTicketId() {
        return ticketId;
    }

    public Vehicle getVehicle() {
        return vehicle;
    }

    public ParkingSpot getSpot() {
        return spot;
    }

    public LocalDateTime getEntryTime() {
        return entryTime;
    }

    public LocalDateTime getExitTime() {
        return exitTime;
    }

    public TicketStatus getStatus() {
        return status;
    }

    @Override
    public String toString() {
        return "Ticket[" + ticketId + ", " + vehicle + ", Spot: " + spot.getSpotId() + 
               ", Entry: " + entryTime + ", Status: " + status + "]";
    }
}
