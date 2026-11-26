import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.locks.ReentrantLock;

public class MeetingRoom {
    private final String id;
    private final int capacity;
    private final List<String> amenities;
    private final IntervalTree intervalTree;
    private final ReentrantLock lock;

    public MeetingRoom(String id, int capacity, List<String> amenities) {
        this.id = id;
        this.capacity = capacity;
        this.amenities = new ArrayList<>(amenities);
        this.intervalTree = new IntervalTree();
        this.lock = new ReentrantLock();
    }

    public String getId() {
        return id;
    }

    public int getCapacity() {
        return capacity;
    }

    public List<String> getAmenities() {
        return new ArrayList<>(amenities);
    }

    public List<Meeting> getBookedMeetings() {
        lock.lock();
        try {
            return intervalTree.getAllMeetings();
        } finally {
            lock.unlock();
        }
    }

    public boolean hasOverlap(Interval interval) {
        lock.lock();
        try {
            return intervalTree.hasOverlap(interval);
        } finally {
            lock.unlock();
        }
    }

    public boolean bookMeeting(Meeting meeting) {
        lock.lock();
        try {
            if (intervalTree.hasOverlap(meeting.getInterval())) {
                return false;
            }
            intervalTree.insert(meeting);
            return true;
        } finally {
            lock.unlock();
        }
    }

    public Meeting cancelMeeting(String meetingId) {
        lock.lock();
        try {
            List<Meeting> meetings = intervalTree.getAllMeetings();
            Meeting targetMeeting = null;
            for (Meeting m : meetings) {
                if (m.getId().equals(meetingId)) {
                    targetMeeting = m;
                    break;
                }
            }
            if (targetMeeting != null) {
                intervalTree.remove(targetMeeting);
            }
            return targetMeeting;
        } finally {
            lock.unlock();
        }
    }
}
