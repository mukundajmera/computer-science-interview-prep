import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

public class UserPreferenceMatrix {
    private Map<String, Map<String, List<String>>> preferences = new ConcurrentHashMap<>();

    public void setPreference(String userId, String notificationType, List<String> channels) {
        preferences.computeIfAbsent(userId, k -> new ConcurrentHashMap<>())
                   .put(notificationType, new ArrayList<>(channels));
    }

    public List<String> getPreferredChannels(String userId, String notificationType) {
        Map<String, List<String>> userPrefs = preferences.get(userId);
        if (userPrefs != null) {
            List<String> channels = userPrefs.get(notificationType);
            if (channels != null) {
                return channels;
            }
        }
        return Collections.singletonList("EMAIL");
    }
}
