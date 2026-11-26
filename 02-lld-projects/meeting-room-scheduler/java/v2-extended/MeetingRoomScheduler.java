import java.util.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.stream.Collectors;

public class MeetingRoomScheduler {
    private final List<MeetingRoom> rooms;
    private final RoomAllocationStrategy allocationStrategy;
    private final List<NotificationListener> notificationListeners;
    private final AtomicInteger meetingIdCounter;

    // Maintain history for quick lookup
    private final Map<String, List<Meeting>> userMeetings;

    public MeetingRoomScheduler(RoomAllocationStrategy allocationStrategy) {
        this.rooms = new ArrayList<>();
        this.allocationStrategy = allocationStrategy;
        this.notificationListeners = new ArrayList<>();
        this.meetingIdCounter = new AtomicInteger(1);
        this.userMeetings = new HashMap<>();
    }

    public void addRoom(MeetingRoom room) {
        synchronized (this.rooms) {
            this.rooms.add(room);
        }
    }

    public void addNotificationListener(NotificationListener listener) {
        synchronized (this.notificationListeners) {
            this.notificationListeners.add(listener);
        }
    }

    public Meeting bookMeeting(String title, int capacity, Interval interval, List<String> amenities, List<User> attendees) {
        MeetingRoom selectedRoom;
        synchronized (this.rooms) {
            selectedRoom = allocationStrategy.allocateRoom(this.rooms, capacity, interval, amenities);
        }

        if (selectedRoom == null) {
            return null; // No suitable room available
        }

        String meetingId = "M" + meetingIdCounter.getAndIncrement();
        Meeting meeting = new Meeting(meetingId, title, interval, attendees, selectedRoom);

        if (selectedRoom.bookMeeting(meeting)) {
            // Update user histories
            synchronized (this.userMeetings) {
                for (User user : attendees) {
                    userMeetings.computeIfAbsent(user.getId(), k -> new ArrayList<>()).add(meeting);
                }
            }

            // Notify
            List<NotificationListener> listeners;
            synchronized (this.notificationListeners) {
                listeners = new ArrayList<>(this.notificationListeners);
            }
            for (NotificationListener listener : listeners) {
                listener.onMeetingBooked(meeting);
            }

            return meeting;
        }

        return null; // Concurrency failure (e.g., booked in between check and act)
    }

    public List<Meeting> getLast20MeetingsForUser(String userId) {
        synchronized (this.userMeetings) {
            List<Meeting> meetings = userMeetings.getOrDefault(userId, new ArrayList<>());
            List<Meeting> sorted = new ArrayList<>(meetings);
            sorted.sort((m1, m2) -> Long.compare(m2.getInterval().getStartTime(), m1.getInterval().getStartTime())); // Descending
            return sorted.stream().limit(20).collect(Collectors.toList());
        }
    }

    public List<Meeting> getLast20MeetingsForRoom(String roomId) {
        MeetingRoom targetRoom = null;
        synchronized (this.rooms) {
            for (MeetingRoom room : rooms) {
                if (room.getId().equals(roomId)) {
                    targetRoom = room;
                    break;
                }
            }
        }

        if (targetRoom == null) return Collections.emptyList();

        List<Meeting> roomMeetings = targetRoom.getBookedMeetings();
        List<Meeting> sorted = new ArrayList<>(roomMeetings);
        sorted.sort((m1, m2) -> Long.compare(m2.getInterval().getStartTime(), m1.getInterval().getStartTime())); // Descending
        return sorted.stream().limit(20).collect(Collectors.toList());
    }

    public List<Interval> findCommonFreeSlots(List<User> users, long searchStart, long searchEnd) {
        List<Interval> busyIntervals = new ArrayList<>();
        
        synchronized (this.userMeetings) {
            for (User user : users) {
                List<Meeting> meetings = userMeetings.getOrDefault(user.getId(), Collections.emptyList());
                for (Meeting meeting : meetings) {
                    busyIntervals.add(meeting.getInterval());
                }
            }
        }

        if (busyIntervals.isEmpty()) {
            return Collections.singletonList(new Interval(searchStart, searchEnd));
        }

        // Merge overlapping intervals
        busyIntervals.sort(Comparator.comparingLong(Interval::getStartTime));
        List<Interval> merged = new ArrayList<>();
        Interval current = busyIntervals.get(0);

        for (int i = 1; i < busyIntervals.size(); i++) {
            Interval next = busyIntervals.get(i);
            if (current.getEndTime() >= next.getStartTime()) { // They overlap or touch
                current = new Interval(current.getStartTime(), Math.max(current.getEndTime(), next.getEndTime()));
            } else {
                merged.add(current);
                current = next;
            }
        }
        merged.add(current);

        // Find gaps within [searchStart, searchEnd)
        List<Interval> freeSlots = new ArrayList<>();
        long currentStart = searchStart;

        for (Interval busy : merged) {
            if (busy.getStartTime() > currentStart) {
                if (busy.getStartTime() <= searchEnd) {
                    freeSlots.add(new Interval(currentStart, busy.getStartTime()));
                } else {
                    freeSlots.add(new Interval(currentStart, searchEnd));
                    currentStart = searchEnd;
                    break;
                }
            }
            currentStart = Math.max(currentStart, busy.getEndTime());
        }

        if (currentStart < searchEnd) {
            freeSlots.add(new Interval(currentStart, searchEnd));
        }

        return freeSlots;
    }
}
