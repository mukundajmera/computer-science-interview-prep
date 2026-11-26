public class EmailChannel implements Channel {
    @Override
    public boolean send(Notification notification) {
        return !notification.getUserId().equals("fail_first");
    }
}
