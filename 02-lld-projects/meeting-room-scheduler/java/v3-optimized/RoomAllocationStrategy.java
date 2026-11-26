import java.util.List;

public interface RoomAllocationStrategy {
    MeetingRoom allocateRoom(List<MeetingRoom> rooms, int capacity, Interval interval, List<String> amenities);
}
