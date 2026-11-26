public interface NotificationListener {
    void onMeetingBooked(Meeting meeting);
    void onMeetingCancelled(Meeting meeting);
    void onMeetingRescheduled(Meeting meeting);
}
