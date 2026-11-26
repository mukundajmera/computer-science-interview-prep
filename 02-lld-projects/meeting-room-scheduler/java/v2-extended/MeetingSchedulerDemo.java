import java.util.Arrays;
import java.util.Collections;

public class MeetingSchedulerDemo {
    public static void main(String[] args) {
        RoomAllocationStrategy strategy = new BestFitAllocationStrategy();
        MeetingRoomScheduler scheduler = new MeetingRoomScheduler(strategy);

        scheduler.addNotificationListener(new NotificationListener() {
            @Override
            public void onMeetingBooked(Meeting meeting) {
                System.out.println("Meeting booked: " + meeting.getTitle() + " in " + meeting.getRoom().getId());
            }

            @Override
            public void onMeetingCancelled(Meeting meeting) {
                System.out.println("Meeting cancelled: " + meeting.getTitle());
            }
        });

        MeetingRoom room1 = new MeetingRoom("R1", 10, Arrays.asList("Projector", "Whiteboard"));
        MeetingRoom room2 = new MeetingRoom("R2", 4, Arrays.asList("Whiteboard"));
        scheduler.addRoom(room1);
        scheduler.addRoom(room2);

        User u1 = new User("U1", "Alice", "alice@example.com");
        User u2 = new User("U2", "Bob", "bob@example.com");

        // [100, 200)
        scheduler.bookMeeting("Design Sync", 3, new Interval(100, 200), Collections.singletonList("Whiteboard"), Arrays.asList(u1, u2));
    }
}
