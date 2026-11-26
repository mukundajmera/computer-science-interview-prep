package enums;

/**
 * ReservationStatus.java - Lifecycle of a reservation.
 */
public enum ReservationStatus {
    PENDING, // Just created
    CONFIRMED, // Payment received
    CHECKED_IN, // Guest checked in
    CHECKED_OUT, // Guest left
    CANCELLED // Reservation cancelled
}
