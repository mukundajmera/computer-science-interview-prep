import java.util.List;
import java.util.Collections;
import java.util.ArrayList;

public class Meeting {
    private final String id;
    private final String title;
    private final Interval interval;
    private final List<User> attendees;
    private final MeetingRoom room;

    public Meeting(String id, String title, Interval interval, List<User> attendees, MeetingRoom room) {
        this.id = id;
        this.title = title;
        this.interval = interval;
        this.attendees = new ArrayList<>(attendees);
        this.room = room;
    }

    public String getId() {
        return id;
    }

    public String getTitle() {
        return title;
    }

    public Interval getInterval() {
        return interval;
    }

    public List<User> getAttendees() {
        return Collections.unmodifiableList(attendees);
    }

    public MeetingRoom getRoom() {
        return room;
    }
}
