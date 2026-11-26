import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.locks.ReentrantLock;

public class MeetingRoomScheduler {
    private final List<MeetingRoom> rooms;
    private final RoomAllocationStrategy allocationStrategy;
    private final List<NotificationListener> notificationListeners;
    private int meetingIdCounter;

    private final ReentrantLock roomsLock;
    private final ReentrantLock listenersLock;
    private final ReentrantLock userMeetingsLock;

    private final Map<String, List<Meeting>> userMeetings;

    public MeetingRoomScheduler(RoomAllocationStrategy allocationStrategy) {
        this.rooms = new ArrayList<>();
        this.allocationStrategy = allocationStrategy;
        this.notificationListeners = new ArrayList<>();
        this.meetingIdCounter = 1;

        this.roomsLock = new ReentrantLock();
        this.listenersLock = new ReentrantLock();
        this.userMeetingsLock = new ReentrantLock();

        this.userMeetings = new HashMap<>();
    }

    public void addRoom(MeetingRoom room) {
        roomsLock.lock();
        try {
            rooms.add(room);
        } finally {
            roomsLock.unlock();
        }
    }

    public void addNotificationListener(NotificationListener listener) {
        listenersLock.lock();
        try {
            notificationListeners.add(listener);
        } finally {
            listenersLock.unlock();
        }
    }

    public List<Meeting> bookMeeting(String title, int capacity, Interval interval, List<String> amenities, List<User> attendees, String recurrence, int count) {
        List<Meeting> bookedMeetings = new ArrayList<>();
        Interval currentInterval = interval;
        
        for (int i = 0; i < count; i++) {
            boolean bookedSuccessfully = false;
            int maxRetries = 3;
            int retries = 0;
            
            while (!bookedSuccessfully && retries < maxRetries) {
                MeetingRoom selectedRoom;
                roomsLock.lock();
                try {
                    selectedRoom = allocationStrategy.allocateRoom(rooms, capacity, currentInterval, amenities);
                } finally {
                    roomsLock.unlock();
                }
    
                if (selectedRoom == null) {
                    break;
                }
    
                String meetingId;
                roomsLock.lock();
                try {
                    meetingId = "M" + meetingIdCounter;
                    meetingIdCounter++;
                } finally {
                    roomsLock.unlock();
                }
    
                Meeting meeting = new Meeting(meetingId, title, currentInterval, attendees, selectedRoom);
    
                if (selectedRoom.bookMeeting(meeting)) {
                    userMeetingsLock.lock();
                    try {
                        for (User user : attendees) {
                            userMeetings.computeIfAbsent(user.getId(), k -> new ArrayList<>()).add(meeting);
                        }
                    } finally {
                        userMeetingsLock.unlock();
                    }
    
                    List<NotificationListener> listenersSnapshot;
                    listenersLock.lock();
                    try {
                        listenersSnapshot = new ArrayList<>(notificationListeners);
                    } finally {
                        listenersLock.unlock();
                    }
    
                    for (NotificationListener listener : listenersSnapshot) {
                        listener.onMeetingBooked(meeting);
                    }
                    
                    bookedMeetings.add(meeting);
                    bookedSuccessfully = true;
                } else {
                    retries++;
                }
            }
            
            if (!bookedSuccessfully) {
                break;
            }
            
            if ("daily".equals(recurrence)) {
                currentInterval = new Interval(currentInterval.getStartTime() + 86400, currentInterval.getEndTime() + 86400);
            } else if ("weekly".equals(recurrence)) {
                currentInterval = new Interval(currentInterval.getStartTime() + 7 * 86400, currentInterval.getEndTime() + 7 * 86400);
            } else {
                break;
            }
        }

        return bookedMeetings;
    }

    public Meeting bookMeeting(String title, int capacity, Interval interval, List<String> amenities, List<User> attendees) {
        List<Meeting> meetings = bookMeeting(title, capacity, interval, amenities, attendees, null, 1);
        if (meetings.isEmpty()) {
            return null;
        }
        return meetings.get(0);
    }
    
    public boolean cancelMeeting(String meetingId) {
        Meeting targetMeeting = null;
        roomsLock.lock();
        try {
            for (MeetingRoom room : rooms) {
                Meeting m = room.cancelMeeting(meetingId);
                if (m != null) {
                    targetMeeting = m;
                    break;
                }
            }
        } finally {
            roomsLock.unlock();
        }
        
        if (targetMeeting != null) {
            userMeetingsLock.lock();
            try {
                for (User user : targetMeeting.getAttendees()) {
                    List<Meeting> userM = userMeetings.get(user.getId());
                    if (userM != null) {
                        userM.removeIf(m -> m.getId().equals(meetingId));
                    }
                }
            } finally {
                userMeetingsLock.unlock();
            }
            
            List<NotificationListener> listenersSnapshot;
            listenersLock.lock();
            try {
                listenersSnapshot = new ArrayList<>(notificationListeners);
            } finally {
                listenersLock.unlock();
            }

            for (NotificationListener listener : listenersSnapshot) {
                listener.onMeetingCancelled(targetMeeting);
            }
            return true;
        }
        return false;
    }
    
    public Meeting rescheduleMeeting(String meetingId, Interval newInterval) {
        Meeting targetMeeting = null;
        roomsLock.lock();
        try {
            for (MeetingRoom room : rooms) {
                for (Meeting m : room.getBookedMeetings()) {
                    if (m.getId().equals(meetingId)) {
                        targetMeeting = m;
                        break;
                    }
                }
                if (targetMeeting != null) break;
            }
        } finally {
            roomsLock.unlock();
        }
        
        if (targetMeeting == null) {
            return null;
        }
        
        cancelMeeting(meetingId);
        
        Meeting newMeeting = bookMeeting(targetMeeting.getTitle(), targetMeeting.getAttendees().size(), newInterval, new ArrayList<>(), targetMeeting.getAttendees());
        
        if (newMeeting != null) {
            List<NotificationListener> listenersSnapshot;
            listenersLock.lock();
            try {
                listenersSnapshot = new ArrayList<>(notificationListeners);
            } finally {
                listenersLock.unlock();
            }

            for (NotificationListener listener : listenersSnapshot) {
                listener.onMeetingRescheduled(newMeeting);
            }
            return newMeeting;
        }
        
        return null;
    }

    public List<Meeting> getLast20MeetingsForUser(String userId) {
        userMeetingsLock.lock();
        try {
            List<Meeting> meetings = new ArrayList<>(userMeetings.getOrDefault(userId, new ArrayList<>()));
            meetings.sort((m1, m2) -> Long.compare(m2.getInterval().getStartTime(), m1.getInterval().getStartTime()));
            return meetings.size() > 20 ? meetings.subList(0, 20) : meetings;
        } finally {
            userMeetingsLock.unlock();
        }
    }

    public List<Meeting> getLast20MeetingsForRoom(String roomId) {
        MeetingRoom targetRoom = null;
        roomsLock.lock();
        try {
            for (MeetingRoom room : rooms) {
                if (room.getId().equals(roomId)) {
                    targetRoom = room;
                    break;
                }
            }
        } finally {
            roomsLock.unlock();
        }

        if (targetRoom == null) {
            return new ArrayList<>();
        }

        List<Meeting> meetings = targetRoom.getBookedMeetings();
        meetings.sort((m1, m2) -> Long.compare(m2.getInterval().getStartTime(), m1.getInterval().getStartTime()));
        return meetings.size() > 20 ? meetings.subList(0, 20) : meetings;
    }

    public List<Interval> findCommonFreeSlots(List<User> users, long searchStart, long searchEnd) {
        List<Interval> busyIntervals = new ArrayList<>();

        userMeetingsLock.lock();
        try {
            for (User user : users) {
                List<Meeting> meetings = userMeetings.getOrDefault(user.getId(), new ArrayList<>());
                for (Meeting meeting : meetings) {
                    busyIntervals.add(meeting.getInterval());
                }
            }
        } finally {
            userMeetingsLock.unlock();
        }

        if (busyIntervals.isEmpty()) {
            List<Interval> result = new ArrayList<>();
            result.add(new Interval(searchStart, searchEnd));
            return result;
        }

        busyIntervals.sort(Comparator.comparingLong(Interval::getStartTime));
        List<Interval> merged = new ArrayList<>();
        Interval current = busyIntervals.get(0);

        for (int i = 1; i < busyIntervals.size(); i++) {
            Interval next = busyIntervals.get(i);
            if (current.getEndTime() >= next.getStartTime()) {
                current = new Interval(current.getStartTime(), Math.max(current.getEndTime(), next.getEndTime()));
            } else {
                merged.add(current);
                current = next;
            }
        }
        merged.add(current);

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
