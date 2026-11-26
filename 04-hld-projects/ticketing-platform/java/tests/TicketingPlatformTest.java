import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.time.Instant;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

public class TicketingPlatformTest {

    static class InMemoryEventRepository implements TicketBookingService.EventRepository {
        private final Map<String, TicketBookingService.Seat> seats = new HashMap<>();

        public InMemoryEventRepository(List<TicketBookingService.Seat> initialSeats) {
            for (TicketBookingService.Seat s : initialSeats) {
                seats.put(s.getSeatId(), s);
            }
        }

        @Override
        public List<Map<String, String>> search(String city, String category, Instant start, Instant end, int page, int pageSize) {
            return Collections.emptyList();
        }

        @Override
        public List<TicketBookingService.Seat> getSeatMap(String eventId) {
            return new ArrayList<>(seats.values());
        }

        @Override
        public List<TicketBookingService.Seat> getSeatsForUpdate(String eventId, List<String> seatIds) {
            List<TicketBookingService.Seat> result = new ArrayList<>();
            for (String id : seatIds) {
                if (seats.containsKey(id)) {
                    result.add(seats.get(id));
                }
            }
            return result;
        }
    }

    static class InMemoryHoldRepository implements TicketBookingService.HoldRepository {
        private final Map<String, TicketBookingService.SeatHold> holds = new HashMap<>();

        @Override
        public Optional<TicketBookingService.SeatHold> findById(String holdId) {
            return Optional.ofNullable(holds.get(holdId));
        }

        @Override
        public TicketBookingService.SeatHold save(TicketBookingService.SeatHold hold) {
            holds.put(hold.getHoldId(), hold);
            return hold;
        }

        @Override
        public void deleteExpired(Instant now) {}
    }

    static class InMemoryBookingRepository implements TicketBookingService.BookingRepository {
        private final Map<String, String> bookings = new HashMap<>();

        @Override
        public String createBooking(String holdId, String userId, String idempotencyKey) {
            bookings.put(idempotencyKey, holdId);
            return holdId;
        }

        @Override
        public Optional<String> findByIdempotencyKey(String idempotencyKey) {
            return Optional.ofNullable(bookings.get(idempotencyKey));
        }
    }

    static class MockPaymentGateway implements TicketBookingService.PaymentGateway {
        @Override
        public boolean authorize(String paymentToken, long amountInCents) {
            return true;
        }
    }

    @Test
    public void testV1Basic_ReserveSeatAndPurchaseTicket() throws InterruptedException {
        List<TicketBookingService.Seat> seats = Arrays.asList(
            new TicketBookingService.Seat("A1", "evt_1", "A", "1", 1),
            new TicketBookingService.Seat("A2", "evt_1", "A", "1", 2),
            new TicketBookingService.Seat("A3", "evt_1", "A", "1", 3)
        );

        TicketBookingService.EventRepository eventRepo = new InMemoryEventRepository(seats);
        TicketBookingService service = new TicketBookingService(
            eventRepo,
            new InMemoryHoldRepository(),
            new InMemoryBookingRepository(),
            new MockPaymentGateway()
        );

        int numThreads = 100;
        ExecutorService executor = Executors.newFixedThreadPool(numThreads);
        AtomicInteger successes = new AtomicInteger(0);
        AtomicInteger failures = new AtomicInteger(0);

        for (int i = 0; i < numThreads; i++) {
            final int userId = i;
            executor.submit(() -> {
                try {
                    TicketBookingService.SeatHold hold = service.createHold("user_" + userId, "evt_1", Arrays.asList("A1", "A2", "A3"), 300);
                    service.confirmBooking(hold.getHoldId(), "tok_visa", "idem_" + userId);
                    successes.incrementAndGet();
                } catch (Exception e) {
                    failures.incrementAndGet();
                }
            });
        }

        executor.shutdown();
        executor.awaitTermination(10, TimeUnit.SECONDS);

        assertEquals(1, successes.get(), "Expected exactly 1 success");
        assertEquals(99, failures.get(), "Expected exactly 99 failures");
    }

    static class MockLockStore implements SeatHoldCoordinator.LockStore {
        private final Map<String, String> locks = new HashMap<>();

        @Override
        public synchronized boolean tryLockSeat(String eventId, String seatId, String holdId, Instant expiresAt) {
            String key = eventId + ":" + seatId;
            if (locks.containsKey(key)) {
                return false;
            }
            locks.put(key, holdId);
            return true;
        }

        @Override
        public synchronized void unlockSeat(String eventId, String seatId, String holdId) {
            String key = eventId + ":" + seatId;
            if (holdId.equals(locks.get(key))) {
                locks.remove(key);
            }
        }

        @Override
        public synchronized Optional<String> currentOwner(String eventId, String seatId) {
            return Optional.ofNullable(locks.get(eventId + ":" + seatId));
        }
    }

    static class MockHoldLedger implements SeatHoldCoordinator.HoldLedger {
        private final Map<String, SeatHoldCoordinator.HoldToken> holds = new HashMap<>();

        @Override
        public synchronized SeatHoldCoordinator.HoldToken save(SeatHoldCoordinator.HoldToken token) {
            holds.put(token.getHoldId(), token);
            return token;
        }

        @Override
        public synchronized Optional<SeatHoldCoordinator.HoldToken> find(String holdId) {
            return Optional.ofNullable(holds.get(holdId));
        }

        @Override
        public synchronized void markExpired(String holdId) {}
    }

    @Test
    public void testV2Scaled_ConcurrencyCheckToPreventDoubleBooking() throws InterruptedException {
        SeatHoldCoordinator coordinator = new SeatHoldCoordinator(new MockLockStore(), new MockHoldLedger());

        int numThreads = 100;
        ExecutorService executor = Executors.newFixedThreadPool(numThreads);
        AtomicInteger successes = new AtomicInteger(0);
        AtomicInteger failures = new AtomicInteger(0);

        for (int i = 0; i < numThreads; i++) {
            final int userId = i;
            executor.submit(() -> {
                try {
                    coordinator.reserveSeats("user_" + userId, "evt_1", Arrays.asList("B1", "B2", "B3"), 300);
                    successes.incrementAndGet();
                } catch (Exception e) {
                    failures.incrementAndGet();
                }
            });
        }

        executor.shutdown();
        executor.awaitTermination(10, TimeUnit.SECONDS);

        assertEquals(1, successes.get(), "Expected exactly 1 success");
        assertEquals(99, failures.get(), "Expected exactly 99 failures");
    }

    static class MockRegionRouter implements DistributedTicketingService.RegionRouter {
        @Override
        public String routeReadRegion(String userRegion, String eventId) {
            return "us-east-1";
        }

        @Override
        public String routeWriteRegion(String eventId) {
            return "us-west-2";
        }
    }

    static class MockBookingOrchestrator implements DistributedTicketingService.BookingOrchestrator {
        @Override
        public String createBooking(String region, String eventId, String holdId, String paymentToken, String idempotencyKey) {
            return "booking_123";
        }

        @Override
        public void reconcile(String bookingId) {}
    }

    static class MockGlobalEventRepository implements DistributedTicketingService.GlobalEventRepository {
        @Override
        public List<Map<String, String>> search(String region, String city, int page, int pageSize) {
            Map<String, String> event = new HashMap<>();
            event.put("id", "evt_global");
            event.put("city", city);
            return Arrays.asList(event);
        }
    }

    @Test
    public void testV3Distributed_WaitingRoomQueueAndSeatExpiration() {
        DistributedTicketingService service = new DistributedTicketingService(
            new MockRegionRouter(),
            new MockBookingOrchestrator(),
            new MockGlobalEventRepository()
        );

        DistributedTicketingService.RegionPlan plan = service.getRegionPlan("evt_global");
        assertEquals("us-west-2", plan.getPrimaryRegion());

        String bookingId = service.createBookingGlobal("evt_global", "hold_999", "tok_amex", "idem_999");
        assertEquals("booking_123", bookingId);
    }
}
