import java.time.Instant;

public class Reservation {
    private final String reservationId;
    private final String compartmentId;
    private final Instant expiresAt;
    private ReservationStatus status;

    public Reservation(String reservationId, String compartmentId, Instant expiresAt) {
        this.reservationId = reservationId;
        this.compartmentId = compartmentId;
        this.expiresAt = expiresAt;
        this.status = ReservationStatus.RESERVED;
    }

    public String getReservationId() {
        return reservationId;
    }

    public String getCompartmentId() {
        return compartmentId;
    }

    public Instant getExpiresAt() {
        return expiresAt;
    }

    public ReservationStatus getStatus() {
        return status;
    }

    public void setStatus(ReservationStatus status) {
        this.status = status;
    }

    public boolean isExpired(Instant now) {
        return now.isAfter(expiresAt);
    }
}
