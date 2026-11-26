import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;

import static org.junit.jupiter.api.Assertions.*;

class MeetingRoomSchedulerConcurrencyTest {

    private MeetingRoomScheduler scheduler;

    @BeforeEach
    void setUp() {
        scheduler = new MeetingRoomScheduler(new BestFitAllocationStrategy());
    }

    @Test
    void testConcurrentBookingStressTest() throws InterruptedException {
        MeetingRoom r1 = new MeetingRoom("R1", 100, Collections.singletonList("Projector"));
        scheduler.addRoom(r1);

        int numThreads = 16;
        AtomicInteger successCount = new AtomicInteger(0);
        ExecutorService executor = Executors.newFixedThreadPool(numThreads);

        for (int i = 0; i < numThreads; i++) {
            final int workerId = i;
            executor.submit(() -> {
                User u = new User("U" + workerId, "User " + workerId, "u@example.com");
                Meeting m = scheduler.bookMeeting(
                        "Concurrent Meeting " + workerId,
                        5,
                        new Interval(100, 200),
                        Collections.singletonList("Projector"),
                        Collections.singletonList(u)
                );
                if (m != null) {
                    successCount.incrementAndGet();
                }
            });
        }

        executor.shutdown();
        executor.awaitTermination(5, TimeUnit.SECONDS);

        // Only 1 thread should succeed in booking this overlapping timeslot
        assertEquals(1, successCount.get());
        assertEquals(1, r1.getBookedMeetings().size());
    }

    @Test
    void testConcurrentIndependentBookings() throws InterruptedException {
        scheduler.addRoom(new MeetingRoom("R1", 100, Collections.emptyList()));
        scheduler.addRoom(new MeetingRoom("R2", 100, Collections.emptyList()));

        int numThreads = 16;
        AtomicInteger successCount = new AtomicInteger(0);
        ExecutorService executor = Executors.newFixedThreadPool(numThreads);

        for (int i = 0; i < numThreads; i++) {
            final int workerId = i;
            executor.submit(() -> {
                Meeting m = scheduler.bookMeeting(
                        "Independent Meeting " + workerId,
                        5,
                        new Interval(workerId * 100L, workerId * 100L + 50L),
                        Collections.emptyList(),
                        Collections.emptyList()
                );
                if (m != null) {
                    successCount.incrementAndGet();
                }
            });
        }

        executor.shutdown();
        executor.awaitTermination(5, TimeUnit.SECONDS);

        // All non-overlapping bookings should succeed
        assertEquals(numThreads, successCount.get());
    }
}
