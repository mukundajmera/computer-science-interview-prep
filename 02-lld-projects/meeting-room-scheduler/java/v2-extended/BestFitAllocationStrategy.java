import java.util.List;
import java.util.stream.Collectors;

public class BestFitAllocationStrategy implements RoomAllocationStrategy {
    @Override
    public MeetingRoom allocateRoom(List<MeetingRoom> rooms, int capacity, Interval interval, List<String> amenities) {
        List<MeetingRoom> suitableRooms = rooms.stream()
            .filter(room -> room.getCapacity() >= capacity)
            .filter(room -> room.getAmenities().containsAll(amenities))
            .filter(room -> isAvailable(room, interval))
            .sorted((r1, r2) -> Integer.compare(r1.getCapacity(), r2.getCapacity()))
            .collect(Collectors.toList());

        return suitableRooms.isEmpty() ? null : suitableRooms.get(0);
    }

    private boolean isAvailable(MeetingRoom room, Interval interval) {
        synchronized (room) {
            for (Meeting meeting : room.getBookedMeetings()) {
                if (meeting.getInterval().overlaps(interval)) {
                    return false;
                }
            }
            return true;
        }
    }
}
