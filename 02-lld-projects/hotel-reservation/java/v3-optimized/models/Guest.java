package models;

import java.util.ArrayList;
import java.util.List;

/**
 * Guest.java - Hotel guest entity.
 */
public class Guest {
    private final String guestId;
    private String name;
    private String email;
    private String phone;
    private final List<Reservation> reservationHistory;

    public Guest(String guestId, String name, String email, String phone) {
        this.guestId = guestId;
        this.name = name;
        this.email = email;
        this.phone = phone;
        this.reservationHistory = new ArrayList<>();
    }

    public String getGuestId() {
        return guestId;
    }

    public String getName() {
        return name;
    }

    public String getEmail() {
        return email;
    }

    public String getPhone() {
        return phone;
    }

    public void addReservation(Reservation reservation) {
        reservationHistory.add(reservation);
    }

    public List<Reservation> getReservationHistory() {
        return new ArrayList<>(reservationHistory);
    }

    @Override
    public String toString() {
        return String.format("Guest[%s: %s]", guestId, name);
    }
}
