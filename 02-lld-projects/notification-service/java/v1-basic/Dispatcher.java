import java.util.HashMap;
import java.util.Map;

public class Dispatcher {
    private Map<String, Channel> channels;

    public Dispatcher() {
        channels = new HashMap<>();
        channels.put("EMAIL", new EmailChannel());
        channels.put("SMS", new SMSChannel());
    }

    public void setChannel(String type, Channel channel) {
        channels.put(type, channel);
    }

    public boolean dispatch(Notification notification) {
        Channel channel = channels.get(notification.getChannelType());
        if (channel != null) {
            return channel.send(notification);
        }
        return false;
    }
}
