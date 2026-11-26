import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Resource-oriented API simulation with idempotent create and two pagination styles.
 */
public class VersionedBookingApi {
    private static final class Booking {
        private final String bookingId;
        private final String eventId;
        private final String userId;

        private Booking(String bookingId, String eventId, String userId) {
            this.bookingId = bookingId;
            this.eventId = eventId;
            this.userId = userId;
        }

        @Override
        public String toString() {
            return "{bookingId='" + bookingId + "', eventId='" + eventId + "', userId='" + userId + "'}";
        }
    }

    private final List<Booking> bookings = new ArrayList<>();
    private final Map<String, String> idempotencyToBooking = new HashMap<>();
    private int sequence = 1;

    public Booking postV1EventsEventIdBookings(String eventId, String userId, String idempotencyKey) {
        String existingId = idempotencyToBooking.get(idempotencyKey);
        if (existingId != null) {
            return getById(existingId);
        }

        String bookingId = "b-" + sequence++;
        Booking booking = new Booking(bookingId, eventId, userId);
        bookings.add(booking);
        idempotencyToBooking.put(idempotencyKey, bookingId);
        return booking;
    }

    public List<Booking> getV1BookingsOffset(int offset, int limit) {
        int start = Math.max(0, Math.min(offset, bookings.size()));
        int end = Math.max(start, Math.min(start + limit, bookings.size()));
        return bookings.subList(start, end);
    }

    public Map<String, Object> getV1BookingsCursor(String cursor, int limit) {
        int start = cursor == null ? 0 : Integer.parseInt(cursor);
        int end = Math.max(start, Math.min(start + limit, bookings.size()));

        Map<String, Object> response = new HashMap<>();
        response.put("items", new ArrayList<>(bookings.subList(start, end)));
        response.put("nextCursor", end < bookings.size() ? String.valueOf(end) : null);
        response.put("hasMore", end < bookings.size());
        return response;
    }

    private Booking getById(String bookingId) {
        for (Booking booking : bookings) {
            if (booking.bookingId.equals(bookingId)) {
                return booking;
            }
        }
        return null;
    }

    public static void main(String[] args) {
        VersionedBookingApi api = new VersionedBookingApi();

        System.out.println("Create 1: " + api.postV1EventsEventIdBookings("e-100", "u-1", "req-1"));
        System.out.println("Create 1 retry: " + api.postV1EventsEventIdBookings("e-100", "u-1", "req-1"));
        System.out.println("Create 2: " + api.postV1EventsEventIdBookings("e-101", "u-2", "req-2"));
        System.out.println("Create 3: " + api.postV1EventsEventIdBookings("e-102", "u-3", "req-3"));

        System.out.println("Offset page: " + api.getV1BookingsOffset(0, 2));
        System.out.println("Cursor page 1: " + api.getV1BookingsCursor(null, 2));
        System.out.println("Cursor page 2: " + api.getV1BookingsCursor("2", 2));
    }
}
