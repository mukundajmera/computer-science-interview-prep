package models;

import enums.ReservationStatus;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.UUID;

/**
 * Reservation.java - Hotel reservation record.
 */
public class Reservation {
    private final String reservationId;
    private final Guest guest;
    private final Room room;
    private final LocalDate checkInDate;
    private final LocalDate checkOutDate;
    private ReservationStatus status;
    private double totalAmount;
    private final LocalDateTime createdAt;

    public Reservation(Guest guest, Room room, LocalDate checkIn, LocalDate checkOut) {
        this.reservationId = "RES-" + UUID.randomUUID().toString().substring(0, 8);
        this.guest = guest;
        this.room = room;
        this.checkInDate = checkIn;
        this.checkOutDate = checkOut;
        this.status = ReservationStatus.PENDING;
        this.createdAt = LocalDateTime.now();
        this.totalAmount = calculateTotal();
    }

    private double calculateTotal() {
        long nights = getNumberOfNights();
        return nights * room.getBasePrice();
    }

    public long getNumberOfNights() {
        return ChronoUnit.DAYS.between(checkInDate, checkOutDate);
    }

    public String getReservationId() {
        return reservationId;
    }

    public Guest getGuest() {
        return guest;
    }

    public Room getRoom() {
        return room;
    }

    public LocalDate getCheckInDate() {
        return checkInDate;
    }

    public LocalDate getCheckOutDate() {
        return checkOutDate;
    }

    public ReservationStatus getStatus() {
        return status;
    }

    public double getTotalAmount() {
        return totalAmount;
    }

    public void confirm() {
        this.status = ReservationStatus.CONFIRMED;
    }

    public void checkIn() {
        this.status = ReservationStatus.CHECKED_IN;
    }

    public void checkOut() {
        this.status = ReservationStatus.CHECKED_OUT;
    }

    public void cancel() {
        this.status = ReservationStatus.CANCELLED;
    }

    @Override
    public String toString() {
        return String.format("Reservation[%s: %s -> Room %s, %s to %s, $%.2f]",
                reservationId, guest.getName(), room.getRoomNumber(),
                checkInDate, checkOutDate, totalAmount);
    }
}
