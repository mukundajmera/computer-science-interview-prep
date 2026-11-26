from interval import Interval
from user import User
from meeting_room import MeetingRoom
from meeting import Meeting
from allocation_strategy import BestFitAllocationStrategy
from notification import NotificationListener
from scheduler import MeetingRoomScheduler

class PrintNotificationListener(NotificationListener):
    def on_meeting_booked(self, meeting: Meeting):
        print(f"Meeting booked: {meeting.title} in {meeting.room.id}")

    def on_meeting_cancelled(self, meeting: Meeting):
        print(f"Meeting cancelled: {meeting.title}")

def main():
    strategy = BestFitAllocationStrategy()
    scheduler = MeetingRoomScheduler(strategy)
    
    scheduler.add_notification_listener(PrintNotificationListener())

    room1 = MeetingRoom("R1", 10, ["Projector", "Whiteboard"])
    room2 = MeetingRoom("R2", 4, ["Whiteboard"])
    
    scheduler.add_room(room1)
    scheduler.add_room(room2)

    u1 = User("U1", "Alice", "alice@example.com")
    u2 = User("U2", "Bob", "bob@example.com")

    scheduler.book_meeting("Design Sync", 3, Interval(100, 200), ["Whiteboard"], [u1, u2])

if __name__ == "__main__":
    main()
