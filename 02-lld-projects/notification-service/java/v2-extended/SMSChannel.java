public class SMSChannel implements Channel {
    @Override
    public boolean send(Notification notification) {
        return true;
    }
}
