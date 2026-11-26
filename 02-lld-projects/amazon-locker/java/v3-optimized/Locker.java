import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class Locker {
    private final List<Compartment> compartments;
    private final Map<String, AccessToken> tokens;
    private final Map<String, Reservation> reservations;
    private final Clock clock;
    private final Duration tokenTtl;
    private final Duration reservationTtl;
    private AllocationPolicy allocationPolicy;
    private long tokenCounter;
    private long reservationCounter;

    public Locker(int smallCount, int mediumCount, int largeCount) {
        this(smallCount, mediumCount, largeCount, new SystemClock(), Duration.ofDays(7), Duration.ofMinutes(3), new FallbackSizePolicy());
    }

    public Locker(int smallCount, int mediumCount, int largeCount, Clock clock, Duration tokenTtl, Duration reservationTtl, AllocationPolicy allocationPolicy) {
        this.compartments = new ArrayList<>();
        this.tokens = new HashMap<>();
        this.reservations = new HashMap<>();
        this.clock = clock;
        this.tokenTtl = tokenTtl;
        this.reservationTtl = reservationTtl;
        this.allocationPolicy = allocationPolicy;
        this.tokenCounter = 0;
        this.reservationCounter = 0;
        initCompartments(smallCount, mediumCount, largeCount);
    }

    public String depositPackage(PackageSize size) {
        String reservationId = reserveCompartment(size);
        if (reservationId == null) {
            return null;
        }
        return confirmDeposit(reservationId);
    }

    public String reserveCompartment(PackageSize size) {
        expireReservations();
        Compartment c = allocationPolicy.select(compartments, size);
        if (c == null) {
            return null;
        }

        c.markOccupied();
        String reservationId = "R-" + (++reservationCounter);
        Reservation reservation = new Reservation(reservationId, c.getId(), clock.now().plus(reservationTtl));
        reservations.put(reservationId, reservation);
        return reservationId;
    }

    public String confirmDeposit(String reservationId) {
        Reservation reservation = reservations.get(reservationId);
        if (reservation == null || reservation.getStatus() != ReservationStatus.RESERVED) {
            return null;
        }
        if (reservation.isExpired(clock.now())) {
            reservation.setStatus(ReservationStatus.EXPIRED);
            Compartment c = findById(reservation.getCompartmentId());
            if (c != null) {
                c.markAvailable();
            }
            reservations.remove(reservationId);
            return null;
        }

        reservation.setStatus(ReservationStatus.CONFIRMED);
        String tokenCode = "T-" + (++tokenCounter);
        AccessToken token = new AccessToken(tokenCode, reservation.getCompartmentId(), clock.now().plus(tokenTtl));
        tokens.put(tokenCode, token);
        reservations.remove(reservationId);
        return tokenCode;
    }

    public boolean cancelReservation(String reservationId) {
        Reservation reservation = reservations.get(reservationId);
        if (reservation == null || reservation.getStatus() != ReservationStatus.RESERVED) {
            return false;
        }
        reservation.setStatus(ReservationStatus.CANCELLED);
        Compartment c = findById(reservation.getCompartmentId());
        if (c != null) {
            c.markAvailable();
        }
        reservations.remove(reservationId);
        return true;
    }

    public int expireReservations() {
        List<String> expiredIds = new ArrayList<>();
        Instant now = clock.now();
        for (Map.Entry<String, Reservation> entry : reservations.entrySet()) {
            if (entry.getValue().isExpired(now)) {
                expiredIds.add(entry.getKey());
            }
        }

        for (String id : expiredIds) {
            Reservation reservation = reservations.remove(id);
            reservation.setStatus(ReservationStatus.EXPIRED);
            Compartment c = findById(reservation.getCompartmentId());
            if (c != null) {
                c.markAvailable();
            }
        }
        return expiredIds.size();
    }

    public boolean pickup(String tokenCode) {
        AccessToken token = tokens.get(tokenCode);
        if (token == null || token.isExpired(clock.now())) {
            return false;
        }

        Compartment c = findById(token.getCompartmentId());
        if (c == null) {
            return false;
        }

        c.markAvailable();
        tokens.remove(tokenCode);
        return true;
    }

    public boolean pickupPackage(String tokenCode) {
        return pickup(tokenCode);
    }

    public int clearExpiredDeposits() {
        int cleared = 0;
        Instant now = clock.now();
        List<String> expiredCodes = new ArrayList<>();
        for (Map.Entry<String, AccessToken> entry : tokens.entrySet()) {
            if (entry.getValue().isExpired(now)) {
                expiredCodes.add(entry.getKey());
            }
        }

        for (String code : expiredCodes) {
            AccessToken token = tokens.remove(code);
            Compartment c = findById(token.getCompartmentId());
            if (c != null) {
                c.markAvailable();
                cleared++;
            }
        }
        return cleared;
    }

    private Compartment findById(String id) {
        for (Compartment c : compartments) {
            if (c.getId().equals(id)) {
                return c;
            }
        }
        return null;
    }

    private void initCompartments(int smallCount, int mediumCount, int largeCount) {
        for (int i = 1; i <= smallCount; i++) {
            compartments.add(new Compartment("S-" + i, PackageSize.SMALL));
        }
        for (int i = 1; i <= mediumCount; i++) {
            compartments.add(new Compartment("M-" + i, PackageSize.MEDIUM));
        }
        for (int i = 1; i <= largeCount; i++) {
            compartments.add(new Compartment("L-" + i, PackageSize.LARGE));
        }
    }
}
