import java.util.ArrayList;
import java.util.List;
import java.util.Collections;

public class MeetingRoom {
    private final String id;
    private final int capacity;
    private final List<String> amenities;
    private final List<Meeting> bookedMeetings;

    public MeetingRoom(String id, int capacity, List<String> amenities) {
        this.id = id;
        this.capacity = capacity;
        this.amenities = new ArrayList<>(amenities);
        this.bookedMeetings = new ArrayList<>();
    }

    public String getId() {
        return id;
    }

    public int getCapacity() {
        return capacity;
    }

    public List<String> getAmenities() {
        return Collections.unmodifiableList(amenities);
    }

    public List<Meeting> getBookedMeetings() {
        synchronized (this) {
            return new ArrayList<>(bookedMeetings);
        }
    }

    public synchronized boolean bookMeeting(Meeting meeting) {
        // Check for interval collisions
        for (Meeting existing : bookedMeetings) {
            if (existing.getInterval().overlaps(meeting.getInterval())) {
                return false; // Collision detected
            }
        }
        bookedMeetings.add(meeting);
        return true;
    }
}
