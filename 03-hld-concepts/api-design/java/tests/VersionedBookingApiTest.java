import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;

public class VersionedBookingApiTest {

    private VersionedBookingApi api;

    @BeforeEach
    public void setUp() {
        api = new VersionedBookingApi();
    }

    @Test
    public void testIdempotentCreateBooking() {
        Object booking1 = api.postV1EventsEventIdBookings("event-1", "user-1", "idem-1");
        Object booking2 = api.postV1EventsEventIdBookings("event-1", "user-1", "idem-1");

        assertNotNull(booking1);
        assertSame(booking1, booking2, "Idempotency key should return the exact same booking object");

        Object booking3 = api.postV1EventsEventIdBookings("event-2", "user-2", "idem-2");
        assertTrue(booking1 != booking3, "Different idempotency keys should return different bookings");

        String b1String = booking1.toString();
        assertTrue(b1String.contains("event-1"));
        assertTrue(b1String.contains("user-1"));
    }

    @Test
    public void testOffsetPagination() {
        for (int i = 0; i < 5; i++) {
            api.postV1EventsEventIdBookings("e" + i, "u" + i, "req" + i);
        }

        var page1 = api.getV1BookingsOffset(0, 2);
        assertEquals(2, page1.size());

        var page2 = api.getV1BookingsOffset(2, 2);
        assertEquals(2, page2.size());

        var page3 = api.getV1BookingsOffset(4, 2);
        assertEquals(1, page3.size());

        var outOfBounds = api.getV1BookingsOffset(10, 5);
        assertTrue(outOfBounds.isEmpty());
    }

    @Test
    public void testCursorPagination() {
        for (int i = 0; i < 3; i++) {
            api.postV1EventsEventIdBookings("e" + i, "u" + i, "req" + i);
        }

        Map<String, Object> page1 = api.getV1BookingsCursor(null, 2);
        List<?> items1 = (List<?>) page1.get("items");
        assertEquals(2, items1.size());
        assertEquals("2", page1.get("nextCursor"));
        assertEquals(true, page1.get("hasMore"));

        Map<String, Object> page2 = api.getV1BookingsCursor((String) page1.get("nextCursor"), 2);
        List<?> items2 = (List<?>) page2.get("items");
        assertEquals(1, items2.size());
        assertNull(page2.get("nextCursor"));
        assertEquals(false, page2.get("hasMore"));
    }
}
