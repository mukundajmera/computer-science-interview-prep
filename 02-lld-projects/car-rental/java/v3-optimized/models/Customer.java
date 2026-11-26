package models;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.*;

public class Customer {
    private final String customerId;
    private String name;
    private String email;
    private String phone;
    private String drivingLicense;
    private int loyaltyPoints;
    private final List<Reservation> reservations;

    public Customer(String customerId, String name, String email, 
                    String phone, String drivingLicense) {
        this.customerId = customerId;
        this.name = name;
        this.email = email;
        this.phone = phone;
        this.drivingLicense = drivingLicense;
        this.reservations = new ArrayList<>();
        this.loyaltyPoints = 0;
    }

    public void addReservation(Reservation reservation) {
        reservations.add(reservation);
    }

    public List<Reservation> getActiveReservations() {
        List<Reservation> active = new ArrayList<>();
        for (Reservation r : reservations) {
            if (r.getStatus() == ReservationStatus.CONFIRMED || 
                r.getStatus() == ReservationStatus.ACTIVE) {
                active.add(r);
            }
        }
        return active;
    }

    public String getCustomerId() { return customerId; }
    public String getName() { return name; }
    public String getEmail() { return email; }
    public String getDrivingLicense() { return drivingLicense; }
    public int getLoyaltyPoints() { return loyaltyPoints; }
    public void addLoyaltyPoints(int points) { this.loyaltyPoints += points; }
    public List<Reservation> getReservations() { return new ArrayList<>(reservations); }
}
