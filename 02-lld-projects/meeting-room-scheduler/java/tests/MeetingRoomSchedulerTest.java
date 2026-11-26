import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;

import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.ArrayList;

import static org.junit.jupiter.api.Assertions.*;
class MeetingRoomSchedulerTest {

    private MeetingRoomScheduler scheduler;
    private User u1;
    private User u2;

    @BeforeEach
    void setUp() {
        scheduler = new MeetingRoomScheduler(new BestFitAllocationStrategy());
        u1 = new User("U1", "Alice", "alice@example.com");
        u2 = new User("U2", "Bob", "bob@example.com");
    }

    private static class MockNotificationListener implements NotificationListener {
        List<Meeting> bookedEvents = new ArrayList<>();
        List<Meeting> cancelledEvents = new ArrayList<>();
        List<Meeting> rescheduledEvents = new ArrayList<>();

        @Override
        public void onMeetingBooked(Meeting meeting) {
            bookedEvents.add(meeting);
        }

        @Override
        public void onMeetingCancelled(Meeting meeting) {
            cancelledEvents.add(meeting);
        }

        @Override
        public void onMeetingRescheduled(Meeting meeting) {
            rescheduledEvents.add(meeting);
        }
    }

    @Test
    void testIntervalTreeOverlap() {
        MeetingRoom r1 = new MeetingRoom("R1", 10, Collections.singletonList("Projector"));
        scheduler.addRoom(r1);

        Meeting m1 = scheduler.bookMeeting("M1", 5, new Interval(100, 200), Collections.singletonList("Projector"), Collections.singletonList(u1));
        assertNotNull(m1);

        Meeting m2 = scheduler.bookMeeting("M2", 5, new Interval(150, 250), Collections.singletonList("Projector"), Collections.singletonList(u1));
        assertNull(m2);

        Meeting m3 = scheduler.bookMeeting("M3", 5, new Interval(200, 300), Collections.singletonList("Projector"), Collections.singletonList(u1));
        assertNotNull(m3);

        Meeting m4 = scheduler.bookMeeting("M4", 5, new Interval(120, 150), Collections.singletonList("Projector"), Collections.singletonList(u1));
        assertNull(m4);
    }

    @Test
    void testNotificationsObserver() {
        MeetingRoom r1 = new MeetingRoom("R1", 10, Collections.singletonList("Projector"));
        scheduler.addRoom(r1);

        MockNotificationListener listener = new MockNotificationListener();
        scheduler.addNotificationListener(listener);

        Meeting m1 = scheduler.bookMeeting("M1", 5, new Interval(100, 200), Collections.singletonList("Projector"), Collections.singletonList(u1));
        assertNotNull(m1);
        assertEquals(1, listener.bookedEvents.size());
        assertEquals(m1.getId(), listener.bookedEvents.get(0).getId());

        scheduler.cancelMeeting(m1.getId());
        assertEquals(1, listener.cancelledEvents.size());
        assertEquals(m1.getId(), listener.cancelledEvents.get(0).getId());
    }

    @Test
    void testRescheduleObserver() {
        MeetingRoom r1 = new MeetingRoom("R1", 10, Collections.singletonList("Projector"));
        scheduler.addRoom(r1);

        MockNotificationListener listener = new MockNotificationListener();
        scheduler.addNotificationListener(listener);

        Meeting m1 = scheduler.bookMeeting("M1", 5, new Interval(100, 200), Collections.singletonList("Projector"), Collections.singletonList(u1));
        assertNotNull(m1);

        Meeting newMeeting = scheduler.rescheduleMeeting(m1.getId(), new Interval(300, 400));
        assertNotNull(newMeeting);
        assertEquals(300, newMeeting.getInterval().getStartTime());

        assertEquals(1, listener.rescheduledEvents.size());
        assertEquals(newMeeting.getId(), listener.rescheduledEvents.get(0).getId());
    }

    @Test
    void testRecurringMeetings() {
        MeetingRoom r1 = new MeetingRoom("R1", 10, Collections.singletonList("Projector"));
        scheduler.addRoom(r1);

        List<Meeting> meetings = scheduler.bookMeeting("Daily Standup", 5, new Interval(100, 200), Collections.singletonList("Projector"), Collections.singletonList(u1), "daily", 3);
        
        assertEquals(3, meetings.size());
        assertEquals(100, meetings.get(0).getInterval().getStartTime());
        assertEquals(100 + 86400, meetings.get(1).getInterval().getStartTime());
        assertEquals(100 + 86400 * 2, meetings.get(2).getInterval().getStartTime());
    }

    @Test
    void testCapacityAndAmenitiesFiltering() {
        MeetingRoom r1 = new MeetingRoom("R1", 5, Collections.singletonList("Projector"));
        MeetingRoom r2 = new MeetingRoom("R2", 15, Collections.singletonList("Whiteboard"));
        MeetingRoom r3 = new MeetingRoom("R3", 20, Arrays.asList("Projector", "Whiteboard"));

        scheduler.addRoom(r1);
        scheduler.addRoom(r2);
        scheduler.addRoom(r3);

        Meeting m1 = scheduler.bookMeeting("M1", 10, new Interval(100, 200), Collections.singletonList("Projector"), Collections.singletonList(u1));
        assertNotNull(m1);
        assertEquals("R3", m1.getRoom().getId());

        Meeting m2 = scheduler.bookMeeting("M2", 5, new Interval(300, 400), Collections.singletonList("Projector"), Collections.singletonList(u1));
        assertNotNull(m2);
        assertEquals("R1", m2.getRoom().getId());
    }
}
