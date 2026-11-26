/**
 * Ticketing Platform - V1 Basic
 * Minimal interface-first skeleton for event browse + hold + booking.
 */

import java.time.Instant;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.locks.ReentrantLock;

public class TicketBookingService {

    public enum SeatState {
        AVAILABLE,
        HELD,
        BOOKED
    }

    public static class Seat {
        private final String seatId;
        private final String eventId;
        private final String section;
        private final String row;
        private final int number;
        private SeatState state;
        private int version;
        private final ReentrantLock lock = new ReentrantLock();

        public Seat(String seatId, String eventId, String section, String row, int number) {
            this.seatId = seatId;
            this.eventId = eventId;
            this.section = section;
            this.row = row;
            this.number = number;
            this.state = SeatState.AVAILABLE;
            this.version = 0;
        }

        public String getSeatId() { return seatId; }
        public String getEventId() { return eventId; }
        public SeatState getState() { return state; }
        public void setState(SeatState state) { this.state = state; }
        public int getVersion() { return version; }
        public void incrementVersion() { this.version++; }
        public ReentrantLock getLock() { return lock; }
    }

    public static class SeatHold {
        private final String holdId;
        private final String userId;
        private final List<String> seatIds;
        private final Instant expiresAt;
        private final String eventId;

        public SeatHold(String holdId, String eventId, String userId, List<String> seatIds, Instant expiresAt) {
            this.holdId = holdId;
            this.eventId = eventId;
            this.userId = userId;
            this.seatIds = seatIds;
            this.expiresAt = expiresAt;
        }

        public String getHoldId() { return holdId; }
        public String getEventId() { return eventId; }
        public String getUserId() { return userId; }
        public List<String> getSeatIds() { return seatIds; }
        public Instant getExpiresAt() { return expiresAt; }
    }

    public interface EventRepository {
        List<Map<String, String>> search(String city, String category, Instant start, Instant end, int page, int pageSize);
        List<Seat> getSeatMap(String eventId);
        List<Seat> getSeatsForUpdate(String eventId, List<String> seatIds);
    }

    public interface HoldRepository {
        Optional<SeatHold> findById(String holdId);
        SeatHold save(SeatHold hold);
        void deleteExpired(Instant now);
    }

    public interface BookingRepository {
        String createBooking(String holdId, String userId, String idempotencyKey);
        Optional<String> findByIdempotencyKey(String idempotencyKey);
    }

    public interface PaymentGateway {
        boolean authorize(String paymentToken, long amountInCents);
    }

    private final EventRepository eventRepo;
    private final HoldRepository holdRepo;
    private final BookingRepository bookingRepo;
    private final PaymentGateway paymentGateway;

    public TicketBookingService(EventRepository eventRepo, HoldRepository holdRepo, BookingRepository bookingRepo, PaymentGateway paymentGateway) {
        this.eventRepo = eventRepo;
        this.holdRepo = holdRepo;
        this.bookingRepo = bookingRepo;
        this.paymentGateway = paymentGateway;
    }

    public List<Map<String, String>> searchEvents(
        String city,
        String category,
        Instant start,
        Instant end,
        int page,
        int pageSize
    ) {
        return eventRepo.search(city, category, start, end, page, pageSize);
    }

    public SeatHold createHold(String userId, String eventId, List<String> seatIds, int holdSeconds) {
        List<Seat> seats = eventRepo.getSeatsForUpdate(eventId, seatIds);
        if (seats.size() != seatIds.size()) {
            throw new IllegalArgumentException("Some seats do not exist");
        }

        // Lock in consistent order to prevent deadlocks
        seats.sort(Comparator.comparing(Seat::getSeatId));

        List<Seat> acquiredLocks = new ArrayList<>();
        try {
            for (Seat seat : seats) {
                try {
                    if (!seat.getLock().tryLock(5, TimeUnit.SECONDS)) {
                        throw new RuntimeException("Lock contention");
                    }
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    throw new RuntimeException("Lock interrupted", e);
                }
                acquiredLocks.add(seat);

                if (seat.getState() != SeatState.AVAILABLE) {
                    throw new RuntimeException("Seat not available");
                }
            }

            for (Seat seat : seats) {
                seat.setState(SeatState.HELD);
                seat.incrementVersion();
            }

            String holdId = UUID.randomUUID().toString();
            SeatHold hold = new SeatHold(
                holdId,
                eventId,
                userId,
                seatIds,
                Instant.now().plusSeconds(holdSeconds)
            );
            return holdRepo.save(hold);
        } finally {
            for (int i = acquiredLocks.size() - 1; i >= 0; i--) {
                acquiredLocks.get(i).getLock().unlock();
            }
        }
    }

    public String confirmBooking(String holdId, String paymentToken, String idempotencyKey) {
        Optional<String> existing = bookingRepo.findByIdempotencyKey(idempotencyKey);
        if (existing.isPresent()) {
            return existing.get();
        }

        SeatHold hold = holdRepo.findById(holdId)
            .orElseThrow(() -> new IllegalArgumentException("Hold not found"));

        if (Instant.now().isAfter(hold.getExpiresAt())) {
            throw new RuntimeException("Hold expired");
        }

        List<Seat> seats = eventRepo.getSeatsForUpdate(hold.getEventId(), hold.getSeatIds());
        seats.sort(Comparator.comparing(Seat::getSeatId));

        List<Seat> acquiredLocks = new ArrayList<>();
        try {
            for (Seat seat : seats) {
                try {
                    if (!seat.getLock().tryLock(5, TimeUnit.SECONDS)) {
                        throw new RuntimeException("Lock contention");
                    }
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    throw new RuntimeException("Lock interrupted", e);
                }
                acquiredLocks.add(seat);

                if (seat.getState() != SeatState.HELD) {
                    throw new RuntimeException("Seat not held");
                }
            }

            if (!paymentGateway.authorize(paymentToken, 1000L)) {
                throw new RuntimeException("Payment failed");
            }

            for (Seat seat : seats) {
                seat.setState(SeatState.BOOKED);
                seat.incrementVersion();
            }

            return bookingRepo.createBooking(holdId, hold.getUserId(), idempotencyKey);
        } finally {
            for (int i = acquiredLocks.size() - 1; i >= 0; i--) {
                acquiredLocks.get(i).getLock().unlock();
            }
        }
    }
}
