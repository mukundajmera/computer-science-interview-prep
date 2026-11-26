package models;

import enums.ReservationStatus;
import java.time.LocalDate;
import java.time.temporal.ChronoUnit;

/**
 * Reservation.java - Car rental reservation.
 */
public class Reservation {
    private final String id;
    private final Customer customer;
    private final Vehicle vehicle;
    private final LocalDate startDate;
    private final LocalDate endDate;
    private ReservationStatus status;
    private double totalCost;

    public Reservation(String id, Customer customer, Vehicle vehicle, LocalDate start, LocalDate end) {
        this.id = id;
        this.customer = customer;
        this.vehicle = vehicle;
        this.startDate = start;
        this.endDate = end;
        this.status = ReservationStatus.PENDING;
        this.totalCost = calculateCost();
    }

    private double calculateCost() {
        long days = ChronoUnit.DAYS.between(startDate, endDate);
        return Math.max(1, days) * vehicle.getDailyRate();
    }

    public String getId() {
        return id;
    }

    public Customer getCustomer() {
        return customer;
    }

    public Vehicle getVehicle() {
        return vehicle;
    }

    public ReservationStatus getStatus() {
        return status;
    }

    public double getTotalCost() {
        return totalCost;
    }

    public void confirm() {
        this.status = ReservationStatus.CONFIRMED;
    }

    public void pickUp() {
        this.status = ReservationStatus.ACTIVE;
        vehicle.setAvailable(false);
    }

    public void returnVehicle() {
        this.status = ReservationStatus.COMPLETED;
        vehicle.setAvailable(true);
    }

    public void cancel() {
        this.status = ReservationStatus.CANCELLED;
    }

    @Override
    public String toString() {
        return String.format("Reservation[%s: %s -> %s, $%.2f]", id, customer.getName(), vehicle, totalCost);
    }
}
